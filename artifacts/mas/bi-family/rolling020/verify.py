"""Reproducible raw-input experiment with independent geometric oracle."""
import importlib.util
import json
import random
import time
import resource
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from chanlab.algo.bi import BiSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

ROOT = Path(__file__).resolve().parent


def raw_from(bars):
    rng=random.Random(20261110)
    return KlineTSeries(tuple(Kline('SYN','1m','seeded Monte Carlo',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),rng.uniform(lo,hi),hi,lo,rng.uniform(lo,hi),rng.randint(0,10000)) for i,(lo,hi) in enumerate(bars)))


def check(bars, policy='UP', tie='FIRST', compare=True):
    raw=raw_from(bars)
    merged=MergedKlineSeries.derive_from(raw, {'initialization':policy}, 'memo015')
    if not isinstance(merged,MergedKlineSeries):
        if merged['kind']=='pending': return Counter(pending=1)
        counts=Counter(dual=1)
        for branch in (merged['main'],merged['comparison']):
            counts.update(check_merged(branch,tie,compare))
        return counts
    return check_merged(merged,tie,compare)


def independent(source):
    # Independent full-range oracle; intentionally does not use optimized helpers.
    def good(a,b):
        x,y=source[a],source[b];i,j=x.source_start+1,y.source_start+1
        if j-i<4 or x.kind==y.kind:return False
        top,bottom=(x,y) if x.kind=='top' else (y,x)
        t=source.source_series[top.source_start+1];d=source.source_series[bottom.source_start+1]
        return t.high>d.high and d.low<t.low and all(z.high<=t.high and z.low>=d.low for z in source.source_series[i:j+1])
    result=[];working=None;s=0 if len(source) else None
    for f in range(1,len(source)):
        if working is None:
            if source[f].kind==source[s].kind:
                if (source[f].price>source[s].price if source[f].kind=='top' else source[f].price<source[s].price):s=f
            elif good(s,f):working=(s,f);s=f
        else:
            a,b=working
            if source[f].kind==source[b].kind:
                stronger=source[f].price>=source[b].price if source[f].kind=='top' else source[f].price<=source[b].price
                if stronger and good(a,f):working=(a,f);s=f
            elif good(b,f):result.append(working);working=(b,f);s=f
    return result,working,s


def check_merged(merged,tie,compare):
    source=FenxingSeries.derive_from(merged,{'anchor_tie':tie},'memo019')
    actual=BiSeries.scan(source,'memo020:rolling')
    result=[(p.start_fenxing_index,p.end_fenxing_index) for p in actual['series']]
    expected,working,pending=independent(source)
    try:
        assert result==expected and actual['cache_pair']==working and actual['pending_start']==pending
        assert actual['next_position']==len(source)
        pairs=result+([] if working is None else [working])
        for index,(a,b) in enumerate(pairs):
            x,y=source[a],source[b];i,j=x.source_start+1,y.source_start+1
            assert j-i>=4 and x.kind!=y.kind
            top,bottom=(merged[i],merged[j]) if x.kind=='top' else (merged[j],merged[i])
            assert top.high>bottom.high and bottom.low<top.low
            assert all(z.high<=top.high and z.low>=bottom.low for z in merged[i:j+1])
            if index:assert pairs[index-1][1]==a
        for event in actual['series'].trace:
            before,after=event['before'],event['after']
            assert after[0][:len(before[0])]==before[0]
            if event['rule'].startswith('reject_'):assert after[1]==before[1]
        assert len(actual['series'])==len(result) # EOF does not commit working
    except Exception:
        fig=source.plot(volume=False,title='Rolling020 validation problem')
        fig.write_html(ROOT/'problem.html');(ROOT/'problem-figure.json').write_text(fig.to_json())
        raise
    return Counter(completed=1,raw=len(merged.source_series),merged=len(merged),fractals=len(source),committed=len(result),working=working is not None,empty=not result,decisions=len(actual['series'].trace))


def main():
    start=time.perf_counter(); layers={}; counts=Counter(); rng=random.Random(20261110)
    for seed in range(10000):
        r=random.Random(seed); layer=seed%6; n=r.choice([9,17,33,49,65])
        values=[]; v=100
        for i in range(n):
            if layer==0: v+=r.choice([-1,1,2,3])
            elif layer==1: v+=r.randint(-9,9)
            elif layer==2: v+=r.choice([-25,-1,1,25])
            elif layer==3: v+=r.choice([-1,0,1])
            elif layer==4: v+=r.choice([-6,-3,3,6])
            else: v+=r.randint(-4,4)
            width=0 if layer==4 else (r.randint(0,25) if layer==3 else r.randint(1,5))
            values.append((v-width,v+width))
        try:
            result=check(values, 'UP', ['FIRST','LAST'][seed%2])
            if seed<100:
                for policy in ('UP','DOWN','OUTER','UNSET','BOTH'):
                    for tie in ('FIRST','LAST'): check(values,policy,tie)
            counts.update(result); layers.setdefault(str(layer),Counter()).update(result)
            if seed<100:
                for transformed in (tuple((-hi,-lo) for lo,hi in values),tuple((lo+300,hi+300) for lo,hi in values),tuple((lo*2,hi*2) for lo,hi in values)):
                    check(transformed)
        except Exception as exc:
            (ROOT/'monte-carlo').mkdir(exist_ok=True)
            (ROOT/'monte-carlo/failure.json').write_text(json.dumps({'seed':seed,'bars':values,'error':repr(exc)}))
            raise
    report={'seed_range':[0,9999],'generated':10000,'counts':dict(counts),'layers':{k:dict(v) for k,v in layers.items()},'transformed_probes':300,'seconds':time.perf_counter()-start,'failures':0,'peak_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'policy_tie_probes':1000,'layer_names':{'0':'trend','1':'oscillation','2':'gaps','3':'inclusion and equality','4':'single price','5':'variable width'},'reference_comparisons':'all completed branches','lengths':[9,17,33,49,65]}
    (ROOT/'monte-carlo').mkdir(exist_ok=True)
    (ROOT/'monte-carlo/report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

if __name__=='__main__': main()
