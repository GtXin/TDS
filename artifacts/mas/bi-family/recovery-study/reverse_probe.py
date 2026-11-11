"""Probe deferred reverse choices; stop at first EOF witness, not all outputs."""
import json,runpy
from pathlib import Path
from chanlab.algo.bi import BiSeries
p=Path(__file__).resolve().parent
# Reuse the independent definition edge graph, not production pair checks.
ns=runpy.run_path(str(p/'probe.py'));fx=ns['fx'];edges=ns['edges'];initial=ns['initial']
pending=[((initial,),initial,None,initial+1)];steps=0;blocked=0;route=None
while pending and steps<100000:
    prefix,a,b,cursor=pending.pop();dead=False
    while cursor<len(fx):
        steps+=1
        if steps>100000:dead=True;break
        f=cursor;cursor+=1
        if b is None:
            if f in edges[a]:pending.append((prefix,a,None,cursor));b=f
        elif fx[f].kind==fx[b].kind:
            better=fx[f].price>fx[b].price if fx[b].kind=='top' else fx[f].price<fx[b].price
            if better:
                if f in edges[a]:b=f
                else:dead=True;blocked+=1;break
            elif fx[f].price==fx[b].price and f in edges[a]:pending.append((prefix,a,f,cursor))
        elif f in edges[b]:
            # Missing checkpoint in production: defer this reverse F, retaining
            # the PRE-accept pair so later same-type B extension can be revisited.
            pending.append((prefix,a,b,cursor))
            prefix=prefix+(b,);a,b=b,f
    if not dead and b is not None:route=prefix+(b,);break
if route:assert all(b in edges[a] for a,b in zip(route,route[1:]))
result={'complete_EOF_witness':route is not None,'states':steps,'blocked':blocked,'route':route,'stroke_count':len(route)-1 if route else 0,'limitation':'experimental additional reverse checkpoint; first witness only, not all-route or unique-selector implementation'}
(p/'reverse-checkpoint.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k!='route'})
