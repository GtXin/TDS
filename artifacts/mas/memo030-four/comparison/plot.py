"""Overlay saved four-mode routes without recalculating or shifting geometry."""
from __future__ import annotations
import json
from pathlib import Path
import plotly.graph_objects as go

ROOT=Path(__file__).resolve().parent
CHARTS=ROOT.parent/'charts'
MODES=['bi-strong_xd-strong','bi-strong_xd-weak','bi-weak_xd-strong','bi-weak_xd-weak']
COLORS=['#2563eb','#ea580c','#16a34a','#a21caf']
DASH=['solid','dash','dot','dashdot']
NAMES=['Bi S / XD S','Bi S / XD W','Bi W / XD S','Bi W / XD W']

def main() -> None:
    """Reuse all exact figure arrays and audit segment membership."""
    manifest=json.loads((CHARTS/'manifest.json').read_text())
    pages=[]
    for stem in ['overview']+[f'detail-{i:03d}' for i in range(1,8)]:
        sources=[json.loads((CHARTS/m/(stem+'.figure.json')).read_text()) for m in MODES]
        layout=sources[0]['layout']
        traces=[x for x in sources[0]['data'] if x.get('meta',{}).get('kind')=='merged']
        if traces:traces[0]['name']='Price ranges'
        ids=[]
        for mi,source in enumerate(sources):
            xs=[];ys=[];custom=[]
            for trace in source['data']:
                if trace.get('meta',{}).get('kind')!='xd':continue
                for x,y,c in zip(trace['x'],trace['y'],trace['customdata']):
                    xs.append(x);ys.append(y)
                    if c is None:custom.append(None)
                    else:
                        row=list(c);row[0]=int(row[0])+1000*mi;custom.append(row);ids.append(row[0])
            traces.append({'type':'scatter','mode':'lines','x':xs,'y':ys,'customdata':custom,'meta':{'kind':'xd'},'name':NAMES[mi], 'line':{'color':COLORS[mi],'width':3.5-mi*.5,'dash':DASH[mi]},'hovertemplate':NAMES[mi]+'<br>segment=%{customdata[0]} raw=%{x} price=%{y}<extra></extra>'})
        # Common y range includes every mode; source coordinates remain untouched.
        ranges=[s['layout']['yaxis']['range'] for s in sources]
        layout['yaxis']['range']=[min(x[0] for x in ranges),max(x[1] for x in ranges)]
        layout['title']['text']='Four-mode Xianduan overlay — '+stem+'<br><sup>S=strong; W=weak | same price/time axis; exact saved routes | use legend to toggle</sup>'
        layout['annotations']=[];layout['shapes']=[]
        figure=go.Figure(data=traces,layout=layout)
        figure.write_html(ROOT/(stem+'.html'),include_plotlyjs='../charts/plotly.min.js')
        (ROOT/(stem+'.figure.json')).write_text(figure.to_json())
        first=next(p for p in manifest if p['mode']==MODES[0] and Path(p['png']).stem==stem)
        pages.append({**first,'html':stem+'.html','png':stem+'.png','figure_json':stem+'.figure.json','fx_positions':[],'bi_positions':[],'xd_positions':sorted(set(ids))})
    (ROOT/'manifest.json').write_text(json.dumps(pages,indent=2))
    (ROOT/'index.html').write_text('<meta charset="utf-8"><h1>Four-mode comparison</h1><p>Blue: Bi strong / XD strong. Orange: Bi strong / XD weak. Green: Bi weak / XD strong. Purple: Bi weak / XD weak. Exact overlap may hide lines; toggle legends in interactive charts. No prices shifted.</p>'+''.join(f'<p><a href="{p["html"]}">{p["html"]}</a> · <a href="{p["png"]}">PNG</a></p>' for p in pages))
    print('8 comparison pages; exact source arrays reused')

if __name__=='__main__':main()
