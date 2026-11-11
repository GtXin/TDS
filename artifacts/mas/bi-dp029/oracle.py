"""Independent direct-range endpoint graph and forward-relaxation reference."""
from itertools import combinations


def pair(source,a,b,gap):
    x,y=source[a],source[b];i,j=x.source_start+1,y.source_start+1
    if i>=j or j-i<gap or x.kind==y.kind:return False
    top,bottom=(source.source_series[i],source.source_series[j]) if x.kind=='top' else (source.source_series[j],source.source_series[i])
    return top.high>bottom.high and bottom.low<top.low and max(z.high for z in source.source_series[i:j+1])<=top.high and min(z.low for z in source.source_series[i:j+1])>=bottom.low


def solve(source,gap,exhaustive=False):
    n=len(source);edges={a:[b for b in range(a+1,n) if pair(source,a,b,gap)] for a in range(n)}
    a=next((a for a in range(n) if edges[a]),None)
    best=[-1]*n;prev=[None]*n
    if a is None:return (),tuple(best),tuple(prev)
    best[a]=0
    # Forward propagation rather than the production end-outer loop.
    for p in range(a,n):
        if best[p]<0:continue
        for f in edges[p]:
            proposal=best[p]+1
            if proposal>best[f]:best[f]=proposal;prev[f]=p
    end=max(i for i in range(n) if best[i]>=1)
    route=[end]
    while route[-1]!=a:route.append(prev[route[-1]])
    route=tuple(reversed(route))
    if exhaustive:
        paths=[(a,)]
        for size in range(1,n-a):
            for tail in combinations(range(a+1,n),size):
                path=(a,)+tail
                if all(v in edges[u] for u,v in zip(path,path[1:])):paths.append(path)
        for f in range(a+1,n):
            options=[p for p in paths if p[-1]==f]
            if options:
                winner=min(options,key=lambda p:(-len(p),tuple(reversed(p[:-1]))))
                assert len(winner)-1==best[f] and winner[-2]==prev[f]
            else:assert best[f]==-1
        expected=min([p for p in paths if len(p)>1],key=lambda p:(-p[-1],-len(p),tuple(reversed(p[:-1]))))
        assert expected==route
    return route,tuple(best),tuple(prev)
