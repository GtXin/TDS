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
(ROOT/"real.pid").write_text(str(os.getpid()))
sample=Path('samples/chan_table');paths=[next(sample.glob('*chan_table*.csv')),next(sample.glob('*context*.csv'))]
raw=KlineTSeries.read_csv(*paths)
m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015')
fx=FenxingSeries.derive_from(m,{},'memo019')
results={};timing=[]
import faulthandler
faulthandler.dump_traceback_later(45,repeat=True)
previous=json.loads((ROOT/"scaling.json").read_text())
expected={(x["fx"],x["bi"],x["xd"]):x["segments"] for x in previous["records"]}
routes={}
for count in (100,1000,3000):
 stop=m[fx[count-1].source_start+2].source_stop
 prefix=KlineTSeries(tuple(raw)[:stop],context=raw.context)
 for bm in ('weak','strong'):
  for xm in ('weak','strong'):
   runs=[]
   for repeat in range(3):
    t=time.perf_counter();mm=MergedKlineSeries.derive_from(prefix,{'initialization':'UP'},'memo015');t1=time.perf_counter();ff=FenxingSeries.derive_from(mm,{},'memo019');t2=time.perf_counter();bi=BiSeries.derive_from(ff,{'distance_mode':bm},'memo029');t3=time.perf_counter();print('stage',count,bm,xm,repeat,'Bi',len(bi),flush=True);core=recognize(XianduanSeries._prices(bi),xm);t4=time.perf_counter();print('core',t4-t3,flush=True);s=XianduanSeries.derive_from(bi,{'xd_mode':xm});t5=time.perf_counter();print('factory',t5-t4,flush=True);assert len(s)==expected[count,bm,xm];route=tuple((x.source_start,x.source_stop) for x in s);assert routes.setdefault((count,bm,xm),route)==route;print('repeat and independently validated objective count PASS',flush=True)
    assert core['confirmed']==[(x.source_start,x.source_stop) for x in s]
    runs.append(dict(merged=t1-t,fenxing=t2-t1,bi=t3-t2,xd_core=t4-t3,xd_factory=t5-t4,end_to_end=t3-t+t5-t4))
   timing.append(dict(fx=count,bi=bm,xd=xm,strokes=len(bi),segments=len(s),runs=runs,medians={k:statistics.median(r[k] for r in runs) for k in runs[0]}))
   print('timing',count,bm,xm,len(s),flush=True)
   (ROOT/'scaling-final.json').write_text(json.dumps({'records':timing,'prior_independent_reference':'scaling.json and real-progress.txt: all36runs validated by full-list event checks and backward objective DP; final runs compare count and deterministic full routes across3repetitions','environment':platform.platform(),'python':platform.python_version(),'cache':'warm files; no result cache; rebuilt upstream each repetition; load/oracle excluded','memory':'process cumulative high water including oracle','peak_rss':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2))
