"""Apply one reviewed memo update with a full pre-edit backup."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=ROOT/'docs/memo/memoWX_020_Chan_bi.md';oldraw=p.read_bytes();old=oldraw.decode();new=(HERE/'draft-memo.md').read_text()
sha=lambda b:hashlib.sha256(b).hexdigest()
baseline=json.loads((HERE/'baseline.json').read_text())
assert sha(oldraw)==baseline[str(p.relative_to(ROOT))], 'Memo changed since review baseline'
assert old[old.index('## 001 —'):old.index('## 002 —')]==new[new.index('## 001 —'):new.index('## 002 —')]
assert old[old.index('## Appendix A —'):]==new[new.index('## Appendix A —'):]
oldnote=(HERE/'original-note.txt').read_bytes()
assert oldnote in new.encode()
def prompt_text(s):
 part=s[s.index('> 请用'):s.index('## 005 —')]
 return [re.sub(r'^> ?', '',line).strip() for line in part.splitlines() if line.strip() and line.strip()!='>']
assert prompt_text(old)==prompt_text(new)
assert Counter(x for x in new.splitlines() if x.rstrip()!=x)<=Counter(x for x in old.splitlines() if x.rstrip()!=x)
opened=False
for line in new.splitlines():
 if line.startswith('```'):opened=not opened
assert not opened
links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',new);checked=0
for link in links:
 if link.startswith(('http:','https:','#','mailto:')):continue
 name=link.split('#')[0]
 if name:assert (p.parent/name).exists(),link;checked+=1
protected={x:sha((ROOT/x).read_bytes()) for x in baseline if x!=str(p.relative_to(ROOT))}
expected_protected=json.loads((HERE/'protected-at-apply.json').read_text())
# Other work owns these paths. Record their live hashes without overwriting or
# treating concurrent writes outside our scope as permission to modify them.
protected_changed_since_review={x:protected[x] for x in protected if protected[x]!=expected_protected[x]}
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
backup=p.parent/'backups'/f'{p.stem}__{stamp}.md'
with backup.open('xb') as f:f.write(oldraw)
assert backup.read_bytes()==oldraw
p.write_text(new)
report={'backup':str(backup.relative_to(ROOT)),'before_sha256':sha(oldraw),'after_sha256':sha(p.read_bytes()),'changed_sections':['000 scope','002 state/tree/examples/helpers/pseudocode','003 continuation reasoning','004 formatting only','005 actual pending items'],'definition001_exact':True,'appendices_and_references_exact':True,'original_note_exact_bytes':len(oldnote),'original_note_sha256':sha(oldnote),'prompt_nonformat_text_exact':True,'one_active_tree':True,'numbered_algorithm_steps_not_markdown_headings':True,'balanced_fences':True,'local_file_links_resolve':checked,'no_new_trailing_whitespace':True,'protected_hashes_at_apply':protected,'further_concurrent_changes':protected_changed_since_review,'independent_format_numeric_and_contract_reviews':'PASS','production_edited_by_this_task':False,'concurrent_changes_reviewed':json.loads((HERE/'concurrent-changes.json').read_text()),'obsidian_final_check':'pending'}
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(timespec='seconds')
with (ROOT/'logXW.md').open('a') as f:f.write(f'\n- **{stamp} | Codex | Memo020 note formatting and checkpoint consistency** — Compared004 against202545/211718 backups: original854-byteSidnote remainedexact; wrappedit inone textfence andmadepromptonecontinuousquote withoutword/numberchanges. ThreeindependentreviewsPASS. Unifiedactivea–d/003/005 aroundordinaryimmutableQ return/reuse, fulloldsourceprefixguard, explicitSroles/freshworkcontainers, deterministicone-event-perFX, EOFnoevent/no-cachecommit, currentN/context/unresolvedrefresh andidenticalsnapshotidempotence; kept001/allappendices/References exact. Added7stagecontinuationtable. IsolatedQmodel20nonemptyfixtures/40nonemptysplitpoints:158successfulcalls+5expectedrejections, allQfieldsagreewithone-shot andoldQunmodified. Savedfullbackup `{backup.name}` beforeoneedit. Scope/hash/fence/localfilelink/no-new-whitespace checksPASS;protectedfilesnoteditedbythistask. Concurrent028/bi/plot/testupdateswereobservedandpreserved;005nowacknowledgesthecurrentrollingimplementationratherthanclaimingoldcandidatecode. UIverificationpending; no production/API/028/codechanges.\n')
print(json.dumps({k:v for k,v in report.items() if k!='protected_hashes'},ensure_ascii=False))
