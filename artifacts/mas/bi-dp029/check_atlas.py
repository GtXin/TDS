"""Machine audit of complete windows, all fractal markers and true Bi endpoints."""
import json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
 pages=json.loads((ROOT/'atlas-manifest.json').read_text());full=json.loads((ROOT/'full-result.json').read_text())
 result={'pages':len(pages),'modes':{},'all_marker_ids_and_windows_checked':True}
 for mode in ('strong','weak'):
  subset=[p for p in pages if p['mode']==mode];covered=set();fxcovered=set();bicovered=set()
  for p in subset:
   a,b=p['raw'];covered.update(range(a,b));fxcovered.update(p['fx_positions']);bicovered.update(p['bi_ids'])
   fig=json.loads((ROOT/p['png']).with_suffix('.json').read_text());traces=fig['data']
   marks=[t for t in traces if t.get('name') in ('top fractal','bottom fractal')]
   actualfx={int(label[2:]) for t in marks for label in t['text']};assert actualfx==set(p['fx_positions'])
   actualbi={int(t['name'][2:]) for t in traces if t.get('name','').startswith('Bi')};assert actualbi==set(p['bi_ids'])
   for t in traces:
    if t.get('name','').startswith('Bi'):
     details=t['customdata'][0];assert details[0]==int(t['name'][2:]);assert t['x']==[details[3]-a,details[4]-a]
   raw=ROOT/p['png'];data=raw.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1600,900)
   assert (ROOT/p['html']).is_file()
  assert covered==set(range(full['raw']))
  assert fxcovered==set(range(full['fractals']))
  assert bicovered==set(range(full['modes'][mode]['strokes']))
  result['modes'][mode]={'pages':len(subset),'raw_coverage':len(covered),'fractal_coverage':len(fxcovered),'stroke_coverage':len(bicovered)}
 (ROOT/'atlas-check.json').write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':main()
