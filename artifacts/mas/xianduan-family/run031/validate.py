"""Reproducible raw-input MC, independent event normalization and full-chain oracle.
Sources: memo031001.d/e; memo030002; frozen memo030-e/test_engine.py.
"""
import importlib.util,json,sys,time,random
from pathlib import Path
from collections import Counter
from chanlab.algo.xianduan import recognize, XianduanSeries
from chanlab.algo.bi import BiSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

sys.path.insert(0,str(REPO/'artifacts/mas/bi-dp029'))
gen=load('rawgen031',REPO/'artifacts/mas/bi-dp029/verify.py')
rec=load('refrec031',REPO/'artifacts/mas/memo021-1000fx/recognizer.py')
ref=load('reference031',REPO/'artifacts/mas/memo021-1000fx/independent_validate.py')
local=load('eventref031',ROOT/'reference_events.py')


def oracle(p,mode):
    events,shape=local.scanner(p,mode,rec,ref.Reference(p),True)
    table={(a,b):events(a,b) for a in range(len(p)-3) for b in range(a+3,len(p),2)}
    scores=[]
    def visit(chain):
        count=0
        for i,(a,b) in enumerate(chain[:-1]):
            c=chain[i+1][1]
            good=any((w['kind']!='gap' and w['dep_endpoint']<=c) or (w['kind']=='gap' and w['reverse_end']==c and i+2<len(chain) and w['dep_endpoint']<=chain[i+2][1]) for w in table[a,b])
            if not good:break
            count+=1
        if count:scores.append((count,chain[count-1][1]))
        c=chain[-1][1]
        for e in range(c+3,len(p),2):
            if shape(c,e):visit(chain+[(c,e)])
    for a,b in table:
        if shape(a,b):visit([(a,b)])
    return max(scores,default=(0,-1)),table


def check(s):
    p=XianduanSeries._prices(s.source_series);mode=s.config['xd_mode']
    event,_=local.scanner(p,mode,rec,ref.Reference(p),True)
    for t in s.trace:
        assert any(s.source_series.source_series._same_evidence(t['certificate'],MergedKlineSeries._freeze_data({**w,"profile":"XD030-E"})) for w in event(*t['S']))
    if len(p)<=16:
        score,_=oracle(p,mode)
        assert score==(len(s),s[-1].source_stop if len(s) else -1),(p,mode,score,s.items)
        return True
    expected=reference_dp(p,mode)
    assert expected==(len(s),s[-1].source_stop if len(s) else -1)
    return False


def reference_dp(p,mode):
    from functools import cache
    event,shape=local.scanner(p,mode,rec,ref.Reference(p),True)
    n=len(p)-1
    ends={a:[b for b in range(a+3,n+1,2) if shape(a,b)] for a in range(n)}
    table={(a,b):event(a,b) for a in ends for b in ends[a]}
    @cache
    def suffix(a,b,c):
        scores=[(0,-1)]
        for w in table[a,b]:
            if w['kind']!='gap':
                if w['dep_endpoint']>c:continue
                scores.append((1,b))
                next_ends=ends.get(c,[])
            else:
                if w['reverse_end']!=c:continue
                next_ends=[e for e in ends.get(c,[]) if e>=w['dep_endpoint']]
                if next_ends:scores.append((1,b))
            for e in next_ends:
                count,end=suffix(b,c,e)
                if count:scores.append((count+1,end))
        return max(scores)
    return max((suffix(a,b,c) for a in ends for b in ends[a] if table[a,b] for c in ends.get(b,[]) if any((w['kind']!='gap' and w['dep_endpoint']<=c) or (w['kind']=='gap' and w['reverse_end']==c) for w in table[a,b])),default=(0,-1))

def main():
    started=time.perf_counter();counts={};strata={};inputs=ROOT/'random-inputs.jsonl'
    with inputs.open('w') as out:
        for seed in range(10000):
            bars,layer=gen.generate(seed);raw=gen.raw_from(bars,seed)
            out.write(json.dumps({'seed':seed,'layer':layer,'bars':bars,'ohlcv':[[x.open,x.high,x.low,x.close,x.volume] for x in raw],'timestamp_start':'2026-01-01T00:00:00+00:00','period':'1m'})+'\n')
            try:
                merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015')
                fx=FenxingSeries.derive_from(merged,{},'memo019')
                for bm in ('weak','strong'):
                    bi=BiSeries.derive_from(fx,{'distance_mode':bm},'memo029')
                    for xm in ('weak','strong'):
                        s=XianduanSeries.derive_from(bi,{'xd_mode':xm});exhaustive=check(s)
                        key=f'bi-{bm}_xd-{xm}';c=counts.setdefault(key,Counter());c.update(inputs=1,segments=len(s),empty=not len(s),exhaustive=exhaustive,pens=len(bi));strata.setdefault(f'{key}|layer{layer}|raw{len(raw)}',Counter()).update(inputs=1,segments=len(s),empty=not len(s),exhaustive=exhaustive)
                        if seed<100:
                            p=XianduanSeries._prices(bi);r=recognize(p,xm)
                            for changed in ([-v for v in p],[v+300 for v in p],[2*v for v in p]):
                                q=recognize(changed,xm);assert q['confirmed']==r['confirmed'] and q['tail']==r['tail']
            except Exception as e:
                (ROOT/'failure.json').write_text(json.dumps({'seed':seed,'bars':bars,'error':repr(e)}));raise
            if seed%1000==0:print('MC',seed,flush=True)
    report={'inputs':10000,'counts':counts,'strata':strata,'seconds':time.perf_counter()-started,'failures':0}
    (ROOT/'monte-carlo.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()
