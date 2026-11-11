"""Isolated snapshot evaluation; emits only JSON summary and path."""
import importlib.util
import json
import random
import sys
from pathlib import Path
from verify import raw_from
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
path=Path(sys.argv[1]).resolve();spec=importlib.util.spec_from_file_location('snapshot',path);mod=importlib.util.module_from_spec(spec);sys.modules['snapshot']=mod;spec.loader.exec_module(mod)
outputs=[]
for seed in range(200):
    rng=random.Random(seed);raw=raw_from([(v,v+1) for v in [rng.randint(0,20) for _ in range(33)]])
    merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015');source=FenxingSeries.derive_from(merged,{},'019')
    report=mod.BiSeries.derive_candidates(source,{},'020')
    outputs.append(sorted([list(s.config['route']) for g in report['groups'].values() for s in g]))
print(json.dumps({'imported':str(Path(mod.__file__).resolve()),'outputs':outputs}))
