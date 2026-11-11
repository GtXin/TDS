# Full-data rolling cache: focused numerical audit

Executed exactly one read-only sample pipeline and one BiSeries.scan:
KlineTSeries.read_csv -> merged initialization UP/rule memo015 ->
FenxingSeries config{}/rule memo019 -> Bi.scan rule memo020:rolling.
Did NOT execute full.py or verify.py top-level, any broad suite, table writer
or picture writer. Imports disabled bytecode output. No source, memo, log,
memory, dataset or prior artifact was changed; only this review was written.

Input: samples/chan_table/dce-KQ.m-at-m_15m_20241028_20260819_chan_table_v20261108.csv
and its context_v20261108.csv. Result matches
artifacts/mas/bi-family/rolling020/full-result.json:
10060 raw,6200 merged,3027 FX,24 committed R,cache(148,149),
pending_start149,next_position3027,status open_cache,
unresolved((0,1),(306,6200)); tail length5894 merged bars.

## Exact source facts

FX numbers are source FenxingSeries POSITIONS, not merged centers/raw anchors.

| FX | Kind | Merged center | Center[low,high] | Price | Merged window | Raw anchor |
|---:|---|---:|---|---:|---|---:|
| 148 | top | 301 | [2810,2818] | 2818 | [300,303) | 481 |
| 149 | bottom | 305 | [2802,2808] | 2802 | [304,307) | 487 |
| 150 | top | 306 | [2815,2824] | 2824 | [305,308) | 488 |
| 151 | bottom | 310 | [2794,2806] | 2794 | [309,312) | 496 |

## Independent targeted complete-pair checks

- Existing148->149: gap4,range min2802/max2818; endpoint extrema pass.
  Relative intervals2818>2808 and2802<2810 pass. Cache remains legal.
- Reverse149->150: centers305->306,gap1<4. Range min2802/max2824,
  both extrema and relative intervals2824>2808,2802<2815 pass.
  The ONLY failure is distance.
- Extension148->151: centers301->310,gap9; range min2794/max2824.
  Relative intervals2818>2806,2794<2810 pass; lower bound passes.
  The ONLY failure is merged306.high2824>fixed top148.high2818.
  The reduced extension suffix[306,311) includes the same high witness.

At FX149 the scan commits the previous145->148, increasing R23->24,
and installs148->149. FX150 rejects reverse;FX151 rejects extension.
All2877 decisions FX150..FX3026 comprise:

- 1439 reject_reverse
- 285 reject_extension
- 1153 weaker_end

ZERO later extend,commit_reverse or first_cache events occur. The trace
contains3026 candidate decisions plus a separately installed initialFX0;
the cursor reaches3027. Traversal continued; successful endpoint updates did not.

## Persistent witnesses under unchanged history

With fixed cache A=top148(high2818),B=bottom149(low2802):

1. Every future bottom extension suffix after merged305 contains
   merged306.high2824>A.high2818. A lower future bottom cannot repair
   this fixed upper bound. Weaker bottom candidates are simply not adopted.
2. Every future top reverse from B, after FX151, contains
   merged310.low2794<B.low2802. A higher future top cannot repair this
   fixed lower bound.

Thus this cache cannot ever advance through a successful extension/reversal
under the same rules and prefix-preserving future input. That is stronger
than observing one ordinary unfinished EOF tail. Existing R/cache remain
geometrically valid, and the reject/continue actions follow current020;
these facts alone do not establish a code/tree implementation violation.
They establish a progress limitation if sustained coverage/eventual completion
is required. No reset,reselection,rollback,confirmation or canonical policy
is adopted here. No further tests were needed for this focused conclusion.
