"""Raw master table; feature calculations are deferred."""

import csv
import math
from collections.abc import Iterable, Iterator, Mapping
from datetime import datetime, timedelta
from pathlib import Path
from types import MappingProxyType

COLUMNS = (
    "raw_index",
    "timestamp",
    "symbol",
    "period",
    "source",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "mk_ids",
    "mk_direction",
    "mk_start_ids",
    "mk_end_ids",
    "fx_ids",
    "fx_kind",
    "fx_start_ids",
    "fx_end_ids",
    "fx_anchor_ids",
    "bi_ids",
    "bi_direction",
    "bi_start_ids",
    "bi_end_ids",
    "xd_ids",
    "xd_direction",
    "xd_start_ids",
    "xd_end_ids",
    "zs_ids",
    "zs_lower",
    "zs_upper",
    "zs_start_ids",
    "zs_end_ids",
    "zou_ids",
    "zou_kind",
    "zou_start_ids",
    "zou_end_ids",
    "bc_ids",
    "bc_kind",
    "bsp_ids",
    "bsp_side",
    "bsp_category",
)


class ChanTable:
    """Immutable master table of raw OHLCV rows and provenance context."""

    def __init__(
        self,
        rows: Iterable[Mapping[str, str]],
        context: Mapping[str, str] | None = None,
    ) -> None:
        self.rows = tuple(MappingProxyType(dict(row)) for row in rows)
        self.context = MappingProxyType(dict(context or {}))
        self.validate()

    def validate(self) -> None:
        """Reject invalid raw rows and nonempty reserved feature columns."""
        if not self.rows:
            raise ValueError("empty table")
        previous: datetime | None = None
        instrument: tuple[str, str] | None = None
        for i, row in enumerate(self.rows):
            if tuple(row) != COLUMNS or row["raw_index"] != str(i):
                raise ValueError("schema/raw index mismatch")
            if any(row[key] != "NA" for key in COLUMNS[10:]):
                raise ValueError("reserved feature columns must be NA")
            if any(
                not row[key].strip() or row[key] == "NA"
                for key in ("symbol", "period", "source")
            ):
                raise ValueError("required provenance")
            identity = (row["symbol"], row["period"])
            if instrument is not None and instrument != identity:
                raise ValueError("mixed instrument/period")
            instrument = identity
            timestamp = datetime.fromisoformat(row["timestamp"])
            if timestamp.utcoffset() != timedelta(0):
                raise ValueError("UTC timestamp required")
            if previous is not None and timestamp <= previous:
                raise ValueError("unordered timestamps")
            previous = timestamp
            o, h, low, c, v = (
                float(row[key]) for key in ("open", "high", "low", "close", "volume")
            )
            if (
                not all(math.isfinite(x) for x in (o, h, low, c, v))
                or not low <= min(o, c) <= max(o, c) <= h
                or v < 0
            ):
                raise ValueError("invalid OHLCV")

    @classmethod
    def read_csv(
        cls, path: str | Path, context_path: str | Path | None = None
    ) -> "ChanTable":
        """Read a master CSV and optional key/value context CSV."""
        context = {}
        if context_path is not None:
            with Path(context_path).open(newline="") as stream:
                reader = csv.reader(stream)
                if next(reader, None) != ["key", "value"]:
                    raise ValueError("context schema mismatch")
                for pair in reader:
                    if len(pair) != 2 or not pair[0] or pair[0] in context:
                        raise ValueError("invalid context entry")
                    context[pair[0]] = pair[1]
        with Path(path).open(newline="") as stream:
            reader2 = csv.DictReader(stream)
            if tuple(reader2.fieldnames or ()) != COLUMNS:
                raise ValueError("schema mismatch")
            return cls(reader2, context)

    def write_csv(
        self, path: str | Path, context_path: str | Path | None = None
    ) -> None:
        """Write validated rows and optional provenance context."""
        self.validate()
        with Path(path).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)
        if context_path is not None:
            with Path(context_path).open("w", newline="") as stream:
                writer2 = csv.writer(stream)
                writer2.writerow(("key", "value"))
                writer2.writerows(self.context.items())

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[Mapping[str, str]]:
        return iter(self.rows)

    def __getitem__(self, index: int) -> Mapping[str, str]:
        return self.rows[index]
