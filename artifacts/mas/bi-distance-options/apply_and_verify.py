"""Apply the reviewed distance-option documentation after a full backup."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=ROOT/'docs/memo/memoWX_020_Chan_bi.md';raw=p.read_bytes();old=raw.decode();new=(HERE/'draft-memo.md').read_text()
sha=lambda b:hashlib.sha256(b).hexdigest()
baseline=json.loads((HERE/'baseline.json').read_text())
assert sha(raw)==baseline[str(p.relative_to(ROOT))], 'User memo changed during draft; reread before applying'
assert old[old.index('## Appendix A —'):]==new[new.index('## Appendix A —'):]
def user_blocks(s):
 part=s[s.index('## 004 —'):s.index('## 005 —')]
 note=re.search(r'```text\n(.*?)\n```',part,re.S).group(1)
 quote=part[part.index('> 请用'):].strip()
 return note,quote
assert user_blocks(new)==user_blocks(old)
# Other five definition criteria and the user's version3 text are unchanged.
for n in range(1,6):
 line=next(x for x in old.splitlines() if x.startswith(f'{n}. **'))
 assert line in new
for line in old.splitlines():
 if '版本三' in line:assert line in new
assert Counter(x for x in new.splitlines() if x.rstrip()!=x)<=Counter(x for x in old.splitlines() if x.rstrip()!=x)
assert sum(line.startswith('```') for line in new.splitlines())%2==0
assert not re.search(r'^#{1,6} 2\.[1-9]',new[:new.index('## Appendix A —')],re.M)
a=new[new.index('### 002.a —'):new.index('### 002.b —')]
assert len(re.findall(r'```text\n(.*?)\n```',a,re.S))==1
c=new[new.index('### 002.c —'):new.index('### 002.d —')]
helpers=re.findall(r'^#### .*：(_[a-z_]+)$',c,re.M)
assert len(helpers)==8
for name in helpers:assert name in new[new.index('### 002.d —'):new.index('## 003 —')]
links=0
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',new):
 if target.startswith(('http:','https:','#','mailto:')):continue
 name=target.split('#')[0]
 if name:assert (p.parent/name).exists(),target;links+=1
protected={x:sha((ROOT/x).read_bytes()) for x in baseline if x!=str(p.relative_to(ROOT))}
external_changes={x:{'baseline':baseline[x],'at_apply':v} for x,v in protected.items() if baseline[x]!=v}
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f');b=p.parent/'backups'/f'{p.stem}__{stamp}.md'
with b.open('xb') as f:f.write(raw)
assert b.read_bytes()==raw
p.write_text(new)
report={'backup':str(b.relative_to(ROOT)),'before_sha256':sha(raw),'after_sha256':sha(p.read_bytes()),'scopes':'Active000–005 distance normalization; source/archived tail exact','user_004_note_and_prompt_exact':True,'other_five_elements_and_user_version3_exact':True,'appendices_references_exact':True,'one_active_tree':True,'no_numbered_algorithm_markdown_headings':True,'helpers':helpers,'local_file_links_resolve':links,'no_new_trailing_whitespace':True,'protected_hashes_at_apply':protected,'concurrent_changes_preserved':external_changes,'independent_contract_numeric_proof_reviews':'PASS','production_edited_by_this_task':False,'visual_check':'pending'}
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(timespec='seconds')
with (ROOT/'logXW.md').open('a') as f:f.write(f'\n- **{stamp} | Codex | Memo020 strong/weak distance integration** — Added mutually exclusive strong4/weak3 distance policy across active000–005: corrected weak zero-independent-bar wording, defaultstrong/inherit-on-resume/reject-change, Q metadata, first/reverse/full checks, eighth policy helper, mode-specific examples/proofs and implementation boundary. Preserved004 note/prompt and all source/archived appendices exactly; other five elements/version3 unchanged. Three independent reviewsPASS. Isolated two-mode model:22nonemptyfixtures×2,102mode/splitpoints,383successful process calls+20expected process rejections,3additional policy/output guards; full Q/same-mode one-shot equality and mode packing checked. Full backup `{b.name}` precedes one edit; scope/links/fences/whitespace checksPASS. No028/code/test/data changes or new cache/commit policy.\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('protected_hashes_at_apply','helpers')},ensure_ascii=False))
