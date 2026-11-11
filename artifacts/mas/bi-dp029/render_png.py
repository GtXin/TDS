from pathlib import Path
import json,time
import plotly.io as pio
root=Path(__file__).resolve().parent
pages=json.loads((root/'atlas-manifest.json').read_text());started=time.perf_counter()
for offset in range(0,len(pages),8):
 batch=pages[offset:offset+8]
 figures=[pio.from_json((root/p['png']).with_suffix('.json').read_text()) for p in batch]
 targets=[str(root/p['png']) for p in batch]
 pio.write_images(figures,targets,width=1600,height=900,scale=1)
 print(f'rendered {min(offset+8,len(pages))}/{len(pages)} pages',flush=True)
(root/'render.json').write_text(json.dumps({'pages':len(pages),'seconds':time.perf_counter()-started,'width':1600,'height':900},indent=2))
