"""Two small read-only production/spec diagnoses; no algorithm changes."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
import json,hashlib
from chanlab.algo.kline import Kline,KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
protected=['docs/memo/memoWX_020_Chan_bi.md','docs/memo/memoWX_028_biFamily.md','src/chanlab/algo/bi.py','tests/test_bi.py']
before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in protected}

def analyze(raw,policy,tie):
    merged=MergedKlineSeries.derive_from(raw,policy,'memo015-readonly-review')
    source=FenxingSeries.derive_from(merged,tie,'memo019-readonly-review')
    report=BiSeries.derive_candidates(source,{'max_states':100000},'current020-readonly-review')
    def independent_pair(a,b):
        x,y=source[a],source[b];i,j=x.source_start+1,y.source_start+1
        if i>=j or j-i<4 or x.kind==y.kind:return False
        top,bottom=(merged[i],merged[j]) if x.kind=='top' else (merged[j],merged[i])
        return (top.high>bottom.high and bottom.low<top.low
                and max(p.high for p in merged[i:j+1])<=top.high
                and min(p.low for p in merged[i:j+1])>=bottom.low)
    edges={i:[j for j in range(i+1,len(source)) if independent_pair(i,j)] for i in range(len(source))}
    return {'raw_count':len(raw),'merged_count':len(merged),'fractal_count':len(source),
            'initial_a':report['initial_a'],'status':report['status'],
            'viable_routes':[list(s.config['route']) for g in report['groups'].values() for s in g],
            'blocked':[{'prefix':list(x['prefix']),'failed':x['failed']} for x in report['blocked']],
            'fractals':[{'position':i,'center':f.source_start+1,'kind':f.kind,'price':f.price,
                         'interval':[merged[f.source_start+1].low,merged[f.source_start+1].high]}
                         for i,f in enumerate(source)],
            'independent_legal_edges':edges}
casefile=ROOT/'artifacts/mas/bi-family/restart-20261110_040433/problem/case.json'
case=json.loads(casefile.read_text())
raw=KlineTSeries(tuple(Kline('SYN','1m','saved seed50',datetime.fromisoformat(p['timestamp']),p['open'],p['high'],p['low'],p['close'],p['volume']) for p in case['raw_ohlcv']))
seed=analyze(raw,case['merged_config'],case['source_config'])
assert seed['raw_count']==49 and seed['merged_count']==31 and seed['fractal_count']==16
assert seed['initial_a']==1 and seed['independent_legal_edges'][1]==[4] and not seed['independent_legal_edges'][4]
assert not seed['viable_routes']
values=(8,9,6,4,2,0,11,-1,0)
# Opens/closes only construct valid raw input; high/low determine the example.
raw=KlineTSeries(tuple(Kline('SYN','1m','synthetic9bar review',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),v+.25,v+1,v,v+.75,1) for i,v in enumerate(values)))
small=analyze(raw,{'initialization':'UP'},{'anchor_tie':'FIRST'})
assert [(p['center'],p['kind']) for p in small['fractals']]==[(1,'top'),(5,'bottom'),(6,'top'),(7,'bottom')]
assert small['independent_legal_edges']=={0:[1],1:[],2:[],3:[]}
assert not small['viable_routes']
# Verify the existing full-data legal-path witness without enumerating all paths.
csv=sorted((ROOT/'samples/chan_table').glob('*chan_table_*.csv'))[0]
fullraw=KlineTSeries.read_csv(csv)
fullmerged=MergedKlineSeries.derive_from(fullraw,{'initialization':'UP'},'memo015-readonly-review')
fullfx=FenxingSeries.derive_from(fullmerged,{'anchor_tie':'FIRST'},'memo019-readonly-review')
fullreport=BiSeries.derive_candidates(fullfx,{'max_states':100000},'current020-readonly-review')
witness=json.loads((ROOT/'artifacts/mas/bi-family/recovery-study/witness.json').read_text())['witness_route']
for a,b in zip(witness,witness[1:]):
    x,y=fullfx[a],fullfx[b];i,j=x.source_start+1,y.source_start+1
    assert i<j and j-i>=4 and x.kind!=y.kind
    top,bottom=(fullmerged[i],fullmerged[j]) if x.kind=='top' else (fullmerged[j],fullmerged[i])
    assert top.high>bottom.high and bottom.low<top.low
    assert max(p.high for p in fullmerged[i:j+1])<=top.high
    assert min(p.low for p in fullmerged[i:j+1])>=bottom.low
assert witness[0]==fullreport['initial_a']==0 and witness[-1]==len(fullfx)-1
assert not fullreport['groups']
current=list(fullreport['blocked'][0]['prefix'])
first_divergence=next(i for i,(a,b) in enumerate(zip(current,witness)) if a!=b)
full={'raw_count':len(fullraw),'merged_count':len(fullmerged),'fractal_count':len(fullfx),
      'production_routes':0,'states':fullreport['states'],'initial_a':fullreport['initial_a'],
      'blocked_at':fullreport['blocked'][0]['failed'],
      'six_condition_witness_strokes':len(witness)-1,'witness_reaches_last_fractal':True,
      'first_divergence':{'path_position':first_divergence,'common_previous':current[first_divergence-1],
                          'current_next':current[first_divergence],'witness_next':witness[first_divergence]},
      'witness_scope':'pair-definition-valid only, not compliance with current temporal protocol'}
after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in protected}
assert before==after
result={'scope':'read-only diagnosis; no proposed rule adopted','seed50':seed,'synthetic9':small,'full_sample':full,
        'protected_sha256':before,'protected_files_unchanged':True,
        'saved_seed_case_sha256':hashlib.sha256(casefile.read_bytes()).hexdigest()}
(HERE/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
print('FULL',json.dumps(full))
print(json.dumps({name:{k:v for k,v in data.items() if k in ('raw_count','merged_count','fractal_count','initial_a','status','viable_routes','blocked')} for name,data in [('seed50',seed),('synthetic9',small)]}))
