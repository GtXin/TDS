"""Finite local WAIT_REVERSE model; not a complete canonical stroke selector."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from collections import Counter
import json


@dataclass(frozen=True)
class FX:
    c: int
    kind: str
    price: int


def scan(v: tuple[int, ...]) -> tuple[FX, ...]:
    assert all(a != b for a, b in zip(v, v[1:]))
    out=[]
    for i in range(1,len(v)-1):
        if v[i]>max(v[i-1],v[i+1]): out.append(FX(i,'top',v[i]+2))
        elif v[i]<min(v[i-1],v[i+1]): out.append(FX(i,'bottom',v[i]))
    return tuple(out)


def pair_reasons(v: tuple[int,...],a: FX,b: FX) -> list[str]:
    if a.c>=b.c: return ['order']
    if a.kind==b.kind: return ['same_kind']
    reasons=[]
    if b.c-a.c<4: reasons.append('distance')
    top=a if a.kind=='top' else b
    bottom=b if a.kind=='top' else a
    if not(v[top.c]+2>v[bottom.c]+2 and v[bottom.c]<v[top.c]):
        reasons.append('interval_order')
    if max(v[a.c:b.c+1])>v[top.c]: reasons.append('interior_high')
    if min(v[a.c:b.c+1])<v[bottom.c]: reasons.append('interior_low')
    return reasons


def more_extreme(new: FX,old: FX) -> bool:
    assert new.kind==old.kind
    return new.price>old.price if new.kind=='top' else new.price<old.price


def mirror(v: tuple[int,...]) -> tuple[int,...]:
    # [v,v+2] maps to [-v-2,-v] under price sign reversal.
    return tuple(-x-2 for x in v)


def machine(v: tuple[int,...]) -> dict:
    """One selected initial-seed branch, retaining rejected input candidates.

    All ties remain pending; initial seed and reverse acceptance choices are
    deliberately outside a complete canonical-selector claim.
    """
    fs=scan(v)
    if not fs:
        return {'events': [],'phase':'SEEK_END','A':None,'B':None,
                'paired_history':[],'retained':[], 'tail_breach':False}
    a=fs[0]; b=None; cursor=a.c; paired=[]; retained=[]; events=[]
    for f in fs[1:]:
        assert f.c>cursor; cursor=f.c
        before=[a.c,None if b is None else b.c]
        if b is None:
            reasons=pair_reasons(v,a,f)
            if not reasons:
                b=f; event='candidate_end_found'
            else:
                retained.append(f.c); event='seek_reject_or_alternative_seed'
        elif f.kind==b.kind:
            if more_extreme(f,b):
                reasons=pair_reasons(v,a,f)
                if not reasons:
                    b=f; event='extend_end'
                else:
                    retained.append(f.c); event='extension_rejected_needs_branch_or_rollback'
            else:
                reasons=['equal' if f.price==b.price else 'less_extreme']
                retained.append(f.c); event='same_kind_retained'
        else:
            reasons=pair_reasons(v,b,f)
            if not reasons:
                paired.append([a.c,b.c])
                a,b=b,f; event='qualified_reverse_found'
            else:
                retained.append(f.c); event='reverse_rejected'
        if b is not None:
            assert not pair_reasons(v,a,b)
        for p,q in paired:
            lookup={x.c:x for x in fs}
            assert not pair_reasons(v,lookup[p],lookup[q])
        events.append({'F':f.c,'event':event,'before':before,
                       'after':[a.c,None if b is None else b.c],
                       'reasons':reasons})
    breach=False
    if b is not None:
        tail=v[b.c+1:]
        if tail:
            breach=max(tail)>v[b.c] if b.kind=='top' else min(tail)<v[b.c]
    return {'events':events,'phase':'SEEK_END' if b is None else 'WAIT_REVERSE',
            'A':a.c,'B':None if b is None else b.c,
            'paired_history':paired,'retained':retained,'tail_breach':breach}


def mirror_result(result, flip=True):
    copied=json.loads(json.dumps(result))
    swap={'interior_high':'interior_low','interior_low':'interior_high'} if flip else {}
    for event in copied['events']:
        event['reasons']=sorted(swap.get(reason,reason) for reason in event['reasons'])
    return copied


def example(name,v, expected_event=None):
    vals=tuple(v); result=machine(vals)
    if expected_event: assert any(x['event']==expected_event for x in result['events'])
    mirrored=machine(mirror(vals))
    assert mirror_result(result)==mirror_result(mirrored,False)
    return {'name':name,'bars_low_high':[[x,x+2] for x in vals],
            'fractals':[{'center':f.c,'kind':f.kind,'price':f.price} for f in scan(vals)],
            'result':result,'mirror_same_transitions':True}


def main():
    # Initial A bottom1; B top5 qualifies as candidate only. Bottom7 is too
    # close; new higher top9 extends B; bottom13 qualifies reverse afterwards.
    good=[1,0,3,6,9,12,10,8,12,16,13,10,7,4,5]
    a=example('candidate_then_extension_then_qualified_reverse',good,'extend_end')
    ev=a['result']['events']
    assert [(x['F'],x['event']) for x in ev]==[
        (5,'candidate_end_found'),(7,'reverse_rejected'),(9,'extend_end'),
        (13,'qualified_reverse_found')]
    assert a['result']['paired_history']==[[1,9]]
    # A top1; B bottom6; top8 exceeds A but is too close to B; lower bottom10
    # cannot extend B from the fixed A because that new top breaks maximum.
    bad=[14,15,12,9,6,3,0,9,20,8,-2,-1]
    b=example('more_extreme_extension_rejected_after_start_bound_breach',bad,
              'extension_rejected_needs_branch_or_rollback')
    assert b['result']['B']==6
    failure=[x for x in b['result']['events'] if x['event'].startswith('extension_rejected')][0]
    assert failure['F']==10 and failure['reasons']==['interior_high']
    # The last two bars rise past B, but neither is a complete top yet.
    tail=[1,0,3,6,9,12,10,11,13,14]
    c=example('unresolved_bar_extreme_before_new_complete_fractal',tail)
    assert c['result']['B']==5 and c['result']['tail_breach']
    assert all(f.c<8 for f in scan(tuple(tail)))
    # Equal later top retained, no silent most-recent tie policy.
    equal=[1,0,3,6,9,12,9,6,9,12,10]
    d=example('equal_top_does_not_silently_finalize_or_replace',equal,'same_kind_retained')
    assert d['result']['B']==5
    # Enumerate all 11-bar scalar paths over {0,1,2,3} with unequal adjacent
    # values: 4*3^10 paths, all continuous inclusion-free [v,v+2] inputs.
    count=0; counts=Counter(); pair_checks=0
    for first in range(4):
        for choices in product(range(3),repeat=10):
            values=[first]
            for choice in choices:
                options=[x for x in range(4) if x!=values[-1]]
                values.append(options[choice])
            vals=tuple(values); r=machine(vals); mr=machine(mirror(vals))
            assert mirror_result(r)==mirror_result(mr,False)
            count+=1
            counts.update(x['event'] for x in r['events'])
            pair_checks+=len(r['paired_history'])+(r['B'] is not None)
    assert count==4*3**10
    report={'scope':'local phase correction only; no canonical or stable-prefix claim',
            'examples':[a,b,c,d],
            'finite_checks':{'continuous_scalar_paths':count,
                             'mirrored_paths':count,
                             'stored_pair_invariant_checks_at_final_state':pair_checks,
                             'event_counts':dict(counts),
                             'production_detector_execution':False}}
    out=Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['finite_checks'],ensure_ascii=False))
    print(out)


if __name__=='__main__': main()
