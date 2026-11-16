"""Compare production031 against memo030's current XD030-E saved experiment."""
import json,hashlib
from pathlib import Path
from chanlab.algo.chan_table import ChanTable
ROOT=Path(__file__).resolve().parent
oldpath=ROOT.parents[1]/'memo030-e/results.json'
old=json.loads(oldpath.read_text());new=json.loads((ROOT/'full-result.json').read_text());report={}
for key,d in new.items():
 s=ChanTable.read_csv(ROOT/'full'/key/'table.csv',ROOT/'full'/key/'context.csv').feature_series[key]
 bi=s.source_series;fx=bi.source_series
 pens=json.loads((ROOT.parents[1]/'memo030-four/input'/f'bi-{bi.config["distance_mode"]}.json').read_text())['pens']
 assert len(pens)==len(bi)
 for p,q in zip(bi,pens):assert (p.start_fenxing_index,p.end_fenxing_index,p.start_price,p.end_price)==(q['start']['fx_position'],q['end']['fx_position'],q['start']['price'],q['end']['price'])
 route=[[p.source_start,p.source_stop] for p in s]
 assert route==old[key]['confirmed'] and [list(x) for x in s.tail]==old[key]['tail']
 diffs=[]
 for i,(trace,w) in enumerate(zip(d['trace'],old[key]['witnesses'])):
  a=dict(trace['certificate']);b=dict(w)
  if a.get('profile')!=b.get('profile'):diffs.append([i,a.get('profile'),b.get('profile')])
  a.pop('profile',None);b.pop('profile',None)
  assert a==b,(key,i,a,b)
  chain=old[key]['confirmed']+old[key]['tail']
  assert trace['S']==chain[i] and trace['T']==chain[i+1]
  assert trace['U']==(chain[i+2] if w['kind']=='gap' else None)
 assert len(d['trace'])==len(old[key]['witnesses'])==old[key]['count']==len(s)
 bounds=[fx[bi[s[0].source_start].start_fenxing_index].id,fx[bi[s[-1].source_stop-1].end_fenxing_index].id]
 assert bounds==old[key]['fx_bounds']
 report[key]={'count':len(s),'fx_bounds':bounds,'every_input_bi_endpoint_and_price_equal':True,'complete_confirmed_route_equal':True,'actual_candidate_tail_equal':True,'all_confirmation_certificate_fields_equal_except_version_label':True,'actual_STU_binding_equal':True,'version_label_differences':diffs}
result={'reference':'memo030 current XD030-E, not historical A/B/C/D','reference_sha256':hashlib.sha256(oldpath.read_bytes()).hexdigest(),'modes':report,'all_equal':True,'scope':'031 adds production IDs/status/UTC evidence-time and persistence interfaces; those fields were not exposed by030 result JSON, so not claimed as direct old-field comparisons.'}
(ROOT/'memo030-comparison.json').write_text(json.dumps(result,indent=2));print({k:(v['count'],v['fx_bounds'],len(v['version_label_differences'])) for k,v in report.items()})
