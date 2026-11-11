"""Finite two-distance Q model; no production imports or old report execution."""
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace
import ast,json
HERE=Path(__file__).resolve().parent
prior=HERE.parent/'bi-tree-details/check_decomposition.py'
names={'source','fractals','center','kind','price','compare','bounds'}
ns={};tree=ast.parse(prior.read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(prior),'exec'),ns)
source,fractals,center,kind,price,compare,bounds=(ns[n] for n in ('source','fractals','center','kind','price','compare','bounds'))
MAPPING={'strong':4,'weak':3}
KEY=('synthetic-intervals','exact-price','Q-distance-options-v1')
@dataclass(frozen=True)
class Context:
    bars:tuple
    fx:tuple
    key:tuple
    distance_mode:str
    min_gap:int
@dataclass(frozen=True)
class Q:
    R:tuple
    Bi002:tuple|None
    S:int|None
    E:None
    next_position:int
    source_context:Context
    evidence:tuple
    unresolved:tuple
issued=set()
counts={'calls':0,'success':0,'first':0,'extension':0,'reverse':0}

def resolve_mode(arg=None,previous_state=None):
    if arg is not None and (type(arg) is not str or arg not in MAPPING):
        raise ValueError('unknown distance mode')
    if previous_state is None:mode='strong' if arg is None else arg
    else:
        ctx=getattr(previous_state,'source_context',None)
        if not hasattr(ctx,'distance_mode') or not hasattr(ctx,'min_gap'):
            raise ValueError('legacy checkpoint lacks distance metadata')
        old_mode,old_gap=ctx.distance_mode,ctx.min_gap
        if type(old_mode) is not str or old_mode not in MAPPING or type(old_gap) is not int or old_gap!=MAPPING[old_mode]:
            raise ValueError('inconsistent checkpoint distance metadata')
        mode=old_mode if arg is None else arg
        if mode!=old_mode:raise ValueError('cannot change mode on continuation')
    return mode,MAPPING[mode]

def full(v,fx,a,b,g):
    i,j=center(fx,a),center(fx,b)
    if i>=j or kind(fx,a)==kind(fx,b) or j-i<g:return False
    top,bottom=(a,b) if kind(fx,a)=='top' else (b,a)
    return (v[center(fx,top)][1]>v[center(fx,bottom)][1]
        and v[center(fx,bottom)][0]<v[center(fx,top)][0]
        and all(lo>=v[center(fx,bottom)][0] and hi<=v[center(fx,top)][1] for lo,hi in v[i:j+1]))
def ranged(v,i,j):return min(lo for lo,hi in v[i:j+1]),max(hi for lo,hi in v[i:j+1])
def first(v,fx,s,f,g):
    counts['first']+=1;i,j=center(fx,s),center(fx,f);gap=j-i
    if gap<g:ok=False;e=('first-gap',gap,g)
    elif kind(fx,f)=='top':
        actual=max(hi for lo,hi in v[i:j+1]);ok=actual==price(v,fx,f);e=('first-high',gap,g,i,j,actual,price(v,fx,f))
    else:
        actual=min(lo for lo,hi in v[i:j+1]);ok=actual==price(v,fx,f);e=('first-low',gap,g,i,j,actual,price(v,fx,f))
    assert ok==full(v,fx,s,f,g)
    return ok,e
def extension(v,fx,a,b,f):
    counts['extension']+=1
    i,j=center(fx,b)+1,center(fx,f);lo,hi=ranged(v,i,j);lower,upper=bounds(v,fx,a,f)
    return lo>=lower and hi<=upper,('extension',i,j,lo,hi,lower,upper)
def reverse(v,fx,b,f,g):
    counts['reverse']+=1;i,j=center(fx,b),center(fx,f);gap=j-i
    if gap<g:ok=False;e=('reverse-gap',gap,g)
    else:
        lo,hi=ranged(v,i,j);lower,upper=bounds(v,fx,b,f)
        ok=lo>=lower and hi<=upper;e=('reverse',gap,g,i,j,lo,hi,lower,upper)
    assert ok==full(v,fx,b,f,g)
    return ok,e

def unresolved(v,fx,R,cache):
    if cache is None:return ((0,len(v)),)
    start=R[0][0] if R else cache[0]
    return tuple((i,j) for i,j in ((0,center(fx,start)),(center(fx,cache[1])+1,len(v))) if i<j)
def validate(v,fx,q,before,mode,g):
    assert mode in MAPPING and g==MAPPING[mode]
    assert q.source_context.distance_mode==mode and q.source_context.min_gap==g
    assert len(q.R)>=len(before) and q.R[:len(before)]==before
    assert q.next_position==len(fx) and q.E is None
    pairs=q.R+((q.Bi002,) if q.Bi002 else ())
    assert all(full(v,fx,*p,g) for p in pairs)
    assert all(a[1]==b[0] and kind(fx,a[0])!=kind(fx,b[0]) for a,b in zip(pairs,pairs[1:]))
    assert q.S is None if not fx else q.S in range(len(fx))
    assert not q.R or q.Bi002 is not None
    if q.Bi002:assert q.S==q.Bi002[1]
    assert q.source_context.bars==tuple(v) and q.source_context.fx==tuple(fx)
    assert q.unresolved==unresolved(v,fx,q.R,q.Bi002)
    assert len(q.evidence)==len(fx) and tuple(e[0] for e in q.evidence)==tuple(range(len(fx)))

def process(v,distance_mode=None,previous_state=None,key=KEY):
    counts['calls']+=1;v=tuple(v)
    if not v:raise ValueError('merged must be nonempty')
    try:fx=tuple(fractals(v))
    except AssertionError:raise ValueError('invalid merged')
    if previous_state is not None:
        if not isinstance(previous_state,Q) or previous_state not in issued:raise ValueError('unissued checkpoint')
        ctx=previous_state.source_context
        if key!=ctx.key:raise ValueError('stable context changed')
        if len(v)<len(ctx.bars) or v[:len(ctx.bars)]!=ctx.bars:raise ValueError('merged prefix changed')
        if len(fx)<len(ctx.fx) or fx[:len(ctx.fx)]!=ctx.fx:raise ValueError('FX prefix changed')
    mode,g=resolve_mode(distance_mode,previous_state)
    if previous_state is None:R=[];cache=None;S=None;cursor=0;evidence=[]
    else:
        q=previous_state;R=list(q.R);cache=q.Bi002;S=q.S;cursor=q.next_position;evidence=list(q.evidence)
    before=tuple(R)
    if S is None and cursor<len(fx):
        S=cursor;cursor+=1;evidence.append((S,center(fx,S),kind(fx,S),'initialize',price(v,fx,S)))
    while cursor<len(fx):
        f=cursor;cursor+=1;oldS,oldcache=S,cache
        if cache is None:
            if kind(fx,S)==kind(fx,f):
                rel=compare(v,fx,S,f);e=('initial-compare',price(v,fx,S),price(v,fx,f),rel)
                if rel>0:S=f
                action='replace-start' if rel>0 else 'keep-start'
            else:
                ok,e=first(v,fx,S,f,g);action='accept-first' if ok else 'reject-first'
                if ok:cache=(S,f);S=f
        else:
            a,b=cache
            if kind(fx,b)==kind(fx,f):
                rel=compare(v,fx,b,f)
                if rel<0:
                    assert not full(v,fx,a,f,g)
                    action='weaker-end';e=('end-compare',price(v,fx,b),price(v,fx,f),rel)
                else:
                    assert full(v,fx,a,b,g)
                    ok,e=extension(v,fx,a,b,f);assert ok==full(v,fx,a,f,g)
                    action='extend' if ok else 'reject-extension'
                    if ok:cache=(a,f);S=f
            else:
                ok,e=reverse(v,fx,b,f,g);action='commit-rotate' if ok else 'reject-reverse'
                if ok:R.append((a,b));cache=(b,f);S=f
        evidence.append((f,center(fx,f),kind(fx,f),oldS,oldcache,action,e))
    q=Q(tuple(R),cache,S,None,cursor,Context(v,fx,key,mode,g),tuple(evidence),unresolved(v,fx,R,cache))
    validate(v,fx,q,before,mode,g);issued.add(q);counts['success']+=1
    return q

def selection(q):return (q.R,q.Bi002,q.S,q.next_position,q.unresolved)
def view(q):return {'R':q.R,'Bi002':q.Bi002,'S':q.S,'cursor':q.next_position,'unresolved':q.unresolved,'distance_mode':q.source_context.distance_mode,'min_gap':q.source_context.min_gap,'evidence_count':len(q.evidence)}
MAIN=[9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7]
OPEN=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]
DIFF=[1,0,2,4,5,4,2,1,3,6,5]
fixtures={'one_bar':source([9]),'no_fx':source([9,10]),'one_fx':source([9,10,0]),'main19':source(MAIN),'open21':source(OPEN),'equal_start':source([9,10,0,10,9]),'equal_end':source([1,0,3,6,9,10,8,5,8,10,9]),'reverse_end_bound':source([1,0,3,6,9,12,5,-2,3,8,6,4,2,-1,0]),'extend15':source([1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],2),'zero_height':source(MAIN,0),'distance11':source(DIFF)}
fixtures.update({'mirror_'+n:[(-hi,-lo) for lo,hi in v] for n,v in list(fixtures.items())})
results={mode:{n:process(v,mode) for n,v in fixtures.items()} for mode in MAPPING}
assert results['strong']['distance11'].R==() and results['strong']['distance11'].Bi002==(0,3)
assert results['weak']['distance11'].R==((0,1),) and results['weak']['distance11'].Bi002==(1,2)
for n in ('main19','open21','equal_start','equal_end'):
    assert selection(results['strong'][n])==selection(results['weak'][n])
assert results['strong']['main19'].evidence!=results['weak']['main19'].evidence
splits=[];stages={}
for mode in MAPPING:
    for name in ('main19','open21','distance11'):
        v=fixtures[name]
        for cut in range(1,len(v)+1):
            old=process(v[:cut],mode);old_repr=repr(old)
            got=process(v,previous_state=old)
            assert got==results[mode][name] and repr(old)==old_repr
            assert process(v,previous_state=got)==got
            splits.append((mode,name,cut))
    ext=source(MAIN+[9,10,12,11]);saved=None;stages[mode]=[]
    for n in (2,3,11,12,15,19,23):
        old=saved;saved=process(ext[:n],mode if old is None else None,old)
        assert saved==process(ext[:n],mode)
        if old:assert saved.R[:len(old.R)]==old.R
        stages[mode].append({'N':n,**view(saved)})
# Default is strong on first call; omitted continuation mode inherits even weak.
assert process(source(DIFF))==results['strong']['distance11']
w0=process(source(DIFF[:2]),'weak');s0=process(source(DIFF[:2]),'strong')
assert process(source(DIFF),previous_state=w0)==results['weak']['distance11']
assert process(source(DIFF),'weak',w0)==results['weak']['distance11']
probes=[]
def reject(name,fn,exception=ValueError):
    try:fn()
    except exception as e:probes.append((name,str(e)))
    else:raise AssertionError(name+' accepted')
reject('weak-to-strong-empty',lambda:process(source(DIFF),'strong',w0))
reject('strong-to-weak-empty',lambda:process(source(DIFF),'weak',s0))
for bad in ('invalid','',3,4,True,[],{}):reject('invalid-mode-'+repr(bad),lambda bad=bad:process(source(DIFF),bad))
reject('empty-dict-is-not-fresh',lambda:process(source(DIFF),previous_state={}))
reject('legacy-checkpoint-missing-mode',lambda:resolve_mode(None,SimpleNamespace(source_context=SimpleNamespace(key=KEY))))
reject('stored-mode-gap-disagree',lambda:resolve_mode(None,replace(w0,source_context=replace(w0.source_context,min_gap=4))))
# A self-consistent but wrong output mode must fail even if all pairs satisfy both thresholds.
q=results['weak']['main19'];packed=replace(q,source_context=replace(q.source_context,distance_mode='strong',min_gap=4))
reject('output-mode-differs-from-call',lambda:validate(tuple(source(MAIN)),tuple(fractals(source(MAIN))),packed,(),'weak',3),AssertionError)
for mode in MAPPING:
    q=results[mode]['main19'];changed=source(MAIN);changed[0]=(9.25,10.25)
    reject(mode+'-empty-merged',lambda:process([] ,mode))
    reject(mode+'-changed-prefix',lambda:process(changed,previous_state=q))
    reject(mode+'-shortened-prefix',lambda:process(source(MAIN[:-1]),previous_state=q))
    reject(mode+'-changed-stable-context',lambda:process(source(MAIN),previous_state=q,key=('changed',)))
    reject(mode+'-forged-state',lambda:process(source(MAIN),previous_state=replace(q,S=0)))
# Window arithmetic, independent of prices.
window_cases=[]
for d in (1,2,3,4,5):
    a=set(range(0,3));b=set(range(d,d+3));independent=set(range(2,d+1))-a-b
    assert (not a.intersection(b))==(d>=3)
    assert len(independent)==max(0,d-3)
    window_cases.append({'center_gap':d,'disjoint':not a.intersection(b),'independent_bars':len(independent)})
report={'scope':'Finite nonempty interval/fractal/Q model; no production Bi/raw-provenance/persisted-checkpoint execution. Read arithmetic definitions only; old top-level report writers not executed.','counts':counts,'base_nonempty_fixtures':len(fixtures),'fresh_mode_cases':len(fixtures)*2,'mode_split_points':len(splits),'all_Q_fields_match_same_mode_one_shot':True,'old_Q_and_committed_R_unchanged':True,'same_snapshot_idempotent':True,'reduced_checks_match_full_predicate':True,'strong_default_and_weak_inherited':True,'process_rejections':counts['calls']-counts['success'],'direct_policy_or_output_rejection_probes':len(probes)-(counts['calls']-counts['success']),'expected_rejections':probes,'window_cases':window_cases,'distance_fixture_lows':DIFF,'distance_fixture':{mode:view(results[mode]['distance11']) for mode in MAPPING},'main19':{mode:view(results[mode]['main19']) for mode in MAPPING},'stages':stages,'cross_mode_MAIN_evidence_different':True}
(HERE/'mode-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'counts':counts,'base_fixtures':len(fixtures),'fresh_mode_cases':len(fixtures)*2,'split_points':len(splits),'expected_rejections':len(probes),'distance_fixture':report['distance_fixture']},ensure_ascii=False))
