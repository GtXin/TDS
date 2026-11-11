"""Save the first unexpected empty/blocked Monte Carlo output for review."""
import json
import hashlib
from pathlib import Path
from plotly import graph_objects as go
ROOT=Path(__file__).resolve().parent

def save_problem(source,report):
    folder=ROOT/'problem';folder.mkdir(exist_ok=True)
    raw=source.source_series.source_series
    block=report['blocked'][0];path=block['prefix'];failed=block['failed']
    data={'classification':'020-permitted blocked empty output; user review required, not definition violation','raw_ohlcv':[{'timestamp':p.timestamp.isoformat(),'open':p.open,'high':p.high,'low':p.low,'close':p.close,'volume':p.volume} for p in raw],'initial_a':report['initial_a'],'historical_fractal_positions':list(path),'failed_fractal_position':failed,'source_config':dict(source.config),'merged_config':dict(source.source_series.config)}
    key=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()[:12]
    if (folder/f'{key}.json').exists(): return
    (folder/f'{key}.json').write_text(json.dumps(data,indent=2))
    first=not (folder/'case.json').exists()
    if first: (folder/'case.json').write_text(json.dumps(data,indent=2))
    fig=source.plot(volume=False,title='Monte Carlo problem: no EOF route — historical strokes only')
    fig.add_trace(go.Scatter(x=[source[i].anchor_raw_index for i in path],y=[source[i].price for i in path],mode='lines+markers',name='Blocked history — not final Bi',line={'color':'#7c3aed','dash':'dot','width':3}))
    fig.add_trace(go.Scatter(x=[source[failed].anchor_raw_index],y=[source[failed].price],mode='markers',name='Failed mandatory extension',marker={'symbol':'x','size':17,'color':'black'}))
    fig.write_html(folder/f'{key}.html',include_plotlyjs='directory')
    if first:
        fig.write_html(folder/'problem.html',include_plotlyjs='directory')
        (folder/'figure.json').write_text(fig.to_json())


def save_exception(raw, error):
    """Persist and plot available input even if an upstream stage fails."""
    folder=ROOT/'exception';folder.mkdir(exist_ok=True)
    data={'error':repr(error),'raw_ohlcv':[{'timestamp':p.timestamp.isoformat(),'open':p.open,'high':p.high,'low':p.low,'close':p.close,'volume':p.volume} for p in raw]}
    (folder/'case.json').write_text(json.dumps(data,indent=2))
    fig=raw.plot(volume=False,title=f'Validation exception: {type(error).__name__}')
    fig.write_html(folder/'problem.html',include_plotlyjs='directory')
    (folder/'figure.json').write_text(fig.to_json())
