"""Independent endpoint-DAG witness; does not change temporal selection policy."""
import json
from pathlib import Path
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
root=Path(__file__).resolve().parent
raw=KlineTSeries.read_csv(next(Path('samples/chan_table').glob('*chan_table_*.csv')))
m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015');fx=FenxingSeries.derive_from(m,{},'019')
# Sparse-table-free pair oracle: precompute valid outgoing pairs in O(M*N),
# maintaining exact extrema while the right endpoint advances.
edges=[[] for _ in fx]
for i,a in enumerate(fx):
    start=a.source_start+1; lo=m[start].low;hi=m[start].high; cursor=start
    for j in range(i+1,len(fx)):
        b=fx[j]; stop=b.source_start+1
        while cursor<stop:
            cursor+=1;lo=min(lo,m[cursor].low);hi=max(hi,m[cursor].high)
        if a.kind==b.kind or stop-start<4:continue
        t,d=(m[start],m[stop]) if a.kind=='top' else (m[stop],m[start])
        if t.high>d.high and d.low<t.low and hi<=t.high and lo>=d.low:edges[i].append(j)
initial=next((i for i,e in enumerate(edges) if e),None)
# Longest connected valid path from the confirmed sole initialA, independent
# of mandatory extension / first-reverse policy. This is a witness, not a selector.
length=[-1]*len(fx);parent=[None]*len(fx);length[initial]=0
for i in range(initial,len(fx)):
    if length[i]<0:continue
    for j in edges[i]:
        if length[j]<length[i]+1:length[j]=length[i]+1;parent[j]=i
last=max((i for i in range(len(fx)) if length[i]>=0),default=initial)
path=[];v=last
while v is not None:path.append(v);v=parent[v]
path.reverse()
assert all(b in edges[a] for a,b in zip(path,path[1:]))
report={'initial_a':initial,'latest_reachable_fractal':last,'fractal_count':len(fx),'valid_strokes':len(path)-1,'witness_route':path,'covers_previous_failure':last>151,'claim':'definition-valid connected witness only; does not enforce memo020 temporal selection'}
(root/'witness.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='witness_route'})
