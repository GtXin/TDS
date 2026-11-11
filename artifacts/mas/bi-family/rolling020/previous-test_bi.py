"""Independent candidate oracle, route contracts and integration regressions."""
import importlib.util
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from chanlab.algo.bi import Bi, BiSeries
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import Kline,KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.data import bi_table

spec=importlib.util.spec_from_file_location('bi_verify',Path(__file__).parents[1]/'artifacts/mas/bi-family/verify.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
VALUES=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]


def source(values=VALUES):
    raw=verify.raw_from(tuple((x,x+1) for x in values))
    merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015')
    return FenxingSeries.derive_from(merged,{},'019')


def series():
    f=source();report=BiSeries.derive_candidates(f,{},'020')
    return next(iter(report['groups'].values()))[0]


def test_reference_recovery_and_selection():
    f=source(); report=BiSeries.derive_candidates(f,{},'020')
    results=[s for g in report['groups'].values() for s in g]
    centers={tuple(f[i].source_start+1 for i in s.config['route']) for s in results}
    assert centers==verify.reference.run(tuple((x,x+1) for x in VALUES))
    assert (1,11,15,19) in centers and (1,5,9,19) not in centers
    assert report['blocked']
    with pytest.raises(ValueError): BiSeries.derive_from(f,{},'020')
    s=results[0]
    assert BiSeries.derive_from(f,{'route':s.config['route']},'020').items==s.items
    with pytest.raises(ValueError): BiSeries.derive_from(f,{'route':(999,)},'020')
    with pytest.raises(RuntimeError): BiSeries.derive_candidates(f,{'max_states':1},'020')
    assert BiSeries.derive_candidates(source([1,2]),{},'020')['groups']=={}


@pytest.mark.parametrize('values',[
[1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],
[8,9,6,4,2,0,4,7,5,3,1,0,1,2,3,4,3],
[1,0,3,6,9,12,9,6,9,12,10,7,4,2,3],
[1,0,3,6,9,12,10,11,13,14],VALUES])
def test_directed_mirrors(values):
    for bars in ([(v,v+1) for v in values],[(-v-1,-v) for v in values]): verify.check(bars)


def test_access_and_immutability():
    s=series(); assert tuple(s)==s[:]; assert s[-1] is s.items[-1]
    assert s.get_by_id(s[0].id) is s[0]
    with pytest.raises(KeyError): s.get_by_id(999)
    with pytest.raises(ValueError): s.get_by_id(True)
    with pytest.raises(FrozenInstanceError): s[0].id=4
    with pytest.raises(TypeError): s.config['x']=1
    e=s.explain(0); assert e['rule_tree_ref']=='020' and e['decisions']


@pytest.mark.parametrize('changes',[{'id':True},{'id':-1},{'start_price':float('nan')},{'end_price':True},{'direction':'bad'},{'status':'confirmed'},{'confirmed_at':datetime.now(timezone.utc)},{'end_fenxing_index':0}])
def test_invalid_record(changes):
    with pytest.raises(ValueError): replace(series()[0],**changes)


@pytest.mark.parametrize('changes',[{'rule_tree_ref':''},{'source_series':None},{'config':{'bad':1}},{'config':{'max_states':False}},{'trace_by_point':()},{'trace_by_point':((999,),)},{'items':(None,)}])
def test_invalid_series(changes):
    with pytest.raises((ValueError,TypeError)): replace(series(),**changes)


def test_table_roundtrip(tmp_path):
    s=series(); raw=s.source_series.source_series.source_series
    table=ChanTable.from_source_series(raw,{'snapshot':'synthetic'})
    out=s.to_chan_table(table,'bi'); assert BiSeries.from_chan_table(out,'bi') is s
    assert len(out.feature_series)==3
    assert out.source_series is raw and table[0]['bi_ids']=='NA'
    path=tmp_path/'table.csv'; context=tmp_path/'context.csv'
    out.write_csv(path,context)
    restored=ChanTable.read_csv(path,context)
    r=BiSeries.from_chan_table(restored,'bi'); assert r.items==s.items and r.explain(0)['centers']==s.explain(0)['centers']
    assert r.source_series is restored.feature_series['bi:source']
    payload=json.loads(out.context[bi_table.FEATURE_CONTEXT]); payload['bi']['records'][0]['start_price']=999
    with pytest.raises(ValueError): bi_table.decode_features(json.dumps(payload),{})
    with pytest.raises(ValueError): BiSeries.from_chan_table(out,'bi:source')
    frame=s.to_dataframe(); assert len(frame)==len(s) and tuple(frame.attrs['config']['route'])==s.config['route']


def test_plot():
    s=series()
    for market in ('US','China'):
        fig=s.plot(raw_start=3,raw_stop=20,market=market,volume=False)
        strokes=[t for t in fig.data if t.name.startswith('Bi')]
        assert strokes and strokes[-1].line.dash=='dash'
        assert all('unconfirmed' in t.name for t in strokes)
    assert s.plot(show_gaps=True)


def test_left_to_right_first_qualified_start():
    f=source([0,5,0,1,2,3,4,5,6,5,4,3,2,1,0,1])
    report=BiSeries.derive_candidates(f,{},'020')
    expected=next((i for i,a in enumerate(f) if any(verify.reference.pair(tuple((b.low,b.high) for b in f.source_series),(a.source_start+1,a.kind),(b.source_start+1,b.kind)) for b in f[i+1:])),None)
    assert expected==1
    assert report['groups']
    assert all(s.config['route'][0]==expected for group in report['groups'].values() for s in group)


def test_no_later_start_fallback_after_blocking():
    f=source([6,5,6,7,8,10,9,4,6,8,10,12,11])
    report=BiSeries.derive_candidates(f,{},'020')
    assert not report['groups'] and report['blocked']


def test_no_qualified_start():
    report=BiSeries.derive_candidates(source([0,1,0,1,0]),{},'020')
    assert not report['groups']
