"""Seeded rawOHLCV→merged→fractals→Bi; both distance modes, independent oracle."""
import json,random,time,resource
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
from oracle import solve,pair
from chanlab.algo.kline import Kline,KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
ROOT=Path(__file__).resolve().parent


def raw_from(bars,seed=0):
    rng=random.Random(seed)
    return KlineTSeries(tuple(Kline('SYN','1m',f'MonteCarlo seed{seed}',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),rng.uniform(lo,hi),hi,lo,rng.uniform(lo,hi),rng.randint(0,10000)) for i,(lo,hi) in enumerate(bars)))


def generate(seed):
    rng=random.Random(seed);layer=seed%6;n=rng.choice([9,17,33,65,129]);v=100;bars=[]
    for i in range(n):
        v+=rng.choice([-1,1,2,3]) if layer==0 else (rng.choice([-25,-1,1,25]) if layer==2 else rng.randint(-9,9))
        width=0 if layer==4 else (rng.randint(0,25) if layer==3 else rng.randint(1,5))
        bars.append((v-width,v+width))
    return bars,layer


def verify_source(fx,mode,exhaustive=True):
    gap=4 if mode=='strong' else 3
    s=BiSeries.derive_from(fx,{'distance_mode':mode},'memo029:002a-f')
    route=() if not len(s) else (s[0].start_fenxing_index,)+tuple(p.end_fenxing_index for p in s)
    expected,best,prev=solve(fx,gap,exhaustive and len(fx)<=11)
    actual,actual_best,actual_prev=BiSeries._solve(fx,gap)
    assert route==expected==actual and best==actual_best and prev==actual_prev
    assert all(pair(fx,a,b,gap) for a,b in zip(route,route[1:]))
    assert all(s[i-1].direction!=s[i].direction for i in range(1,len(s)))
    return s,Counter(results=1,strokes=len(s),empty=not len(s),exhaustive=len(fx)<=11,fractals=len(fx),raw=len(fx.source_series.source_series),merged=len(fx.source_series))


def main():
    started=time.perf_counter();counts={m:Counter() for m in ('strong','weak')};layers={};problem=None
    for seed in range(10000):
        bars,layer=generate(seed);raw=raw_from(bars,seed);fx=None;s=None
        try:
            m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015')
            fx=FenxingSeries.derive_from(m,{'anchor_tie':'FIRST' if seed%2==0 else 'LAST'},'memo019')
            original={}
            for mode in counts:
                s,c=verify_source(fx,mode);counts[mode].update(c);layers.setdefault(str(layer),{}).setdefault(mode,Counter()).update(c)
                original[mode]=tuple((p.start_fenxing_index,p.end_fenxing_index) for p in s)
            if seed<100:
                for policy in ('UP','DOWN','OUTER','UNSET','BOTH'):
                    up=MergedKlineSeries.derive_from(raw,{'initialization':policy},'memo015')
                    paths=[up] if isinstance(up,MergedKlineSeries) else ([] if up['kind']=='pending' else [up['main'],up['comparison']])
                    for path in paths:
                        for tie in ('FIRST','LAST'):
                            f=FenxingSeries.derive_from(path,{'anchor_tie':tie},'memo019')
                            for mode in counts:verify_source(f,mode)
                for changed,policy in (([(-hi,-lo) for lo,hi in bars],'DOWN'),([(lo+300,hi+300) for lo,hi in bars],'UP'),([(lo*2,hi*2) for lo,hi in bars],'UP')):
                    up=MergedKlineSeries.derive_from(raw_from(changed,seed),{'initialization':policy},'memo015')
                    f=FenxingSeries.derive_from(up,dict(fx.config),'memo019')
                    for mode in counts:
                        result,_=verify_source(f,mode)
                        assert tuple((p.start_fenxing_index,p.end_fenxing_index) for p in result)==original[mode]
        except Exception as error:
            folder=ROOT/f'problem-seed{seed}';folder.mkdir(exist_ok=True)
            (folder/'case.json').write_text(json.dumps({'seed':seed,'layer':layer,'raw_bars':bars,'error':repr(error),'mode':mode},indent=2))
            fig=fx.plot(volume=False) if fx is not None else raw.plot(volume=False)
            fig.write_html(folder/'problem.html');(folder/'figure.json').write_text(fig.to_json())
            raise
    report={'seeds':[0,9999],'input_sequences':10000,'modes':{k:dict(v) for k,v in counts.items()},'layers':{k:{m:dict(c) for m,c in v.items()} for k,v in layers.items()},'distance_modes':['strong','weak'],'lengths':[9,17,33,65,129],'extra_policy_tie_inputs':100,'transformed_inputs':300,'seconds':time.perf_counter()-started,'peak_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'failures':0}
    (ROOT/'monte-carlo.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()
