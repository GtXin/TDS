"""Load frozen variants by verified file path and compare common inputs."""
import importlib.util
import hashlib
import json
import random
import sys
from pathlib import Path
from verify import raw_from
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.merged_kline import MergedKlineSeries

root=Path(__file__).resolve().parent
modules=[]
for name in ('baseline','python_pro'):
    path=root/name/'bi.py'
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);modules.append(mod)
count=0
for seed in range(200):
    rng=random.Random(seed); values=[rng.randint(0,20) for _ in range(33)]
    raw=raw_from([(v,v+1) for v in values]); merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015'); source=FenxingSeries.derive_from(merged,{},'019')
    outputs=[]
    for mod in modules:
        report=mod.BiSeries.derive_candidates(source,{},'020')
        outputs.append({tuple(s.config['route']) for g in report['groups'].values() for s in g})
    assert outputs[0]==outputs[1];count+=1
# Review correction: baseline accepted route metadata disagreeing with items.
from dataclasses import replace
probe_source=source
probe=None
for mod in modules:
    r=mod.BiSeries.derive_candidates(probe_source,{},'020')
    if r['groups']: probe=next(iter(r['groups'].values()))[0];break
accepted=[]
if probe:
    for mod in modules:
        r=mod.BiSeries.derive_candidates(probe_source,{},'020');s=next(iter(r['groups'].values()))[0]
        try: replace(s,config={'route':(999,)})
        except ValueError: accepted.append(False)
        else: accepted.append(True)
result={'common_inputs':count,'route_sets_equal':True,'accepted_corrupt_route_metadata':accepted,'files':{name:{'path':str(root/name/'bi.py'),'sha256':hashlib.sha256((root/name/'bi.py').read_bytes()).hexdigest()} for name in ('baseline','python_pro')},'limitation':'sequential continuation with prior skill exposure; no causal skill claim'}
(root/'comparison.json').write_text(json.dumps(result,indent=2));print(result)
