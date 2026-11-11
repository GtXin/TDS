"""Reproduce arithmetic and graph-only selection checks; no xianduan recognizer."""
from itertools import combinations
from pathlib import Path
import json

BASE = Path(__file__).parent
DATA = json.loads((BASE / 'numeric-check.json').read_text())


def graph_check(nodes):
    ids = {key: i for i, key in enumerate(nodes)}
    order = sorted(nodes, key=lambda key: (nodes[key]['j'], nodes[key]['i'], ids[key]))
    roots = [nodes[key]['i'] for key in order if nodes[key]['root']]
    start = min(roots, default=None)
    best = dict.fromkeys(order, -1)
    previous = dict.fromkeys(order, None)
    for key in order:
        node = nodes[key]
        assert node['j'] - node['i'] >= 3 and (node['j'] - node['i']) % 2 == 1
        if node['root'] and node['i'] == start:
            best[key] = 1
        for pred in sorted(node['pred'], key=order.index):
            assert nodes[pred]['j'] == node['i'] < node['j']
            if best[pred] >= 1 and best[pred] + 1 > best[key]:
                best[key] = best[pred] + 1
                previous[key] = pred
    selected = None
    for key in order:
        if best[key] >= 1 and (selected is None or (nodes[key]['j'], best[key]) > (nodes[selected]['j'], best[selected])):
            selected = key
    route = []
    cursor = selected
    while cursor is not None:
        route.append(cursor)
        cursor = previous[cursor]
    route.reverse()
    reference = dict.fromkeys(order, -1)
    valid = []
    subsets = 0
    for size in range(len(order) + 1):
        for path in combinations(order, size):
            subsets += 1
            if not path or not nodes[path[0]]['root'] or nodes[path[0]]['i'] != start:
                continue
            if any(left not in nodes[right]['pred'] for left, right in zip(path, path[1:])):
                continue
            reference[path[-1]] = max(reference[path[-1]], len(path))
            valid.append(path)
    assert best == reference
    if selected is None:
        assert not valid
    else:
        objective = max((nodes[path[-1]]['j'], len(path)) for path in valid)
        assert (nodes[selected]['j'], len(route)) == objective
    return {'a': start, 'end': None if selected is None else nodes[selected]['j'], 'count': len(route), 'route': route, 'best': best, 'prev': previous, 'subsets': subsets}


def intervals(prices):
    return [(min(a, b), max(a, b)) for a, b in zip(prices, prices[1:])]


for fixture in DATA['source_fixtures'].values():
    prices = fixture['prices']
    assert all((b > a) == (i % 2 == 0) for i, (a, b) in enumerate(zip(prices, prices[1:])))
    pens = intervals(prices)
    assert max(low for low, _ in pens[:3]) < min(high for _, high in pens[:3])
    feature = [pens[i] for i in fixture['F1']['pen_indices']]
    (low0, high0), (low1, high1), (low2, high2) = feature
    assert high0 < high1 > high2 and low0 < low1 > low2
    assert (high0 < low1) == fixture['F1']['gap']
    assert prices[fixture['geometry_endpoint']['P']] == fixture['geometry_endpoint']['price']
    if 'F2' in fixture:
        (low0, high0), (low1, high1), (low2, high2) = [pens[i] for i in fixture['F2']['last3_pen_indices']]
        assert low0 > low1 < low2 and high0 > high1 < high2
    assert fixture['evidence']['last_pen'] + 1 == fixture['evidence']['last_P']

results = {}
for name, case in DATA['abstract_graphs'].items():
    actual = graph_check(case['nodes'])
    for key in ('a', 'end', 'count', 'route', 'best', 'prev'):
        assert actual[key] == case['dp'][key], (name, key)
    results[name] = actual
output = {'source_arithmetic_passed': 2, 'graphs': results, 'subsets_total': sum(case['subsets'] for case in results.values()), 'scope': 'Graph-only DP and isolated source arithmetic; no candidate generator, compatibility proof or production execution.'}
(BASE / 'root-recheck.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'PASS': True, 'source_cases': 2, 'graphs': len(results), 'subsets': output['subsets_total']}))
