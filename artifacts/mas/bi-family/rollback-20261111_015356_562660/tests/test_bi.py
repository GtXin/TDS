"""Memo020 rolling protocol: definition, committed R and open cache."""
from datetime import datetime, timedelta, timezone
from dataclasses import replace
import pytest
from chanlab.algo.bi import Bi, BiSeries
from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.chan_table import ChanTable

VALUES=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1]

def source(values=VALUES):
    raw=KlineTSeries(tuple(Kline('S','1m','test',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),v,v+1,v,v+1,1) for i,v in enumerate(values)))
    merged=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015')
    return FenxingSeries.derive_from(merged,{},'019')

def test_rejected_extension_preserves_cache_and_R():
    f=source();r=BiSeries.scan(f,'020');s=r['series']
    assert len(s)==1 and r['cache_pair']==(1,2)
    assert tuple((p.start_fenxing_index,p.end_fenxing_index) for p in s)==((0,1),)
    assert any(e['rule']=='reject_extension' for e in s.trace)
    assert r['working'].id==len(s) and r['next_position']==len(f)
    assert r['working'] not in s.items

@pytest.mark.parametrize('values',[[1],[1,2],[1,2,1],[1,0,3,6,9,12,9,6,9,12,10,7,4,2,3],VALUES])
def test_definition_and_eof(values):
    f=source(values);r=BiSeries.scan(f,'020');s=r['series'];pairs=[(p.start_fenxing_index,p.end_fenxing_index) for p in s]
    if r['working']:pairs.append(r['cache_pair'])
    for i,(a,b) in enumerate(pairs):
        assert BiSeries._check_pair(f,a,b)
        if i:assert pairs[i-1][1]==a
    assert r['next_position']==len(f)
    assert BiSeries.derive_from(f,{},'020').items==s.items


def test_continuation_and_old_records():
    values=VALUES+[2,4,6,8,6,4,2,0,2]
    first=BiSeries.scan(source(),'020');old_items=first['series'].items
    r=BiSeries.scan(source(values),'020',first);fresh=BiSeries.scan(source(values),'020')
    assert r['series'].items==fresh['series'].items and r['cache_pair']==fresh['cache_pair']
    assert r['series'].items[:len(old_items)]==old_items
    assert BiSeries.scan(source(values),'020',r)['series'].items==r['series'].items
    with pytest.raises(ValueError):BiSeries.scan(source([v+100 for v in values]),'020',first)
    with pytest.raises(ValueError):BiSeries.scan(source(values),'other',first)
    with pytest.raises(ValueError):BiSeries.scan(source(values),'020',{**first,'next_position':999})
    with pytest.raises(ValueError):BiSeries.scan(source(values),'020',{**first,'cache_pair':None})


def test_access_and_table(tmp_path):
    r=BiSeries.scan(source(),'020');s=r['series'];raw=s.source_series.source_series.source_series
    assert tuple(s)==s[:];assert s.get_by_id(0)==s[0];assert not s.explain(0)['working']
    with pytest.raises(KeyError):s.get_by_id(999)
    with pytest.raises(ValueError):replace(s,config={'protocol':'rolling020','route':(999,)})
    t=s.to_chan_table(ChanTable.from_source_series(raw,{}),'bi');p=tmp_path/'a.csv';c=tmp_path/'c.csv';t.write_csv(p,c)
    restored=BiSeries.from_chan_table(ChanTable.read_csv(p,c),'bi')
    assert restored.items==s.items
    assert len(s.to_dataframe())==len(s)
    assert s.plot(volume=False)

@pytest.mark.parametrize('changes',[{'id':True},{'start_price':float('nan')},{'direction':'x'},{'status':'confirmed'}])
def test_bad_record(changes):
    with pytest.raises(ValueError):replace(Bi(0,0,1,1,2,'up'),**changes)


def test_empty_to_first_fractal_and_plot_cache():
    initial=BiSeries.scan(source([1,2]),'020')
    continued=BiSeries.scan(source([1,2,1,0,1,2,3,4,3]),'020',initial)
    assert continued['next_position']==len(continued['series'].source_series)
    r=BiSeries.scan(source(),'020');s=r['series']
    fig=s.plot(working=r['working'],volume=False)
    assert {'top fractal','bottom fractal'} <= {t.name for t in fig.data}
    assert any(t.line.dash=='dash' for t in fig.data if t.name.endswith('unfinished cache'))
    assert all(t.line.dash=='solid' for t in fig.data if t.name.endswith('committed — unconfirmed'))
    s.plot(raw_start=0,raw_stop=1,working=r['working'])

@pytest.mark.parametrize('changes',[{'source_series':None},{'rule_tree_ref':''},{'config':{}},{'trace_by_point':()},{'trace_by_point':((999,),)},{'items':(None,)}])
def test_invalid_series(changes):
    s=BiSeries.scan(source(),'020')['series']
    with pytest.raises((ValueError,AttributeError)):replace(s,**changes)


def test_trace_corruption():
    s=BiSeries.scan(source(),'020')['series']
    with pytest.raises(ValueError):replace(s,trace=({'rule':'invented'},))
    with pytest.raises(ValueError):replace(s,trace=({'rule':'extend','before':(),'after':()},))
    with pytest.raises(ValueError):BiSeries.derive_from(source(),{'route':(0,1)},'020')
    with pytest.raises(ValueError):BiSeries.scan(None,'020')
