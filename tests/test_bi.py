"""DP029 objective, complete pair evidence, independent optimality and adapters."""
import importlib.util
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest
from chanlab.algo.bi import Bi,BiSeries
from chanlab.algo.kline import Kline,KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.chan_table import ChanTable
from chanlab.data import bi_table

spec=importlib.util.spec_from_file_location('dp029oracle',Path(__file__).parents[1]/'artifacts/mas/bi-dp029/oracle.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
VALUES=[2,0,2,4,6,8,6,4,2,0,2,4,6,8,6,4,2,0,2]

def source(values=VALUES):
 raw=KlineTSeries(tuple(Kline('S','1m','test',datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=i),v,v+1,v,v+1,1) for i,v in enumerate(values)))
 m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'015')
 return FenxingSeries.derive_from(m,{},'019')

def series(mode='strong',values=VALUES):return BiSeries.derive_from(source(values),{'distance_mode':mode},'029')

def test_memo029_example_and_per_endpoint_optimum():
 f=source();s=series();assert len(s)==4
 route,best,prev=BiSeries._solve(f,4)
 assert route==(0,1,2,3,4) and best==(0,1,2,3,4) and prev==(None,0,1,2,3)
 assert oracle.solve(f,4,True)==(route,best,prev)
 assert s.unresolved_ranges()==((0,1),(18,19))
 assert BiSeries.derive_from(f,{},'029').items==s.items

@pytest.mark.parametrize('mode,gap',[('strong',4),('weak',3)])
@pytest.mark.parametrize('values',[[1],[1,2],[1,2,1],[0,5,0,1,2,3,4,5,6,5,4,3,2,1,0,1],[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1],[1,0,2,4,2,0,2,4,2,0,1]])
def test_exhaustive_definition_and_objective(mode,gap,values):
 f=source(values);s=BiSeries.derive_from(f,{'distance_mode':mode},'029');route=() if not len(s) else (s[0].start_fenxing_index,)+tuple(p.end_fenxing_index for p in s)
 assert (route,)+BiSeries._solve(f,gap)[1:]==oracle.solve(f,gap,True)
 if not len(s):assert s.unresolved_ranges()==((0,len(f.source_series)),)


def test_strong_weak_distance_boundary():
 f=source([1,0,2,4,2,0,2,4,2,0,1]);a=series('strong',[1,0,2,4,2,0,2,4,2,0,1]);b=series('weak',[1,0,2,4,2,0,2,4,2,0,1])
 assert len(b)>=len(a)
 for i in range(len(f)):
  for j in range(i+1,len(f)):
   assert BiSeries._check_pair(f,i,j,3)[0]==oracle.pair(f,i,j,3)


def test_access_freezing_explain():
 s=series();assert tuple(s)==s[:] and s[-1] is s.items[-1];assert s.get_by_id(0) is s[0]
 with pytest.raises(KeyError):s.get_by_id(999)
 with pytest.raises(ValueError):s.get_by_id(True)
 with pytest.raises(FrozenInstanceError):s[0].id=9
 with pytest.raises(TypeError):s.config['distance_mode']='weak'
 assert s.explain(0)['evidence']['pair']==(0,1)
 assert s.explain(0)['raw_anchors']==(1,5)

@pytest.mark.parametrize('changes',[{'id':True},{'id':-1},{'start_fenxing_index':2},{'end_fenxing_index':0},{'start_price':float('nan')},{'start_price':True},{'end_price':float('inf')},{'direction':'bad'},{'status':'confirmed'},{'confirmed_at':datetime.now(timezone.utc)}])
def test_bad_record(changes):
 with pytest.raises(ValueError):replace(series()[0],**changes)

@pytest.mark.parametrize('config',[{'distance_mode':'bad'},{'distance_mode':True},{'route':(0,1)},{'min_gap':3}])
def test_bad_config(config):
 with pytest.raises(ValueError):BiSeries.derive_from(source(),config,'029')

@pytest.mark.parametrize('changes',[{'source_series':None},{'rule_tree_ref':''},{'trace':()},{'trace_by_point':()},{'trace_by_point':((999,),)},{'items':(None,)}])
def test_invalid_series(changes):
 with pytest.raises(ValueError):replace(series(),**changes)


def test_input_indices_and_recovery_errors():
 f=source()
 for a,b in [(True,1),(-1,1),(0,99)]:
  with pytest.raises(ValueError):BiSeries._check_pair(f,a,b,4)
 assert not BiSeries._check_pair(f,1,0,4)[0]
 assert not BiSeries._check_pair(f,0,2,4)[0]
 with pytest.raises(ValueError):BiSeries._recover([None,None],0,1)
 with pytest.raises(ValueError):BiSeries._validate_route(f,(0,2),4)
 with pytest.raises(ValueError):BiSeries.derive_from(None,{},'029')


def test_registration_and_versioned_roundtrip(tmp_path):
 s=series();raw=s.source_series.source_series.source_series;t=ChanTable.from_source_series(raw,{})
 table=s.to_chan_table(t,'strong');weak=BiSeries.derive_from(s.source_series,{'distance_mode':'weak'},'029');table=weak.to_chan_table(table,'weak')
 assert BiSeries.from_chan_table(table,'strong') is s and BiSeries.from_chan_table(table,'weak') is weak
 assert len(table.feature_series)==4
 path=tmp_path/'table.csv';context=tmp_path/'context.csv';table.write_csv(path,context);out=ChanTable.read_csv(path,context)
 assert out.feature_series['strong'].items==s.items
 assert out.feature_series['strong'].source_series is out.feature_series['weak'].source_series
 assert s.to_dataframe().attrs['config']['distance_mode']=='strong'
 with pytest.raises(ValueError):BiSeries.from_chan_table(table,'strong:source')
 data=json.loads(table.context[bi_table.FEATURE_CONTEXT]);data['strong']['records'][0]['start_price']=999
 with pytest.raises(ValueError):bi_table.decode_features(json.dumps(data),dict(table.feature_series))


def test_plot_every_fractal_ids_and_cross_boundary():
 s=series();fig=s.plot(raw_start=3,raw_stop=16,volume=False)
 assert {'top fractal','bottom fractal'} <= {t.name for t in fig.data}
 assert any(t.name=='Bi0' for t in fig.data)
 assert all(t.line.dash!='dash' for t in fig.data if t.name.startswith('Bi'))
 assert any('FX' in text for t in fig.data if t.name in ('top fractal','bottom fractal') for text in t.text)
 assert s.plot(show_gaps=True,market='China')
 assert len(series(values=[1,2]).to_dataframe())==0


def test_gap_three_is_weak_only():
 values=[1,0,1,2,3,2,1,0,1]
 assert len(series('strong',values))==0
 assert len(series('weak',values))==2
