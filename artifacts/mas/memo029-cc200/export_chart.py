import sys,json
from pathlib import Path
sys.path.insert(0,'src')
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
p=Path('samples/chan_table');raw=KlineTSeries.read_csv(next(p.glob('*chan_table_*.csv')),next(p.glob('*context_*.csv')));m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015');f=FenxingSeries.derive_from(m,{},'memo019');r=json.loads(Path('artifacts/mas/memo029-cc200/result.json').read_text())
Path('/tmp/cc200-chart.json').write_text(json.dumps({'bars':[[i,k.low,k.high] for i,k in enumerate(m[:f[199].source_stop])],'fx':[[x.source_start+1,x.price,1 if x.kind=='top' else 0] for x in f[:200]],'route':r['reports']['strong']['route']}))
