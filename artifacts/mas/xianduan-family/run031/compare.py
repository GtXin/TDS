"""Independent-process frozen baseline vs Python Pro production continuation."""
import json,subprocess,sys,hashlib
from pathlib import Path
from validate import ROOT,load,local,rec,ref
if len(sys.argv)>1:
 inputs=json.loads((ROOT/'comparison-input.json').read_text());out=[]
 if sys.argv[1]=='baseline':selector=load('baseline031',ROOT/'baseline-instrumented.py')
 else:
  from chanlab.algo.xianduan import recognize
 for p,mode in inputs:
  if sys.argv[1]=='baseline':
   events,_=local.scanner(p,mode,rec,ref.Reference(p));nodes=[]
   for a in range(len(p)-3):
    for b in range(a+3,len(p),2):
     nodes.extend({'root':True,'i':a,'j':b,'certificate':c} for c in events(a,b))
   pens=[{'start':{'price':p[i],'fx_position':i},'end':{'price':p[i+1],'fx_position':i+1}} for i in range(len(p)-1)]
   r=selector.solve({'xd_mode':mode,'bi_mode':'source','nodes':nodes},pens)
  else:r=recognize(p,mode)
  for w in r['witnesses']:w.pop('profile',None)
  out.append({k:r[k] for k in ('confirmed','tail','witnesses','state_digest')})
 (ROOT/f'{sys.argv[1]}-comparison.json').write_text(json.dumps(out));sys.exit()
import random
rng=random.Random(31031);inputs=[]
for seed in range(200):
 p=[100.]
 for i in range(24):p.append(p[-1]+(1 if i%2==0 else -1)*rng.randint(1,20))
 for mode in ('weak','strong'):inputs.append((p,mode))
(ROOT/'comparison-input.json').write_text(json.dumps(inputs))
for version in ('baseline','production'):subprocess.run([sys.executable,__file__,version],check=True)
a=json.loads((ROOT/'baseline-comparison.json').read_text());b=json.loads((ROOT/'production-comparison.json').read_text());assert a==b
report={'cases':len(a),'route_tail_evidence_equal':True,'profile_label_excluded':True,'processes':2,'baseline':str(ROOT/'baseline-instrumented.py'),'production':'src/chanlab/algo/xianduan.py','skill':'mas/skills/python-pro/SKILL.md','skill_version':'1.1.0','causal_claim':False}
(ROOT/'comparison.json').write_text(json.dumps(report,indent=2));print(report)
