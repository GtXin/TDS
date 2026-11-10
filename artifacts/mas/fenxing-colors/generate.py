"""Back up existing charts and render matching red/green fractal palettes."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import shutil
import json
from hashlib import sha256
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from test_fenxing import derive
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
images=root/'docs/memo/memoWX_027_fenxingFamily'
backup=root/'docs/memo/backups'/f'memoWX_027_fenxingFamily__{stamp}'
shutil.copytree(images,backup)
prior=out/'before'/stamp
shutil.copytree(root/'artifacts/fenxing',prior)
sample=root/'samples/chan_table'
raw=KlineTSeries.read_csv(next(sample.glob('*chan_table*.csv')),next(sample.glob('*context*.csv')))
m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015:002:v1')
assert isinstance(m,MergedKlineSeries)
s=FenxingSeries.derive_from(m,{},'memo019:002:v1')
report={}
for name,series,kwargs in [('cc-last80',s,{}),('cc-last80-china',s,{'market':'China'}),('cc-last80-calendar',s,{'show_gaps':True}),('worked-example',derive(),{'volume':False})]:
    market=kwargs.get('market','US')
    fig=series.plot(**({'raw_start':len(raw)-80,'title':'CC 15m — geometric fractals (unconfirmed)'} if name!='worked-example' else {'title':'Memo019 example — 10 raw bars / 7 merged units / 3 geometric fractals'}),**kwargs)
    expected={'top fractal':'#dc2626' if market=='US' else '#16a34a','bottom fractal':'#16a34a' if market=='US' else '#dc2626'}
    for t in fig.data:
        if t.name in expected: assert t.marker.color==expected[t.name]
    dest=root/'artifacts/fenxing'/name
    fig.write_html(dest.with_suffix('.html'),include_plotlyjs=True)
    fig.write_image(dest.with_suffix('.png'),width=1440,height=750 if name=='worked-example' else 820)
    shutil.copy2(dest.with_suffix('.png'),images/f'{name}.png')
    report[name]={'market':market,'colors':expected,'sha256':sha256(dest.with_suffix('.png').read_bytes()).hexdigest()}
(out/'verification.json').write_text(json.dumps({'charts':report,'backup':str(backup.relative_to(root))},indent=2))
