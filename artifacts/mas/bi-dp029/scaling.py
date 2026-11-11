"""Three warm-process repetitions per real CC prefix; no generated repetition."""
import json, platform, resource, statistics, time
from pathlib import Path
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
from full_atlas import independent_full
ROOT=Path(__file__).resolve().parent
sample=Path('samples/chan_table')
raw=KlineTSeries.read_csv(next(sample.glob('*chan_table*.csv')),next(sample.glob('*context*.csv')))
m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015:002')
fx=FenxingSeries.derive_from(m,{},'memo019:002')
records=[]
for count in (100,1000,3000):
    stop=m[fx[count-1].source_start+2].source_stop
    prefix=KlineTSeries(tuple(raw)[:stop],context=raw.context)
    for mode,gap in [('strong',4),('weak',3)]:
        runs=[]
        for repeat in range(3):
            start=time.perf_counter(); mm=MergedKlineSeries.derive_from(prefix,{'initialization':'UP'},'memo015:002'); t1=time.perf_counter()
            ff=FenxingSeries.derive_from(mm,{},'memo019:002'); t2=time.perf_counter(); assert len(ff)==count
            route,best,prev=BiSeries._solve(ff,gap); t3=time.perf_counter()
            series=BiSeries.derive_from(ff,{'distance_mode':mode},'memo029:001,002a-f'); t4=time.perf_counter()
            assert (route,best,prev)==independent_full(ff,gap)
            actual=(series[0].start_fenxing_index,)+tuple(p.end_fenxing_index for p in series)
            assert route==actual
            runs.append(dict(merged=t1-start,fenxing=t2-t1,dp_core=t3-t2,bi_factory=t4-t3,end_to_end=(t2-start)+(t4-t3)))
        records.append(dict(fractals=count,raw=len(prefix),merged=len(mm),mode=mode,strokes=len(series),route=route,unresolved=series.unresolved_ranges(),runs_seconds=runs,median_seconds={k:statistics.median(x[k] for x in runs) for k in runs[0]},reference_all_endpoints_equal=True))
report=dict(environment=dict(python=platform.python_version(),platform=platform.platform(),processor=platform.processor()),cache='same process, warm file cache; no DP result cache; upstream reconstructed per repetition; loading excluded',memory='process high-water RSS includes oracle and all earlier tiers, not per-stage allocation',peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,records=records)
(ROOT/'scaling.json').write_text(json.dumps(report,indent=2))
print([(x['fractals'],x['mode'],x['strokes'],x['median_seconds']) for x in records])
