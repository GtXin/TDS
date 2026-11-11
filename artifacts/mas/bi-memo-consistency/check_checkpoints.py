"""Finite Q-contract model, independent of production Bi/raw-source APIs."""
from dataclasses import dataclass, replace, FrozenInstanceError
from pathlib import Path
import ast, json

HERE=Path(__file__).resolve().parent
# Load arithmetic helpers ONLY. Do not run the historical top-level report writer.
prior=HERE.parent/'bi-tree-details/check_decomposition.py'
tree=ast.parse(prior.read_text())
names={'source','fractals','center','kind','price','compare','bounds','full'}
space={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(prior),'exec'),space)
source,fractals,center,kind,price,compare,bounds,full=(space[n] for n in ('source','fractals','center','kind','price','compare','bounds','full'))
KEY=('synthetic-intervals','unit-position','old-bi-six-conditions','exact-price','Q-contract-v1')
@dataclass(frozen=True)
class Context:
    bars: tuple
    fx: tuple
    key: tuple
@dataclass(frozen=True)
class Q:
    R: tuple
    Bi002: tuple|None
    S: int|None
    E: None
    next_position: int
    source_context: Context
    evidence: tuple
    unresolved: tuple
issued=set()                         # Models trusted in-process checkpoints only.
counts={'calls':0,'success':0,'expected_rejections':0,'first':0,'extension':0,'reverse':0}

def ranged(v,i,j):
    return min(lo for lo,hi in v[i:j+1]),max(hi for lo,hi in v[i:j+1])
def check_first(v,fx,s,f):
    counts['first']+=1;i,j=center(fx,s),center(fx,f);gap=j-i
    if gap<4:ok=False;e=('first-gap',gap)
    elif kind(fx,f)=='top':
        actual=max(hi for lo,hi in v[i:j+1]);ok=actual==price(v,fx,f);e=('first-high',gap,i,j,actual,price(v,fx,f))
    else:
        actual=min(lo for lo,hi in v[i:j+1]);ok=actual==price(v,fx,f);e=('first-low',gap,i,j,actual,price(v,fx,f))
    assert ok==full(v,fx,s,f)
    return ok,e

def check_extension(v,fx,a,b,f):
    counts['extension']+=1
    assert full(v,fx,a,b) and compare(v,fx,b,f)>=0
    i,j=center(fx,b)+1,center(fx,f);lo,hi=ranged(v,i,j);lower,upper=bounds(v,fx,a,f)
    ok=lo>=lower and hi<=upper
    assert ok==full(v,fx,a,f)
    return ok,('extension',i,j,lo,hi,lower,upper)

def check_reverse(v,fx,b,f):
    counts['reverse']+=1;i,j=center(fx,b),center(fx,f);gap=j-i
    if gap<4:ok=False;e=('reverse-gap',gap)
    else:
        lo,hi=ranged(v,i,j);lower,upper=bounds(v,fx,b,f);ok=lo>=lower and hi<=upper;e=('reverse',gap,i,j,lo,hi,lower,upper)
    assert ok==full(v,fx,b,f)
    return ok,e

def unresolved(v,fx,R,cache):
    if cache is None:return ((0,len(v)),)
    first=R[0][0] if R else cache[0]
    return tuple((i,j) for i,j in ((0,center(fx,first)),(center(fx,cache[1])+1,len(v))) if i<j)

def validate(v,fx,q,before):
    assert len(q.R)>=len(before) and q.R[:len(before)]==before
    assert q.next_position==len(fx) and q.E is None
    pairs=q.R+((q.Bi002,) if q.Bi002 else ())
    assert all(full(v,fx,*p) for p in pairs)
    assert all(a[1]==b[0] and kind(fx,a[0])!=kind(fx,b[0]) for a,b in zip(pairs,pairs[1:]))
    assert q.S is None if not fx else q.S in range(len(fx))
    assert not q.R or q.Bi002 is not None
    if q.Bi002:assert q.S==q.Bi002[1]
    assert q.source_context.bars==tuple(v) and q.source_context.fx==tuple(fx)
    assert q.unresolved==unresolved(v,fx,q.R,q.Bi002)
    assert len(q.evidence)==len(fx)
    assert tuple(e[0] for e in q.evidence)==tuple(range(len(fx)))

def process(v,previous_state=None,key=KEY):
    counts['calls']+=1
    v=tuple(v)
    if not v:raise ValueError('merged must be nonempty')
    try:fx=tuple(fractals(v))
    except AssertionError:raise ValueError('invalid merged')
    if previous_state is None:R=[];cache=None;S=None;cursor=0;evidence=[]
    else:
        q=previous_state
        if q not in issued:raise ValueError('unissued checkpoint')
        ctx=q.source_context
        if key!=ctx.key:raise ValueError('stable context changed')
        if len(v)<len(ctx.bars) or v[:len(ctx.bars)]!=ctx.bars:raise ValueError('merged prefix changed')
        if len(fx)<len(ctx.fx) or fx[:len(ctx.fx)]!=ctx.fx:raise ValueError('FX prefix changed')
        R=list(q.R);cache=q.Bi002;S=q.S;cursor=q.next_position;evidence=list(q.evidence)
    before=tuple(R)
    if S is None and cursor<len(fx):
        S=cursor;cursor+=1;evidence.append((S,center(fx,S),kind(fx,S),'initialize',price(v,fx,S)))
    while cursor<len(fx):
        f=cursor;cursor+=1;oldS,oldcache=S,cache
        if cache is None:
            if kind(fx,S)==kind(fx,f):
                relation=compare(v,fx,S,f);e=('initial-compare',price(v,fx,S),price(v,fx,f),relation)
                if relation>0:S=f
                action='replace-start' if relation>0 else 'keep-start'
            else:
                ok,e=check_first(v,fx,S,f);action='accept-first' if ok else 'reject-first'
                if ok:cache=(S,f);S=f
        else:
            a,b=cache
            if kind(fx,b)==kind(fx,f):
                relation=compare(v,fx,b,f)
                if relation<0:
                    assert not full(v,fx,a,f)
                    action='weaker-end';e=('end-compare',price(v,fx,b),price(v,fx,f),relation)
                else:
                    ok,e=check_extension(v,fx,a,b,f);action='extend' if ok else 'reject-extension'
                    if ok:cache=(a,f);S=f
            else:
                ok,e=check_reverse(v,fx,b,f);action='commit-rotate' if ok else 'reject-reverse'
                if ok:R.append((a,b));cache=(b,f);S=f
        evidence.append((f,center(fx,f),kind(fx,f),oldS,oldcache,action,e))
    q=Q(tuple(R),cache,S,None,cursor,Context(v,fx,key),tuple(evidence),unresolved(v,fx,R,cache))
    validate(v,fx,q,before);issued.add(q);counts['success']+=1
    return q

MAIN=[9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7]
OPEN=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]
fixtures={
 'one_bar':source([9]),'no_fx':source([9,10]),'one_fx':source([9,10,0]),
 'main19':source(MAIN),'open21':source(OPEN),'equal_start':source([9,10,0,10,9]),
 'equal_end':source([1,0,3,6,9,10,8,5,8,10,9]),
 'reverse_end_bound':source([1,0,3,6,9,12,5,-2,3,8,6,4,2,-1,0]),
 'extend15':source([1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],2),
 'zero_height':source(MAIN,0)}
fixtures.update({'mirror_'+n:[(-hi,-lo) for lo,hi in v] for n,v in list(fixtures.items())})
results={n:process(v) for n,v in fixtures.items()}
# Check ALL returned fields, not only the old projected view(R/cache/S/cursor).
all_splits=[]
for name in ('main19','open21'):
    v=fixtures[name]
    for cut in range(1,len(v)+1):
        prefix=process(v[:cut]);before=repr(prefix)
        got=process(v,prefix)
        assert got==results[name] and repr(prefix)==before
        assert process(v,got)==got
        all_splits.append((name,cut))

extended=source(MAIN+[9,10,12,11]);stages=[];saved=None
for n in (2,3,11,12,15,19,23):
    old=saved;saved=process(extended[:n],saved)
    assert saved==process(extended[:n])
    if old:assert saved.R[:len(old.R)]==old.R
    stages.append({'N':n,'FX':saved.next_position,'R':saved.R,'Bi002':saved.Bi002,'S':saved.S,'E':saved.E,'evidence_count':len(saved.evidence),'unresolved':saved.unresolved,'source_merged_length':len(saved.source_context.bars)})
assert results['main19'].R==((4,7),) and saved.R==((4,7),) and saved.Bi002==(7,10)
q11=process(extended[:11]);q12=process(extended[:12],q11)
for attr in ('R','Bi002','S','E','next_position','evidence'):assert getattr(q11,attr)==getattr(q12,attr)
assert q11.unresolved!=q12.unresolved and q11.source_context!=q12.source_context
assert process(extended[:12],q12)==q12

# The frozen record and all of its reachable containers resist in-place modification.
try:q12.R=()
except FrozenInstanceError:pass
else:raise AssertionError('Q not frozen')
assert isinstance(q12.R,tuple) and isinstance(q12.evidence,tuple) and isinstance(q12.source_context.bars,tuple)
probes=[]
def reject(name,fn):
    try:fn()
    except ValueError as e:probes.append((name,str(e)));counts['expected_rejections']+=1
    else:raise AssertionError(name+' was accepted')
reject('empty_merged',lambda:process([]))
changed=source(MAIN);changed[0]=(9.25,10.25)
reject('changed_prior_merged',lambda:process(changed,results['main19']))
reject('shortened_prior_merged',lambda:process(source(MAIN[:-1]),results['main19']))
reject('changed_stable_context',lambda:process(source(MAIN),results['main19'],('different-context',)))
initial=process(source(MAIN[:5]))
reject('forged_weaker_S',lambda:process(source(MAIN),replace(initial,S=2)))

report={'scope':'Finite immutable-Q interval model. Full previous interval/FX prefix and stable model-key checks; trusted in-process checkpoints only. No production Bi, raw-provenance chain or persisted-checkpoint serialization executed.',
 'counts':counts,'nonempty_fixtures':len(fixtures),'nonempty_split_points':len(all_splits),'all_Q_fields_equal_one_shot':True,'saved_Q_not_mutated':True,'per_FX_deterministic_evidence':True,'EOF_no_persistent_event':True,'no_new_FX_context_range_refresh':True,'identical_snapshot_idempotent':True,'immutable_outer_and_inner_values':True,'stages':stages,'rejections':probes,
 'main19':{'R':results['main19'].R,'Bi002':results['main19'].Bi002,'S':results['main19'].S,'cursor':results['main19'].next_position,'unresolved':results['main19'].unresolved},
 'open21':{'R':results['open21'].R,'Bi002':results['open21'].Bi002,'S':results['open21'].S,'cursor':results['open21'].next_position,'unresolved':results['open21'].unresolved}}
(HERE/'checkpoint-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('counts','nonempty_fixtures','nonempty_split_points','all_Q_fields_equal_one_shot','no_new_FX_context_range_refresh','identical_snapshot_idempotent')},ensure_ascii=False))
