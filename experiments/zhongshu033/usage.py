"""Runnable public factory/table/plot example on the first 1000 real raw bars."""

from chanlab.algo.bi import BiSeries
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.zhongshu import ZhongshuSeries
from experiments.zhongshu033.validate import OUT, load_raw

raw_all = load_raw()
raw = KlineTSeries(tuple(raw_all)[:1000], context=raw_all.context)
merged = MergedKlineSeries.derive_from(raw, {"initialization": "UP"}, "memo015")
fx = FenxingSeries.derive_from(merged, {}, "memo019")
bi = BiSeries.derive_from(fx, {}, "memo029")
xd = XianduanSeries.derive_from(bi)
zs = ZhongshuSeries.derive_from(xd)
table = zs.to_chan_table(ChanTable.from_source_series(raw, raw.context), "zs:weak")
assert ZhongshuSeries.from_chan_table(table, "zs:weak") is zs
frame = zs.to_dataframe()
print(
    "raw/merged/FX/Bi/XD/ZS:", len(raw), len(merged), len(fx), len(bi), len(xd), len(zs)
)
print("DataFrame shape:", frame.shape)
print("unformed source positions:", zs.unresolved_ranges())
if len(zs):
    print("explain(0):", zs.explain(0))
fig = zs.plot(raw_start=0, raw_stop=200, volume=False, market="China")
fig.write_html(OUT / "usage.html", include_plotlyjs="charts/plotly.min.js")
