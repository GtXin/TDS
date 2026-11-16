"""Complete 200-raw/20-overlap four-mode atlas from production registrations."""
import json,math
from pathlib import Path
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.xianduan import XianduanSeries
from validate import ROOT
out=ROOT/'overview';out.mkdir(exist_ok=True)
manifest=[]
for bm,xm in [('weak','weak'),('weak','strong'),('strong','weak'),('strong','strong')]:
 key=f'bi-{bm}_xd-{xm}';folder=ROOT/'full'/key
 table=ChanTable.read_csv(folder/'table.csv',folder/'context.csv');s=XianduanSeries.from_chan_table(table,key)
 raw=table.source_series;n=len(raw);dest=out/key;dest.mkdir(exist_ok=True)
 windows=[(0,n)]
 for page,(a,b) in enumerate(windows):
  fig=s.plot(raw_start=a,raw_stop=b,volume=False,market='China')
  ids={'fx':set(),'bi':set(),'xd':set()};seen=set()
  for t in fig.data:
   name=t.name or ''
   kind='raw' if t.type=='candlestick' else ('fx' if 'fractal' in name else ('bi' if name.startswith('Bi') else ('xd' if name.startswith('XD') else ('tail' if name.startswith('candidate') else 'merged'))))
   t.meta={'kind':kind,'type':'top' if name.startswith('top') else 'bottom'}
   t.showlegend=kind not in seen;seen.add(kind)
   if kind=='fx':t.mode='markers'
   if kind in ('fx','bi'):
    for row in t.customdata or []:
     ids[kind].add(int(row[0]))
   if kind=='xd':
    idx=int(name[2:]);t.customdata=[[idx],[idx]];ids['xd'].add(idx)
  lows=[x.low for x in raw[a:b]];highs=[x.high for x in raw[a:b]];lo=min(lows);hi=max(highs);pad=max((hi-lo)*.1,1)
  fig.layout.annotations=()
  fig.update_layout(title=f'{key} | FULL OVERVIEW | raw {a}:{b}<br>XD030-E: actual adjacent evidence; candidate tail dashed',xaxis_range=[-.8,b-a-.2],yaxis_range=[lo-pad,hi+pad],width=1800,height=900)
  name='overview'
  (dest/f'{name}.figure.json').write_text(fig.to_json());fig.write_html(dest/f'{name}.html',include_plotlyjs='directory')
  manifest.append({'key':key,'page':page+1,'raw_start':a,'raw_stop':b,'utc':[raw[a].timestamp.isoformat(),raw[b-1].timestamp.isoformat()],'figure_json':f'{key}/{name}.figure.json','png':f'{key}/{name}.png','html':f'{key}/{name}.html','fx_positions':sorted(ids['fx']),'bi_positions':sorted(ids['bi']),'xd_positions':sorted(ids['xd'])})
  if page%10==0:print(key,page,flush=True)
 coverage=set(k for a,b in windows for k in range(a,b));assert coverage==set(range(n))
 links=''.join(f'<li><a href="page-{i+1:03d}.html">Page {i+1}</a></li>' for i in range(len(windows)))
 (dest/'index.html').write_text(f'<h1>{key}</h1><ul>{links}</ul>')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
(out/'index.html').write_text('<h1>Xianduan family XD030-E — default weak/weak</h1>'+''.join(f'<p><a href="bi-{bm}_xd-{xm}/index.html">Bi {bm} / XD {xm}</a></p>' for bm,xm in [('weak','weak'),('weak','strong'),('strong','weak'),('strong','strong')]))
print('pages',len(manifest))

(out/"index.html").write_text('<h1>Full-sample overview — XD030-E</h1><p>10,060 raw bars / 3,027 fractals. Default: weak Bi / weak Xianduan.</p><a href="../charts/index.html">Detailed atlas</a><p><img style="max-width:100%" src="comparison/compact-overview.png"></p><p><a href="bi-weak_xd-weak/overview.html">bi-weak_xd-weak interactive overview</a> · <a href="bi-weak_xd-weak/overview.png">PNG</a></p><p><a href="bi-weak_xd-strong/overview.html">bi-weak_xd-strong interactive overview</a> · <a href="bi-weak_xd-strong/overview.png">PNG</a></p><p><a href="bi-strong_xd-weak/overview.html">bi-strong_xd-weak interactive overview</a> · <a href="bi-strong_xd-weak/overview.png">PNG</a></p><p><a href="bi-strong_xd-strong/overview.html">bi-strong_xd-strong interactive overview</a> · <a href="bi-strong_xd-strong/overview.png">PNG</a></p>')
