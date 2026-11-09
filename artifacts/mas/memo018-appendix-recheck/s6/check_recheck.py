"""Verify S6 source supplements; never import or execute CC reference code."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
memo=ROOT/'docs/memo/memoWX_023_Chan_zoushi.md'
text=memo.read_text()
baseline=json.loads((HERE.parent/'baseline.json').read_text())
expected=next(item['main_prefix_sha256'] for item in baseline if item['memo']==str(memo.relative_to(ROOT)))
assert hashlib.sha256(text.split('## Appendix A —',1)[0].encode()).hexdigest()==expected
old=json.loads((ROOT/'artifacts/mas/memo018-appendix-study/s6/quote_manifest.json').read_text())
new=json.loads((HERE/'added_quotes.json').read_text())
assert len(old)==7 and len(new)==7
for row in old+new:
    p=ROOT/f'references/chan_theory/{row["lesson"]:03d}.md'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256']
    source='\n'.join(p.read_text().splitlines()[row['start_line']-1:row['stop_line']])
    assert source==row['source_text']
    rendered=re.sub(r'</?span\b[^>]*>','',source).replace('==','\\=\\=')
    rendered=rendered.replace('(017/image001.jpg)','(memoWX_023_Chan_zoushi/lesson017-image001.jpg)')
    rendered=rendered.replace('(020/image005.jpg)','(memoWX_023_Chan_zoushi/lesson020-image005.jpg)')
    block='\n'.join('> '+line if line else '>' for line in rendered.splitlines())
    assert block in text,(row['lesson'],row['start_line'])
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
    if not target.startswith(('http://','https://','#')):
        assert (memo.parent/target).exists(),target
refs=re.findall(r'^\[(\d+)\]\s',text,re.M)
assert refs==[str(n) for n in range(1,22)]
assert set(re.findall(r'\[(\d+)\](?!\()',text))<=set(refs)
images=json.loads((ROOT/'artifacts/mas/memo018-appendix-study/s6/figure_provenance.json').read_text())
for row in images:
    raw=(ROOT/row['source']).read_bytes()
    assert (ROOT/row['destination']).read_bytes()==raw
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
cc=ROOT/'references/cc_algo/local_snapshot/374268381a3e/src/cc/algo'
tree=ast.parse((cc/'same_level.py').read_bytes())
funcs={n.name:(n.lineno,n.end_lineno) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
assert funcs['first_exit']==(1405,1437)
assert funcs['exit_is_valid_for_final_cores']==(1439,1471)
assert funcs['exit_survives_internal_extension']==(1473,1511)
assert funcs['valid_exit_through']==(1515,1555)
assert funcs['refine_complete_phase_partitions']==(1681,1857)
# Reconfirm displayed teaching arithmetic only, without executing its source builder.
example=json.loads((ROOT/'artifacts/mas/memo018-appendix-study/s6/manual_example.json').read_text())
points=example['points']; assert max(points[12:14])<example['centers']['B']['zd']
assert points[14]<points[12]
assert set(range(13)) & set(range(9,13))=={9,10,11,12}
assert not (14<points[12]) and 27>points[9]
out={'memo':str(memo.relative_to(ROOT)),'main_prefix_sha256':expected,
     'original_quote_blocks_preserved':7,'added_quote_blocks':7,'total_source_blocks':14,
     'source_quote_match':'all14 exactly match stated ranges after disclosed styling/path/equality normalization',
     'reference_count':21,'relative_links':'passed','source_image_copies_unchanged':2,
     'new_figures':0,'manual_example':'originalextend arithmetic and provisionaloverlap reconfirmed; noCC execution',
     'nested_function_lines':'AST locations checked','cc_execution':False,
     'remaining_gaps':['No dynamicCC/equivalence/stability/proof tests',
                        'Complexsame_level/refinement andrecursivesharedturn have sourcecoverage, not complete numericalruntime replay',
                        'Selected topicalcontexts reviewed; no claim everyword/image across108lessons was audited']}
(HERE/'final_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
