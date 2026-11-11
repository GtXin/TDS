"""Isolated finite-input replay of the documented rule choices, not production Bi."""
from copy import deepcopy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = [9, 10, 0, 9, 1, 12, 11, 8, 5, 2, 4, 7, 3, 0, 2, 4, 6, 8, 7]
OPEN = [8, 9, 6, 4, 2, 0, 2, 4, 6, 7, 3, -1, 1, 3, 5, 8, 5, 2, 0, -2, -1]


def bars(lows):
    return [(low, low + 1) for low in lows]


def fractals(values):
    for a, b in zip(values, values[1:]):
        assert (a[0] < b[0] and a[1] < b[1]) or (a[0] > b[0] and a[1] > b[1])
    result = []
    for i in range(1, len(values) - 1):
        if all(values[i][j] > values[i - 1][j] and values[i][j] > values[i + 1][j] for j in (0, 1)):
            result.append((i, "top"))
        elif all(values[i][j] < values[i - 1][j] and values[i][j] < values[i + 1][j] for j in (0, 1)):
            result.append((i, "bottom"))
    return result


def qualified(values, kinds, a, b):
    if a >= b or kinds[a] == kinds[b] or b - a < 4:
        return False
    top, bottom = (a, b) if kinds[a] == "top" else (b, a)
    return (
        values[top][1] > values[bottom][1]
        and values[bottom][0] < values[top][0]
        and max(high for _, high in values[a : b + 1]) <= values[top][1]
        and min(low for low, _ in values[a : b + 1]) >= values[bottom][0]
    )


def check_state(values, kinds, state):
    pairs = state["R"] + ([state["pending"]] if state["pending"] else [])
    assert all(qualified(values, kinds, *pair) for pair in pairs)
    for first, second in zip(pairs, pairs[1:]):
        assert first[1] == second[0]
        assert kinds[first[0]] != kinds[second[0]]
    if state["pending"]:
        assert state["S"] == state["pending"][1]
    else:
        assert not state["R"]


def scan(values, previous=None):
    fx = fractals(values)
    state = deepcopy(previous) if previous is not None else {
        "R": [], "pending": None, "S": None, "cursor": 0,
        "input_bars": [], "input_fx": [], "events": [],
    }
    # A raw-bar append is not sufficient; the already-read merged/FX prefix must match.
    assert values[: len(state["input_bars"])] == state["input_bars"], "merged prefix changed"
    assert fx[: state["cursor"]] == state["input_fx"][: state["cursor"]], "fractal prefix changed"
    kinds = dict(fx)
    saved_prefix = tuple(state["R"])
    while state["cursor"] < len(fx):
        f, kind = fx[state["cursor"]]
        state["cursor"] += 1
        old_result = tuple(state["R"])
        pair, ok = None, None
        if state["S"] is None:
            assert not state["R"] and state["pending"] is None
            state["S"] = f
            action = "initialize_start"
        elif state["pending"] is None:
            s = state["S"]
            if kind == kinds[s]:
                better = values[f][1] > values[s][1] if kind == "top" else values[f][0] < values[s][0]
                if better:
                    state["S"] = f
                action = "replace_start" if better else "keep_start"
            else:
                pair = (s, f)
                ok = qualified(values, kinds, *pair)
                if ok:
                    state["pending"] = pair
                    state["S"] = f
                action = "accept_first" if ok else "continue_initial_failure"
        else:
            a, b = state["pending"]
            pair = (a, f) if kind == kinds[b] else (b, f)
            ok = qualified(values, kinds, *pair)
            if kind == kinds[b]:
                if ok:
                    state["pending"] = pair
                    state["S"] = f
                action = "update_pending" if ok else "continue_extension_failure"
            else:
                if ok:
                    state["R"].append(state["pending"])
                    state["pending"] = pair
                    state["S"] = f
                action = "submit_and_rotate" if ok else "continue_reverse_failure"
        assert tuple(state["R"][: len(old_result)]) == old_result
        check_state(values, kinds, state)
        state["events"].append({
            "center": f, "action": action, "checked_pair": pair, "qualified": ok,
            "R": deepcopy(state["R"]), "pending": state["pending"], "S": state["S"],
        })
    assert state["cursor"] == len(fx)
    assert tuple(state["R"][: len(saved_prefix)]) == saved_prefix
    state["input_bars"] = values
    state["input_fx"] = fx
    check_state(values, kinds, state)
    return state


cases = {
    "main19": bars(MAIN),
    "open21": bars(OPEN),
    "equal_pending11": bars([1, 0, 3, 6, 9, 10, 8, 5, 8, 10, 9]),
    "equal_initial5": bars([9, 10, 0, 10, 9]),
    "no_fractal2": bars([9, 10]),
    "single_fractal3": bars([9, 10, 0]),
    "reflected_main19": [(-high, -low) for low, high in bars(MAIN)],
    "reflected_open21": [(-high, -low) for low, high in bars(OPEN)],
}
results = {name: scan(values) for name, values in cases.items()}
assert results["main19"]["R"] == [(5, 13)] and results["main19"]["pending"] == (13, 17)
assert results["open21"]["R"] == [(1, 5)] and results["open21"]["pending"] == (5, 9)
assert [event["center"] for event in results["open21"]["events"]] == [1, 5, 9, 11, 15, 19]
assert results["open21"]["events"][-2]["action"] == "continue_extension_failure"
assert results["open21"]["events"][-1]["action"] == "continue_reverse_failure"
assert results["equal_pending11"]["pending"] == (1, 9)
assert results["equal_initial5"]["S"] == 1 and results["equal_initial5"]["pending"] is None
assert results["no_fractal2"]["S"] is None
assert results["single_fractal3"]["S"] == 1
for original, reflected in (("main19", "reflected_main19"), ("open21", "reflected_open21")):
    for field in ("R", "pending", "S", "cursor"):
        assert results[original][field] == results[reflected][field]

continuations = {}
for name, count in (("split_after_first_pair", 11), ("resume_no_fractal", 2), ("resume_single_fractal", 3)):
    first = scan(bars(MAIN[:count]))
    continued = scan(bars(MAIN), first)
    for field in ("R", "pending", "S", "cursor"):
        assert continued[field] == results["main19"][field]
    continuations[name] = {"first_batch": first, "continued": continued}
extended = scan(bars(OPEN + [2, 6, 11, 7, 3, -1, -4, -2]), results["open21"])
assert extended["R"] == [(1, 5)] and extended["pending"] == (5, 9) and extended["cursor"] == 8
continuations["open21_to29"] = {"first_batch": results["open21"], "continued": extended}
modified = list(bars(MAIN))
modified[0] = (90, 91)
try:
    scan(modified, results["main19"])
except AssertionError as error:
    assert str(error) == "merged prefix changed"
else:
    raise AssertionError("Changed historical prefix must not silently reuse state")

report = {
    "scope": "Isolated note-based interval/fractal/state replay; no production Bi/API, raw-market pipeline, all-route search or guarantee of future completion.",
    "fresh_cases": results,
    "continuation_cases": continuations,
    "changed_prefix_rejected": True,
    "all_complete_fractals_read": True,
    "final_prefix_never_modified": True,
    "eof_does_not_submit_pending": True,
    "counts": {"fresh_cases": len(results), "continuation_cases": len(continuations), "successful_scan_calls": len(results) + 2 * 3 + 1, "total_scan_calls": len(results) + 2 * 3 + 2, "changed_prefix_probe": 1},
}
(HERE / "replay.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "fresh_cases": len(results), "continuations": len(continuations),
    "main19": {"R": results["main19"]["R"], "pending": results["main19"]["pending"]},
    "open21": {"R": results["open21"]["R"], "pending": results["open21"]["pending"], "read_centers": [event["center"] for event in results["open21"]["events"]]},
    "changed_prefix_rejected": True,
}, ensure_ascii=False))
