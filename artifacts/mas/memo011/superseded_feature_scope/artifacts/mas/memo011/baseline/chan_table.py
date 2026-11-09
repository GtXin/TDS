"""Raw-axis ChanTable interchange; detection and feature reconstruction are deferred."""
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from types import MappingProxyType

COLUMNS = ('raw_index', 'timestamp', 'symbol', 'period', 'source', 'open', 'high', 'low', 'close', 'volume', 'mk_ids', 'mk_direction', 'mk_start_ids', 'mk_end_ids', 'fx_ids', 'fx_kind', 'fx_start_ids', 'fx_end_ids', 'fx_anchor_ids', 'bi_ids', 'bi_direction', 'bi_start_ids', 'bi_end_ids', 'xd_ids', 'xd_direction', 'xd_start_ids', 'xd_end_ids', 'zs_ids', 'zs_lower', 'zs_upper', 'zs_start_ids', 'zs_end_ids', 'zou_ids', 'zou_kind', 'zou_start_ids', 'zou_end_ids', 'bc_ids', 'bc_kind', 'bsp_ids', 'bsp_side', 'bsp_category')

@dataclass(frozen=True)
class Kline:
    symbol: str
    period: str
    source: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self):
        self.validate()

    def validate(self):
        if not all(isinstance(x, str) and x for x in (self.symbol,self.period,self.source)):
            raise ValueError("required provenance")
        if self.timestamp.utcoffset() != timedelta(0):
            raise ValueError("UTC timestamp required")
        values = (self.open,self.high,self.low,self.close,self.volume)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("finite OHLCV required")
        if not self.low <= min(self.open,self.close) <= max(self.open,self.close) <= self.high or self.volume < 0:
            raise ValueError("invalid OHLCV")

@dataclass(frozen=True)
class KlineTSeries:
    klines: tuple[Kline, ...]

    def __post_init__(self):
        object.__setattr__(self,"klines",tuple(self.klines))
        self.validate()

    def validate(self):
        if not self.klines:
            raise ValueError("empty series")
        for i,bar in enumerate(self.klines):
            bar.validate()
            if (bar.symbol,bar.period) != (self.klines[0].symbol,self.klines[0].period):
                raise ValueError("mixed instrument/period")
            if i and bar.timestamp <= self.klines[i-1].timestamp:
                raise ValueError("unordered timestamps")

    def __len__(self):
        return len(self.klines)

    def __getitem__(self,key):
        return self.klines[key]

    def __iter__(self):
        return iter(self.klines)

class ChanTable:
    def __init__(self, rows, context=None):
        self.rows = tuple(MappingProxyType(dict(r)) for r in rows)
        self.context = MappingProxyType(dict(context or {}))
        self.feature_series = MappingProxyType({})
        bars = []
        for i,r in enumerate(self.rows):
            if tuple(r) != COLUMNS or r["raw_index"] != str(i):
                raise ValueError("schema/raw index mismatch")
            for name in COLUMNS[10:]:
                value = r[name]
                if name.endswith("_ids") and value != "NA":
                    ids = json.loads(value)
                    if not isinstance(ids,list) or any(type(v) is not int for v in ids) or len(ids)!=len(set(ids)):
                        raise ValueError("integer ID list required")
            bars.append(Kline(r["symbol"],r["period"],r["source"],datetime.fromisoformat(r["timestamp"].replace("Z","+00:00")),*(float(r[k]) for k in ("open","high","low","close","volume"))))
        self.source_series = KlineTSeries(tuple(bars))
        self.memberships = MappingProxyType({k:tuple(self._ids(r[k]) for r in self.rows) for k in COLUMNS if k.endswith("_ids") and not any(x in k for x in ("_start_","_end_","_anchor_"))})
        for attr,suffix in (("start_ids","_start_ids"),("end_ids","_end_ids"),("anchor_ids","_anchor_ids")):
            setattr(self,attr,MappingProxyType({k:tuple(self._ids(r[k]) for r in self.rows) for k in COLUMNS if k.endswith(suffix)}))

    @staticmethod
    def _ids(value):
        return None if value == "NA" else tuple(json.loads(value))

    @classmethod
    def read_csv(cls,path,context_path=None):
        context = {}
        if context_path:
            with Path(context_path).open(newline="") as f:
                context = dict(list(csv.reader(f))[1:])
        with Path(path).open(newline="") as f:
            return cls(list(csv.DictReader(f)),context)

    def write_csv(self,path,context_path=None):
        with Path(path).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(self.rows)
        if context_path:
            with Path(context_path).open("w",newline="") as f:
                w=csv.writer(f)
                w.writerow(("key","value"))
                w.writerows(self.context.items())
