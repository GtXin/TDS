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
spec = importlib.util.spec_from_file_location('reference', ROOT/'reference.py')
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


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


def check_merged(merged,tie,compare):
    # Independent postconditions: exact raw coverage and noninclusion.
    assert merged[0].source_start==0 and merged[-1].source_stop==len(merged.source_series)
    for a,b in zip(merged,merged[1:]):
        assert a.source_stop==b.source_start
        assert (a.low<b.low and a.high<b.high) or (a.low>b.low and a.high>b.high)
    source=FenxingSeries.derive_from(merged,{'anchor_tie':tie},'memo019')
    intervals=tuple((b.low,b.high) for b in merged)
    expected_fx=reference.scan(intervals)
    assert tuple((f.source_start+1,f.kind) for f in source)==expected_fx
    for f in source:
        center=merged[f.source_start+1]
        assert f.price==(center.high if f.kind=='top' else center.low)
        members=[i for i in range(center.source_start,center.source_stop) if (merged.source_series[i].high if f.kind=='top' else merged.source_series[i].low)==f.price]
        assert f.anchor_raw_index==(members[0] if tie=='FIRST' else members[-1])
    report=BiSeries.derive_candidates(source,{},'memo020')
    routes=set(); strokes=0
    for boundary,group in report['groups'].items():
        for series in group:
            path=tuple(series.config['route'])
            assert boundary==(path[0],path[-1])
            centers=tuple(source[i].source_start+1 for i in path)
            routes.add(centers)
            for index,item in enumerate(series):
                a,b=source[item.start_fenxing_index],source[item.end_fenxing_index]
                i,j=a.source_start+1,b.source_start+1
                assert j-i>=4 and a.kind!=b.kind
                top,bottom=(merged[i],merged[j]) if a.kind=='top' else (merged[j],merged[i])
                assert top.high>bottom.high and bottom.low<top.low
                assert all(x.high<=top.high and x.low>=bottom.low for x in merged[i:j+1])
                assert item.start_price==a.price and item.end_price==b.price
                assert item.direction==('down' if a.kind=='top' else 'up')
                if index:
                    assert series[index-1].end_fenxing_index==item.start_fenxing_index
                    assert series[index-1].direction!=item.direction
                assert item.confirmed_at is None and item.status=='unconfirmed'
                strokes+=1
    if compare:
        assert routes==reference.run(intervals)
    return Counter(completed=1, raw=len(merged.source_series),merged=len(merged),fractals=len(source),routes=len(routes),strokes=strokes,empty=not routes,states=report['states'],blocked=len(report['blocked']))


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
