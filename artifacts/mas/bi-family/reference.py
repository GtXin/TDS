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
        if any(pair(bars,a,b) for b in fs[initial_pos+1:]):
            seek(a,initial_pos+1)
            break
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

