"""Isolated executable interpretation of memo020 b–d; no production imports."""
from copy import deepcopy
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
counts = {"first": 0, "extension": 0, "reverse": 0, "weaker": 0, "scan_calls": 0}

def source(lows, width=1):
    return [(x, x + width) for x in lows]

def fractals(v):
    assert all(lo <= hi for lo, hi in v)
    assert all((a[0] < b[0] and a[1] < b[1]) or (a[0] > b[0] and a[1] > b[1]) for a,b in zip(v,v[1:]))
    return [(i, "top" if v[i][0] > v[i-1][0] else "bottom") for i in range(1,len(v)-1)
            if all(v[i][k] > v[i-1][k] and v[i][k] > v[i+1][k] for k in (0,1))
            or all(v[i][k] < v[i-1][k] and v[i][k] < v[i+1][k] for k in (0,1))]

def center(fx, x): return fx[x][0]
def kind(fx, x): return fx[x][1]
def price(v, fx, x): return v[center(fx,x)][1 if kind(fx,x)=="top" else 0]
def compare(v,fx,x,f):
    assert kind(fx,x)==kind(fx,f)
    diff=price(v,fx,f)-price(v,fx,x)
    return (diff>0)-(diff<0) if kind(fx,f)=="top" else (diff<0)-(diff>0)
def bounds(v,fx,a,f):
    t,b=(a,f) if kind(fx,a)=="top" else (f,a)
    return v[center(fx,b)][0],v[center(fx,t)][1]
def full(v,fx,a,b):
    i,j=center(fx,a),center(fx,b)
    if i>=j or kind(fx,a)==kind(fx,b) or j-i<4:return False
    t,d=(a,b) if kind(fx,a)=="top" else (b,a)
    return (v[center(fx,t)][1]>v[center(fx,d)][1]
        and v[center(fx,d)][0]<v[center(fx,t)][0]
        and all(lo>=v[center(fx,d)][0] and hi<=v[center(fx,t)][1] for lo,hi in v[i:j+1]))
def first(v,fx,s,f):
    counts["first"]+=1
    i,j=center(fx,s),center(fx,f)
    result=j-i>=4 and (max(hi for lo,hi in v[i:j+1])==price(v,fx,f) if kind(fx,f)=="top" else min(lo for lo,hi in v[i:j+1])==price(v,fx,f))
    assert result==full(v,fx,s,f)
    return result
def extension(v,fx,a,b,f):
    counts["extension"]+=1
    assert full(v,fx,a,b) and compare(v,fx,b,f)>=0
    lower,upper=bounds(v,fx,a,f)
    result=all(lo>=lower and hi<=upper for lo,hi in v[center(fx,b)+1:center(fx,f)+1])
    assert result==full(v,fx,a,f)
    return result
def reverse(v,fx,b,f):
    counts["reverse"]+=1
    i,j=center(fx,b),center(fx,f)
    lower,upper=bounds(v,fx,b,f)
    result=j-i>=4 and all(lo>=lower and hi<=upper for lo,hi in v[i:j+1])
    assert result==full(v,fx,b,f)
    return result

def validate(v,fx,s,before):
    pairs=s["R"]+([s["cache"]] if s["cache"] else [])
    assert all(full(v,fx,*pair) for pair in pairs)
    assert all(a[1]==b[0] and kind(fx,a[0])!=kind(fx,b[0]) for a,b in zip(pairs,pairs[1:]))
    assert s["R"][:len(before)]==before and s["cursor"]==len(fx)
    assert (s["S"] is None)==(len(fx)==0)
    assert not s["R"] or s["cache"] is not None
    if s["cache"]:assert s["S"]==s["cache"][1]

def scan(v,previous=None,reduced=True):
    counts["scan_calls"]+=1
    fx=fractals(v)
    s=deepcopy(previous) if previous is not None else {"R":[],"cache":None,"S":None,"cursor":0,"old_v":[],"old_fx":[]}
    assert v[:len(s["old_v"])]==s["old_v"], "merged prefix changed"
    assert fx[:len(s["old_fx"])]==s["old_fx"], "FX prefix changed"
    before=deepcopy(s["R"])
    if s["S"] is None and s["cursor"]<len(fx):
        assert not s["R"] and s["cache"] is None
        s["S"]=s["cursor"];s["cursor"]+=1
    while s["cursor"]<len(fx):
        f=s["cursor"];s["cursor"]+=1
        old=deepcopy(s["R"])
        if s["cache"] is None:
            start=s["S"]
            if kind(fx,start)==kind(fx,f):
                if compare(v,fx,start,f)>0:s["S"]=f
            elif (first(v,fx,start,f) if reduced else full(v,fx,start,f)):
                s["cache"]=(start,f);s["S"]=f
        else:
            a,b=s["cache"]
            if kind(fx,b)==kind(fx,f):
                if compare(v,fx,b,f)<0:
                    counts["weaker"]+=1;assert not full(v,fx,a,f)
                elif (extension(v,fx,a,b,f) if reduced else full(v,fx,a,f)):
                    s["cache"]=(a,f);s["S"]=f
            elif (reverse(v,fx,b,f) if reduced else full(v,fx,b,f)):
                s["R"].append((a,b));s["cache"]=(b,f);s["S"]=f
        assert s["R"][:len(old)]==old
    validate(v,fx,s,before)
    s["old_v"]=v;s["old_fx"]=fx
    return s

def view(s):return {k:s[k] for k in ("R","cache","S","cursor")}
MAIN=[9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7]
OPEN=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]
fixtures={
 "empty":[],"one_bar":source([9]),"no_fx":source([9,10]),"one_fx":source([9,10,0]),
 "main19":source(MAIN),"open21":source(OPEN),"equal_start":source([9,10,0,10,9]),
 "equal_end":source([1,0,3,6,9,10,8,5,8,10,9]),
 "reverse_end_bound":source([1,0,3,6,9,12,5,-2,3,8,6,4,2,-1,0]),
 "extend15":source([1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],2),
 "zero_height":source(MAIN,0),
}
fixtures.update({"mirror_"+n:[(-hi,-lo) for lo,hi in v] for n,v in list(fixtures.items())})
results={}
for n,v in fixtures.items():
    got=scan(v);ref=scan(v,reduced=False)
    assert view(got)==view(ref)
    results[n]=view(got)
assert results["main19"]["R"]==[(4,7)] and results["main19"]["cache"]==(7,8)
assert results["open21"]["R"]==[(0,1)] and results["open21"]["cache"]==(1,2)
assert results["equal_start"]["S"]==0 and results["equal_end"]["cache"]==(0,3)
continuations=[]
for n in ("main19","open21"):
    v=fixtures[n]
    for cut in range(len(v)+1):
        prefix=scan(v[:cut]);saved=deepcopy(prefix)
        continued=scan(v,prefix)
        assert view(continued)==results[n] and prefix==saved
        assert view(scan(v,continued))==results[n]
        continuations.append({"case":n,"cut":cut,"result":view(continued)})
# Check immutable final record after a later successful cache extension.
initial=scan(source(MAIN));later=scan(source(MAIN+[9,10,12,11]),initial)
assert later["R"]==initial["R"]==[(4,7)] and later["cache"]==(7,10)
assert view(later)==view(scan(source(MAIN+[9,10,12,11])))
changed=source(MAIN);changed[0]=(90,91)
try:scan(changed,initial)
except AssertionError:changed_rejected=True
else:raise AssertionError("changed prefix accepted")
report={"scope":"Isolated interval/fractal pseudocode interpretation; trusted checkpoints only; no production API/raw provenance implementation.","counts":counts,"fixtures":results,"all_prefix_splits":continuations,"late_extension":view(later),"changed_prefix_rejected":changed_rejected,"final_R_immutable":True,"eof_keeps_cache":True}
(HERE/'decomposition-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({"fixtures":len(fixtures),"split_points":len(continuations),"counts":counts,"main19":results['main19'],"open21":results['open21'],"passed":True}))
