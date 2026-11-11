"""Run one frozen implementation in an isolated process with verified path."""
import importlib.util,sys,json,random
from pathlib import Path
from verify import raw_from
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
p=Path(sys.argv[1]).resolve();spec=importlib.util.spec_from_file_location('snapshot',p);mod=importlib.util.module_from_spec(spec);sys.modules['snapshot']=mod;spec.loader.exec_module(mod)
results=[]
for seed in range(200):
 rng=random.Random(seed);raw=raw_from([(v,v+1) for v in [rng.randint(0,20) for _ in range(33)]],seed)
 m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015');fx=FenxingSeries.derive_from(m,{},'019')
 for mode in ('strong','weak'):
  s=mod.BiSeries.derive_from(fx,{'distance_mode':mode},'029');route=() if not len(s) else (s[0].start_fenxing_index,)+tuple(x.end_fenxing_index for x in s)
  results.append({'seed':seed,'mode':mode,'route':route,'evidence':[{k:v for k,v in e.items()} for e in s.trace]})
print(json.dumps({'imported':str(p),'results':results}))
