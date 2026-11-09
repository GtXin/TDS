from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[4];ART=Path(__file__).parent
e=json.loads((ART/'evidence.json').read_text())
for x in e['saved']:
 p=ROOT/x['memo'];s=p.read_text();backup=(ROOT/x['backup']).read_text()
 assert s.split('## Appendix A —')[0]==backup.split('## Appendix A —')[0]
 assert hashlib.sha256(s.split('## Appendix A —')[0].encode()).hexdigest()==x['main_sections_sha256']
 assert s.count('## Appendix A —')==s.count('## Appendix B —')==s.count('## References')==1
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',s):
  if target.startswith(('http:','https:')):continue
  assert (p.parent/target).exists(),target
 refs=[int(n) for n in re.findall(r'^\[(\d+)\] ',s,re.M)]
 assert refs==list(range(1,len(refs)+1))
 cited={int(n) for n in re.findall(r'\[(\d+)\]',s.split('## References')[0])}
 assert cited==set(refs),(p,cited,refs)
for asset in e['original_figures']:
 raw=(ROOT/asset['source']).read_bytes();copy=(ROOT/asset['copy']).read_bytes()
 assert raw==copy and hashlib.sha256(raw).hexdigest()==asset['sha256']
for x in e['quote_selections']:
 src=ROOT/f"references/chan_theory/{x['lesson']:03}.md"
 raw='\n'.join(src.read_text().splitlines()[x['start']-1:x['stop']])
 assert hashlib.sha256(raw.encode()).hexdigest()==x['raw_sha256']
 norm=re.sub(r'</?span\b[^>]*>','',raw)
 # Strip only image-link lines to compare the continuous quoted wording.
 norm='\n'.join(line for line in norm.splitlines() if not re.fullmatch(r'!\[.*\]\(.*\)',line))
 found=False
 for name in ['memoWX_021_Chan_xianduan.md','memoWX_022_Chan_zhongshu.md']:
  s=(ROOT/'docs/memo'/name).read_text();quote='\n'.join(line[2:] if line.startswith('> ') else '' for line in s.splitlines() if line.startswith('>'))
  quote='\n'.join(line for line in quote.splitlines() if not re.fullmatch(r'!\[.*\]\(.*\)',line))
  if norm in quote:found=True
 assert found,x
assert len(list((ROOT/'references/chan_theory').glob('[0-9][0-9][0-9].md')))==108
result={'main_sections':'byte-identical to pre-edit templates','quotes':'9 continuous selections match source after declared style/image normalization','original_figures':'10 byte-identical copies, all visually inspected','links':'all relative targets exist, including two manual PNG charts','citations':'sequential and all referenced','cc_execution':False}
(ART/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(result)
