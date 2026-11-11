"""Apply user's one-tree presentation correction after a fresh full backup."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import Counter
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
p=ROOT/'docs/memo/memoWX_020_Chan_bi.md'
report=json.loads((HERE/'verification.json').read_text())
raw=p.read_bytes();old=raw.decode()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)==report['after_sha256'], 'Memo changed; reread before applying'
start=old.index('### 002.a —');stop=old.index('### 002.b —')
a=(HERE/'section-002a.md').read_text()
new=old[:start]+a+old[stop:]
assert new[:start]==old[:start] and new[new.index('### 002.b —'):]==old[stop:]
assert not re.search(r'^#{1,6} 2\.[1-9]',a,re.M)
fences=re.findall(r'```text\n(.*?)\n```',a,re.S)
assert len(fences)==1 and fences[0]+'\n'==(HERE/'unified-tree.txt').read_text()
labels=re.findall(r'^[│ ├└─]*(2\.[1-9]) ',fences[0],re.M)
assert labels==[f'2.{i}' for i in range(1,10)],labels
refs=re.findall(r'(?:回|转)(2\.[1-9](?:\.[ab])?)',a)
assert all(x in labels or x in ('2.6.a','2.6.b') for x in refs)
assert Counter(x for x in new.splitlines() if x.rstrip()!=x)<=Counter(x for x in old.splitlines() if x.rstrip()!=x)
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
b=p.parent/'backups'/f'{p.stem}__{stamp}.md'
with b.open('xb') as f:f.write(raw)
assert b.read_bytes()==raw
p.write_text(new)
report['edits']=[{'backup':report['backup'],'after_sha256':report['after_sha256'],'description':'Filledb–d; first formatting pass used separate numbered headings, superseded by user correction.'},{'backup':str(b.relative_to(ROOT)),'after_sha256':sha(p.read_bytes()),'description':'One rooted texttree;2.x are algorithm nodes, not Markdown headings.'}]
report['backup']=str(b.relative_to(ROOT));report['after_sha256']=sha(p.read_bytes())
report['changed_scope']='002.a one-tree presentation/example move;002.b–d completion;000–001 and003onward exact'
report.pop('active_tree_decisions_exact',None)
report['active_tree_semantics_review']='PASS; only presentation and wording compacted; previous decisions retained'
report.pop('headings',None)
report['numbered_markdown_headings']=0;report['tree_code_blocks']=1;report['algorithm_nodes']=labels
report['bcd_unchanged_in_second_edit']=True
report['one_rooted_tree']=True
(HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'logXW.md').open('a') as f:
 stamp=datetime.now(ZoneInfo('America/Los_Angeles')).isoformat(timespec='seconds')
 f.write(f'\n- **{stamp} | Codex | Memo020 details and one-tree correction** — Added002.b numerical/state examples,002.c seven private helper contracts and002.d pure pseudocode after full backup memoWX_020_Chan_bi__20261110_211718_919409.md; moved19bar example froma→b. Independent numeric and contract reviewsPASS; isolated22fixtures/42splitpoints/174scans compare reduced/full decisions, preserveR and openEOF. First formatting pass wrongly used2.x Markdown headings; user clarified these are algorithm nodes and requested one tree like015. Read015, saved another complete backup `{b.name}`, and replaced only002.a with one rooted texttree, nesting2.3/2.4 under2.2.a; common2.7 andEOF2.8→2.9 preserved. ReviewerPASS. Definitions001,003onward/original004/allappendices and protectedfiles unchanged. One nativeUIcall timed out/reset; reconnect succeeded, final one-treeUI verification pending.\n')
print(json.dumps({'backup':str(b.relative_to(ROOT)),'one_tree':True,'nodes':labels,'bcd_preserved':True,'memo_sha256':report['after_sha256']}))
