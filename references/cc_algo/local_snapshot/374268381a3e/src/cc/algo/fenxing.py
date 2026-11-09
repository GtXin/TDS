"""分型（顶分型 / 底分型）— 在合并 K 线序列上识别 (算法说明卡 fenxing-v1)。

口径来源（口径优先链 §1.1）：
- 第 62 课：顶分型 = 中间 K 线 high 是相邻三 K 线 high 中最高、且 low 也是三者中最高；
  底分型对称。
- 用户确认（fenxing-v1 §16）：本层只产**原始**顶/底分型（取舍 / 最小 K 线数 / 有效性归
  笔层 PR-4）；平台 / 等价极值采**严格**判定（相等致「严格最高且最高」不成立则不构成分型）；
  相邻同型分型如实产出、不取舍。

分型在**合并后**序列上识别（包含已消除，保证三者可比、答案唯一，第65课）。
本模块是合并单元列表的**纯函数**：合并列表由 `KlineCombiner` 增量维护，故逐根增量与批量
结果一致（golden 自洽，§1.4）。

trace（§1.7）：每个分型落 `merged_range`（三根合并单元 index）+ `source_range`
（三根覆盖的原始 K 线 ts 范围）= PR-3 最小 trace 目标。
"""

from __future__ import annotations

from cc.algo.models import Fenxing, FxType, MergedKline
from cc.algo.trace import RULE_FENXING_BOTTOM, RULE_FENXING_TOP, StructTrace

_ALGO_CARD_ID = "fenxing-v1"


def detect_fenxings(merged: list[MergedKline]) -> list[Fenxing]:
    """识别合并序列中全部顶/底分型（严格，不取舍）。"""
    out: list[Fenxing] = []
    for i in range(1, len(merged) - 1):
        a, b, c = merged[i - 1], merged[i], merged[i + 1]
        is_top = (
            b.high > a.high and b.high > c.high and b.low > a.low and b.low > c.low
        )
        is_bottom = (
            b.low < a.low and b.low < c.low and b.high < a.high and b.high < c.high
        )
        if not (is_top or is_bottom):
            continue
        fx_type = FxType.TOP if is_top else FxType.BOTTOM
        rule_id = RULE_FENXING_TOP if is_top else RULE_FENXING_BOTTOM
        fx_high = max(a.high, b.high, c.high)
        fx_low = min(a.low, b.low, c.low)
        trace = StructTrace(
            algo_card_id=_ALGO_CARD_ID,
            rule_id=rule_id,
            merged_from_index=i - 1,
            merged_to_index=i + 1,
            source_from_ts=a.start_ts,
            source_to_ts=c.end_ts,
        )
        out.append(
            Fenxing(
                period=b.period,
                fx_type=fx_type,
                index=i,  # 中间合并单元下标
                timestamp=b.start_ts,  # 中间合并单元代表时间（§13）
                high=fx_high,
                low=fx_low,
                trace=trace,
            )
        )
    return out
