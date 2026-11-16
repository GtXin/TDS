"""Audit every raw/fractal/stroke/segment coordinate against exact production sources."""
import json,hashlib
from pathlib import Path
from chanlab.algo.chan_table import ChanTable
from validate import ROOT
root=ROOT/'charts';manifest=json.loads((root/'manifest.json').read_text());sources=json.loads((ROOT/'source-hashes.json').read_text());checked=[]
for key in dict.fromkeys(p['key'] for p in manifest):
 folder=ROOT/'full'/key;table=ChanTable.read_csv(folder/'table.csv',folder/'context.csv');s=table.feature_series[key];bi=s.source_series;fx=bi.source_series;raw=table.source_series;covered=set()
 for page in (p for p in manifest if p['key']==key):
  a,b=page['raw_start'],page['raw_stop'];covered.update(range(a,b));f=json.loads((root/page['figure_json']).read_text());raw_count=0
  for t in f['data']:
   kind=t['meta']['kind'];xs=t['x']
   if kind=='raw':
    assert [v+a for v in xs]==list(range(a,b));assert t['high']==[v.high for v in raw[a:b]];assert t['low']==[v.low for v in raw[a:b]];raw_count+=len(xs)
   elif kind=='fx':
    for pos,x,y in zip(t['customdata'],xs,t['y']):
     q=fx[pos[0]];assert x+a==q.anchor_raw_index and y==q.price
   elif kind in ('bi','xd'):
    idx=int(t['name'][2:]);q=bi[idx] if kind=='bi' else s[idx]
    u,v=(q.start_fenxing_index,q.end_fenxing_index) if kind=='bi' else (bi[q.source_start].start_fenxing_index,bi[q.source_stop-1].end_fenxing_index)
    assert [x+a for x in xs]==[fx[u].anchor_raw_index,fx[v].anchor_raw_index]
    assert t['y']==[q.start_price,q.end_price]
  assert raw_count==b-a
  page.update(rule_tree_ref=s.rule_tree_ref,source_hashes=sources)
  checked.append({'key':key,'page':page['page'],'raw_count':raw_count,'all_coordinates_pass':True})
 assert covered==set(range(len(raw)))
(root/'manifest.json').write_text(json.dumps(manifest,indent=2));(ROOT/'atlas-check.json').write_text(json.dumps({'pages':len(checked),'checks':checked,'all_raw_positions_covered':True},indent=2));print('Atlas coordinate checks',len(checked),'PASS')
# Human-friendly same-window comparisons and per-page navigation.
style='<style>body{font:16px system-ui;max-width:1150px;margin:32px auto;padding:0 20px}a{color:#5b21b6}li{margin:10px 0}img{max-width:100%}</style>'
keys=list(dict.fromkeys(p['key'] for p in manifest))
rows=[]
for i in range(1,57):
 pages=[p for p in manifest if p['page']==i]
 links=' · '.join(f'<a href="{p["html"]}">{p["key"]}</a>' for p in pages)
 rows.append(f'<li>raw {pages[0]["raw_start"]}:{pages[0]["raw_stop"]} — <a href="comparison/compact-page-{i:03d}.png">four-mode comparison</a> · {links}</li>')
(root/'index.html').write_text(style+'<h1>Xianduan family · XD030-E</h1><p>Default: weak Bi / weak Xianduan. Purple solid: confirmed prefix; dashed gray: actual candidate evidence tail. Four independent modes; all 10,060 raw bars covered.</p><p><a href="bi-weak_xd-weak/index.html">Open default weak/weak gallery</a> · <a href="manifest.json">Source and window manifest</a></p><ol>'+''.join(rows)+'</ol>')
for key in keys:
 pages=[p for p in manifest if p['key']==key]
 links=''.join(f'<li><a href="page-{p["page"]:03d}.html">Page {p["page"]}: raw {p["raw_start"]}:{p["raw_stop"]}</a> · <a href="page-{p["page"]:03d}.png">PNG</a></li>' for p in pages)
 (root/key/'index.html').write_text(style+f'<h1>{key}</h1><a href="../index.html">Four-mode comparison</a><ol>{links}</ol>')
 for p in pages:
  path=root/p['html'];html=path.read_text();i=p['page'];nav=f'<nav><a href="../index.html">All modes</a> · <a href="index.html">Gallery</a> · <a href="page-{max(i-1,1):03d}.html">Previous</a> · <a href="page-{min(i+1,56):03d}.html">Next</a> · <a href="page-{i:03d}.png">PNG</a></nav>'
  html=html.replace('<body>','<body>'+nav,1);path.write_text(html)
