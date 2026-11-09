"""笔（Bi）— 在分型序列上派生 (算法说明卡 bi-v1 v4)。

统一参数化引擎：一套底层参数 + 成笔模式 (standard/strong/secondary)；profile 只是预设名。
口径优先链 (§1.1 / decision-0001 v1.4 §12.3：原文 > 用户确认的本项目口径 > 本项目自主实现；
参考项目 chan.py-main / czsc / chanlun-pro 无固定优先级，只作对照/启发/差异发现来源)；
分型恒在合并序列识别 (PR-3)。

成笔判定 (standard)：距离(bi_span_mode) → 端点检查(bi_endpoint_check) → 端点极值(bi_require_peak)。
- 距离 merged_center：分型中心合并下标差 (+缺口折算) ≥ bi_min_span。
- 距离 raw_extreme：①不共用 K（三元窗口无公共合并单元，内建）②极值原始 K 索引差 ≥ bi_min_span。
强势笔 (strong)：标准失败时，候选幅度 ≥ ratio × 相邻反向笔幅度（前一笔或后一笔）则成笔。
次笔 (secondary)：第一反向分型不成笔(pending)，第二同型处成笔；中间夹相反成笔则回退标准。

**纯函数**：合并/分型由引擎批量重派生 (版本缓存)，本模块无跨调用状态。strong_next「后一笔」
在单次派生内 = 向分型数组后方有界 look-ahead；回补由「dep 依赖水位线 + provisional」承载
(每笔记成笔实际查阅的最大分型下标 dep_to_index，serializer 据此判 confirmed，保证 strong_next
不在 confirmed 区插删笔)。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cc.algo.config import (
    BiEndpointCheck,
    BiFormationMode,
    BiSpanMode,
    ChanConfig,
)
from cc.algo.models import Bi, BiDir, Fenxing, FxType, MergedKline
from cc.algo.trace import (
    RULE_BI_DOWN_4K,
    RULE_BI_DOWN_5K,
    RULE_BI_DOWN_SECONDARY,
    RULE_BI_DOWN_STRONG_NEXT,
    RULE_BI_DOWN_STRONG_PREV,
    RULE_BI_UP_4K,
    RULE_BI_UP_5K,
    RULE_BI_UP_SECONDARY,
    RULE_BI_UP_STRONG_NEXT,
    RULE_BI_UP_STRONG_PREV,
    StructTrace,
)
from cc.data.models import Kline

_ALGO_CARD_ID = "bi-v1"

# rule_kind → (up rule_id, down rule_id)。standard 再按 span_mode 细分 5k/4k (见 _rule_for)。
_RULE_STRONG_PREV = (RULE_BI_UP_STRONG_PREV, RULE_BI_DOWN_STRONG_PREV)
_RULE_STRONG_NEXT = (RULE_BI_UP_STRONG_NEXT, RULE_BI_DOWN_STRONG_NEXT)
_RULE_SECONDARY = (RULE_BI_UP_SECONDARY, RULE_BI_DOWN_SECONDARY)
_RULE_STD_MERGED = (RULE_BI_UP_5K, RULE_BI_DOWN_5K)
_RULE_STD_RAW = (RULE_BI_UP_4K, RULE_BI_DOWN_4K)


def bi_dep_index(bi: Bi) -> int | None:
    """笔依赖水位（与既有 overlay confirmed 判定同一事实来源）。"""
    if bi.trace is None:
        return None
    return bi.trace.dep_to_index if bi.trace.dep_to_index is not None else bi.trace.merged_to_index


def bi_confirmed_flags(bis: Sequence[Bi], n_merged: int) -> list[bool]:
    """返回每笔是否 confirmed；逐字保持 bi-v1 §10 的既有三条末端规则。"""
    n_bis = len(bis)
    last_dep = bi_dep_index(bis[-1]) if n_bis else None
    last_unstable = last_dep is None or last_dep >= n_merged - 2
    flags: list[bool] = []
    for i, bi in enumerate(bis):
        dep = bi_dep_index(bi)
        provisional = (
            i == n_bis - 1
            or dep is None
            or dep >= n_merged - 2
            or (i == n_bis - 2 and last_unstable)
        )
        flags.append(not provisional)
    return flags


@dataclass(slots=True)
class _WorkBi:
    """构建期可变笔。rule_kind ∈ standard/strong_prev/strong_next/secondary；dep = 依赖水位。"""

    start_fx: Fenxing
    end_fx: Fenxing
    direction: BiDir
    rule_kind: str
    dep_index: int


def build_bis(
    merged: list[MergedKline],
    fenxings: list[Fenxing],
    raw_klines: list[Kline],
    cfg: ChanConfig,
    *,
    profile_id: str,
    config_hash: str,
) -> list[Bi]:
    """从分型序列派生笔序列（纯函数，按 cfg 统一参数 + 成笔模式判定）。"""
    cfg = cfg.normalize()
    builder = _BiBuilder(merged, fenxings, raw_klines, cfg)
    builder.run()
    return builder.finish(profile_id, config_hash)


class _BiBuilder:
    """单次派生的内部状态机（不跨调用持久）。"""

    def __init__(
        self,
        merged: list[MergedKline],
        fenxings: list[Fenxing],
        raw_klines: list[Kline],
        cfg: ChanConfig,
    ) -> None:
        self._merged = merged
        self._fxs = fenxings
        self._raw = raw_klines
        self._cfg = cfg
        self._bis: list[_WorkBi] = []
        self._candidates: list[Fenxing] = []  # standard/strong 首笔候选

    def run(self) -> None:
        if self._cfg.bi_formation_mode is BiFormationMode.SECONDARY:
            # 次笔 = 高一级别一笔 = 老笔的线段(特征序列法)。**暂搁置不输出**(用户 2026-06-17)：
            # 旧"破坏式合并"在长趋势上过度合并 → 已回退；待特征序列法线段草案确认后实现 (§5.8)。
            self._bis = []
        else:
            for i, fx in enumerate(self._fxs):
                self._feed_std_strong(i, fx)

    # ── standard / strong 主循环 ─────────────────────────────────────────
    def _feed_std_strong(self, i: int, fx: Fenxing) -> None:
        if not self._bis:
            self._try_first_bi(fx)
            return
        last = self._bis[-1]
        if fx.fx_type is last.end_fx.fx_type:
            self._extend_same_fx(fx)
            return
        if self._try_standard_form(last.end_fx, fx):
            self._append(last.end_fx, fx, "standard", fx.index)
            return
        # 标准失败 → 强势 (前/后一笔)
        if self._cfg.bi_formation_mode is BiFormationMode.STRONG and self._try_strong(
            i, last.end_fx, fx
        ):
            return
        if self._cfg.bi_fractal_repair:
            self._repair_sub_peak(i, fx)

    def _try_first_bi(self, fx: Fenxing) -> None:
        for cand in self._candidates:
            if cand.fx_type is fx.fx_type:
                continue
            if self._try_standard_form(cand, fx):
                self._append(cand, fx, "standard", fx.index)
                self._candidates = []
                return
        self._candidates.append(fx)

    # ── 强势笔 (前一笔 / 后一笔；前优先) ─────────────────────────────────
    def _try_strong(self, i: int, start_fx: Fenxing, end_fx: Fenxing) -> bool:
        cand_amp = _bi_amplitude(start_fx, end_fx)
        ratio = self._cfg.bi_strength_ratio
        # 前一笔 (实时，已构建的相邻反向笔)
        prev = self._bis[-1]
        prev_amp = _bi_amplitude(prev.start_fx, prev.end_fx)
        if prev_amp > 0 and cand_amp >= ratio * prev_amp:
            self._append(start_fx, end_fx, "strong_prev", end_fx.index)
            return True
        # 后一笔 (有界 look-ahead: 从 end_fx 起首个 standard 反向笔；禁递归强势)
        nxt = self._lookahead_next_std_bi(i, end_fx)
        if nxt is not None:
            next_amp, dep_fx_index = nxt
            if next_amp > 0 and cand_amp >= ratio * next_amp:
                self._append(start_fx, end_fx, "strong_next", dep_fx_index)
                return True
        return False

    def _lookahead_next_std_bi(
        self, i: int, from_fx: Fenxing
    ) -> tuple[float, int] | None:
        """从 from_fx 起，按 standard 规则形成的下一条反向笔的 (幅度, 其端点分型下标)。

        只认 standard（不递归强势，已定 2）；取首个 standard 成笔的反向分型（有界）。
        """
        for q in range(i + 1, len(self._fxs)):
            nf = self._fxs[q]
            if nf.fx_type is from_fx.fx_type:
                continue
            if self._try_standard_form(from_fx, nf):
                return _bi_amplitude(from_fx, nf), nf.index
        return None

    # 次笔(=老笔线段, 特征序列法) 暂搁置, 见 run()。实现待线段草案确认 (用户 2026-06-17)。

    # ── 同型延伸 / sub_peak 修正 (与 standard 共用) ──────────────────────
    def _extend_same_fx(self, fx: Fenxing) -> None:
        # 同型分型永远取更极值 (两顶取更高 / 两底取更低, 第 65 课)。原 first 变体 v7 删除。
        last = self._bis[-1]
        if last.direction is BiDir.UP:
            if fx.high > _top_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)
        else:
            if fx.low < _bottom_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)

    def _repair_sub_peak(self, i: int, fx: Fenxing) -> bool:
        """笔破坏修正 (bi_fractal_repair, 项目变体)：反弹笔起点被反向更极值 fx 击穿时，
        仅当**反向确认守卫**通过 (fx 为真极值、反弹是假反弹) 才吸收反弹笔、把前一笔延伸到 fx。
        守卫见 ``_confirm_reverse_break``；吸收笔 dep_index = 确认处下标 (确认前恒 provisional)。
        """
        if len(self._bis) < 2:
            return False
        last, prev = self._bis[-1], self._bis[-2]
        if last.direction is BiDir.DOWN:
            if fx.high < _top_value(last.start_fx):
                return False
            if _bottom_value(last.end_fx) < _bottom_value(prev.start_fx):
                return False
        else:
            if fx.low > _bottom_value(last.start_fx):
                return False
            if _top_value(last.end_fx) > _top_value(prev.start_fx):
                return False
        if not self._is_peak(prev.start_fx, fx, _direction_of(fx)):
            return False
        confirm_index = self._confirm_reverse_break(i, fx, last)
        if confirm_index is None:
            return False
        popped = self._bis.pop()
        before = self._bis[-1].end_fx
        self._extend_same_fx(fx)
        if self._bis[-1].end_fx is before:
            self._bis.append(popped)
            return False
        self._bis[-1].dep_index = max(self._bis[-1].dep_index, confirm_index)
        return True

    def _confirm_reverse_break(self, i: int, fx: Fenxing, last: _WorkBi) -> int | None:
        """反向确认守卫 (bi-v1 笔破坏修正小节，项目变体)。

        fx 击穿反弹笔 ``last`` 起点后，从 fx 在分型序列向后**有界扫描**：
        - 若价格在「从反弹笔顶/底 T 形成有效反向笔」**之前**先**越过 T 的极值** →
          反弹是假反弹、fx 是真极值 → 返回确认处合并下标 (供 dep 水位线，确认前恒 provisional)。
        - 若先形成「T→反向有效笔」 → 反弹是真实摆动、T 成立 → 返回 ``None`` (不吸收)。
        - 扫到末尾两者皆无 (数据不足) → ``None`` (保守不吸收，随回补再判)。
        """
        t = last.end_fx
        up = last.direction is BiDir.UP
        for q in range(i + 1, len(self._fxs)):
            g = self._fxs[q]
            if up:
                if g.fx_type is FxType.TOP and g.high > t.high:
                    return g.index
                if g.fx_type is FxType.BOTTOM and self._try_standard_form(t, g):
                    return None
            else:
                if g.fx_type is FxType.BOTTOM and g.low < t.low:
                    return g.index
                if g.fx_type is FxType.TOP and self._try_standard_form(t, g):
                    return None
        return None

    def _append(
        self, start: Fenxing, end: Fenxing, rule_kind: str, dep_index: int
    ) -> None:
        self._bis.append(_WorkBi(start, end, _direction_of(end), rule_kind, dep_index))

    # ── 标准成笔判定 (距离 → 端点检查 → 端点极值) ───────────────────────
    def _try_standard_form(self, start: Fenxing, end: Fenxing) -> bool:
        if start.fx_type is end.fx_type:
            return False
        if not self._check_distance(start, end):
            return False
        if not self._check_endpoint(start, end):
            return False
        if self._cfg.bi_require_peak and not self._is_peak(
            start, end, _direction_of(end)
        ):
            return False
        return True

    # ── 距离 (bi_span_mode 分派) ─────────────────────────────────────────
    def _check_distance(self, start: Fenxing, end: Fenxing) -> bool:
        if self._cfg.bi_span_mode is BiSpanMode.MERGED_CENTER:
            return self._check_center_span(start, end)
        return self._check_raw_extreme(start, end)

    def _check_center_span(self, start: Fenxing, end: Fenxing) -> bool:
        base_span = end.index - start.index
        if base_span >= self._cfg.bi_min_span:
            return True
        if not self._cfg.bi_gap_as_bar:
            return False
        gap_count = sum(
            1
            for i in range(start.index, end.index)
            if self._has_gap(self._merged[i], self._merged[i + 1])
        )
        return base_span + gap_count >= self._cfg.bi_min_span

    def _check_raw_extreme(self, start: Fenxing, end: Fenxing) -> bool:
        # ① 不共用 K (三元窗口无公共合并单元，内建)
        if start.index + 1 >= end.index - 1:
            return False
        # ② 极值原始 K 索引差 ≥ bi_min_span
        if end.fx_type is FxType.TOP:
            start_raw = self._extreme_raw_index(start, want_high=False)
            end_raw = self._extreme_raw_index(end, want_high=True)
        else:
            start_raw = self._extreme_raw_index(start, want_high=True)
            end_raw = self._extreme_raw_index(end, want_high=False)
        return end_raw - start_raw >= self._cfg.bi_min_span

    def _has_gap(self, a: MergedKline, b: MergedKline) -> bool:
        a_lo, a_hi = self._raw_extremes(a)
        b_lo, b_hi = self._raw_extremes(b)
        return max(a_lo, b_lo) > min(a_hi, b_hi)

    def _raw_extremes(self, u: MergedKline) -> tuple[float, float]:
        members = self._raw[u.start_index : u.end_index + 1]
        return min(k.low for k in members), max(k.high for k in members)

    def _extreme_raw_index(self, fx: Fenxing, *, want_high: bool) -> int:
        u = self._merged[fx.index]
        members = self._raw[u.start_index : u.end_index + 1]
        if want_high:
            best = max(range(len(members)), key=lambda i: (members[i].high, -i))
        else:
            best = min(range(len(members)), key=lambda i: (members[i].low, i))
        return u.start_index + best

    # ── 端点有效性 (bi_endpoint_check；none 跳过) ───────────────────────
    def _check_endpoint(self, start: Fenxing, end: Fenxing) -> bool:
        method = self._cfg.bi_endpoint_check
        if method is BiEndpointCheck.NONE:
            return True
        s_pre, s_mid, s_next = self._fx_units(start)
        e_pre, e_mid, e_next = self._fx_units(end)
        if start.fx_type is FxType.TOP:  # 向下笔: 顶 → 底
            if method is BiEndpointCheck.HALF:
                item2_high = max(e_pre.high, e_mid.high)
                self_low = min(s_mid.low, s_next.low)
            elif method is BiEndpointCheck.LOSS:
                item2_high = e_mid.high
                self_low = s_mid.low
            else:
                item2_high = max(e_pre.high, e_mid.high, e_next.high)
                self_low = min(s_pre.low, s_mid.low, s_next.low)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.low > item2_high
            return s_mid.high > item2_high and e_mid.low < self_low
        else:  # 向上笔: 底 → 顶
            if method is BiEndpointCheck.HALF:
                item2_low = min(e_pre.low, e_mid.low)
                cur_high = max(s_mid.high, s_next.high)
            elif method is BiEndpointCheck.LOSS:
                item2_low = e_mid.low
                cur_high = s_mid.high
            else:
                item2_low = min(e_pre.low, e_mid.low, e_next.low)
                cur_high = max(s_pre.high, s_mid.high, s_next.high)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.high < item2_low
            return s_mid.low < item2_low and e_mid.high > cur_high

    def _is_peak(self, start: Fenxing, end: Fenxing, direction: BiDir) -> bool:
        if direction is BiDir.UP:
            thr = _top_value(end)
            return all(u.high <= thr for u in self._merged[start.index + 1 : end.index])
        thr = _bottom_value(end)
        return all(u.low >= thr for u in self._merged[start.index + 1 : end.index])

    def _fx_units(self, fx: Fenxing) -> tuple[MergedKline, MergedKline, MergedKline]:
        return (
            self._merged[fx.index - 1],
            self._merged[fx.index],
            self._merged[fx.index + 1],
        )

    # ── 输出 ─────────────────────────────────────────────────────────────
    def finish(self, profile_id: str, config_hash: str) -> list[Bi]:
        out: list[Bi] = []
        for wb in self._bis:
            up = wb.direction is BiDir.UP
            start_price = _bottom_value(wb.start_fx) if up else _top_value(wb.start_fx)
            end_price = _top_value(wb.end_fx) if up else _bottom_value(wb.end_fx)
            rule_id = _rule_for(wb, self._cfg.bi_span_mode)
            trace = StructTrace(
                algo_card_id=_ALGO_CARD_ID,
                rule_id=rule_id,
                profile_id=profile_id,
                config_hash=config_hash or None,
                source_from_ts=self._merged[wb.start_fx.index - 1].start_ts,
                source_to_ts=self._merged[wb.end_fx.index + 1].end_ts,
                merged_from_index=wb.start_fx.index,
                merged_to_index=wb.end_fx.index,
                dep_to_index=wb.dep_index,
            )
            out.append(
                Bi(
                    period=wb.end_fx.period,
                    direction=wb.direction,
                    start_ts=wb.start_fx.timestamp,
                    end_ts=wb.end_fx.timestamp,
                    start_price=start_price,
                    end_price=end_price,
                    high=end_price if up else start_price,
                    low=start_price if up else end_price,
                    trace=trace,
                )
            )
        return out


def _rule_for(wb: _WorkBi, span_mode: BiSpanMode) -> str:
    """rule_id 按成笔实际规则派生 (bi-v1 §7)。standard 再按 span_mode 分 5k/4k。"""
    up = wb.direction is BiDir.UP
    if wb.rule_kind == "strong_prev":
        return _RULE_STRONG_PREV[0 if up else 1]
    if wb.rule_kind == "strong_next":
        return _RULE_STRONG_NEXT[0 if up else 1]
    if wb.rule_kind == "secondary":
        return _RULE_SECONDARY[0 if up else 1]
    # standard
    pair = _RULE_STD_MERGED if span_mode is BiSpanMode.MERGED_CENTER else _RULE_STD_RAW
    return pair[0 if up else 1]


def _bi_amplitude(start_fx: Fenxing, end_fx: Fenxing) -> float:
    """笔幅度 = abs(端点价差)（绝对价差，本轮锁定）。方向由 end_fx 决定。"""
    if end_fx.fx_type is FxType.TOP:  # 向上笔: 底→顶
        return abs(_top_value(end_fx) - _bottom_value(start_fx))
    return abs(_bottom_value(end_fx) - _top_value(start_fx))  # 向下笔: 顶→底


def _direction_of(end_fx: Fenxing) -> BiDir:
    return BiDir.UP if end_fx.fx_type is FxType.TOP else BiDir.DOWN


def _top_value(fx: Fenxing) -> float:
    return fx.high


def _bottom_value(fx: Fenxing) -> float:
    return fx.low
