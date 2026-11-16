"""Executable default weak-Bi/weak-Xianduan usage example for memo031003.e."""
from pathlib import Path
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.chan_table import ChanTable
sample=Path('samples/chan_table')
raw=KlineTSeries.read_csv(next(sample.glob('*chan_table*.csv')),next(sample.glob('*context*.csv')))
raw=KlineTSeries(tuple(raw)[:1000],context=raw.context)
merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015')
fx=FenxingSeries.derive_from(merged,{},'memo019')
bi=BiSeries.derive_from(fx,{},'memo029')
xd=XianduanSeries.derive_from(bi)
assert bi.config['distance_mode']==xd.config['xd_mode']=='weak'
frame=xd.to_dataframe()
table=xd.to_chan_table(ChanTable.from_source_series(raw,raw.context),'xd:weak')
assert XianduanSeries.from_chan_table(table,'xd:weak') is xd
if len(xd):print(dict(xd.explain(0)))
fig=xd.plot(raw_start=0,raw_stop=200,volume=False,market='China')
print({'raw':len(raw),'bi':len(bi),'xd':len(xd),'unresolved_Bi_ranges':xd.unresolved_ranges(),'frame_shape':frame.shape})
