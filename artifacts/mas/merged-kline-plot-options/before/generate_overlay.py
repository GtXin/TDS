"""Gap-free raw40 overlay: merged low/high bands behind unchanged raw candles."""
from pathlib import Path
from hashlib import sha256
import json

from plotly import graph_objects as go
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

root=Path(__file__).resolve().parents[3]
sample=root/'samples/chan_table'
source=next(sample.glob('*chan_table*.csv'));context=next(sample.glob('*context*.csv'))
hashes={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in (source,context)}
raw=KlineTSeries.read_csv(source,context)
rule=root/'docs/memo/memoWX_015_Chan_mergedkline.md'
merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015:sha256:'+sha256(rule.read_bytes()).hexdigest())
assert isinstance(merged,MergedKlineSeries)
start=len(raw)-40;stop=len(raw);bars=raw[start:stop]
selected=[b for b in merged if b.source_stop>start and b.source_start<stop]
fig=go.Figure()
colors={'up':('#2563eb','rgba(37,99,235,0.10)'), 'down':('#ea580c','rgba(234,88,12,0.10)'),None:('#64748b','rgba(100,116,139,0.10)')}
seen=set()
for bar in selected:
    left=max(start,bar.source_start)-start-0.42
    right=min(stop,bar.source_stop)-start-0.58
    edge,fill=colors[bar.direction]
    label=f'MK{bar.id} · raw[{bar.source_start}:{bar.source_stop}) · {bar.direction} · merged low {bar.low:g} / high {bar.high:g}'
    fig.add_trace(go.Scatter(x=[left,right,right,left,left],y=[bar.low,bar.low,bar.high,bar.high,bar.low],
        mode='lines',fill='toself',fillcolor=fill,line={'color':edge,'width':1.6},
        text=[label]*5,hovertemplate='%{text}<extra></extra>',name=f'Merged {bar.direction} · low–high',
        legendgroup=str(bar.direction),showlegend=bar.direction not in seen))
    seen.add(bar.direction)
# Draw original OHLC last, so opaque candles remain in the foreground.
fig.add_trace(go.Candlestick(x=list(range(40)),open=[b.open for b in bars],high=[b.high for b in bars],
    low=[b.low for b in bars],close=[b.close for b in bars],name='Original K-lines',
    text=[b.timestamp.strftime('%Y-%m-%d %H:%M UTC') for b in bars],
    increasing={'line':{'color':'#15803d','width':1.8},'fillcolor':'#86d7a2'},
    decreasing={'line':{'color':'#b91c1c','width':1.8},'fillcolor':'#efa1a1'}))
ticks=[0,5,10,15,20,25,30,35,39]
fig.update_xaxes(type='linear',range=[-0.9,39.9],tickmode='array',tickvals=ticks,
    ticktext=[bars[i].timestamp.strftime('%b %d<br>%H:%M') for i in ticks],rangeslider_visible=False,
    title_text='40 observed bars in source order · UTC labels · time gaps hidden')
lo=min(b.low for b in bars+tuple(selected));hi=max(b.high for b in bars+tuple(selected));margin=max((hi-lo)*0.08,1)
fig.update_yaxes(title_text='Price',range=[lo-margin,hi+margin])
fig.update_layout(template='plotly_white',width=1440,height=720,
    title={'text':f'{bars[0].symbol} · {bars[0].period} · Raw and merged K-lines overlaid<br><sup>40 original candles · {len(selected)} merged ranges · full-data calculation</sup>','x':0.055},
    margin={'l':85,'r':40,'t':125,'b':100},
    legend={'orientation':'h','x':0,'y':1.08,'groupclick':'togglegroup'})
assert fig.data[-1].type=='candlestick'
assert len(fig.data[-1].x)==40 and list(fig.data[-1].low)==[b.low for b in bars]
for trace,bar in zip(fig.data[:-1],selected,strict=True):
    assert list(trace.y)==[bar.low,bar.low,bar.high,bar.high,bar.low]
    assert not trace.error_y.visible
assert fig.layout.xaxis.type=='linear'
assert hashes=={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in (source,context)}
out=root/'artifacts/merged-kline'
fig.write_html(out/'cc-last40-overlay-gapfree.html',include_plotlyjs=True)
fig.write_image(out/'cc-last40-overlay-gapfree.png',width=1440,height=720,scale=1.5)
report=dict(raw_count=40,merged_intervals=len(selected),raw_range=[start,stop],gap_free=True,
    raw_candles_foreground=True,merged_fill_opacity=0.10,source_hashes=hashes,
    no_fabricated_merged_ohlc=True,legend_can_toggle_merged_groups=True,
    png_sha256=sha256((out/'cc-last40-overlay-gapfree.png').read_bytes()).hexdigest())
(root/'artifacts/mas/merged-kline-gapfree/overlay-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
