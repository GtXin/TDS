"""Isolated rolling snapshot comparison on identical full-range checked inputs."""
import sys,importlib.util,json,random
from pathlib import Path
from verify import raw_from
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
p=Path(sys.argv[1]).resolve();spec=importlib.util.spec_from_file_location('snapshot',p);mod=importlib.util.module_from_spec(spec);sys.modules['snapshot']=mod;spec.loader.exec_module(mod)
result=[]
for seed in range(200):
 rng=random.Random(seed);raw=raw_from([(v,v+1) for v in [rng.randint(0,20) for _ in range(33)]])
 m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015');f=FenxingSeries.derive_from(m,{},'019');r=mod.BiSeries.scan(f,'020')
 result.append({'R':[(x.start_fenxing_index,x.end_fenxing_index) for x in r['series']],'cache':r['cache_pair'],'start':r['pending_start'],'cursor':r['next_position']})
print(json.dumps({'imported':str(p),'results':result}))
