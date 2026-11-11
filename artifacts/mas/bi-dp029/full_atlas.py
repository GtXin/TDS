"""Complete both-mode validation and gap-free200bar/20overlap HTML/PNG atlas."""
import json,hashlib,time,html
from pathlib import Path
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.bi import BiSeries
from chanlab.algo.chan_table import ChanTable
ROOT=Path(__file__).resolve().parent


def independent_full(fx,gap):
    # Build independent endpoint edges from monotonically expanded raw ranges;
    # this deliberately does not use production sparse-table queries.
    n=len(fx);edges=[[] for _ in fx];m=fx.source_series
    for a,x in enumerate(fx):
        i=x.source_start+1;cursor=i;low=m[i].low;high=m[i].high
        for b in range(a+1,n):
            y=fx[b];j=y.source_start+1
            while cursor<j:
                cursor+=1;low=min(low,m[cursor].low);high=max(high,m[cursor].high)
            if x.kind==y.kind or j-i<gap:continue
            top,bottom=(m[i],m[j]) if x.kind=='top' else (m[j],m[i])
            if top.high>bottom.high and bottom.low<top.low and high<=top.high and low>=bottom.low:edges[a].append(b)
    a=next((i for i,e in enumerate(edges) if e),None);best=[-1]*n;prev=[None]*n
    if a is None:return (),tuple(best),tuple(prev)
    best[a]=0
    for p in range(a,n):
        if best[p]<0:continue
        for f in edges[p]:
            if best[p]+1>best[f]:best[f]=best[p]+1;prev[f]=p
    end=max(i for i in range(n) if best[i]>0);route=[end]
    while route[-1]!=a:route.append(prev[route[-1]])
    return tuple(reversed(route)),tuple(best),tuple(prev)


def main():
    sample=Path('samples/chan_table');path=next(sample.glob('*chan_table*.csv'));context=next(sample.glob('*context*.csv'))
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (path,context)}
    raw=KlineTSeries.read_csv(path,context);m=MergedKlineSeries.derive_from(raw,{'initialization':'UP'},'memo015:002');fx=FenxingSeries.derive_from(m,{},'memo019:002')
    result={'raw':len(raw),'merged':len(m),'fractals':len(fx),'source_hashes':before,'modes':{}}
    windows=[(a,min(a+200,len(raw))) for a in range(0,len(raw),180)]
    covered=set(i for a,b in windows for i in range(a,b));assert covered==set(range(len(raw)))
    manifest=[]
    for mode,gap in [('strong',4),('weak',3)]:
        t=time.perf_counter();s=BiSeries.derive_from(fx,{'distance_mode':mode},'memo029:001,002a-f');seconds=time.perf_counter()-t
        expected=independent_full(fx,gap);assert BiSeries._solve(fx,gap)==expected
        actual=() if not len(s) else (s[0].start_fenxing_index,)+tuple(p.end_fenxing_index for p in s)
        assert actual==expected[0]
        folder=ROOT/mode;folder.mkdir(exist_ok=True)
        table=s.to_chan_table(ChanTable.from_source_series(raw,dict(raw.context)),f'bi:{mode}')
        table.write_csv(folder/'table.csv',folder/'context.csv')
        reloaded=BiSeries.from_chan_table(ChanTable.read_csv(folder/'table.csv',folder/'context.csv'),f'bi:{mode}')
        assert reloaded.items==s.items and reloaded.config==s.config and reloaded.explain(0)==s.explain(0)
        result['modes'][mode]={'strokes':len(s),'route':actual,'solve_seconds':seconds,'unresolved_merged':s.unresolved_ranges(),'independent_all_endpoint_best_prev_equal':True,'table_roundtrip':True,'pages':len(windows)}
        rows=[]
        for number,(a,b) in enumerate(windows,1):
            stem=f'page-{number:03d}'
            fig=s.plot(raw_start=a,raw_stop=b,volume=False,market='China',title=f'{mode} {number:03d}/{len(windows):03d} — raw[{a}:{b}) — selected snapshot, unconfirmed')
            fig.update_layout(width=1600,height=900,margin={'t':140,'b':95})
            # Keep crossing endpoints as true coordinates while clipping to the
            # selected raw window. Never recompute DP independently by page.
            fig.update_xaxes(range=[-.8,b-a-.2])
            fig.write_html(folder/f'{stem}.html',include_plotlyjs='directory')
            (folder/f'{stem}.json').write_text(fig.to_json())
            fxs=[i for i,f in enumerate(fx) if a<=f.anchor_raw_index<b]
            bis=[p.id for p in s if fx[p.end_fenxing_index].anchor_raw_index>=a and fx[p.start_fenxing_index].anchor_raw_index<b]
            entry={'mode':mode,'page':number,'raw':[a,b],'utc':[raw[a].timestamp.isoformat(),raw[b-1].timestamp.isoformat()],'fx_positions':fxs,'bi_ids':bis,'html':f'{mode}/{stem}.html','png':f'{mode}/{stem}.png','rule':'memo029:001,002a-f','distance_gap':gap,'visually_checked':False}
            manifest.append(entry)
            rows.append(f'<tr><td>{number}</td><td>{a}:{b}</td><td>{html.escape(entry["utc"][0])} — {html.escape(entry["utc"][1])}</td><td><a href="{stem}.html">interactive</a> · <a href="{stem}.png">PNG</a></td></tr>')
        (folder/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Bi029 '+mode+'</title><h1>'+mode+' complete atlas</h1><p>Raw/merged Klines, all visible fractals and selected Bi. No permanent confirmation inferred.</p><table>'+''.join(rows)+'</table>')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in before.items())
    result['source_hashes_unchanged']=True
    (ROOT/'full-result.json').write_text(json.dumps(result,indent=2));(ROOT/'atlas-manifest.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'index.html').write_text('<!doctype html><meta charset="utf-8"><h1>Bi DP029 full validation</h1><p>Complete 200-raw-bar windows with 20-bar overlap. Raw coverage is complete in each distance mode.</p><a href="strong/index.html">Strong atlas</a><br><a href="weak/index.html">Weak atlas</a>')
    print({mode:{k:v for k,v in data.items() if k!='route'} for mode,data in result['modes'].items()})
if __name__=='__main__':main()
