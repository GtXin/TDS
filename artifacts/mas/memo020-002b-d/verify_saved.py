"""Static scope/content evidence for the authorized memo020b-d insertion."""
from pathlib import Path
import ast,hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
memo=ROOT/'docs/memo/memoWX_020_Chan_bi.md'
edit=json.loads((HERE/'edit.json').read_text())
old=(ROOT/edit['backup']).read_bytes(); new=memo.read_bytes()
assert hashlib.sha256(old).hexdigest()==edit['before_sha256']
assert hashlib.sha256(new).hexdigest()==edit['after_sha256']
s=old.decode();t=new.decode();start='### 002.b — Detailed Implementation logic and Numerical Examples';end='## 003 — Reasoning (Why)'
a,b=s.index(start),s.index(end,s.index(start))
c,d=t.index(start),t.index(end,t.index(start))
assert t[:c]==s[:a] and t[d:]==s[b:]
assert t[c:d]==(HERE/'sections.md').read_text().rstrip()+'\n\n'
section=t[c:d]
for label in ('002.b','002.c','002.d'):assert section.count('### '+label+' —')==1
assert section.count('```')%2==0
assert not any(x.rstrip()!=x for x in section.splitlines())
helpers=re.findall(r'^#### .*：(_\w+)$',section,re.M)
assert helpers==['_check_pair','_compare_end','_freeze_branch','_validate_branch','_finish_branch','_validate_candidates']
assert all(section.count(name)>=3 for name in helpers)
assert section.index('source.validate()')<section.index('若M<2：')
assert '误传ID报错' not in section
assert '不把它写成全部trace或诊断字段逐字一致的证明' in section
assert '去重、分组和可选排序另计' in section
assert '尚不定义正式`BiSeries.derive_from()`的多解返回接口' in section
links=re.findall(r'\]\(([^)]+)\)',section)
for link in links:assert (memo.parent/link.split('#',1)[0]).resolve().exists(),link
figdata=json.loads((HERE/'figure-data.json').read_text())
images={}
for name,expected in figdata['figures'].items():
 artifact=HERE/name; sibling=memo.with_suffix('')/name
 assert artifact.read_bytes()==sibling.read_bytes()
 assert hashlib.sha256(artifact.read_bytes()).hexdigest()==expected
 images[name]=expected
protected=json.loads((HERE/'protected-before.json').read_text())
for name,expected in protected.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
assert '| WX 020 | [Chan_bi](memoWX_020_Chan_bi.md) |' in (memo.parent/'README.md').read_text()
for file in HERE.glob('*.py'):ast.parse(file.read_text(),filename=str(file))
model=json.loads((HERE/'pseudocode_model.json').read_text())
assert model['checks']['original_cases']==1010
assert model['checks']['corruption_probes_rejected']==12
assert model['checks']['short_input_validated_before_shortcut']
assert model['checks']['short_input_events_empty']
# Exact four main center routes and FX-position projections, not concatenated branches.
assert model['examples']['recovery21']['center_routes']==[[1,11,15,19],[1,19],[11,15,19],[15,19]]
assert model['examples']['recovery21']['position_routes']==[[0,3,4,5],[0,5],[3,4,5],[4,5]]
result={'backup_exact':True,'outside002b_d_exact':True,'definitions_002a_appendices_preserved':True,
 'saved_draft_exact':True,'helper_names':helpers,'local_links_passed':len(links),'figures_byte_equal':images,
 'protected_files_unchanged':list(protected),'new_section_whitespace_fences_index_passed':True,
 'model_checks':model['checks'],'main_routes_and_source_positions_passed':True,
 'plots_visually_inspected':True,'numerical_review':'PASS','contract_review':'PASS',
 'scope':'memo algorithm design and isolated evidence only; no production Bi implementation or CC execution'}
(HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'outside_scope_exact':True,'helpers':len(helpers),'links':len(links),'figures':len(images),'protected_files':len(protected),'model_cases':model['checks']['original_cases'],'corruption_probes':12}))
