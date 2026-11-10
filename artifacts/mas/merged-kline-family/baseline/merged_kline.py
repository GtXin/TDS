"""Immutable inclusion results and explicit initialization outcomes (memo015)."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from math import isfinite
from collections.abc import Iterator
from typing import Literal, overload, TYPE_CHECKING

from chanlab.algo.kline import KlineTSeries

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

Direction = Literal['up', 'down'] | None
Policy = Literal['UP', 'DOWN', 'BOTH', 'OUTER', 'UNSET']


def _integer(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f'{name}: expected nonnegative integer')


@dataclass(frozen=True, slots=True)
class MergeConfig:
    initialization: Policy

    def __post_init__(self) -> None:
        if self.initialization not in ('UP', 'DOWN', 'BOTH', 'OUTER', 'UNSET'):
            raise ValueError('initialization: unsupported policy')


@dataclass(frozen=True, slots=True)
class MergedKline:
    id: int
    low: float
    high: float
    direction: Direction
    source_start: int
    source_stop: int
    status: str = 'unconfirmed'
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        for name in ('id', 'source_start', 'source_stop'):
            _integer(getattr(self, name), name)
        for value in (self.low, self.high):
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise ValueError('bounds: expected finite numbers')
            try:
                if not isfinite(value):
                    raise ValueError('bounds: expected finite numbers')
            except OverflowError as exc:
                raise ValueError('bounds: outside float range') from exc
        if self.low > self.high or self.source_start >= self.source_stop:
            raise ValueError('bounds/source range: invalid order')
        if self.direction not in ('up', 'down', None):
            raise ValueError('direction: invalid')
        if self.status != 'unconfirmed' or self.confirmed_at is not None:
            raise ValueError('confirmation rule is undefined; require unconfirmed/None')


@dataclass(frozen=True, slots=True)
class Work:
    raw: KlineTSeries
    low: float
    high: float
    direction: Direction
    source_start: int
    source_stop: int

    def __post_init__(self) -> None:
        MergedKline(0, self.low, self.high, self.direction,
                    self.source_start, self.source_stop)
        if self.source_stop > len(self.raw):
            raise ValueError('work source range: out of bounds')


def work_from_raw(raw: KlineTSeries, i: int, direction: Direction = None) -> Work:
    _integer(i, 'raw index')
    if i >= len(raw):
        raise ValueError('raw index: out of bounds')
    return Work(raw, raw[i].low, raw[i].high, direction, i, i + 1)


def has_inclusion(a: Work | MergedKline, b: Work | MergedKline) -> bool:
    return ((a.high >= b.high and a.low <= b.low)
            or (b.high >= a.high and b.low <= a.low))


def direction_between(a: Work | MergedKline, b: Work | MergedKline) -> Direction:
    if has_inclusion(a, b):
        raise ValueError('direction requires noninclusion')
    return 'up' if b.high > a.high else 'down'


def _check_pair(current: Work, candidate: Work) -> None:
    if (current.raw is not candidate.raw
            or current.source_stop != candidate.source_start
            or candidate.source_stop != candidate.source_start + 1
            or not has_inclusion(current, candidate)):
        raise ValueError('merge requires same source, contiguous single candidate and inclusion')


def merge_included(current: Work, candidate: Work) -> Work:
    _check_pair(current, candidate)
    if current.direction is None:
        raise ValueError('merge requires known direction')
    operation = max if current.direction == 'up' else min
    return replace(current, low=operation(current.low, candidate.low),
                   high=operation(current.high, candidate.high),
                   source_stop=candidate.source_stop)


def merge_outer_boundary(current: Work, candidate: Work) -> Work:
    """Caller selects OUTER; reject an already directed current unit."""
    _check_pair(current, candidate)
    if current.direction is not None:
        raise ValueError('outer boundary requires unresolved direction')
    return replace(current, low=min(current.low, candidate.low),
                   high=max(current.high, candidate.high), source_stop=candidate.source_stop)


@dataclass(frozen=True, slots=True)
class MergeDecision:
    rule: str
    raw_index: int
    before: Work
    candidate: Work | None
    after: Work


@dataclass(frozen=True, slots=True)
class PendingMerge:
    source_series: KlineTSeries
    config: MergeConfig
    rule_tree_ref: str
    saved: tuple[MergedKline, ...]
    current: Work
    candidate: Work
    raw_index: int
    trace: tuple[MergeDecision, ...]


@dataclass(frozen=True, slots=True)
class DualMerge:
    main: MergedKlineSeries
    comparison: MergedKlineSeries
    requested_config: MergeConfig
    warning_evaluation: str = 'not_evaluated'


@dataclass(frozen=True, slots=True)
class MergedKlineSeries:
    source_series: KlineTSeries
    klines: tuple[MergedKline, ...]
    config: MergeConfig
    rule_tree_ref: str
    trace: tuple[MergeDecision, ...]
    trace_by_point: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'klines', tuple(self.klines))
        object.__setattr__(self, 'trace', tuple(self.trace))
        object.__setattr__(self, 'trace_by_point', tuple(tuple(x) for x in self.trace_by_point))
        self.validate()

    def validate(self) -> None:
        self.source_series.validate()
        if not isinstance(self.config, MergeConfig):
            raise ValueError('config: expected MergeConfig')
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError('rule_tree_ref: required')
        validate_merged_result(self.source_series, self)
        if len(self.trace_by_point) != len(self):
            raise ValueError('trace mapping length mismatch')
        for indices in self.trace_by_point:
            if not indices:
                raise ValueError('trace mapping must explain each record')
            for i in indices:
                _integer(i, 'trace index')
                if i >= len(self.trace):
                    raise ValueError('trace index: out of bounds')
        for step in self.trace:
            if not isinstance(step, MergeDecision):
                raise ValueError('trace: expected MergeDecision')
            if step.before.raw is not self.source_series or step.after.raw is not self.source_series:
                raise ValueError('trace source mismatch')
            if step.candidate is not None and step.candidate.raw is not self.source_series:
                raise ValueError('trace candidate source mismatch')

    def __len__(self) -> int:
        return len(self.klines)

    def __iter__(self) -> Iterator[MergedKline]:
        return iter(self.klines)

    @overload
    def __getitem__(self, key: int) -> MergedKline: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[MergedKline, ...]: ...
    def __getitem__(self, key: int | slice) -> MergedKline | tuple[MergedKline, ...]:
        return self.klines[key]

    def get_by_id(self, feature_id: int) -> MergedKline:
        _integer(feature_id, 'feature_id')
        for bar in self:
            if bar.id == feature_id:
                return bar
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> str:
        bar = self[point_index]
        steps = (self.trace[i] for i in self.trace_by_point[point_index])
        detail = '; '.join(f'{s.rule} at raw[{s.raw_index}]: '
                           f'[{s.before.low},{s.before.high}] -> [{s.after.low},{s.after.high}]'
                           for s in steps)
        return (f'MK{bar.id} raw[{bar.source_start}:{bar.source_stop}] '
                f'{bar.direction}, {bar.status}; rules={self.rule_tree_ref}; {detail}')

    def plot(self, *, start: int | None = None, stop: int | None = None,
             volume: bool = True, title: str | None = None) -> Figure:
        from chanlab.visualization.merged_kline_plot import plot_merged_kline_series
        return plot_merged_kline_series(self, start=start, stop=stop, volume=volume, title=title)

    @classmethod
    def derive_from(cls, source_series: KlineTSeries, config: MergeConfig,
                    rule_tree_ref: str) -> MergedKlineSeries | PendingMerge | DualMerge:
        source_series.validate()
        if not isinstance(config, MergeConfig):
            raise ValueError('config: expected MergeConfig')
        if not isinstance(rule_tree_ref, str) or not rule_tree_ref.strip():
            raise ValueError('rule_tree_ref: required')
        return _advance(source_series, config, rule_tree_ref,
                        work_from_raw(source_series, 0), 1, (), (), ())


def validate_merged_result(raw: KlineTSeries, result: MergedKlineSeries) -> None:
    if result.source_series is not raw or not result.klines:
        raise ValueError('result must be nonempty and retain exact raw source')
    end = 0
    ids: set[int] = set()
    previous: MergedKline | None = None
    for j, bar in enumerate(result.klines):
        bar.validate()
        if bar.id in ids or bar.source_start != end or bar.source_stop > len(raw):
            raise ValueError(f'result[{j}]: duplicate ID or invalid source coverage')
        if previous is not None and has_inclusion(previous, bar):
            raise ValueError(f'adjacent inclusion at {j-1},{j}: '
                             f'[{previous.source_start},{previous.source_stop}), '
                             f'[{bar.source_start},{bar.source_stop})')
        ids.add(bar.id)
        end = bar.source_stop
        previous = bar
    if end != len(raw):
        raise ValueError('source coverage incomplete')


def _advance(raw: KlineTSeries, config: MergeConfig, ref: str, current: Work,
             i: int, saved: tuple[MergedKline, ...],
             trace: tuple[MergeDecision, ...],
             mappings: tuple[tuple[int, ...], ...],
             active: tuple[int, ...] = ()) -> MergedKlineSeries | PendingMerge | DualMerge:
    # Lists are private to each invocation; immutable prefixes can be shared.
    records = list(saved)
    events = list(trace)
    links = list(mappings)
    relevant = list(active)

    def record(rule: str, before: Work, candidate: Work | None, after: Work) -> None:
        relevant.append(len(events))
        events.append(MergeDecision(rule, i, before, candidate, after))

    def save() -> None:
        records.append(MergedKline(len(records) + 1, current.low, current.high,
                                   current.direction, current.source_start, current.source_stop))
        links.append(tuple(relevant))

    if not events:
        record('2.1.b', current, None, current)
    while i < len(raw):
        candidate = work_from_raw(raw, i)
        before = current
        if not has_inclusion(current, candidate):
            candidate = replace(candidate, direction=direction_between(current, candidate))
            rule = '2.4.a' if candidate.direction == 'up' else '2.4.b'
            record(rule, current, candidate, current)
            save()
            # The transition is relevant to both the closed and new record.
            relevant = [len(events)-1]
            current = candidate
            i += 1
            continue
        if current.direction is None:
            policy = config.initialization
            if policy == 'UNSET':
                record('2.6.UNSET', before, candidate, current)
                return PendingMerge(raw, config, ref, tuple(records), current,
                                    candidate, i, tuple(events))
            if policy == 'BOTH':
                record('2.6.c', before, candidate, current)
                paths = []
                for selected, direction in (('UP', 'up'), ('DOWN', 'down')):
                    path = _advance(raw, MergeConfig(selected), ref,
                                    replace(current, direction=direction), i,
                                    tuple(records), tuple(events), tuple(links), tuple(relevant))
                    assert isinstance(path, MergedKlineSeries)
                    paths.append(path)
                return DualMerge(paths[0], paths[1], config)
            if policy == 'OUTER':
                current = merge_outer_boundary(current, candidate)
                record('2.6.d', before, candidate, current)
                i += 1
                continue
            current = replace(current, direction='up' if policy == 'UP' else 'down')
            record('2.6.a' if policy == 'UP' else '2.6.b', before, candidate, current)
        before = current
        current = merge_included(current, candidate)
        record('2.5.a' if current.direction == 'up' else '2.5.b', before, candidate, current)
        i += 1
    record('2.2.a.EOF', current, None, current)
    save()
    return MergedKlineSeries(raw, tuple(records), config, ref, tuple(events), tuple(links))
