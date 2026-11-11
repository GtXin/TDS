# Independent numeric review

## Scope
Executed interval arithmetic on two supplied continuous legal-pen endpoint fixtures and an independent subset-enumeration comparison for four supplied abstract certified-state DAGs. No CC code imported or run. These checks do not prove full source recognition, completeness of candidate generation, witness compatibility, endpoint-state sufficiency or production correctness.

## Source fixtures

1. **No gap:** `10→20→15→25→18→22→12`. Up-segment candidate `S(0,3)` contains Bi0–Bi2; first-three intersection `[15,20]`. Down-feature source pens Bi1/Bi3/Bi5 give `[15,20],[18,25],[12,22]`: no inclusion, strict top, first/second overlap `[18,20]`. Reverse first-three intersection is `[18,22]`. In this simple example, full first-case structure supports original boundary P3=25 when Bi5 completes at P6=12. Geometric end P3 differs from evidence end P6; Bi3–Bi5 remain outside the completed segment. Sources067:30,071:50–54,077:73–79.
2. **Gap:** `10→18→14→24→19→22→16→20→12→17→14→21`. Candidate `S(0,3)` has initial-three overlap `[14,18]`; Bi1/Bi3/Bi5 give `[14,18],[19,24],[16,22]`, strict top and gap `18<19`. Prefix ending at P6=16 lacks the second bottom, so P3 remains a candidate. The reverse structure's upward pens are Bi4/Bi6/Bi8/Bi10; the last three intervals `[16,20],[12,17],[14,21]` form a strict bottom without inclusion, giving second-case evidence for P3=24 when Bi10 completes at P11=21. The reverse candidate is `S(3,8)` from24 to12, five pens, first-three overlap `[19,22]`. No later high exceeds24. This validates the isolated source comparisons; it does not construct every compatible state or certify an entire route. Sources067:34/38,077:83–89.

## Abstract DP example

This graph is stipulated certified input for selector testing; it is **not derived from either price sequence**. States sorted by `(j,i,id)` are A=S(0,3), B=S(3,6), C=S(0,9), D=S(6,9), E=S(9,12), F=S(12,15), X=S(9,18). Roots A/C; predecessor lists B←A, D←B, E←C/D, F←E, X←C/D. All allowed joins share geometric endpoints and alternate directions by odd segment length.

| State | A | B | C | D | E | F | X |
|---|---:|---:|---:|---:|---:|---:|---:|
| Best completed count |1|2|1|3|4|5|4|

Latest endpoint18 selects `A→B→D→X`, four completed segments, over endpoint15's five-segment route. `C→X` has the same terminal endpoint but only two segments. Independent enumeration of every subset of the seven topologically ordered nodes matches every per-state count and the selected objective.

Additional graph cases add (a) later root L=S(2,21), which cannot displace earliest start0; (b) duplicate geometric interval Y with different context, testing that contexts remain separate and final tie keeps earlier X; and (c) an empty graph. All four cases PASS. Exact inputs/results and subset counts are in `numeric-check.json`.

## Recommendation for memo

Use the abstract table only for DP mechanics and label it explicitly. Keep source fixtures as separate first/second-case examples with exact member/evidence indices. Do not label either fixture as an exhaustive derived graph or use these results to claim state compatibility has been solved. A fixed-boundary first-three nonoverlap cannot be repaired by appending more immutable pens; rejecting that boundary is distinct from stopping the traversal or failing at EOF.
