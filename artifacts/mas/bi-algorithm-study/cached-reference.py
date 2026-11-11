"""Independent recursive reference for the proposed cached-DFS phase policy.

No imports from oracle.py or the root's iterative implementation. Call run(bars)
with chronological (low, high) pairs; it returns viable EOF center paths only.
Historical prefixes of blocked branches are diagnostics, not viable results.
"""
from __future__ import annotations

import itertools
import json
import random
from pathlib import Path

Bar = tuple[int, int]
FX = tuple[int, str]


def input_check(bars: tuple[Bar, ...]) -> None:
    assert all(low <= high for low, high in bars)
    for (lo, hi), (next_lo, next_hi) in zip(bars, bars[1:]):
        assert ((lo < next_lo and hi < next_hi)
                or (lo > next_lo and hi > next_hi))


def scan(bars: tuple[Bar, ...]) -> tuple[FX, ...]:
    # Direct extrema definition, not the root's direction-change classifier.
    output=[]
    for center in range(1,len(bars)-1):
        left,middle,right=bars[center-1:center+2]
        if all(middle[k]>left[k] and middle[k]>right[k] for k in (0,1)):
            output.append((center,'top'))
        elif all(middle[k]<left[k] and middle[k]<right[k] for k in (0,1)):
            output.append((center,'bottom'))
    return tuple(output)


def pair(bars: tuple[Bar,...], a: FX, b: FX) -> bool:
    i,ak=a; j,bk=b
    if j-i<4 or ak==bk:
        return False
    top,bottom=(i,j) if ak=='top' else (j,i)
    lt,ht=bars[top]; lb,hb=bars[bottom]
    return (ht>hb and lb<lt and
            all(lb<=lo and hi<=ht for lo,hi in bars[i:j+1]))


def price(bars: tuple[Bar,...], f: FX) -> int:
    return bars[f[0]][1 if f[1]=='top' else 0]


def solve(bars: tuple[Bar,...]) -> tuple[set[tuple[int,...]],dict]:
    bars=tuple(tuple(x) for x in bars)
    input_check(bars)
    fs=scan(bars); outputs=set(); blocked=[]; events={}
    def event(key):
        events[key]=events.get(key,0)+1
    def emit(prefix,a,b):
        result=prefix+(a[0],b[0])
        lookup={f[0]:f for f in fs}
        assert all(pair(bars,lookup[x],lookup[y]) for x,y in zip(result,result[1:]))
        outputs.add(result)
        event('EOF_provisional')
    def wait(a,b,pos,prefix):
        assert pair(bars,a,b)
        if pos==len(fs):
            emit(prefix,a,b)
            return
        f=fs[pos]
        assert f[0]>b[0]
        if f[1]!=b[1]:
            if pair(bars,b,f):
                event('first_qualified_reverse')
                wait(b,f,pos+1,prefix+(a[0],))
            else:
                event('rejected_reverse_continue')
                wait(a,b,pos+1,prefix)
            return
        delta=price(bars,f)-price(bars,b)
        stricter=delta>0 if b[1]=='top' else delta<0
        if stricter:
            if pair(bars,a,f):
                event('mandatory_extension')
                wait(a,f,pos+1,prefix)
            else:
                event('BLOCKED_extension')
                blocked.append({'historical_prefix':prefix+(a[0],),
                                'old_working_pair':[a[0],b[0]],
                                'F':f[0], 'reason':'mandatory_extension_pair_invalid'})
            return
        if delta==0 and pair(bars,a,f):
            event('equal_fork')
            wait(a,b,pos+1,prefix)
            wait(a,f,pos+1,prefix)
        else:
            event('nonextreme_or_invalid_equal_continue')
            wait(a,b,pos+1,prefix)
    def seek(a,pos):
        if pos==len(fs):
            event('EOF_without_B')
            return
        f=fs[pos]
        if pair(bars,a,f):
            event('valid_first_B_fork')
            wait(a,f,pos+1,())
            # Independent recursive branch restores the pre-accept state.
            seek(a,pos+1)
        else:
            seek(a,pos+1)
    for initial_pos,a in enumerate(fs):
        seek(a,initial_pos+1)
    return outputs,{'fractals':fs,'blocked':blocked,'events':events}


def run(bars: tuple[Bar,...]) -> set[tuple[int,...]]:
    return solve(bars)[0]


def mirror(bars):
    return tuple((-hi,-lo) for lo,hi in bars)


def scalars(values,width=1):
    return tuple((x,x+width) for x in values)


def pack(name,bars):
    outputs,diagnostics=solve(bars)
    assert outputs==run(mirror(bars))
    return {'name':name,'bars_low_high':bars,
            'viable_EOF_paths':sorted(outputs),**diagnostics}


def main():
    safe=scalars([8,9,6,4,2,0,4,7,5,3,1,-1,1,2,3,4,3])
    unsafe=scalars([8,9,6,4,2,0,5,11,8,5,2,-1,1])
    recover=scalars([8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1])
    equal=scalars([8,9,6,4,2,0,4,7,5,3,1,0,1,2,3,4,3])
    # Equal top keep/replace can lead to different viable EOF paths.
    equal_split=scalars([1,0,3,6,9,12,9,6,9,12,10,7,4,2,3])
    cases=[pack('safe_extension',safe),pack('unsafe_13_bars',unsafe),
           pack('restore_earlier_B_choice_21_bars',recover),
           pack('equal_bottom_replacement',equal),pack('equal_top_two_EOF_routes',equal_split)]
    assert (1,11,15) in run(safe)
    assert all(path[0]!=1 for path in run(unsafe))
    assert (7,11) in run(unsafe)
    assert (1,11,15,19) in run(recover)
    assert (1,5,9,19) not in run(recover)
    assert any(d['historical_prefix']==(1,5) and d['old_working_pair']==[5,9]
               and d['F']==15 for d in cases[2]['blocked'])
    assert (1,11,15) in run(equal)
    assert (1,5,13) in run(equal_split) and (1,9,13) in run(equal_split)
    # Bounded enumeration includes all unequal-adjacent scalar paths length9.
    enum_count=0; mirrored_count=0; totals={}
    for first in range(4):
        for choices in itertools.product(range(3),repeat=8):
            values=[first]
            for choice in choices:
                values.append([x for x in range(4) if x!=values[-1]][choice])
            bars=scalars(values)
            outputs,details=solve(bars)
            assert outputs==run(mirror(bars))
            enum_count+=1; mirrored_count+=1
            for key,value in details['events'].items():
                totals[key]=totals.get(key,0)+value
    # Independent variable-width continuous inputs: strict comparable neighbors.
    rng=random.Random(20261110)
    pool=[(lo,hi) for lo in range(-4,7) for hi in range(lo,9) if (lo,hi)!=(-4,8)]
    variable_count=0
    for _ in range(2000):
        bars=[rng.choice(pool)]
        for _ in range(rng.randrange(6,31)):
            lo,hi=bars[-1]
            options=[p for p in pool if ((p[0]>lo and p[1]>hi)
                                         or (p[0]<lo and p[1]<hi))]
            bars.append(rng.choice(options))
        original=tuple(bars)
        assert run(original)==run(mirror(original))
        variable_count+=1
    result={'policy':'mandatory valid extension; first qualified reverse; equal alternatives; all initial seeds and first-B alternatives',
            'cases':cases,
            'checks':{'scalar_sequences_length9':enum_count,
                      'scalar_sign_mirrors':mirrored_count,
                      'variable_width_sequences':variable_count,
                      'variable_width_sign_mirrors':variable_count,
                      'finite_event_counts':totals,
                      'independent_reference':True,'production_or_CC_execution':False}}
    Path(__file__).with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['checks'],ensure_ascii=False))
    for case in cases:
        print(case['name'],case['viable_EOF_paths'])


if __name__=='__main__': main()
