"""Recheck changed evidence without mutating historical batch records or importing CC."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
PREV=ROOT/'artifacts/mas/memo018-appendix-study/s2-s3'
baseline=json.loads((OUT.parent/'baseline.json').read_text())
prefixes={row['memo']:row['main_prefix_sha256'] for row in baseline}
new=json.loads((OUT/'changes.json').read_text())
additional=json.loads((OUT/'additional-source-blocks.json').read_text())
checks=[]

for rec in json.loads((PREV/'source-excerpts.json').read_text()):
    src=ROOT/f"references/chan_theory/{rec['lesson']}.md"
    assert hashlib.sha256(src.read_bytes()).hexdigest()==rec['sha256']
    quoted='\n'.join('> '+line if line else '>' for line in rec['normalized_excerpt'].splitlines())
    assert quoted in (ROOT/f"docs/memo/{rec['memo']}.md").read_text()

def new_quote(rec,stem):
    raw='\n'.join((ROOT/f"references/chan_theory/{rec['lesson']}.md").read_text().splitlines()[rec['start']-1:rec['stop']])
    assert hashlib.sha256(raw.encode()).hexdigest()==rec['source_block_sha256']
    text=re.sub(r'</?span\b[^>]*>','',raw)
    if 'escape literal ==' in rec['normalization']:text=text.replace('==',r'\=\=')
    text=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',lambda m:f'![{m[1]}]({stem}/lesson{rec["lesson"]}-{Path(m[2]).name})',text)
    quote='\n'.join('> '+line if line else '>' for line in text.splitlines())
    assert quote in (ROOT/f'docs/memo/{stem}.md').read_text(),rec

for rec in new:new_quote(rec['detail']['new_quote'],Path(rec['memo']).stem)
for rec in additional['quotes']:new_quote(rec,Path(additional['memo']).stem)

figures=json.loads((PREV/'figure-provenance.json').read_text())
for rec in new:figures+=rec['detail']['new_quote']['figures']
for figure in figures:
    assert (ROOT/figure['source']).read_bytes()==(ROOT/figure['copy']).read_bytes()
    assert hashlib.sha256((ROOT/figure['copy']).read_bytes()).hexdigest()==figure['sha256']

for number,stem in [(19,'fenxing'),(20,'bi')]:
    name=f'docs/memo/memoWX_{number:03d}_Chan_{stem}.md'
    p=ROOT/name; raw=p.read_bytes();text=raw.decode()
    assert hashlib.sha256(raw.split(b'## Appendix A')[0]).hexdigest()==prefixes[name]
    refs=re.findall(r'^\[(\d+)\] ',text,re.M)
    assert refs==[str(i) for i in range(1,len(refs)+1)]
    assert set(re.findall(r'(?<!\\)\[(\d+)\](?!\()',text))<=set(refs)
    for target in re.findall(r'\]\(([^)]+)\)',text):
        assert (p.parent/target.split('#')[0]).exists(),target
    assert text.count('```')%2==0
    checks.append({'memo':name,'references':len(refs),'main_prefix':'matches task-start SHA-256','links_citations':'passed'})

assert len(list((ROOT/'references/chan_theory').glob('[0-9][0-9][0-9].md')))==108
cases=json.loads((OUT/'manual-cases.json').read_text())['cases']
assert [x['name'] for x in cases]==['strong_prev','strong_next','repair_accept','repair_reject']
assert cases[0]['ranges'][15]==[5.5,14] and 17-5.5>=.95*12
assert cases[1]['dep']==19 and 17-7<.95*12 and 17-7>=.95*9
assert cases[2]['dep']==16 and cases[2]['ranges'][12][1]==15.5 and cases[2]['ranges'][16][1]>15.5
assert cases[3]['dep']==18 and cases[3]['ranges'][16][1]<=15.5
graphs=[]
for name in ['cc-stroke-strong-recheck.png','cc-stroke-repair-recheck.png']:
    p=ROOT/'docs/memo/memoWX_020_Chan_bi'/name
    assert p.is_file()
    graphs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'visual_review':'Viewed final PNG; aligned price/source axes, annotations and no clipping.'})
result={'memos':checks,'retained_original_quote_blocks':13,'added_original_quote_blocks':5,'added_source_image_copies':3,'new_manual_cases':4,'new_manual_financial_charts':graphs,'source_quote_checks':'all18 retained/new normalized blocks match recorded sources','figure_copies':'all13 old/new distinct source copy paths byte-identical','cc_execution':False,'limits':'Whole-corpus keyword scan plus selected contextual reading and static code review; no exhaustive read, CC runtime verification or correctness proof.'}
(OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
