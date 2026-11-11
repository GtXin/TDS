# Start-reselection discussion: actual P->C->D pair review

## Scope

Ran ONE read-only upstream pipeline from the saved sample CSV/context through
MergedKlineSeries(initialization UP,rule memo015) and FenxingSeries({},memo019).
Counts:10060 raw,6200 merged,3027 complete fractals. Did NOT call Bi.scan,
full.py,verify.py,write output tables or run broad tests. Bytecode writing was
disabled. Only this authorized review file was created; no rules are adopted.

Input: samples/chan_table/dce-KQ.m-at-m_15m_20241028_20260819_chan_table_v20261108.csv
and its matching context_v20261108.csv.

## Actual points

These FX numbers are source FenxingSeries positions, not merged centers.

| Label | FX position | Kind | Merged center | Center[low,high] | Endpoint price | Raw anchor |
|---|---:|---|---:|---|---:|---:|
| P | 145 | bottom | 293 | [2778,2788] | 2778 | 466 |
| A | 148 | top | 301 | [2810,2818] | 2818 | 481 |
| B | 149 | bottom | 305 | [2802,2808] | 2802 | 487 |
| C | 150 | top | 306 | [2815,2824] | 2824 | 488 |
| D | 151 | bottom | 310 | [2794,2806] | 2794 | 496 |

## Independently checked complete pairs

| Pair | Center gap | Inclusive range minimum/maximum | Strict center-interval relations | Extrema |
|---|---:|---|---|---|
| P145->C150 | 306-293=13 | 2778 / 2824 | 2824>2788;2778<2815 | both pass |
| C150->D151 | 310-306=4 | 2794 / 2824 | 2824>2806;2794<2815 | both pass |

Both pairs have chronological opposite-kind endpoints, gap>=4 and no interior
bar outside their endpoint bounds. Independent complete-range scans found
ZERO upper/lower violating bars in either pair. Thus tentative geometric chain

    P145 -> C150 -> D151
    merged293 ->306 ->310
    bottom2778 ->top2824 ->bottom2794

satisfies all six conditions, with shared C and alternating up/down directions.
Earlier A and B lie inside P->C's center range and do not violate its bounds.
Calling this an A->C operation means REPLACING the top endpoint A with C;
A and C are both tops and do not themselves form a stroke.

## Why resetting only the working start breaks continuity

The prior actual scan audit established that, upon reading B149, the algorithm
committed its previous stroke P145->A148 as the24th record of R and installed
working cache A148->B149. R therefore ends at sourceFX148.

If the working stroke alone is reset to C150->D151, its start becomes150 while
R's final end stays148. They no longer share an endpoint. Appending a fictitious
A148->C150 bridge cannot repair that mismatch because A and C are both tops.

For THIS numerical tentative repair, continuity would require replacing the
last committed P145->A148 with P145->C150 AND replacing the old cache with
C150->D151. Both new pairs have now been numerically verified. R before its
last stroke can still connect at the unchanged P145, but changing the last
record conflicts with current020's explicit append-only committed-R boundary.

This establishes local geometric feasibility, not authorization to edit R or
a generally correct recovery algorithm. It does not prove that one-stroke
revision always suffices, that this chain is unique, that later progress is
guaranteed, or that current confirmation/selection semantics permit it.
