"""Fresh four-combination real CC runs and repeated nested-prefix timing."""
import json,time,statistics,platform,resource,hashlib,sys
from pathlib import Path
from dataclasses import asdict
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
from chanlab.algo.xianduan import XianduanSeries,recognize
from chanlab.algo.chan_table import ChanTable
from chanlab.data.fenxing_table import plain
from validate import ROOT,check
import os
(ROOT/"full.pid").write_text(str(os.getpid()))
sample=Path('samples/chan_table');paths=[next(sample.glob('*chan_table*.csv')),next(sample.glob('*context*.csv'))]
raw=KlineTSeries.read_csv(*paths)
m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015')
fx=FenxingSeries.derive_from(m,{},'memo019')
results={};timing=[]
for bm in ('weak','strong'):
 bi=BiSeries.derive_from(fx,{'distance_mode':bm},'memo029')
 for xm in ('weak','strong'):
  key=f'bi-{bm}_xd-{xm}';s=XianduanSeries.derive_from(bi,{'xd_mode':xm})
  table=s.to_chan_table(ChanTable.from_source_series(raw,raw.context),key)
  folder=ROOT/'full'/key;folder.mkdir(parents=True,exist_ok=True);table.write_csv(folder/'table.csv',folder/'context.csv');r=ChanTable.read_csv(folder/'table.csv',folder/'context.csv');assert r.feature_series[key].items==s.items
  results[key]={'raw':len(raw),'merged':len(m),'fx':len(fx),'pens':len(bi),'segments':len(s),'records':[{**asdict(x),'confirmed_at':x.confirmed_at.isoformat()} for x in s],'trace':plain(s.trace),'tail':s.tail}
  print('full',key,len(s),flush=True)
(ROOT/'full-result.json').write_text(json.dumps(results,indent=2))
(ROOT/'source-hashes.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[Path('docs/memo/memoWX_029_Chan_bi.md'),Path('docs/memo/memoWX_030_Chan_xianduan.md')]},indent=2))
