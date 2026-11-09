"""K 线合并（包含关系处理）— 增量实现 (算法说明卡 kline-merge-v1)。

口径来源（口径优先链 §1.1，原文 > 用户确认 > chan.py-main）：
- 第 65 课：包含合并取值（向上 max/max、向下 min/min）；顺序原则（逐根与末端单元比，
  非包含才新建）；方向「同时严格高低，去等号」。
- 用户确认（kline-merge-v1 §16）：首段方向顺延到首个可定向处（rule `merge.init`）；
  等价极值默认按包含合并（不启用 allow_top_equal 变体）；一字 K 退化为点区间。

增量纪律（§1.3 / §3.3）：本类**只暴露增量 append / 同 ts 末端更新 pop+append**，
不暴露任何全量重算入口；批量参照实现只在 `tests/`。

trace（§1.7）：每个合并单元落轻量 `StructTrace`（rule_id + 来源原始 K 线 ts 范围）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cc.algo.models import KlineDir, MergedKline
from cc.algo.trace import (
    RULE_MERGE_CONTAINS,
    RULE_MERGE_DIR_DOWN,
    RULE_MERGE_DIR_UP,
    RULE_MERGE_INIT,
    StructTrace,
)
from cc.data.models import Kline

_ALGO_CARD_ID = "kline-merge-v1"


def _direction(a_high: float, a_low: float, b_high: float, b_low: float) -> KlineDir | None:
    """相邻非包含两单元方向：同时严格抬高→UP，同时严格降低→DOWN（第65课，去等号）。

    返回 None 表示「包含 / 等价 / 无法唯一判定」（含相等极值）——此时不构成方向判据。
    注：非包含必然落入 UP / DOWN 之一；包含或任一边相等都返回 None。
    """
    if b_high > a_high and b_low > a_low:
        return KlineDir.UP
    if b_high < a_high and b_low < a_low:
        return KlineDir.DOWN
    return None


def _contains(a_high: float, a_low: float, b_high: float, b_low: float) -> bool:
    """a 是否包含 b（区间互含，方向无关；含相等边界 → 视为包含，对应 §16-2/§16-4）。"""
    return a_high >= b_high and a_low <= b_low


@dataclass(slots=True)
class _Unit:
    """内部可变合并单元（输出时转 MergedKline）。"""

    high: float
    low: float
    dir: KlineDir
    rule_id: str  # 该单元形成规则（merge.init / merge.dir.up / merge.dir.down）
    start_index: int  # 原始 K 线序列起始下标
    members: list[Kline] = field(default_factory=list)

    @property
    def end_index(self) -> int:
        return self.start_index + len(self.members) - 1


class KlineCombiner:
    """单 ``period`` 的增量 K 线合并器（串行喂数据）。

    首段方向「顺延」：在方向确立前，原始 K 线缓冲在 ``_lead``，不产合并单元；一旦出现
    首个非包含且同时高低的相邻对，确立方向 d，把之前的包含链坍缩成首个单元（rule
    `merge.init`），并以 d 起算后续。
    """

    def __init__(self, period: str) -> None:
        self.period = period
        self._units: list[_Unit] = []
        self._lead: list[Kline] = []  # 方向未定的前导缓冲
        self._established = False
        self._total = 0  # 已消费原始 K 线根数（= 下一根的全局下标）

    # ── 增量入口 ─────────────────────────────────────────────────────────
    def append(self, k: Kline) -> None:
        """末端追加一根新 K 线（timestamp 严格更大，由 engine 保证）。"""
        if self._established:
            self._append_established(k, self._total)
        else:
            self._lead.append(k)
            self._try_establish()
        self._total += 1

    def pop_last_kline(self) -> None:
        """回退最近一根原始 K 线（供同 ts 末端更新：pop 后 engine 再 append 新值）。"""
        if self._total == 0:
            return
        self._total -= 1
        if not self._established:
            self._lead.pop()
            return
        last = self._units[-1]
        last.members.pop()
        if last.members:
            self._recompute_unit(last)
            return
        self._units.pop()  # 单元清空 → 丢弃
        # 跨 establishment 边界回退（顺延口径 §16-1）: 若只剩首段 merge.init 单元, 说明被弹出的
        # 正是确立方向的那根, 方向依据已消失 → 恢复到方向未定的前导期, 由后续 append 重判。
        if len(self._units) == 1 and self._units[0].rule_id == RULE_MERGE_INIT:
            blob = self._units[0]
            self._lead = list(blob.members)
            self._units = []
            self._established = False
        elif not self._units:  # 防御: 全部弹空 → 回初始
            self._lead = []
            self._established = False

    # ── 输出 ─────────────────────────────────────────────────────────────
    def stable_index(self) -> int:
        """末端稳定点（§10）：倒数第 2 个合并单元的原始 K 线结束下标；不足返回 -1。

        最后一个合并单元为 provisional（新根可能改写），其余 confirmed。O(1)。
        """
        if len(self._units) < 2:
            return -1
        return self._units[-2].end_index

    def merged_count(self) -> int:
        """当前合并单元数量（O(1)）。"""
        return len(self._units)

    def to_merged_klines(self) -> list[MergedKline]:
        """当前合并单元序列（含轻量 trace）。方向未定前导期返回空。"""
        out: list[MergedKline] = []
        for u in self._units:
            trace = StructTrace(
                algo_card_id=_ALGO_CARD_ID,
                rule_id=self._derive_rule_id(u),
                source_from_ts=u.members[0].timestamp,
                source_to_ts=u.members[-1].timestamp,
            )
            out.append(
                MergedKline(
                    period=self.period,
                    dir=u.dir,
                    high=u.high,
                    low=u.low,
                    start_ts=u.members[0].timestamp,
                    end_ts=u.members[-1].timestamp,
                    start_index=u.start_index,
                    end_index=u.end_index,
                    trace=trace,
                )
            )
        return out

    # ── 内部 ─────────────────────────────────────────────────────────────
    def _try_establish(self) -> None:
        """前导期：检查最新相邻对是否确立方向。"""
        n = len(self._lead)
        if n < 2:
            return
        a, b = self._lead[-2], self._lead[-1]
        d = _direction(a.high, a.low, b.high, b.low)
        if d is None:
            return
        # 确立：lead[0..n-2] 必为包含链（更早的可定向对会更早触发），坍缩成首个单元。
        blob = self._lead[: n - 1]
        unit0 = self._merge_blob(blob, d, start_index=0)
        unit1 = _Unit(
            high=b.high, low=b.low, dir=d,
            rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
            start_index=n - 1, members=[b],
        )
        self._units = [unit0, unit1]
        self._lead = []
        self._established = True

    def _merge_blob(self, blob: list[Kline], d: KlineDir, start_index: int) -> _Unit:
        """把方向未定的包含链按确立方向 d 坍缩成首个单元（rule `merge.init`）。"""
        if d is KlineDir.UP:
            high = max(x.high for x in blob)
            low = max(x.low for x in blob)
        else:
            high = min(x.high for x in blob)
            low = min(x.low for x in blob)
        return _Unit(
            high=high, low=low, dir=d, rule_id=RULE_MERGE_INIT,
            start_index=start_index, members=list(blob),
        )

    def _append_established(self, k: Kline, idx: int) -> None:
        last = self._units[-1]
        contained = _contains(last.high, last.low, k.high, k.low) or _contains(
            k.high, k.low, last.high, last.low
        )
        if contained:  # 包含 → 按方向合并取值（rule_id 输出时按成员数派生, 见 _derive_rule_id）
            if last.dir is KlineDir.UP:
                last.high = max(last.high, k.high)
                last.low = max(last.low, k.low)
            else:
                last.high = min(last.high, k.high)
                last.low = min(last.low, k.low)
            last.members.append(k)
            return
        # 非包含 → 必为同时高低之一，新建单元（rule merge.dir.*）
        d = _direction(last.high, last.low, k.high, k.low)
        assert d is not None  # 非包含必可定向
        self._units.append(
            _Unit(
                high=k.high, low=k.low, dir=d,
                rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
                start_index=idx, members=[k],
            )
        )

    def _derive_rule_id(self, u: _Unit) -> str:
        """按单元**当前状态**派生 trace rule_id（§13「最近一次操作」）。

        形成规则 (u.rule_id) 始终保留不变 (merge.init / merge.dir.*)；输出时:
        - 首段 blob → merge.init;
        - 形成后吸收了包含根 (成员 > 1) → merge.contains;
        - 单根方向单元 → 其形成方向 merge.dir.up/down。
        派生而非 mutate, 故 pop/append 回退后 rule_id 自动正确, 无需恢复 (Codex r2 ⚠)。
        """
        if u.rule_id == RULE_MERGE_INIT:
            return RULE_MERGE_INIT
        if len(u.members) > 1:
            return RULE_MERGE_CONTAINS
        return u.rule_id  # 形成时的 merge.dir.up/down

    def _recompute_unit(self, u: _Unit) -> None:
        """从单元剩余 members 按其方向重算极值（pop 末端 K 线后用）。"""
        if u.dir is KlineDir.UP:
            u.high = max(x.high for x in u.members)
            u.low = max(x.low for x in u.members)
        else:
            u.high = min(x.high for x in u.members)
            u.low = min(x.low for x in u.members)
