"""Helper-decomposed experiment for memo020002.a, not production BiSeries.

Mappings mirror field access used by the algorithm; synthetic input adapters
are not replacements for full production FenxingSeries.validate().
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from types import MappingProxyType
import itertools
import json
import operator
import random
import runpy


def _check_pair(source, a, b):
    items=source['items']; bars=source['source_series']['klines']; m=len(items)
    if type(a) is not int or type(b) is not int or not(0<=a<m and 0<=b<m):
        raise ValueError('endpoint position outside exact FenxingSeries')
    x,y=items[a],items[b]; i=x['source_start']+1; j=y['source_start']+1
    reasons=[]
    if not(a<b and i<j): reasons.append('order')
    if x['kind']==y['kind']: reasons.append('same_kind')
    if reasons: return False,tuple(reasons)
    if j-i<4: reasons.append('distance')
    top,bottom=(i,j) if x['kind']=='top' else (j,i)
    lt,ht=bars[top]['low'],bars[top]['high']
    lb,hb=bars[bottom]['low'],bars[bottom]['high']
    if not(ht>hb and lb<lt): reasons.append('interval_order')
    if any(p['high']>ht for p in bars[i:j+1]): reasons.append('interior_high')
    if any(p['low']<lb for p in bars[i:j+1]): reasons.append('interior_low')
    return not reasons,tuple(reasons)


def _compare_end(source,b,f):
    x,y=source['items'][b],source['items'][f]
    if not(b<f and x['kind']==y['kind']): raise ValueError('same-kind later endpoint required')
    if y['price']==x['price']: return 'EQUAL'
    more=y['price']>x['price'] if x['kind']=='top' else y['price']<x['price']
    return 'MORE' if more else 'LESS'


def _freeze_branch(source,prefix,a,b,cursor):
    branch=MappingProxyType({'source':source,'prefix':tuple(prefix),'A':a,'B':b,
                             'phase':'SEEK_B' if b is None else 'WAIT_REVERSE',
                             'cursor':cursor})
    _validate_branch(source,branch)
    return branch


def _validate_branch(source,branch):
    if branch['source'] is not source: raise ValueError('different source identity')
    m=len(source['items']); prefix=branch['prefix']; a,b=branch['A'],branch['B']
    if not isinstance(prefix,tuple) or not prefix or prefix[-1]!=a:
        raise ValueError('prefix must end at A')
    if any(type(p) is not int or not 0<=p<m for p in prefix):
        raise ValueError('prefix endpoint position')
    if type(a) is not int or not 0<=a<m: raise ValueError('A position')
    if any(not _check_pair(source,p,q)[0] for p,q in zip(prefix,prefix[1:])):
        raise ValueError('invalid prefix edge')
    if b is None:
        if prefix!=(a,) or branch['phase']!='SEEK_B': raise ValueError('SEEK_B state')
    elif (type(b) is not int or not 0<=b<m or branch['phase']!='WAIT_REVERSE'
          or not _check_pair(source,a,b)[0]):
        raise ValueError('WAIT_REVERSE state')
    last=a if b is None else b; cursor=branch['cursor']
    if type(cursor) is not int or not last<cursor<=m:
        raise ValueError('next unread cursor outside valid range')


def _finish_branch(source,branch,reason,f=None,reasons=()):
    _validate_branch(source,branch)
    prefix,a,b,cursor=(branch[k] for k in ('prefix','A','B','cursor'))
    if reason=='BLOCKED':
        if b is None or f!=cursor-1 or _compare_end(source,b,f)!='MORE':
            raise ValueError('blocked branch cause')
        ok,actual=_check_pair(source,a,f)
        if ok or tuple(reasons)!=actual: raise ValueError('blocked evidence mismatch')
        return MappingProxyType({'source':source,'kind':'blocked',
                                 'historical_endpoints':prefix+(b,),
                                 'working_pair':(a,b),'failed_F':f,'reasons':actual})
    if reason!='EOF' or cursor!=len(source['items']): raise ValueError('not EOF')
    if b is None:
        return MappingProxyType({'source':source,'kind':'unresolved','seed':a,
                                 'range':(0,len(source['source_series']['klines']))})
    endpoints=prefix+(b,); items=source['items']; bars=source['source_series']['klines']
    start=items[endpoints[0]]['source_start']+1; end=items[b]['source_start']+1
    tail=bars[end+1:]; bound=bars[end]
    breach=any(p['high']>bound['high'] for p in tail) if items[b]['kind']=='top' else any(
        p['low']<bound['low'] for p in tail)
    return MappingProxyType({'source':source,'kind':'candidate','endpoints':endpoints,
                             'provisional_pair':(a,b),'unresolved_head':(0,start),
                             'unresolved_tail':(end+1,len(bars)),'tail_breach':breach})


def _validate_candidates(source,candidates):
    seen=set(); items=source['items']; bars=source['source_series']['klines']
    for route in candidates:
        if route['source'] is not source or route['kind']!='candidate':
            raise ValueError('candidate source/kind')
        points=route['endpoints']
        if not isinstance(points,tuple) or len(points)<2 or points in seen:
            raise ValueError('duplicate or short route')
        if any(not _check_pair(source,p,q)[0] for p,q in zip(points,points[1:])):
            raise ValueError('invalid route edge')
        if route['provisional_pair']!=points[-2:]: raise ValueError('wrong provisional tail')
        first=items[points[0]]['source_start']+1; last=items[points[-1]]['source_start']+1
        if route['unresolved_head']!=(0,first) or route['unresolved_tail']!=(last+1,len(bars)):
            raise ValueError('unresolved range mismatch')
        seen.add(points)


def search(source):
    # Real entry: source must be the exact complete FenxingSeries and validate().
    # This isolated mapping adapter validates only fields used by this experiment.
    bars=source['source_series']['klines']; items=source['items']; m=len(items)
    if not isinstance(bars,tuple) or not isinstance(items,tuple): raise ValueError('immutable inputs required')
    for p,q in zip(bars,bars[1:]):
        if not((p['low']<q['low'] and p['high']<q['high']) or
               (p['low']>q['low'] and p['high']>q['high'])):
            raise ValueError('invalid adjacent merged prices')
    expected=[]
    for i in range(1,len(bars)-1):
        left,mid,right=bars[i-1:i+2]
        for kind,sgn in (('top',1),('bottom',-1)):
            if all(sgn*mid[k]>max(sgn*left[k],sgn*right[k]) for k in ('low','high')):
                expected.append((i,kind,mid['high' if kind=='top' else 'low']))
    actual=[(p['source_start']+1,p['kind'],p['price']) for p in items]
    if actual!=expected or any(p['source_stop']-p['source_start']!=3 for p in items):
        raise ValueError('incomplete or altered input fractals')
    if m<2:
        # Input must be validated before this shortcut, including a sole FX.
        unresolved=MappingProxyType({'source':source,'kind':'unresolved',
                                    'seed':None,'range':(0,len(bars))})
        return MappingProxyType({'source':source,'candidates':(),'groups':(),
                                 'blocked':(),'unresolved':(unresolved,),'events':()})
    pending=[_freeze_branch(source,(a,),a,None,a+1) for a in reversed(range(m))]
    candidates=[]; blocked=[]; unresolved=[]; events=[]
    while pending:
        state=pending.pop(); _validate_branch(source,state)
        prefix,a,b,cursor=(state[k] for k in ('prefix','A','B','cursor'))
        events.append(('RESTORE',a,b,cursor))
        dead=False
        while cursor<m:
            f=cursor; cursor+=1
            if b is None:
                ok,reasons=_check_pair(source,a,f)
                if ok:
                    pending.append(_freeze_branch(source,prefix,a,None,cursor))
                    b=f; events.append(('FIRST_B',a,b,cursor))
                else: events.append(('REJECT_FIRST',f,reasons))
            elif items[f]['kind']==items[b]['kind']:
                relation=_compare_end(source,b,f)
                if relation=='MORE':
                    ok,reasons=_check_pair(source,a,f)
                    if ok:
                        events.append(('EXTEND',b,f)); b=f
                    else:
                        state=_freeze_branch(source,prefix,a,b,cursor)
                        blocked.append(_finish_branch(source,state,'BLOCKED',f,reasons))
                        events.append(('BLOCKED',a,b,f,reasons)); dead=True; break
                elif relation=='EQUAL':
                    ok,reasons=_check_pair(source,a,f)
                    if ok: pending.append(_freeze_branch(source,prefix,a,f,cursor))
                    events.append(('EQUAL_KEEP',b,f,ok,reasons))
                else: events.append(('INFERIOR',b,f))
            else:
                ok,reasons=_check_pair(source,b,f)
                if ok:
                    prefix=prefix+(b,); a,b=b,f
                    events.append(('REVERSE',a,b,cursor))
                else: events.append(('REJECT_REVERSE',f,reasons))
            _validate_branch(source,_freeze_branch(source,prefix,a,b,cursor))
        if not dead:
            outcome=_finish_branch(source,_freeze_branch(source,prefix,a,b,cursor),'EOF')
            if outcome['kind']=='candidate': candidates.append(outcome)
            else: unresolved.append(outcome)
    distinct={p['endpoints']:p for p in candidates}
    candidates=tuple(distinct[k] for k in sorted(distinct))
    _validate_candidates(source,candidates)
    groups={}
    for p in candidates: groups.setdefault((p['endpoints'][0],p['endpoints'][-1]),[]).append(p)
    groups=tuple((key,tuple(p['endpoints'] for p in routes),len(routes)==1)
                 for key,routes in sorted(groups.items()))
    return MappingProxyType({'source':source,'candidates':candidates,'groups':groups,
                             'blocked':tuple(blocked),'unresolved':tuple(unresolved),
                             'events':tuple(events)})


# Test adapters and checks below are not extra algorithm helpers or domain classes.
def make_source(pairs):
    bars=tuple(MappingProxyType({'low':lo,'high':hi}) for lo,hi in pairs)
    merged=MappingProxyType({'klines':bars})
    items=[]
    for i in range(1,len(bars)-1):
        x,y,z=bars[i-1:i+2]
        kind=('top' if all(y[k]>max(x[k],z[k]) for k in ('low','high')) else
              'bottom' if all(y[k]<min(x[k],z[k]) for k in ('low','high')) else None)
        if kind:
            items.append(MappingProxyType({'id':900+7*len(items),'kind':kind,
                'price':y['high' if kind=='top' else 'low'],'anchor_raw_index':1000+3*i,
                'source_start':i-1,'source_stop':i+2,'status':'unconfirmed','confirmed_at':None}))
    return MappingProxyType({'source_series':merged,'items':tuple(items),
        'config':MappingProxyType({'anchor_tie':'FIRST'}),'rule_tree_ref':'memo019002.a',
        'trace':(),'trace_by_point':()})


def main():
    here=Path(__file__).resolve().parent
    reference=runpy.run_path(str(here.parent/'bi-algorithm-study'/'cached-reference.py'))['run']
    counts=Counter(); tested=0
    def check(pairs):
        nonlocal tested
        source=make_source(pairs); before=repr(source); result=search(source)
        assert result['source'] is source and source['source_series'] is result['source']['source_series']
        assert before==repr(source)
        if len(source['items'])<2:
            assert result['events']==() and result['candidates']==()
            assert len(result['unresolved'])==1
            assert result['unresolved'][0]['range']==(0,len(source['source_series']['klines']))
        positions={p['endpoints'] for p in result['candidates']}
        centers={tuple(source['items'][p]['source_start']+1 for p in path) for path in positions}
        assert centers==reference(tuple(pairs))
        reflected=tuple((-hi,-lo) for lo,hi in pairs)
        mirror=search(make_source(reflected))
        assert positions=={p['endpoints'] for p in mirror['candidates']}
        counts.update(e[0] for e in result['events']); tested+=1
        return source,result,centers
    directed={
        'recovery21':[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1],
        'unsafe13':[8,9,6,4,2,0,5,11,8,5,2,-1,1],
        'safe_extension':[1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],
        'equal':[8,9,6,4,2,0,4,7,5,3,1,0,1,2,3,4,3],
        'two_equal_routes':[1,0,3,6,9,12,9,6,9,12,10,7,4,2,3],
        'tail_breach':[1,0,3,6,9,12,10,11,13,14],
        'no_fractal':[1,2,3], 'too_short':[1,2], 'sole_fractal':[0,1,0]}
    examples={}
    for name,values in directed.items():
        _,result,centers=check(tuple((v,v+2) for v in values))
        examples[name]={'center_routes':sorted(centers),'position_routes':
            [p['endpoints'] for p in result['candidates']],
            'blocked':[{k:v for k,v in b.items() if k!='source'} for b in result['blocked']]}
    assert [1,11,15,19] in [list(x) for x in examples['recovery21']['center_routes']]
    rng=random.Random(20261110)
    pool=[(lo,hi) for lo in range(-4,8) for hi in range(lo,10) if (lo,hi)!=(-4,9)]
    for _ in range(1000):
        pairs=[rng.choice(pool)]
        for _ in range(rng.randrange(2,29)):
            lo,hi=pairs[-1]
            pairs.append(rng.choice([p for p in pool if
                (p[0]>lo and p[1]>hi) or (p[0]<lo and p[1]<hi)]))
        check(tuple(pairs))
    # Snapshot tampering probes use a valid branch; source IDs deliberately
    # differ from Fenxing positions, centers, and raw anchors.
    values=directed['safe_extension']; src=make_source(tuple((v,v+2) for v in values))
    seed=_freeze_branch(src,(0,),0,None,1); probes=0
    def reject(call):
        nonlocal probes
        try: call()
        except (ValueError,TypeError,IndexError): probes+=1
        else: raise AssertionError('corruption was accepted')
    # Invalid short inputs must fail before the m<2 early return.
    reject(lambda:search(make_source(((0,4),(1,3)))))
    sole=make_source(((0,1),(1,2),(0,1)))
    altered=dict(sole['items'][0]); altered['price']+=1
    bad_sole=MappingProxyType({**sole,'items':(MappingProxyType(altered),)})
    reject(lambda:search(bad_sole))
    wrong_source=MappingProxyType(dict(src))
    reject(lambda:_validate_branch(wrong_source,seed))
    for cursor in (-1,0,len(src['items'])+1):
        corrupt=dict(seed); corrupt['cursor']=cursor
        reject(lambda c=corrupt:_validate_branch(src,c))
    corrupt=dict(seed); corrupt['phase']='WAIT_REVERSE'
    reject(lambda:_validate_branch(src,corrupt))
    corrupt=dict(seed); corrupt['prefix']=(1,)
    reject(lambda:_validate_branch(src,corrupt))
    reject(lambda:_check_pair(src,src['items'][0]['id'],1))
    # Independent tuple snapshot survives later mutation of caller's list.
    mutable=[0]; frozen=_freeze_branch(src,mutable,0,None,1); mutable.append(1)
    assert frozen['prefix']==(0,)
    reject(lambda:operator.setitem(frozen,'cursor',2))
    _,res,_=check(tuple((v,v+2) for v in directed['safe_extension']))
    valid=res['candidates'][0]; corrupt=dict(valid); corrupt['source']=wrong_source
    reject(lambda:_validate_candidates(res['source'],(corrupt,)))
    corrupt=dict(valid); corrupt['provisional_pair']=(0,0)
    reject(lambda:_validate_candidates(res['source'],(corrupt,)))
    result={'scope':'helper-decomposed research report, not production BiSeries',
            'checks':{'original_cases':tested,'sign_mirrors':tested,
                      'independent_reference_comparisons':tested,'variable_width_cases':1000,
                      'corruption_probes_rejected':probes,'immutable_prefix_alias_probe':True,
                      'exact_source_identity_and_no_input_mutation':True,
                      'short_input_validated_before_shortcut':True,
                      'short_input_events_empty':True,
                      'event_counts':dict(counts)},'examples':examples}
    here.joinpath('pseudocode_model.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['checks'],ensure_ascii=False))


if __name__=='__main__':main()
