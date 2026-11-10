"""Generate exact last40 raw bars with full-input merged bounds on a shared gap-free axis."""
from pathlib import Path
from hashlib import sha256
import json

from plotly import graph_objects as go
from plotly.subplots import make_subplots
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

root=Path(__file__).resolve().parents[3]
sample=root/'samples/chan_table'
source=next(sample.glob('*chan_table*.csv'));context=next(sample.glob('*context*.csv'))
protected={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in (source,context)}
raw=KlineTSeries.read_csv(source,context)
rule=root/'docs/memo/memoWX_015_Chan_mergedkline.md'
merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015:sha256:'+sha256(rule.read_bytes()).hexdigest())
assert isinstance(merged,MergedKlineSeries)
start=len(raw)-40;stop=len(raw);bars=raw[start:stop]
selected=[b for b in merged if b.source_stop>start and b.source_start<stop]
fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.10,
    subplot_titles=('Original K-lines · 40 recorded bars',f'Merged K-lines · {len(selected)} price intervals'),row_heights=[0.52,0.48])
fig.add_trace(go.Candlestick(x=list(range(40)),open=[b.open for b in bars],high=[b.high for b in bars],
    low=[b.low for b in bars],close=[b.close for b in bars],customdata=[b.timestamp.isoformat() for b in bars],
    text=[b.timestamp.strftime('%Y-%m-%d %H:%M UTC') for b in bars],name='Original OHLC',
    increasing_line_color='#16a34a',decreasing_line_color='#dc2626',showlegend=False),row=1,col=1)
colors={'up':('#2563eb','rgba(37,99,235,0.16)'), 'down':('#ea580c','rgba(234,88,12,0.16)'),None:('#64748b','rgba(100,116,139,0.16)')}
seen=set();expected=[]
for bar in selected:
    left=max(start,bar.source_start)-start-0.42
    right=min(stop,bar.source_stop)-start-0.58
    edge,fill=colors[bar.direction]
    x=[left,right,right,left,left];y=[bar.low,bar.low,bar.high,bar.high,bar.low]
    label=f'MK{bar.id} · raw[{bar.source_start}:{bar.source_stop}) · {bar.direction} · low {bar.low:g} / high {bar.high:g}'
    fig.add_trace(go.Scatter(x=x,y=y,mode='lines',fill='toself',fillcolor=fill,line={'color':edge,'width':1.6},
        text=[label]*5,hovertemplate='%{text}<extra></extra>',name=f'Merged {bar.direction}',
        legendgroup=str(bar.direction),showlegend=bar.direction not in seen),row=2,col=1)
    seen.add(bar.direction)
    expected.append(dict(id=bar.id,low=bar.low,high=bar.high,direction=bar.direction,
        source_start=bar.source_start,source_stop=bar.source_stop,display_left=left,display_right=right))
lo=min(b.low for b in bars+tuple(selected));hi=max(b.high for b in bars+tuple(selected));margin=max((hi-lo)*0.08,1)
for row in (1,2):fig.update_yaxes(title_text='Price',range=[lo-margin,hi+margin],row=row,col=1)
ticks=[0,5,10,15,20,25,30,35,39]
fig.update_xaxes(type='linear',range=[-0.9,39.9],tickmode='array',tickvals=ticks,
    ticktext=[bars[i].timestamp.strftime('%b %d<br>%H:%M') for i in ticks],rangeslider_visible=False)
fig.update_xaxes(title_text='40 observed bars in source order · UTC labels · time gaps hidden',row=2,col=1)
clipped=selected[0].source_start<start
note='Merged intervals retain full-data calculation and span their original members; blocks show low–high only.'
if clipped:note+=' First block is clipped at the viewport edge.'
fig.update_layout(template='plotly_white',width=1440,height=920,
    title={'text':f'{bars[0].symbol} · {bars[0].period} · Last 40 raw bars and merged K-lines','x':0.04},
    margin={'l':85,'r':40,'t':105,'b':100},legend={'orientation':'h','y':1.11,'x':0.53},
    annotations=list(fig.layout.annotations))
assert len(fig.data[0].x)==40 and list(fig.data[0].high)==[b.high for b in bars]
assert all(t.type!='scatter' or not t.error_y.visible for t in fig.data)
assert fig.layout.xaxis.type==fig.layout.xaxis2.type=='linear'
assert len(fig.data)==len(selected)+1
for trace,bar in zip(fig.data[1:],selected,strict=True):
    assert list(trace.y)==[bar.low,bar.low,bar.high,bar.high,bar.low]
assert protected=={str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in (source,context)}
out=root/'artifacts/merged-kline';out.mkdir(exist_ok=True)
fig.write_html(out/'cc-last40-raw-and-merged-gapfree.html',include_plotlyjs=True)
fig.write_image(out/'cc-last40-raw-and-merged-gapfree.png',width=1440,height=920,scale=1.5)
report=dict(raw_count=40,raw_range=[start,stop],merged_intervals=len(selected),full_merged_count=len(merged),
    initialization='UP',source_hashes=protected,clipped_first_interval=clipped,
    no_calendar_gaps=True,no_error_bar_marks=True,merged_records=expected,
    output_png_sha256=sha256((out/'cc-last40-raw-and-merged-gapfree.png').read_bytes()).hexdigest())
(root/'artifacts/mas/merged-kline-gapfree/verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='merged_records'},indent=2))
