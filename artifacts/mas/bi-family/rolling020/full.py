"""Full-data rolling result, immutable R/table roundtrip and diagnostic plot."""
import json,hashlib
from pathlib import Path
from verify import check_merged
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
from chanlab.algo.chan_table import ChanTable
root=Path(__file__).resolve().parent
path=next(Path('samples/chan_table').glob('*chan_table_*.csv'));context=next(Path('samples/chan_table').glob('*context_*.csv'))
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (path,context)}
raw=KlineTSeries.read_csv(path,context);m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015');f=FenxingSeries.derive_from(m,{},'memo019')
r=BiSeries.scan(f,'memo020:rolling');s=r['series']; counts=check_merged(m,'FIRST',True)
table=s.to_chan_table(ChanTable.from_source_series(raw,dict(raw.context)),'bi');table.write_csv(root/'full-table.csv',root/'full-context.csv')
restored=BiSeries.from_chan_table(ChanTable.read_csv(root/'full-table.csv',root/'full-context.csv'),'bi');assert restored.items==s.items
for market in ('US','China'):
 fig=s.plot(working=r['working'],raw_start=max(0,f[r['cache_pair'][0]].anchor_raw_index-50),raw_stop=f[r['cache_pair'][1]].anchor_raw_index+100,volume=False,market=market,title='Rolling020: committed R and separate unfinished cache')
 fig.write_html(root/f'full-{market}.html');(root/f'full-{market}-figure.json').write_text(fig.to_json())
result={'raw':len(raw),'merged':len(m),'fractals':len(f),'committed':len(s),'working_pair':r['cache_pair'],'next_position':r['next_position'],'pending_start':r['pending_start'],'unresolved_merged':r['unresolved_merged'],'status':r['status'],'independent_full_range_oracle':dict(counts),'csv_context_roundtrip':True,'original_hashes_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())}
(root/'full-result.json').write_text(json.dumps(result,indent=2));print(result)
