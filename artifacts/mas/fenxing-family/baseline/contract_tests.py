"""Contract tests shared by the frozen baseline and continuation."""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import random

import pytest
from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import Fenxing, FenxingSeries


def merged(bounds):
    raw = KlineTSeries(tuple(Kline('TEST','1m','synthetic',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),low,high,low,high,1) for i,(low,high) in enumerate(bounds)))
    return MergedKlineSeries.derive_from(raw, {'initialization':'UP'}, 'memo015:v1')


def example():
    return merged([(0,3),(3,5),(2,6),(3,6),(1,4),(0,3),(0,2),(2,5),(3,6),(1,4)])


def derive(m=None, config=None):
    return FenxingSeries.derive_from(example() if m is None else m, {} if config is None else config, 'memo019:002:v1')


def test_main_example_and_methods():
    m = example()
    assert [(b.low,b.high,b.source_start,b.source_stop) for b in m] == [(0,3,0,1),(3,6,1,4),(1,4,4,5),(0,2,5,7),(2,5,7,8),(3,6,8,9),(1,4,9,10)]
    s = derive(m)
    assert [(p.id,p.kind,p.price,p.anchor_raw_index,p.source_start,p.source_stop) for p in s] == [(0,'top',6,2,0,3),(1,'bottom',0,5,2,5),(2,'top',6,8,4,7)]
    assert s.source_series is m
    assert len(s.trace)==5 and s.trace_by_point == ((0,),(2,),(4,))
    assert list(s)==list(s.items) and s[-1] is s.get_by_id(2) and s[:] == s.items
    assert 'raw anchor=2' in s.explain(0) and '2.5.a' in s.explain(0)
    assert [p.anchor_raw_index for p in derive(m, {'anchor_tie':'LAST'})] == [3,6,8]
    assert all(p.status=='unconfirmed' and p.confirmed_at is None for p in s)
    with pytest.raises(KeyError): s.get_by_id(99)
    with pytest.raises(ValueError): s.get_by_id(True)
    with pytest.raises(IndexError): s.explain(99)


@pytest.mark.parametrize('bounds', [[(1,3)],[(1,3),(2,4)],[(1,3),(2,4),(3,5)],[(3,5),(2,4),(1,3)]])
def test_empty_results(bounds):
    s = derive(merged(bounds))
    assert not s.items and not s.trace_by_point and len(s.trace)==1


@pytest.mark.parametrize('config', [None,[],{'unknown':'FIRST'},{'anchor_tie':'first'},{'anchor_tie':None}])
def test_bad_configs(config):
    with pytest.raises(ValueError): FenxingSeries.derive_from(example(),config,'v')


@pytest.mark.parametrize('source', [None,{}, {'kind':'pending'}, {'kind':'dual'}])
def test_bad_source(source):
    with pytest.raises(ValueError): FenxingSeries.derive_from(source,{},'v')


@pytest.mark.parametrize('ref', ['', ' ',None,4])
def test_bad_ref(ref):
    with pytest.raises(ValueError): FenxingSeries.derive_from(example(),{},ref)


@pytest.mark.parametrize('changes', [{'id':True},{'id':-1},{'id':1.5},{'kind':'peak'},{'price':float('nan')},{'price':float('inf')},{'price':True},{'price':'6'},{'price':10**1000},{'source_stop':2},{'anchor_raw_index':-1},{'status':'confirmed'},{'confirmed_at':datetime.now(timezone.utc)}])
def test_local_invalid(changes):
    with pytest.raises(ValueError): replace(derive()[0],**changes)


def test_immutability_and_detachment():
    s=derive(); config={'anchor_tie':'FIRST'}; trace=[dict(e) for e in s.trace]
    copied=FenxingSeries(s.source_series,list(s),config,s.rule_tree_ref,trace,list(s.trace_by_point))
    config['anchor_tie']='LAST'; trace[0]['center']=99
    assert copied.config['anchor_tie']=='FIRST' and copied.trace[0]['center']==1
    with pytest.raises(TypeError): copied.trace[0]['anchor']['selected']=9
    with pytest.raises(TypeError): copied.config['anchor_tie']='LAST'
    with pytest.raises(FrozenInstanceError): copied.items=()
    with pytest.raises(FrozenInstanceError): copied[0].price=9


@pytest.mark.parametrize('mode', ['missing','extra','duplicate','wrongprice','wronganchor','wrongwindow','order','trace','links','boollink','shorttrace','itemtype','badsource','badref'])
def test_series_rejects_corruption(mode):
    s=derive(); changes={}
    if mode=='missing': changes={'items':s.items[:-1], 'trace_by_point':s.trace_by_point[:-1]}
    if mode=='extra': changes={'items':s.items+(replace(s[-1],id=8),), 'trace_by_point':s.trace_by_point+((4,),)}
    if mode=='duplicate': changes={'items':(s[0],replace(s[1],id=0),s[2])}
    if mode=='wrongprice': changes={'items':(replace(s[0],price=7),)+s.items[1:]}
    if mode=='wronganchor': changes={'items':(replace(s[0],anchor_raw_index=3),)+s.items[1:]}
    if mode=='wrongwindow': changes={'items':(replace(s[0],source_start=1,source_stop=4),)+s.items[1:]}
    if mode=='order': changes={'items':tuple(reversed(s.items))}
    if mode=='trace': changes={'trace':(dict(s.trace[0],center=9),)+s.trace[1:]}
    if mode=='links': changes={'trace_by_point':((1,),)+s.trace_by_point[1:]}
    if mode=='boollink': changes={'trace_by_point':((False,),)+s.trace_by_point[1:]}
    if mode=='shorttrace': changes={'trace':s.trace[:-1]}
    if mode=='itemtype': changes={'items':(object(),)+s.items[1:]}
    if mode=='badsource': changes={'source_series':{}}
    if mode=='badref': changes={'rule_tree_ref':''}
    with pytest.raises(ValueError): replace(s,**changes)


def test_source_ids_not_positions_and_no_match():
    m=example(); altered=replace(m,klines=tuple(replace(b,id=100+i*3,direction=None) for i,b in enumerate(m)))
    assert derive(altered).items==derive(m).items
    wrong=replace(m,klines=(m[0],replace(m[1],high=7))+m.klines[2:])
    with pytest.raises(ValueError,match='not present'): derive(wrong)
    a,b=m[0],m[1]
    with pytest.raises(ValueError): FenxingSeries._direction_between(a,replace(b,low=a.low))
    with pytest.raises(ValueError): FenxingSeries._validate_result(altered,derive(m))


@pytest.mark.parametrize('mode', ['kind','policy','price','range','source'])
def test_anchor_preconditions(mode):
    m=example(); raw=m.source_series; b=m[1]; kind='top'; price=6; policy='FIRST'
    if mode=='kind': kind='bad'
    if mode=='policy': policy='bad'
    if mode=='price': price=7
    if mode=='range': b=replace(b,source_stop=100)
    if mode=='source': raw=None
    with pytest.raises(ValueError): FenxingSeries._resolve_anchor(raw,b,kind,price,policy)


def test_revision_and_append():
    old=derive()
    bounds=[(0,3),(3,5),(2,6),(3,6),(1,4),(0,3),(0,2),(2,5),(3,6),(4,7)]
    updated=derive(merged(bounds)); appended=derive(merged(bounds+[(2,5)]))
    assert len(old)==3 and len(updated)==2
    assert (appended[-1].price,appended[-1].anchor_raw_index)==(7,9)
    assert old[-1].price==6


def test_short_validator_rejects_fabrication():
    s=derive(merged([(1,3)]))
    with pytest.raises(ValueError): replace(s,trace=({'rule':'fake'},))
    with pytest.raises(ValueError): replace(s,items=(Fenxing(0,'top',3,0,0,3),),trace_by_point=((0,),))


def test_randomized_independent_four_comparison_oracle():
    rng=random.Random(19)
    for _ in range(60):
        value=100; bounds=[]
        for _ in range(rng.randint(3,45)):
            value+=rng.choice((-3,-2,-1,1,2,3)); bounds.append((value,value+10))
        m=merged(bounds); s=derive(m); expected=[]
        for i in range(1,len(m)-1):
            a,b,c=m[i-1],m[i],m[i+1]
            if b.high>max(a.high,c.high) and b.low>max(a.low,c.low): expected.append(('top',b.high,i-1,i+2))
            if b.high<min(a.high,c.high) and b.low<min(a.low,c.low): expected.append(('bottom',b.low,i-1,i+2))
        assert [(p.kind,p.price,p.source_start,p.source_stop) for p in s]==expected
