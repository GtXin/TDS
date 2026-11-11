"""One scoped memo edit, full pre-edit backup, and preservation checks."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
memo=ROOT/'docs/memo/memoWX_020_Chan_bi.md'
baseline=json.loads((HERE/'baseline.json').read_text())
raw=memo.read_bytes();old=raw.decode()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)==baseline['memo_sha256'], 'Memo changed since draft baseline; reread before editing'
start=old.index('### 002.a —')
stop=old.index('## 003 —')
replacement=''.join((HERE/f'section-002{x}.md').read_text() for x in 'abcd')
new=old[:start]+replacement.rstrip()+'\n\n'+old[stop:]
assert new[:start]==old[:start] and new[new.index('## 003 —'):]==old[stop:]
# Move the example but preserve every decision/action line of the active tree.
def tree_content(s):
    a=s[s.index('### 002.a —'):s.index('### 002.b —')]
    a=a[a.index('**判断树：'):a.index('**追加输入时的入口。')]
    return [line.removeprefix('#### ') for line in a.splitlines() if line.strip() and not line.startswith('```')]
assert tree_content(new)==tree_content(old)
assert Counter(line for line in new.splitlines() if line.rstrip()!=line) <= Counter(line for line in old.splitlines() if line.rstrip()!=line)
# Balanced fences, true numbered headings, and local target existence.
assert sum(line.startswith('```') for line in new.splitlines())%2==0
headings=re.findall(r'^#### (2\.[1-9]) ',new[:new.index('## 003 —')],re.M)
assert headings==[f'2.{i}' for i in range(1,10)]
for n in 'abcd':assert len(re.findall(rf'^### 002\.{n} —',new,re.M))==1
links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',new)
checked=0
for link in links:
    if link.startswith(('https://','http://','#','mailto:')):continue
    target=link.split('#')[0]
    if target:
        assert (memo.parent/target).exists(),link
        checked+=1
protected={p:sha((ROOT/p).read_bytes()) for p in baseline['protected_hashes']}
assert protected==baseline['protected_hashes'], 'Protected path changed; inspect concurrent work'
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
backup=memo.parent/'backups'/f'{memo.stem}__{stamp}.md'
with backup.open('xb') as f:f.write(raw)
assert backup.read_bytes()==raw
memo.write_text(new)
assert memo.read_text()==new
report={
 'backup':str(backup.relative_to(ROOT)), 'before_sha256':sha(raw),'after_sha256':sha(memo.read_bytes()),
 'changed_scope':'002.a formatting/example move; fill002.b–d; 003+ and000–001 byte exact',
 'outside002_exact':True,'active_tree_decisions_exact':True,
 'original004_all_appendices_references_exact':True,'headings':headings,
 'balanced_fences':True,'local_file_links_resolve':checked,
 'no_new_trailing_whitespace':True,'protected_hashes':protected,
 'independent_contract_review':'PASS','independent_numeric_review':'PASS',
 'production_changed':False,'obsidian_final_check':'pending'
}
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='protected_hashes'},ensure_ascii=False))
