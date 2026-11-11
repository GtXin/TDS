"""Independent numerical trace for memo020 002.b/c/d; stdlib only.

Runs four directed examples and their price reflections, not broad suites.
Writes only examples.json and numeric-review.md beside this file.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / "bi-algorithm-study"


def candidates(bars):
    assert all(low <= high for low, high in bars)
    signs = []
    for (low, high), (nl, nh) in zip(bars, bars[1:]):
        assert (low < nl and high < nh) or (low > nl and high > nh)
        signs.append(1 if nl > low else -1)
    fx = [(i, "top" if signs[i - 1] > 0 else "bottom")
          for i in range(1, len(bars) - 1) if signs[i - 1] != signs[i]]
    direct = []
    for i in range(1, len(bars) - 1):
        a, b, c = bars[i - 1:i + 2]
        if all(a[k] < b[k] > c[k] for k in (0, 1)):
            direct.append((i, "top"))
        elif all(a[k] > b[k] < c[k] for k in (0, 1)):
            direct.append((i, "bottom"))
    assert fx == direct
    return fx


def pair_evidence(bars, fx, a, b):
    start, ak = fx[a]
    stop, bk = fx[b]
    lows = [x[0] for x in bars[start:stop + 1]]
    highs = [x[1] for x in bars[start:stop + 1]]
    opposite = ak != bk
    result = {"start_fx": a, "end_fx": b, "centers": [start, stop],
              "kinds": [ak, bk], "center_gap": stop - start,
              "independent_bar_count": max(0, stop - start - 3),
              "minimum_low": min(lows), "maximum_high": max(highs),
              "opposite": opposite, "gap_at_least_four": stop - start >= 4}
    reasons = []
    if not opposite:
        reasons.append("same_kind")
    if stop - start < 4:
        reasons.append("center_gap_below_four")
    if opposite:
        top, bottom = (start, stop) if ak == "top" else (stop, start)
        lt, ht = bars[top]
        lb, hb = bars[bottom]
        result.update({"top_center": top, "bottom_center": bottom,
                       "top_interval": [lt, ht], "bottom_interval": [lb, hb],
                       "high_T_gt_high_B": ht > hb, "low_B_lt_low_T": lb < lt,
                       "all_high_le_high_T": max(highs) <= ht,
                       "all_low_ge_low_B": min(lows) >= lb,
                       "bars_above_top": [i for i in range(start, stop + 1) if bars[i][1] > ht],
                       "bars_below_bottom": [i for i in range(start, stop + 1) if bars[i][0] < lb]})
        for key, reason in (("high_T_gt_high_B", "high_interval_relation"),
                            ("low_B_lt_low_T", "low_interval_relation"),
                            ("all_high_le_high_T", "interior_high_exceeds_top"),
                            ("all_low_ge_low_B", "interior_low_below_bottom")):
            if not result[key]:
                reasons.append(reason)
    result["failures"] = reasons
    result["valid"] = not reasons
    return result


def traced_search(bars):
    """Recursive exploration; explicit post-choice snapshots document recovery."""
    fx = candidates(bars)
    context = hashlib.sha256(json.dumps(bars).encode()).hexdigest()
    events, routes, blocked, tail_flags = [], set(), [], {}
    stack = []
    next_checkpoint = 0

    def state(prefix, a, b, cursor):
        return {"source_sha256": context, "prefix_fx": list(prefix),
                "prefix_centers": [fx[x][0] for x in prefix],
                "locally_closed_edges_centers": [[fx[x][0], fx[y][0]] for x, y in zip(prefix, prefix[1:])],
                "A_fx": a, "B_fx": b, "A_center": fx[a][0],
                "B_center": None if b is None else fx[b][0],
                "phase": "SEEK_B" if b is None else "WAIT_REVERSE",
                "next_fx": cursor, "next_center": fx[cursor][0] if cursor < len(fx) else None}

    def event(kind, s, **extra):
        events.append({"event": kind, "state": s, **extra})

    def checkpoint(kind, prefix, a, b, cursor, decision_fx=None):
        nonlocal next_checkpoint
        next_checkpoint += 1
        item = {"checkpoint_id": next_checkpoint, "kind": kind,
                "decision_fx": decision_fx, "post_decision_state": state(prefix, a, b, cursor)}
        stack.append(item)
        return item

    def restore(expected):
        item = stack.pop()
        assert item == expected
        s = item["post_decision_state"]
        event("restore_" + item["kind"], s, checkpoint_id=item["checkpoint_id"])
        return tuple(s["prefix_fx"]), s["A_fx"], s["B_fx"], s["next_fx"]

    def pair(a, b):
        return pair_evidence(bars, fx, a, b)

    def wait(prefix, a, b, cursor):
        assert prefix[-1] == a and pair(a, b)["valid"]
        while cursor < len(fx):
            f = cursor
            cursor += 1
            s = state(prefix, a, b, cursor)
            if fx[f][1] != fx[b][1]:
                evidence = pair(b, f)
                if evidence["valid"]:
                    event("first_qualified_reverse", s, F_fx=f, pair=evidence,
                          post_state=state(prefix + (b,), b, f, cursor))
                    prefix, a, b = prefix + (b,), b, f
                else:
                    event("reject_reverse_keep_working_pair", s, F_fx=f, pair=evidence)
                continue
            k = 1 if fx[b][1] == "top" else 0
            old_price, new_price = bars[fx[b][0]][k], bars[fx[f][0]][k]
            better = new_price > old_price if k else new_price < old_price
            if better:
                evidence = pair(a, f)
                if evidence["valid"]:
                    event("mandatory_end_extension", s, F_fx=f, old_price=old_price,
                          new_price=new_price, pair=evidence,
                          post_state=state(prefix, a, f, cursor))
                    b = f
                else:
                    history = [fx[x][0] for x in prefix + (b,)]
                    blocked.append({"historical_centers": history, "failed_new_end": fx[f][0]})
                    event("blocked_extension", s, F_fx=f, old_price=old_price,
                          new_price=new_price, pair=evidence,
                          historical_centers=history, pending_checkpoint_ids=[x["checkpoint_id"] for x in stack])
                    return
            elif old_price == new_price and pair(a, f)["valid"]:
                cp = checkpoint("equal_replace", prefix, a, f, cursor, f)
                event("cache_equal_replace_keep_old_now", s, F_fx=f, pair=pair(a, f), checkpoint=cp)
                wait(prefix, a, b, cursor)
                wait(*restore(cp))
                return
            else:
                event("retain_same_kind_evidence", s, F_fx=f,
                      equal=old_price == new_price, old_price=old_price, new_price=new_price)
        route = tuple(fx[x][0] for x in prefix + (b,))
        assert all(pair(x, y)["valid"] for x, y in zip(prefix + (b,), (prefix + (b,))[1:]))
        routes.add(route)
        tail = bars[fx[b][0] + 1:]
        breach = bool(tail) and (max(h for _, h in tail) > bars[fx[b][0]][1]
                                if fx[b][1] == "top" else min(l for l, _ in tail) < bars[fx[b][0]][0])
        tail_flags[route] = breach
        event("EOF_provisional_route", state(prefix, a, b, cursor),
              route_centers=route, tail_start=fx[b][0] + 1, tail_stop=len(bars),
              tail_exceeds_working_endpoint=breach)

    def seek(prefix, a, cursor):
        while cursor < len(fx):
            f = cursor
            cursor += 1
            evidence = pair(a, f)
            if not evidence["valid"]:
                event("reject_initial_end", state(prefix, a, None, cursor), F_fx=f, pair=evidence)
                continue
            cp = checkpoint("initial_end_skip", prefix, a, None, cursor, f)
            event("accept_initial_end_cache_skip", state(prefix, a, f, cursor), F_fx=f,
                  pair=evidence, checkpoint=cp)
            wait(prefix, a, f, cursor)
            prefix, a, absent_b, cursor = restore(cp)
            assert absent_b is None
        event("EOF_singleton_not_stroke", state(prefix, a, None, cursor))

    seeds = [checkpoint("seed", (i,), i, None, i + 1) for i in reversed(range(len(fx)))]
    for seed in reversed(seeds):
        prefix, a, b, cursor = restore(seed)
        assert b is None
        seek(prefix, a, cursor)
    assert not stack
    return {"fractals": fx, "routes": sorted(routes), "blocked": blocked,
            "tail_breaches": [{"route": p, "breach": tail_flags[p]} for p in sorted(routes)],
            "events": events,
            "all_pair_evidence": [pair(a, b) for a in range(len(fx)) for b in range(a + 1, len(fx))]}


def main():
    cached_data = json.loads((STUDY / "cached-search.json").read_text())
    cached_model = runpy.run_path(str(STUDY / "cached-search.py"))
    selected = ("blocked_then_cached_earlier_choice", "mandatory_extension",
                "equal_end_alternative_needed", "tail_without_new_complete_top")
    examples = {}
    for name in selected:
        bars = tuple(map(tuple, cached_data["examples"][name]["bars_low_high"]))
        result = traced_search(bars)
        iterative = cached_model["run"](bars)
        assert [list(x) for x in result["routes"]] == cached_data["examples"][name]["routes"]
        assert set(result["routes"]) == iterative["routes"]
        assert result["blocked"] == iterative["blocked"]
        assert {tuple(x["route"]): x["breach"] for x in result["tail_breaches"]} == iterative["tail_breaches"]
        mirror = tuple((-h, -l) for l, h in bars)
        mirrored = traced_search(mirror)
        assert result["routes"] == mirrored["routes"]
        assert result["blocked"] == mirrored["blocked"]
        assert result["tail_breaches"] == mirrored["tail_breaches"]
        assert [x["event"] for x in result["events"]] == [x["event"] for x in mirrored["events"]]
        examples[name] = {"bars_low_high": bars, **result, "reflection_checks_passed": True}
    main_case = examples[selected[0]]
    assert main_case["fractals"] == [(1,"top"),(5,"bottom"),(9,"top"),(11,"bottom"),(15,"top"),(19,"bottom")]
    first_restore = next(e for e in main_case["events"] if e["event"] == "restore_initial_end_skip")
    assert first_restore["state"]["prefix_fx"] == [0]
    assert first_restore["state"]["A_fx"] == 0 and first_restore["state"]["B_fx"] is None
    assert first_restore["state"]["next_fx"] == 2 and first_restore["state"]["next_center"] == 9
    assert len(main_case["routes"]) == 4
    result = {"scope": "four directed examples and four reflected examples; no invented OHLC or production/CC run",
              "source_cached_search_sha256": hashlib.sha256((STUDY / "cached-search.json").read_bytes()).hexdigest(),
              "fx_position_contract": "zero-based position in complete source FenxingSeries; merged center = source_start+1, not raw anchor",
              "main_case": selected[0], "examples": examples, "all_checks": "passed"}
    (HERE / "examples.json").write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "numeric-review.md").write_text(REPORT + "\n")
    print(json.dumps({"all_checks": "passed", "main_routes": main_case["routes"],
                      "directed_cases": len(examples), "reflected_cases": len(examples)}))


REPORT = """# Memo020 numerical review for 002.b/c/d

## Scope
Computer Scientist numerical review of four finite synthetic interval examples,
plus their price reflections. No raw OHLC was invented. Bars are [low,high]
intervals on the processed sequence. No production detector or CC execution.
The recursive evidence runner independently implements the cached temporal
protocol and compares routes, blocked histories and tail flags with cached-search.
Full traces and every chronological candidate pair are in examples.json.

## Main21-bar example
Low values, high=low+1:
8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1.
Strict complete fractals at merged centers1,5,9,11,15,19 have sourceFX positions
0,1,2,3,4,5 respectively, with kinds top,bottom,top,bottom,top,bottom.

Start A=FX0(center1). Accept B=FX1(center5): gap4, min0,max10,
top[9,10],bottom[0,1], both interval inequalities pass.
Cache the ALREADY POST-skip alternative:
prefixFX=[0],A_fx=0,B=None,phase=SEEK_B,next_fx=2(center9).

Read FX2(center9): B5->C9 passes gap4,min0,max8,top[7,8],bottom[0,1].
The local history is now1->5; the still-provisional working pair is5->9.
Read FX3(center11):9->11 has gap2<4; extrema and interval comparisons pass,
but this local bottom cannot form the reverse stroke. Retain it as evidence.
Read FX4(center15): it is a higher top than working B=center9 (high9>8).
Mandatory extension tests5->15: gap10,min-1,max9,top[8,9],bottom[0,1].
Both interval inequalities pass; only the lower extreme bound fails because
bar11.low=-1<bottom5.low0. Block this route, retaining historical1->5->9.
Its state is prefixFX=[0,1],A_fx=1,B_fx=2,next_fx=5(center19).

Restore the saved POST-skip5 checkpoint, NOT the blocked state's cursor:
prefixFX=[0],A_fx=0,B=None,next_fx=2(center9). At center9 the candidate
has the same top kind as A1, so skip it. Center11 is a legal first end:
gap10,min-1,max10,top[9,10],bottom[-1,0]. Cache its skip alternative.
Center15 then passes11->15: gap4,min-1,max9; center19 passes15->19:
gap4,min-2,max9. At EOF local history is1->11->15, with working15->19
still provisional. Recovered route:1->11->15->19.

Exhausting all cached choices and seeds gives exactly FOUR distinct routes:
(1,11,15,19),(1,19),(11,15,19),(15,19).
Only the first two share boundaries1..19. Histories(1,5,9) and(5,9)
are blocked diagnostics, not viable EOF routes. Selected center intervals
cover each route's own boundary span; raw-bar/support-window coverage and
market confirmation are not inferred from that fact.

## Safe extension supplement
15 interval lows, high=low+2:
1,0,3,6,9,12,10,8,12,16,13,10,7,4,5.
Exact fractals: bottom1,top5,bottom7,top9,bottom13.
1->5 passes. Reverse5->7 fails gap2. Top9 exceeds top5 and1->9 passes,
so B must update5->9 while A remains1. Reverse9->13 passes gap4.
Output routes are(1,9,13),(9,13);(1,5) is not a viable final alternative
after mandatory extension. The EOF working9->13 remains provisional.

## Equal and tail supplements
The equal-bottom example has equal bottoms at5,11. Both legal keep/replace
states are retained, yielding(1,5),(1,11,15),(7,11,15),(11,15).
The first route has unresolved later movement; it is not a completed
whole-input partition. No universal first/last tie preference is adopted.

The tail example has lows1,0,3,6,9,12,10,11,13,14, width2. Complete
fractals are bottom1,top5,bottom6. Reverse5->6 fails gap1, and no later
complete top exists. Route(1,5) remains provisional even though later
bars have highs above center5.high14 (final bar high16). This is explicit
unresolved-tail evidence, not confirmation or a fabricated final top.

## Checks and source-index semantics
All adjacent intervals have strict joint movement and no inclusion. Strict
four-inequality fractals agree with direction-turn scanning. Each returned
route's pair checks pass, and price reflection gives identical endpoint
routes, event sequence, blocked histories and tail flags. SourceFX positions
are not feature IDs or raw anchors. For existing Fenxing records, a three-
merged-bar window[source_start,source_stop) has center=source_start+1;
the complete FenxingSeries source is retained even when a subset supplies
stroke endpoints. Cache checkpoints store full post-choice state and the
next unread sourceFX position; a replay may move backward in source time,
but does not reopen the same choice at the same input item.

Reproduce: python3 artifacts/mas/memo020-002b-d/examples.py
The runner writes only examples.json and numeric-review.md beside itself.
No unrelated broad suite was rerun. Parent owns memo/task/memory/event logs.
"""


if __name__ == "__main__":
    main()
