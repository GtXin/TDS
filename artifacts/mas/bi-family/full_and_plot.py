"""Full-data resource probe and visually reviewable synthetic route."""
import hashlib
import json
import time
from pathlib import Path
from verify import raw_from
from chanlab.algo.bi import BiSeries
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
root=Path(__file__).resolve().parent
files=list(Path('samples/chan_table').glob('*chan_table_v*.csv'));path=next(p for p in files if 'context' not in p.name)
before=hashlib.sha256(path.read_bytes()).hexdigest(); raw=KlineTSeries.read_csv(path)
merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015');fx=FenxingSeries.derive_from(merged,{},'memo019')
start=time.perf_counter()
try:
    report=BiSeries.derive_candidates(fx,{'max_states':100000},'memo020')
    outcome={'complete':True,'routes':sum(map(len,report['groups'].values())),'initial_a':report['initial_a'],'status':report['status'],'states':report['states'],'blocked_count':len(report['blocked']),'blocked':[{'prefix':list(x['prefix']),'failed':x['failed']} for x in report['blocked']]}
except RuntimeError as exc: outcome={'complete':False,'reason':str(exc)}
(root/'full-data.json').write_text(json.dumps({'raw':len(raw),'merged':len(merged),'fractals':len(fx),'budget':100000,'seconds':time.perf_counter()-start,'source_hash_unchanged':before==hashlib.sha256(path.read_bytes()).hexdigest(),**outcome},indent=2))
values=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]
m=MergedKlineSeries.derive_from(raw_from([(v,v+1) for v in values]),{'initialization':'UP'},'015');f=FenxingSeries.derive_from(m,{},'019')
s=BiSeries.derive_from(f,{'route':(0,3,4,5)},'020')
for market in ('US','China'):
    fig=s.plot(market=market,volume=False,title='Bi candidate route — unconfirmed')
    fig.write_html(root/f'worked-{market}.html')
    try: fig.write_image(root/f'worked-{market}.png',width=1200,height=650)
    except Exception as exc: print('PNG unavailable',repr(exc))
print((root/'full-data.json').read_text())
