"""Reproduce full-data rules, independent oracle, persistence and actual figures."""
from pathlib import Path
import json
from hashlib import sha256
from dataclasses import asdict
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.chan_table import ChanTable
from chanlab.data.merged_kline_table import source_digest
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
samples=root/'samples/chan_table'
inputs=[next(samples.glob('*chan_table*.csv')),next(samples.glob('*context*.csv'))]
protected=inputs+list((root/'references/proj009data').glob('*'))
hashes={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
raw=KlineTSeries.read_csv(*inputs)
raw_digest=source_digest(raw)
counts={}; records={}
for policy in ('UP','DOWN','OUTER','UNSET','BOTH'):
    m=MergedKlineSeries.derive_from(raw,{'initialization':policy},'memo015:002:v1')
    paths={'complete':m} if isinstance(m,MergedKlineSeries) else ({'main':m['main'],'comparison':m['comparison']} if m['kind']=='dual' else {})
    counts[policy]={'outcome':'complete' if isinstance(m,MergedKlineSeries) else m['kind'],'paths':{}}
    for path,merged in paths.items():
        first=FenxingSeries.derive_from(merged,{},'memo019:002:v1')
        last=FenxingSeries.derive_from(merged,{'anchor_tie':'LAST'},'memo019:002:v1')
        expected=[]
        for i in range(1,len(merged)-1):
            a,b,c=merged[i-1],merged[i],merged[i+1]
            if b.high>max(a.high,c.high) and b.low>max(a.low,c.low): expected.append(('top',b.high,i-1,i+2))
            elif b.high<min(a.high,c.high) and b.low<min(a.low,c.low): expected.append(('bottom',b.low,i-1,i+2))
        assert [(p.kind,p.price,p.source_start,p.source_stop) for p in first]==expected
        assert [(p.kind,p.price,p.source_start,p.source_stop) for p in last]==expected
        counts[policy]['paths'][path]={'merged':len(merged),'fenxing':len(first),'top':sum(p.kind=='top' for p in first),'bottom':sum(p.kind=='bottom' for p in first),'changed_tie_anchors':sum(a.anchor_raw_index!=b.anchor_raw_index for a,b in zip(first,last))}
        if policy=='UP': selected=first
assert source_digest(raw)==raw_digest
registered=selected.to_chan_table(ChanTable.from_source_series(raw,raw.context),'fenxing')
registered.write_csv(out/'full-table.csv',out/'full-context.csv')
restored=ChanTable.read_csv(out/'full-table.csv',out/'full-context.csv')
assert restored.rows==registered.rows
assert FenxingSeries.from_chan_table(restored,'fenxing').items==selected.items
assert restored.feature_series['fenxing'].source_series is restored.feature_series['fenxing:source']
selected.to_dataframe().to_csv(out/'full-fenxing-records.csv',index=False)
assert all(sha256((root/p).read_bytes()).hexdigest()==v for p,v in hashes.items())
figdir=root/'artifacts/fenxing';figdir.mkdir(exist_ok=True)
for name,kwargs in [('cc-last80',{}),('cc-last80-china',{'market':'China'}),('cc-last80-calendar',{'show_gaps':True})]:
    fig=selected.plot(raw_start=len(raw)-80,title='CC 15m — geometric fractals (unconfirmed)',**kwargs)
    fig.write_html(figdir/f'{name}.html',include_plotlyjs=True)
    fig.write_image(figdir/f'{name}.png',width=1440,height=820,scale=1)
    for trace in fig.data:
        if trace.name in ('top fractal','bottom fractal'):
            for x,y,custom in zip(trace.x,trace.y,trace.customdata):
                p=selected.get_by_id(custom[0]); j=p.anchor_raw_index
                assert y==p.price and x==(raw[j].timestamp if kwargs.get('show_gaps') else j-(len(raw)-80))
report={'raw_count':len(raw),'raw_digest':raw_digest,'configuration_results':counts,'protected_hashes':hashes,'roundtrip':'passed','independent_four_comparison_oracle':'passed on every complete configured path','figures':[str(p.relative_to(root)) for p in figdir.glob('*')]}
(out/'full-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='protected_hashes'},indent=2))
