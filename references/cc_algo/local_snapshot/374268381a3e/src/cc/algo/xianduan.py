"""线段（Xianduan）— 在笔序列上经本项目自主**特征序列法**派生
(算法说明卡 xianduan-v1 / decision-0028)。

口径优先链 (§1.1 / decision-0001 v1.4 §12.3): 缠论原文 (第62/65/67/77课) > 用户确认的本项目
口径 > 本项目自主实现; 参考项目 (chan.py-main / czsc / chanlun-pro) 无固定优先级, 只作对照/
启发/差异发现来源。

口径 (decision-0028, 用户 2026-06-19 确认):
- 原文严格定义: 线段 ≥3 笔、开始三笔有重合、被**反向线段**破坏才确认 (第77课); 破坏 = 特征序列
  分型 + 缺口两种情况 (第67课); 上升线段段内可有最高不能有最低 (第八种情况)。
- 默认口径 = 本项目自主**特征序列法** (口径名 ``feature_sequence``, 缠论语义命名, **不用参考
  项目名**); 末段 ``peak``; 基底笔 = bi_5k 老笔。内核思路参考 chan.py-main `CEigen/CEigenFX/
  cal_seg_sure/find_revert_fx` (来源与差异见 xianduan-v1 §3/§6,
  标「用户确认的项目口径」不伪装原文)。
- 第一种情况 (无缺口) → 特征序列分型直接确认; 第二种情况 (有缺口) → 反向特征序列出现反向
  分型才确认 (``find_revert_fx``), 未确认前 provisional。
- 末段未闭合 / 缺口未确认段 → provisional; ``dep_to_index`` 依赖水位保 confirmed 区不被回补改写。

**纯函数**: 线段 = 笔序列上的纯函数派生 (对齐 bi-v1 §11), 挂引擎版本缓存; 无跨调用状态。
Xianduan 的 source_range/merged_range 从构成笔的 trace 聚合。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cc.algo.config import (
    ChanConfig,
    XianduanBreakPolicy,
    XianduanNonstandardPolicy,
    XianduanOscillationPolicy,
)
from cc.algo.models import Bi, BiDir, Xianduan
from cc.algo.trace import (
    RULE_XIANDUAN_DOWN_EXTREME_SPLIT,
    RULE_XIANDUAN_DOWN_FORMING,
    RULE_XIANDUAN_DOWN_FSEQ,
    RULE_XIANDUAN_DOWN_GAP,
    RULE_XIANDUAN_DOWN_NONSTANDARD_REPAIR,
    RULE_XIANDUAN_DOWN_PEN_BREAK_ABSORB,
    RULE_XIANDUAN_DOWN_STRONG_BI_BREAK,
    RULE_XIANDUAN_DOWN_TAIL,
    RULE_XIANDUAN_DOWN_TAIL_EXTEND,
    RULE_XIANDUAN_UP_EXTREME_SPLIT,
    RULE_XIANDUAN_UP_FORMING,
    RULE_XIANDUAN_UP_FSEQ,
    RULE_XIANDUAN_UP_GAP,
    RULE_XIANDUAN_UP_NONSTANDARD_REPAIR,
    RULE_XIANDUAN_UP_PEN_BREAK_ABSORB,
    RULE_XIANDUAN_UP_STRONG_BI_BREAK,
    RULE_XIANDUAN_UP_TAIL,
    RULE_XIANDUAN_UP_TAIL_EXTEND,
    StructTrace,
)

_ALGO_CARD_ID = "xianduan-v1"

# 默认线段算法口径名 (本项目缠论语义, 不用参考项目名)。
XIANDUAN_ALGO_FEATURE_SEQUENCE = "feature_sequence"

# 端点极值拆段最小笔数 (与 chanlun-pro "非标准" 页面一致; 工程补充规则, xianduan-v1 §5.7)。
NONSTANDARD_MIN_BIS = 9

# 笔破坏补齐策略 (内部常量, 不上 UI; xianduan-v1 §5.7 / decision-0028 §3-bis)。
# 内部 orphan 区间用笔破坏(方向极值)法补成合法段; "allow"=补内部空缺(默认), "gap_only"=仅缺口段补。
XIANDUAN_BI_BREAK_POLICY = "allow"


def _opposite(d: BiDir) -> BiDir:
    return BiDir.DOWN if d is BiDir.UP else BiDir.UP


# ══════════════════════════════════════════════════════════════════════════════
# N0/N1/N2 动态冻结状态机 (decision-0028 §3-quater / xianduan-v1 §16 v8)
# ──────────────────────────────────────────────────────────────────────────────
# 定调: "候选成立 ≠ confirmed 冻结"。缠论原文(第67课第一/二种)判候选是否成立; 本状态机判候选
# 何时冻结 confirmed —— 工程动态冻结纪律, 非缠论口径修改。候选由特征序列内核 (_EigenFX) 生成;
# 本状态机管冻结时机的转移 (T1-T7, 含 T6 rollover / T7 pen_break_absorb)。
# 已接入 build_xianduans() / ChanEngine.get_xianduans() (PR-6B 主线)。
# ══════════════════════════════════════════════════════════════════════════════


class XianduanFreezeState(StrEnum):
    """线段冻结状态 (方案 A 显示口径)。"""

    FROZEN = "frozen"  # 已冻结 confirmed (实线; 不被普通后续改写)
    SOFT_N0 = "soft_n0"  # 准完成 N0 (软实线; 有候选终点未冻结, 可尾部延伸)
    PENDING_N1 = "pending_n1"  # 待确认 N1 (虚线 provisional; 可被击破作废)


@dataclass(slots=True)
class _XianduanCand:
    """线段候选 (特征序列内核产生 → 进 N0/N1/N2 状态机)。

    ``start_key`` = 起点关键价位 (上涨段 = 起点 low / 下跌段 = 起点 high), N1 击破判据。
    ``end_key`` = 候选终点极值 (上涨段 = 终点 high / 下跌段 = 终点 low)。延伸时随 end 更新。
    """

    start_bi: int
    end_bi: int
    direction: BiDir
    start_key: float
    end_key: float
    rule: str = "feature_seq"  # 候选来源 (feature_seq / gap / pen_break_absorb); 随候选传到输出
    dep: int = 0  # 依赖水位 (最大查阅笔下标); 随候选传到输出 (状态机不读)
    pen_break_at: int | None = None  # 笔破坏失败吸收段的内部越点笔下标 (T7; 其它段 None)
    confirmation_ts: int | None = None  # 缺口段第二序列反向分型证据笔 end_ts (§16 v10; 冻结带出)
    frozen_by: str = ""  # 冻结事件来源 ("gap_revert" = 缺口第二种反向确认; 随候选/冻结传出)


@dataclass(slots=True)
class _FrozenXianduan:
    """已冻结 confirmed 线段 (不可变语义; 不被普通后续走势改写)。"""

    start_bi: int
    end_bi: int
    direction: BiDir
    rule: str = "feature_seq"
    dep: int = 0
    pen_break_at: int | None = None  # 笔破坏失败吸收段的内部越点笔下标 (T7; 其它段 None)
    confirmation_ts: int | None = None  # 反向确认证据笔 end_ts (gap_revert §16 v10; 与几何终点分离)
    frozen_by: str = ""  # 冻结事件 ("gap_revert" = 由后继缺口反向确认原子冻结; 其它 "")


class _XianduanFreezeMachine:
    """N0/N1/N2 动态冻结状态机 (严格标准)。

    维护: frozen 冻结历史 + soft N0(准完成) + pending N1(待确认)。N0/N1 反向交替。
    5 个转移 (decision-0028 §3-quater)：
      T1 准完成 ``promote_to_n0``      : 候选 → soft N0 (无 N0 时)。
      T2 待确认 ``set_pending_n1``     : 反向候选 → pending N1 (有 N0 无 N1 时)。
      T3 确认   ``confirm_on_n2``      : N2 出现且 N1 未被击破 → 冻结 N0、N1→新 N0、N2→新 N1。
      T4 作废 + T5 延伸 ``invalidate_n1_extend_n0`` : N1 起点被严格击破 → 作废 N1、N0 延伸吞击破区。
    回算水位 = 最后 frozen 段 end+1 (``rebuild_floor``); 冻结历史不回改。
    """

    def __init__(self) -> None:
        self.frozen: list[_FrozenXianduan] = []
        self.n0: _XianduanCand | None = None
        self.n1: _XianduanCand | None = None

    # ── 查询 ──────────────────────────────────────────────────────────────────
    def rebuild_floor(self) -> int:
        """最早可重算笔下标 = 最后 frozen 段 end+1 (冻结区不回改; -1 = 无 frozen 可从 0 起)。"""
        return self.frozen[-1].end_bi + 1 if self.frozen else 0

    def is_n1_broken(self, price: float) -> bool:
        """N1 起点是否被**严格**击破 (触平不算破; 与相等值口径一致)。

        上涨 N1: 后续价 ``< 起点 low`` → 破; 下跌 N1: 后续价 ``> 起点 high`` → 破。
        """
        if self.n1 is None:
            return False
        if self.n1.direction is BiDir.UP:
            return price < self.n1.start_key
        return price > self.n1.start_key

    # ── 5 个转移 ──────────────────────────────────────────────────────────────
    def promote_to_n0(self, cand: _XianduanCand) -> None:
        """T1 准完成: 候选 → soft N0 (仅在无 N0 无 N1 时, 如首段或冻结级联后)。"""
        if self.n0 is not None or self.n1 is not None:
            raise AssertionError("promote_to_n0 须在无 N0/N1 时")
        self.n0 = cand

    def set_pending_n1(self, cand: _XianduanCand) -> None:
        """T2 待确认: 反向候选 → pending N1 (有 N0 无 N1; 方向须与 N0 反向)。"""
        if self.n0 is None or self.n1 is not None:
            raise AssertionError("set_pending_n1 须在有 N0 无 N1 时")
        if cand.direction is not _opposite(self.n0.direction):
            raise AssertionError("N1 方向须与 N0 反向")
        self.n1 = cand

    def confirm_on_n2(self, n2: _XianduanCand) -> None:
        """T3 确认: N2 出现且 N1 未被击破 → 冻结 N0、N1 升为新 N0、N2 成新 N1。

        N2 方向 = N0 方向 (= N1 的反向)。冻结后滚动窗口左移一格。
        """
        if self.n0 is None or self.n1 is None:
            raise AssertionError("confirm_on_n2 须在 N0、N1 都在时")
        if n2.direction is not self.n0.direction:
            raise AssertionError("N2 方向须与 N0 同向 (N1 反向)")
        self.frozen.append(
            _FrozenXianduan(self.n0.start_bi, self.n0.end_bi, self.n0.direction,
                      rule=self.n0.rule, dep=self.n0.dep, pen_break_at=self.n0.pen_break_at,
                      confirmation_ts=self.n0.confirmation_ts, frozen_by=self.n0.frozen_by)
        )
        self.n0 = self.n1  # N1 → 新 soft N0 (缺口段带 confirmation_ts, 下轮冻结时带出)
        self.n1 = n2  # N2 → 新 pending N1

    def invalidate_n1_extend_n0(self, new_end_bi: int, new_end_key: float) -> None:
        """T4 作废 + T5 延伸: N1 起点被严格击破 → 作废 N1; N0 延伸吞掉假反弹+击破区到新极值。

        ``new_end_bi/new_end_key`` = N0 延伸后的新终点 (由特征序列内核重算给出, S2 接入)。
        延伸后 N1 置空, 等新反向候选重新成 N1 (从击破笔后第一根反向笔起)。
        """
        if self.n0 is None or self.n1 is None:
            raise AssertionError("invalidate_n1_extend_n0 须在 N0、N1 都在时")
        self.n1 = None  # T4 作废
        self.n0.end_bi = new_end_bi  # T5 延伸
        self.n0.end_key = new_end_key

    def rollover_n1_to_n0(self) -> None:
        """T6 转接: N1 (反向候选) **跌破/突破了 N0 起点** → N1 是真强反向, N0 已完结 →
        冻结 N0、N1 升为新 soft N0、N1 置空 (下一轮从 N1 之后重找新反向)。

        与 T3(confirm) 区别: T3 靠 N2 出现确认; T6 靠 N1 自身越过 N0 起点 (强反向) 确认。
        修「N0 反向延伸吞掉越过起点的反向段 → 造 B5 反画 → 冻结硬闸断链」。
        """
        if self.n0 is None or self.n1 is None:
            raise AssertionError("rollover_n1_to_n0 须在 N0、N1 都在时")
        self.frozen.append(
            _FrozenXianduan(self.n0.start_bi, self.n0.end_bi, self.n0.direction,
                      rule=self.n0.rule, dep=self.n0.dep, pen_break_at=self.n0.pen_break_at,
                      confirmation_ts=self.n0.confirmation_ts, frozen_by=self.n0.frozen_by)
        )
        self.n0 = self.n1  # N1 → 新 soft N0
        self.n1 = None  # 下一轮重找反向 N1

    def confirm_gap_revert(self, evidence_bi: int, confirmation_ts: int) -> None:
        """T8 gap_revert_confirmed 原子转移 (§16 v10): N1 = 缺口候选、第二特征序列出反向分型 →
        **原子冻结 N0(直接前驱) + N1(缺口段)**, 两段冻结依赖水位/confirmation_ts 均反映
        ``evidence_bi`` (第二特征序列分型证据笔; 不暗示 N0 更早已 frozen); N0、N1 均置空 (调用方
        随后从 N1.end+1 重建新 N0)。

        约束 (调用方 driver 先校验, 见 run()): 当前须 soft N0 + pending 缺口 N1; N0/N1 方向相反且
        连续; 各过 ``_gate_ok``; ``evidence_bi`` 归属当前 N1。任一不满足则不调用本转移。
        **N0 保留原 rule 与自身 source_range (start/end 不变), 只标 frozen_by=gap_revert** (不塞 N1
        几何)。N1 几何终点不变, rule 保持 (gap)。
        """
        if self.n0 is None or self.n1 is None:
            raise AssertionError("confirm_gap_revert 须在 N0、N1 都在时")
        # 冻结 N0 (直接前驱): 保留原候选来源 rule 与几何; 依赖水位/confirmation_ts = evidence_bi。
        self.frozen.append(_FrozenXianduan(
            self.n0.start_bi, self.n0.end_bi, self.n0.direction, rule=self.n0.rule,
            dep=evidence_bi, pen_break_at=self.n0.pen_break_at,
            confirmation_ts=confirmation_ts, frozen_by="gap_revert"))
        # 冻结 N1 (缺口段): 几何终点不变; dep/confirmation_ts = evidence_bi (证据水位 ≠ 几何终点)。
        self.frozen.append(_FrozenXianduan(
            self.n1.start_bi, self.n1.end_bi, self.n1.direction, rule=self.n1.rule,
            dep=evidence_bi, pen_break_at=self.n1.pen_break_at,
            confirmation_ts=confirmation_ts, frozen_by="gap_revert"))
        self.n0 = None
        self.n1 = None


def build_xianduans(
    bis: list[Bi],
    cfg: ChanConfig,
    *,
    profile_id: str,
    config_hash: str,
) -> list[Xianduan]:
    """从笔序列派生线段序列（纯函数，特征序列法；签名对齐 ``build_bis``）。

    Args:
        bis: 引擎已派生的笔序列 (默认主线 = bi_5k 老笔; xianduan-v1 §5)。
        cfg: 缠论口径配置 (PR-6B: 线段默认口径固定 feature_sequence; 暂无可配置变体)。
        profile_id / config_hash: 口径身份 (供 Xianduan trace 回溯 §1.7)。

    Returns:
        线段序列 (上下交替, 带稳定 id + 轻量 trace; confirmed/provisional 由 dep 水位判)。
    """
    if len(bis) < 3:
        return []
    cfg = cfg.normalize()
    builder = _XianduanBuilder(
        bis,
        nonstandard=cfg.xianduan_nonstandard_policy is XianduanNonstandardPolicy.REPAIR,
        oscillation=cfg.xianduan_oscillation_policy is XianduanOscillationPolicy.THREE_BI,
        strong_bi=cfg.xianduan_break_policy is XianduanBreakPolicy.STRONG_BI,
    )
    work = builder.run()
    return _finish(bis, work, profile_id=profile_id, config_hash=config_hash)


# ── 特征元素 / 特征序列分型识别器 ──────────────────────────────────────────────


@dataclass(slots=True)
class _Eigen:
    """特征元素 = 连续 (经包含合并的) 反向笔当 K 线 (第65/67课标准特征序列)。

    把每个反向笔当 K 线: high=笔区间高、low=笔区间低。``idxs`` 记所含笔下标; ``gap`` 与前一
    元素是否有缺口。包含处理 (``test_combine``) **区分两种包含方向** (用户 2026-06-20 口径 §1):
    旧元素包含新笔→恒合并; 新笔包含旧元素→exclude 模式不合并 (保转折分界, 第四/七种情况)。
    合并取值按线段方向 (上升高高、下降低低)。
    """

    xianduan_dir: BiDir
    idxs: list[int]
    high: float
    low: float
    gap: bool = False

    @classmethod
    def of(cls, xianduan_dir: BiDir, idx: int, bi: Bi) -> _Eigen:
        return cls(xianduan_dir=xianduan_dir, idxs=[idx], high=bi.high, low=bi.low)

    def test_combine(
        self, bi: Bi, *, exclude_included: bool, allow_top_equal: int | None
    ) -> str:
        """包含判定 (第65/67课包含处理) → ``combine`` / ``included`` / ``up`` / ``down``。

        - **旧元素包含新笔** (self 全包 bi) → ``combine`` (恒合并)。
        - **新笔包含旧元素** (bi 全包 self) → exclude 模式 ``included`` (不合并、成新元素, 第四/
          七种情况保转折分界); 否则 ``combine``。相等顶/底由 ``allow_top_equal`` 放行成方向
          (1=顶相等不合并 / -1=底相等不合并, 第七种情况, 见 xianduan-v1 §6 相等值口径)。
        - 无包含 → ``up`` (新笔更高) / ``down`` (新笔更低)。
        """
        if self.high >= bi.high and self.low <= bi.low:  # 旧元素包含新笔
            return "combine"
        if self.high <= bi.high and self.low >= bi.low:  # 新笔包含旧元素
            if allow_top_equal == 1 and self.high == bi.high and self.low > bi.low:
                return "down"
            if allow_top_equal == -1 and self.low == bi.low and self.high < bi.high:
                return "up"
            return "included" if exclude_included else "combine"
        if self.high > bi.high and self.low > bi.low:
            return "down"
        return "up"

    def merge(self, idx: int, bi: Bi) -> None:
        """按线段方向合并新笔 (上升取高高、下降取低低; 第65课包含处理)。"""
        if self.xianduan_dir is BiDir.UP:
            self.high = max(self.high, bi.high)
            self.low = max(self.low, bi.low)
        else:
            self.high = min(self.high, bi.high)
            self.low = min(self.low, bi.low)
        self.idxs.append(idx)


class _SeqRole(StrEnum):
    """特征序列角色 (§16 v10; 决定 ``_actual_break`` 突破判定规则)。

    - ``PRIMARY``    第一特征序列: 末原始笔 ``bis[e1.idxs[-1]]`` + k+2 前看 (第八种情况; 现状不动)。
    - ``GAP_REVERT`` 第二特征序列 (缺口第二种反向确认): 用**合并后** ``_Eigen.high/low`` 严格判、
                     **无前看** (第七/78课严格包含处理)。
    """

    PRIMARY = "primary"
    GAP_REVERT = "gap_revert"


class _EigenFX:
    """特征序列分型识别器 (候选线段方向 ``xianduan_dir``; 只接反向笔)。

    三特征元素 e0/e1/e2: 上升线段看顶分型、下降看底分型 (第67课)。**包含处理两层**: 第二元素
    用 exclude (新笔包含旧元素不合并, 保转折分界, 第四种情况); 第三元素允许合并 (第六/八种情况)。
    顶/底分型**同时校验高低点** (第二种情况防假分型); 实际突破规则随 ``sequence_role`` (§16 v10):
    PRIMARY 带前看 (第八种情况), GAP_REVERT 用合并值严格判 (第七/78课, 无前看)。
    """

    __slots__ = ("xianduan_dir", "bis", "ele", "lst", "last_evidence", "sequence_role")

    def __init__(
        self, xianduan_dir: BiDir, bis: list[Bi], *, sequence_role: _SeqRole = _SeqRole.PRIMARY
    ) -> None:
        self.xianduan_dir = xianduan_dir
        self.bis = bis
        self.ele: list[_Eigen | None] = [None, None, None]
        self.lst: list[int] = []  # 已喂入的反向笔下标
        self.last_evidence: int | None = None  # 成分型实际查阅的最大笔下标 (dep 水位)
        self.sequence_role = sequence_role

    def _is_up(self) -> bool:
        return self.xianduan_dir is BiDir.UP

    def _top_equal(self) -> int:
        # 第三元素相等边界口径 (第七种情况): 上升线段(降特征笔)=1 顶相等不合并; 下降=-1 底相等。
        return 1 if self._is_up() else -1

    def add(self, idx: int) -> bool:
        """喂入一根反向笔, 返回是否出现特征序列分型。"""
        bi = self.bis[idx]
        self.lst.append(idx)
        if self.ele[0] is None:
            self.ele[0] = _Eigen.of(self.xianduan_dir, idx, bi)
            return False
        if self.ele[1] is None:
            return self._treat_second(idx, bi)
        if self.ele[2] is None:
            return self._treat_third(idx, bi)
        # 三元素已满还没处理 → 内部不变量错误 (调用方应在出分型时停止喂入)。
        raise AssertionError("eigen sequence overflow: 3 elements already filled")

    def _treat_second(self, idx: int, bi: Bi) -> bool:
        """第二元素: exclude 包含处理 (新笔包含旧元素不合并, 保转折分界, 第四种情况)。"""
        e0 = self.ele[0]
        assert e0 is not None
        cd = e0.test_combine(bi, exclude_included=True, allow_top_equal=None)
        if cd == "combine":
            e0.merge(idx, bi)
            return False
        e1 = _Eigen.of(self.xianduan_dir, idx, bi)
        self.ele[1] = e1
        # 前两元素方向不对 (上升线段 e1 不高于 e0 / 下降线段 e1 不低于 e0) → 不可能成分型, 滑窗。
        if (self._is_up() and e1.high < e0.high) or (
            not self._is_up() and e1.low > e0.low
        ):
            return self._reset()
        return False

    def _treat_third(self, idx: int, bi: Bi) -> bool:
        """第三元素: 允许合并 (exclude 关, 第六/八种情况); 相等边界用 allow_top_equal。"""
        e1 = self.ele[1]
        assert e1 is not None
        self.last_evidence = idx
        cd = e1.test_combine(
            bi, exclude_included=False, allow_top_equal=self._top_equal()
        )
        if cd == "combine":
            e1.merge(idx, bi)
            return False
        self.ele[2] = _Eigen.of(self.xianduan_dir, idx, bi)
        if not self._actual_break():
            return self._reset()
        if self._is_fx():
            self._mark_gap()
            return True
        return self._reset()

    def _actual_break(self) -> bool:
        """e2 实际突破判定 (随 ``sequence_role``; §16 v10)。

        - ``GAP_REVERT`` (第二特征序列, 第七/78课): e2 须严格突破**合并后** ``e1.low/e1.high``,
          **无前看** —— 合并元素不退回末原始笔 (避免触平漏判; 详 §16 v10)。
        - ``PRIMARY`` (第一特征序列, 第八种情况): e2 须突破 e1 **末原始笔**; 表面未破则**前看后一笔
          第二笔** (现状不变)。
        """
        e1, e2 = self.ele[1], self.ele[2]
        assert e1 is not None and e2 is not None
        if self.sequence_role is _SeqRole.GAP_REVERT:  # 第二特征序列: 合并值严格判, 无前看
            return e2.low < e1.low if self._is_up() else e2.high > e1.high
        last_e1 = self.bis[e1.idxs[-1]]  # e1 末构成笔 (合并后用末笔极值, 非合并值)
        if self._is_up():
            if e2.low < last_e1.low:
                return True
        elif e2.high > last_e1.high:
            return True
        # 前看: e2 因表面包含未直接突破, 但其笔后第二笔已形成实际突破 (第八种情况)。
        k = e2.idxs[0]
        if k + 2 < len(self.bis):
            e2_bi, ahead = self.bis[k], self.bis[k + 2]
            if self._is_up() and e2_bi.direction is BiDir.DOWN and ahead.low < e2_bi.low:
                self.last_evidence = k + 2  # 前看突破: 依赖到 k+2 笔
                return True
            if (
                not self._is_up()
                and e2_bi.direction is BiDir.UP
                and ahead.high > e2_bi.high
            ):
                self.last_evidence = k + 2
                return True
        return False

    def _is_fx(self) -> bool:
        """顶/底分型 (第67课; **同时校验高低点**防假分型, 第二种情况)。

        顶分型 (上升线段): e0.high < e1.high 且 e2.high ≤ e1.high 且 e2.low < e1.low。
        底分型 (下降线段): e2.high > e1.high 且 e0.low > e1.low 且 e2.low ≥ e1.low。
        """
        e0, e1, e2 = self.ele[0], self.ele[1], self.ele[2]
        assert e0 is not None and e1 is not None and e2 is not None
        if self._is_up():
            return e0.high < e1.high and e2.high <= e1.high and e2.low < e1.low
        return e2.high > e1.high and e0.low > e1.low and e2.low >= e1.low

    def _mark_gap(self) -> None:
        """标记 e1 与 e0 间是否有特征序列缺口 (第67课第一种 vs 第二种情况)。"""
        e0, e1 = self.ele[0], self.ele[1]
        assert e0 is not None and e1 is not None
        if self._is_up():
            e1.gap = e0.high < e1.low  # 上升: e0 顶 低于 e1 底 → 缺口
        else:
            e1.gap = e0.low > e1.high  # 下降: e0 底 高于 e1 顶 → 缺口

    def _reset(self) -> bool:
        """非分型 → 从第二根特征笔起重排滑窗 (再喂入)。"""
        rest = self.lst[1:]
        self.ele = [None, None, None]
        self.lst = []
        for j in rest:
            if self.add(j):
                return True
        return False

    def has_gap(self) -> bool:
        e1 = self.ele[1]
        return bool(e1 and e1.gap)

    def peak_end_bi_idx(self) -> int:
        """线段端点笔下标 = 峰值特征笔的前一笔 (第67课, GetPeakBiIdx 思路)。

        上升线段: e1 内 high 最高的特征笔 (下降笔) 的前一笔 (上升笔) 终点 = 顶 = 线段终点。
        """
        e1 = self.ele[1]
        assert e1 is not None
        if self._is_up():
            p = max(e1.idxs, key=lambda i: self.bis[i].high)
        else:
            p = min(e1.idxs, key=lambda i: self.bis[i].low)
        return p - 1


# ── 主流程 (镜像 chan SegListChan.cal_seg_sure / treat_fx_eigen / collect_left) ──


@dataclass(slots=True)
class _WorkXianduan:
    """构建期线段 + 冻结状态。rule_kind = 候选来源 (feature_seq/gap/forming);
    freeze_state ∈ FROZEN(已冻结实线) / SOFT_N0(准完成软实线) / PENDING_N1(待确认虚线)。"""

    start_bi: int
    end_bi: int
    direction: BiDir
    rule_kind: str
    dep_index: int
    freeze_state: XianduanFreezeState
    pen_break_at: int | None = None  # 笔破坏失败吸收段的内部越点笔下标 (T7; 其它段 None)
    confirmation_ts: int | None = None  # gap_revert 反向确认证据 end_ts (§16 v10)
    frozen_by: str = ""  # 冻结事件来源 ("gap_revert" / "")


class _XianduanBuilder:
    """单次派生的内部状态机 (不跨调用持久)。"""

    def __init__(
        self, bis: list[Bi], *, nonstandard: bool = False, oscillation: bool = False,
        strong_bi: bool = False,
    ) -> None:
        self.bis = bis
        self.xianduans: list[_WorkXianduan] = []
        # 实战变体开关 (严格标准均 False; xianduan-v1 §5 / xianduan-practical-v1 §16)。
        self.nonstandard = nonstandard  # 非标准连续拆分补齐
        self.oscillation = oscillation  # 横向震荡三笔成段 (TODO: 后续实现)
        self.strong_bi = strong_bi  # 强势笔破坏两阶段确认 (单笔破坏 N0 + 反向标准段 N2 确认)
        # 诊断记录 (供图上验收/调试)。
        self.orphan_debug: list[tuple[int, int, str]] = []
        # tail 区间记录 (末端无法成合法 provisional 段的原因)。
        self.tail_debug: list[tuple[int, int, str]] = []

    def run(self) -> list[_WorkXianduan]:
        """N0/N1/N2 动态冻结 pipeline (decision-0028 §3-quater / xianduan-v1 §16 v8):

        ① 定首段方向/起点 (暖机头 B5 锁定) → ② 特征序列内核逐段产生**候选** (不立即冻结) →
        ③ 候选进 N0/N1/N2 状态机: N2 出现且 N1 未被击破 → 冻结 N0; N1 起点被严格击破 → 作废 N1、
        N0 延伸吞击破区、新 N1 从击破笔后第一根反向笔重找 → ④ 输出 frozen(实线)/soft N0(软实线)/
        pending N1(虚线) + 末尾兜底。**confirmed 冻结历史不回改** (回算水位)。

        "候选成立 ≠ confirmed 冻结": 原文(第一/二种)判候选, 状态机判冻结时机。"""
        n = len(self.bis)
        if n < 3:
            return self.xianduans
        first = self._first_xianduan()
        if first is None:
            return self._emit(_XianduanFreezeMachine())  # 无法定向 → 整窗兜底 forming
        begin, d = first
        c0 = self._candidate(begin, d)
        if c0 is None:
            return self._emit(_XianduanFreezeMachine())
        sm = _XianduanFreezeMachine()
        sm.promote_to_n0(c0)  # T1 准完成
        guard = 0
        while guard < 4 * n:  # 防御性上界 (每次推进至少前移一笔)
            guard += 1
            if sm.n1 is None:
                assert sm.n0 is not None
                rev = self._candidate(sm.n0.end_bi + 1, _opposite(sm.n0.direction))
                # N0 方向若在反向候选区内 (或其后) 创新极值 → 先延伸 N0 过子顶/子底 (第五/八种);
                # 否则反向候选 = 真反向段 → pending N1。
                begin = sm.n0.end_bi + 1
                limit = rev.end_bi if rev is not None else len(self.bis) - 1
                ext = self._first_new_extreme(sm.n0, begin, limit)
                ep = (self._extreme_problem(sm.n0.start_bi, ext[0], sm.n0.direction)
                      if ext is not None else None)
                # strong_bi 单笔段**恒不延伸/不吸收** (几何 = 破坏单笔本身, 用户 2026-07-10 Q2);
                # 跳过 N0 延伸与 T7, 直接进反向候选/strong 拆分, 保持单笔不变。
                strong_n0 = sm.n0.rule == "strong_bi"
                # ① 干净延伸 (起点仍是极值) → 延伸 N0 过子顶/子底 (第五/八种)。
                if not strong_n0 and ext is not None and ep is None:
                    sm.n0.end_bi, sm.n0.end_key = ext
                    continue
                # ② T7 笔破坏失败吸收 (decision-0028 §3-quinquies): 反向**未成合法线段**
                #    (rev is None) + 原方向创新极值 (ext) + 延伸区**越过 N0 起点** (ep == "start",
                #    = 失败笔破坏越点) → 把该失败笔破坏吸收进 N0, 延伸到新极值, 标 pen_break_absorb
                #    (允许内部越点, B5 豁免)。**不 break**, driver 继续。
                if not strong_n0 and rev is None and ext is not None and ep == "start":
                    sm.n0.end_bi, sm.n0.end_key = ext
                    sm.n0.rule = "pen_break_absorb"
                    sm.n0.pen_break_at = self._pen_break_bi(sm.n0, begin, ext[0])
                    continue
                if rev is None:
                    break  # 无反向也无延伸 → N0 是末段 (soft), 反向边交兜底
                # ③ strong_bi 两阶段确认 (实战变体; xianduan-practical-v1 §16, 用户 2026-07-10):
                #    N0 之后**首根反向单笔**严格破坏 N0 起点关键极值 (start_key), 且其**紧接**又形成
                #    一条对该单笔的反向标准线段 (N2 = _candidate(single+1, N0向)) → 该单笔登记为
                #    strong_bi 单笔 N1 (不立即冻结); 由标准 N2 裁决 (confirm_on_n2) 两滞后冻结。
                #    N2 未成形 → 不登记 → 回退标准 rev (含 T7 pen_break_absorb 吸收)。
                if self.strong_bi:
                    strong = self._try_strong_bi_break(sm.n0)
                    if strong is not None:
                        sm.set_pending_n1(strong)
                        continue
                sm.set_pending_n1(rev)  # T2 待确认
                continue
            # 有 N0+N1: ① N1 延伸 → ② N2 成功冻结 → ③ N2 失败作废延伸 → ④ 未决 (见 _advance_n0n1)。
            assert sm.n0 is not None
            verdict = self._advance_n0n1(sm)
            if verdict[0] == "break":
                # strong_bi 单笔 N0 **不可延伸** (用户 2026-07-10 Q2): 本会 T4+T5 作废 N1、延伸
                # N0 的情形, 单笔段改走 T6 转接 (冻结单笔 N0、N1 升 soft N0)——单笔既已被反向标准段
                # 确认, 后续再破坏它起点只是走势延续, 不回头改写单笔几何。
                if sm.n0.rule == "strong_bi":
                    if not self._gate_ok(sm.n0):
                        break
                    sm.rollover_n1_to_n0()
                else:
                    sm.invalidate_n1_extend_n0(verdict[1], verdict[2])  # T4+T5 作废+延伸
            elif verdict[0] == "rollover":
                # T6 转接: N1 越过 N0 起点 (真强反向) → 冻结 N0、N1 升 N0。N0 须过冻结硬闸。
                if not self._gate_ok(sm.n0):
                    break
                sm.rollover_n1_to_n0()
            elif verdict[0] == "extend_n1":
                sm.n1.end_bi, sm.n1.end_key = verdict[1], verdict[2]  # N1 延伸 (子顶/子底)
            elif verdict[0] == "confirm":
                if not self._gate_ok(sm.n0):  # 冻结硬闸 (absorb 段豁免 B5, 见 _gate_ok)
                    break
                sm.confirm_on_n2(verdict[1])  # T3 冻结 N0、N1→N0、N2→N1
            elif verdict[0] == "gap_revert":
                # T8 缺口第二种反向确认 (§16 v10): 缺口 N1 经第二特征序列反向分型确认 → 原子冻结
                # N0(前驱)+N1(缺口段)。原子前提: 两段各过硬闸 + 方向相反且连续; 任一不满足则不触发
                # (退回 break, N1 保持 pending)。冻结后 **G-a 链式 seed**: 用同一反向分型 e1 peak 作
                # 下一段(反向)候选终点 → 新 soft N0 (不由同一证据 frozen), 再由标准 pipeline 裁决。
                assert sm.n1 is not None
                evidence_bi, peak_bi = verdict[1], verdict[2]
                if not (self._gate_ok(sm.n0) and self._gate_ok(sm.n1)
                        and sm.n1.direction is _opposite(sm.n0.direction)
                        and sm.n1.start_bi == sm.n0.end_bi + 1):
                    break
                next_begin = sm.n1.end_bi + 1
                next_dir = _opposite(sm.n1.direction)
                sm.confirm_gap_revert(evidence_bi, self.bis[evidence_bi].end_ts)
                # 链式 seed 下一 soft N0 = [next_begin, peak_bi] (peak_bi = 反向分型 e1 极值端点)。
                if (peak_bi - next_begin >= 2 and self.bis[next_begin].direction is next_dir
                        and self.bis[peak_bi].direction is next_dir):
                    sm.promote_to_n0(_XianduanCand(
                        start_bi=next_begin, end_bi=peak_bi, direction=next_dir,
                        start_key=self._start_key(next_begin, next_dir),
                        end_key=self._end_key(peak_bi, next_dir), rule="feature_seq", dep=peak_bi,
                    ))
                    continue
                # seed 端点退化 (不足3笔/端点方向不符) → 无法 seed → 交兜底 forming。
                break
            else:  # "none": 扫到尾未决 → N1 仍 pending (末段)
                break
        return self._emit(sm)

    # ── 候选生成 (特征序列内核; 不做冻结判定) ─────────────────────────────────────

    def _candidate(self, begin: int, xianduan_dir: BiDir) -> _XianduanCand | None:
        """从 begin 起、方向 xianduan_dir, 喂反向笔成特征序列, **首个分型 → 一个候选** (不冻结)。

        候选 = 原文第一种(无缺口)/第二种(有缺口)产生的线段候选; 冻结时机交 N0/N1/N2 状态机。
        返回 _XianduanCand (含 start_key/end_key 供击破判定 + rule/dep 供输出), 无分型 → None。
        """
        n = len(self.bis)
        feat_dir = _opposite(xianduan_dir)
        fx = _EigenFX(xianduan_dir, self.bis)
        i = begin
        while i < n:
            if self.bis[i].direction is feat_dir and fx.add(i):
                end_bi = fx.peak_end_bi_idx()
                # 候选须 ≥3 笔且**端点为段内真极值** (B5 自洽); 否则是子顶/子底 → 重起特征序列
                # 从该分型后继续扫更深分型 (第八种"段内更极值", 直到端点是真极值)。
                if (
                    end_bi - begin >= 2
                    and self._extreme_problem(begin, end_bi, xianduan_dir) is None
                ):
                    dep = fx.last_evidence if fx.last_evidence is not None else end_bi
                    rule = "gap" if fx.has_gap() else "feature_seq"
                    return _XianduanCand(
                        start_bi=begin, end_bi=end_bi, direction=xianduan_dir,
                        start_key=self._start_key(begin, xianduan_dir),
                        end_key=self._end_key(end_bi, xianduan_dir),
                        rule=rule, dep=dep,
                    )
                fx = _EigenFX(xianduan_dir, self.bis)  # 子顶/子底 → 延伸, 从 end_bi+1 重扫
                i = end_bi
            i += 1
        return None

    def _first_new_extreme(
        self, n0: _XianduanCand, begin: int, limit: int
    ) -> tuple[int, float] | None:
        """[begin, limit] 内**首个严格超过 N0 端点极值**的本段方向笔 (上涨首个新高/下跌首个新低)。

        增量延伸: 延伸到首个新极值后由主循环重新找反向; 仅在 N0 方向真创新极值时触发 (合法反向段
        的 highs/lows 不会越过 N0 端点, 故不会误延伸过真反向段)。
        """
        hi = min(limit, len(self.bis) - 1)
        for i in range(begin, hi + 1):
            b = self.bis[i]
            if b.direction is not n0.direction:
                continue
            if n0.direction is BiDir.UP and b.high > n0.end_key:
                return i, b.high
            if n0.direction is BiDir.DOWN and b.low < n0.end_key:
                return i, b.low
        return None

    def _start_key(self, bi: int, d: BiDir) -> float:
        """起点关键价位 (N1 击破判据): 上涨段 = 起点 low / 下跌段 = 起点 high。"""
        return self.bis[bi].low if d is BiDir.UP else self.bis[bi].high

    def _end_key(self, bi: int, d: BiDir) -> float:
        """终点极值: 上涨段 = 终点 high / 下跌段 = 终点 low。"""
        return self.bis[bi].high if d is BiDir.UP else self.bis[bi].low

    def _breaks_start_key(self, n0: _XianduanCand, bi_idx: int) -> bool:
        """单笔 ``bi_idx`` 是否**严格**破坏 N0 起点关键极值 (触平不算; 对齐 ``is_n1_broken``)。

        上涨 N0 (start_key=起点 low): 反向下降笔 ``low < start_key`` → 破;
        下降 N0 (start_key=起点 high): 反向上升笔 ``high > start_key`` → 破。
        """
        b = self.bis[bi_idx]
        if n0.direction is BiDir.UP:
            return b.low < n0.start_key
        return b.high > n0.start_key

    def _try_strong_bi_break(self, prev_seg: _XianduanCand) -> _XianduanCand | None:
        """strong_bi 两阶段确认: 试把 ``prev_seg`` 之后首根反向单笔拆成 strong_bi 单笔段候选。

        ``prev_seg`` = 被破坏的前一段 (在 ``sm.n1 is None`` 处 = 当前 soft N0; 在 ``_advance_n0n1``
        生成 N2 处 = 当前 pending N1)。条件 (全满足才产出, 否则 None → 回退标准候选):
        - 首根反向笔 ``s = prev_seg.end_bi + 1`` 方向与 ``prev_seg`` 反向 (反向单笔);
        - ``s`` **严格破坏** ``prev_seg`` 起点关键极值 (``_breaks_start_key``; 强势破坏, 触平不算);
        - **阶段2 前置**: 紧接 ``s`` 之后形成一条对该单笔的**反向标准线段** =
          ``_candidate(s+1, prev_seg.direction)`` 且其起点 == ``s+1`` (连续)。该反向标准段是标准
          确认证据; 单笔本身由状态机 ``confirm_on_n2`` 两滞后冻结, **不立即确认**; 反向标准段
          不成形则返回 None (回退 → 单笔不自成段, 走 T7 吸收 / 标准流程)。

        返回 strong_bi 单笔候选 (start==end==s, 方向 = prev_seg 反向, rule="strong_bi"); dep 取反向
        标准段依赖水位。cutoff 安全: 反向标准段未到齐时 ``_candidate`` 返回 None → 不产出。
        """
        s = prev_seg.end_bi + 1
        if s >= len(self.bis):
            return None
        d = _opposite(prev_seg.direction)
        if self.bis[s].direction is not d:  # 首根须是反向单笔
            return None
        if not self._breaks_start_key(prev_seg, s):  # 须强势破坏 prev_seg 起点关键极值
            return None
        rev_std = self._candidate(s + 1, prev_seg.direction)  # 阶段2 前置: 紧接反向标准线段
        if rev_std is None or rev_std.start_bi != s + 1:
            return None
        return _XianduanCand(
            start_bi=s, end_bi=s, direction=d,
            start_key=self._start_key(s, d), end_key=self._end_key(s, d),
            rule="strong_bi", dep=rev_std.dep,
        )

    def _revert_confirm(self, seg_dir: BiDir, peak_end_bi: int) -> tuple[int, int] | None:
        """缺口第二种反向确认 (第67课第二种 / §16 v10)。

        从 ``peak_end_bi+2`` 起, 在**反向方向**建第二特征序列 (``_SeqRole.GAP_REVERT``, 合并值判
        分型、无前看); **首个**反向分型 → 返回 ``(evidence_bi, peak_bi)``:
        - ``evidence_bi`` = 反向分型 ``last_evidence`` 笔下标 (证据水位);
        - ``peak_bi`` = 反向序列 ``peak_end_bi_idx()`` = 第二特征序列**中间元素 e1 极值端点** → 用作
          gap_revert **链式 seed 的下一段 (反向 seg_dir) 候选终点** (G-a; 用户 2026-07-09)。
        扫到尾无分型 → None。**不递归**: 第二特征序列自身即使有缺口, 只要形成分型即确认 (原文第67课:
        第二个序列的分型不分第一/二种情况)。方向: 反向序列方向 = ``peak_end_bi+2`` 笔方向的反向
        (镜像 chan ``find_revert_fx``: ``revert_bi_dir(bi_list[begin].dir)``)。
        """
        begin = peak_end_bi + 2
        n = len(self.bis)
        if begin >= n:
            return None
        rev_dir = _opposite(seg_dir)  # 反向序列线段方向 = 被确认段(seg_dir)的反向 = 下一段方向
        if self.bis[begin].direction is not seg_dir:
            return None  # 守护: peak+2 笔方向应与被确认段同向 (镜像 chan); 否则数据退化
        fx = _EigenFX(rev_dir, self.bis, sequence_role=_SeqRole.GAP_REVERT)
        i = begin
        while i < n:
            if self.bis[i].direction is seg_dir and fx.add(i):  # 只喂 seg_dir 笔 (rev 序列的反向笔)
                ev = fx.last_evidence if fx.last_evidence is not None else i
                return ev, fx.peak_end_bi_idx()  # 证据笔 + e1 peak (下一段候选终点)
            i += 1
        return None

    def _second_sequence_elements(self, seg_dir: BiDir, peak_end_bi: int) -> list[_Eigen]:
        """只读显示辅助 (xianduan-v1 §16 v10 显示层「第二特征序列」, 用户 2026-07-10 Commit C)。

        复现 ``_revert_confirm`` 同一驱动 (同一 ``_EigenFX`` 类 + ``GAP_REVERT`` 规则 + 同一喂入
        循环), 返回其累积的特征元素 —— **与算法确认逻辑同源, 不重新实现合并规则**（根因：显示层
        此前用另一套简化规则模拟"第二序列", 与算法真实判分型逻辑语义不一致, 曾致 bi416-424 排查
        反复误判, 详模块 banner「三类显示单元」）。

        分型形成后即停 (定格 e0/e1/e2, 与 ``_revert_confirm`` 返回时刻一致); 扫到尾未形成分型时
        返回当前累积的部分元素 (调试可见"正在生长")。独立 ``_EigenFX`` 实例, 不与 ``_revert_
        confirm`` 共享可变状态、不影响其行为。
        """
        begin = peak_end_bi + 2
        n = len(self.bis)
        if begin >= n or self.bis[begin].direction is not seg_dir:
            return []
        rev_dir = _opposite(seg_dir)
        fx = _EigenFX(rev_dir, self.bis, sequence_role=_SeqRole.GAP_REVERT)
        i = begin
        while i < n:
            if self.bis[i].direction is seg_dir and fx.add(i):
                break
            i += 1
        return [e for e in fx.ele if e is not None]

    # ── N2 出现 vs N1 击破 (先到先判) ─────────────────────────────────────────────

    def _advance_n0n1(self, sm: _XianduanFreezeMachine) -> tuple:
        """有 N0+N1 时推进一步, 返回 verdict (顺序: N1 延伸 → N2 成败裁决 → 未决):

        核心裁决 (用户 2026-06-26): **「N1 起点被击破」≠「N1 立即失败」**。击破笔本就是 N2 的起点
        (N2 与 N0 同向、与 N1 反向, 天然越过 N1 起点)。故击破后**先给 N2 成长机会**:
        - N2 = `_candidate(N1.end+1, N0向)` **非 None** (起点即段内极值且 B5 自洽) → **N2 成功**:
          N1 成立, N0 冻结 (`confirm`)。`_candidate` 起点极值自检 = 「N2 连续成长」判据, 不会远跳。
        - N2 **为 None** (起点被反向越过, 价格反转回 N1 向) 且 N1 起点确被严格击破 → **N2 失败**
          (第五种假反向): 作废 N1, N0 延伸到击破后同向真实极值 (`break`)。
        - N2 为 None 且无明确击破 → 未决 (`none`): 保持 N0 soft + N1 pending, **不提前冻结**。

        verdict: ('extend_n1',end,key) / ('confirm',n2) / ('break',end,key) / ('none',)。
        """
        assert sm.n0 is not None and sm.n1 is not None
        n0dir = sm.n0.direction
        n1 = sm.n1
        n = len(self.bis)
        begin = n1.end_bi + 1
        n2 = self._candidate(begin, n0dir)
        # ① N1 子顶/子底延伸 (B5 守护): N1 创新极值且 [起点,新极值] 仍 B5 自洽 (起点未被破) → 延伸
        #    (第八种段内更极值)。先于裁决, 让 N1 长到真极值再判确认。
        #    strong_bi 单笔段**恒不延伸** (单笔段几何 = 破坏单笔本身, 用户 2026-07-10 Q2)。
        limit = n2.end_bi if n2 is not None else n - 1
        if n1.rule != "strong_bi":
            ext = self._first_new_extreme(n1, begin, limit)
            if ext is not None and self._extreme_problem(n1.start_bi, ext[0], n1.direction) is None:
                return ("extend_n1", ext[0], ext[1])
        # 击破/反转证据 (两类 N1 共用; 供确认 vs 失效的 evidence index 先后裁决)。
        brk = self._first_break(n1, begin, n - 1)
        rev = self._first_new_extreme(n1, begin, n - 1)  # 反向回 N1 向的极值 = 失效证据
        # ② 确认裁决 (用户 2026-07-09 最终口径, 见 §16 v10):
        #    缺口第二种情况本质 = **缺口段不得在无反向结构证据时确认**。反向结构证据分两级:
        #      · **完整反向线段 N2** (更强证据, 内含反向特征序列分型背书);
        #      · **裸反向特征序列分型 gap_revert** (末端/cutoff N2 未形成、但反向分型已完成的卡住)。
        #    中段历史数据: 后续已形成完整 N2 → 仍按 N2/两滞后状态机确认缺口段, **保持现有稳定分段**;
        #    **不因裸分型更早出现就强行改用 atomic gap_revert** (atomic 在触平边界与两滞后发散、噪声
        #    数据会崩塌)。末端无 N2 但裸分型已完成 → 落 ④ gap_revert 补全。
        #    "N2 确认非绕过第二种": N2 ⊃ 裸反向分型 (完整反向段必含反向分型背书); 全 frozen 缺口段有
        #    第二序列背书由 test_all_frozen_gap_segments_have_second_sequence_backing 硬证。
        #    strong_bi 变体 (xianduan-practical-v1 §16, 用户 2026-07-10): 即将确认 N1 时, 若 N1
        #    之后首根笔是**强势破坏 N1 起点的反向单笔**且其后紧接反向标准段 → 用 strong_bi 单笔段作
        #    N2 (把 N1 之后本会长成的标准反向段细化为「单笔 strong 段 + 反向标准段」; 单笔破坏可级联
        #    ——单笔成不了标准段, 故**不要求** standard n2 存在, 只需反向标准段前置)。仅 strong_bi
        #    开; 严格 standard 不触发 → golden 零回归。单笔由后续 confirm_on_n2 两滞后冻结。
        if self.strong_bi:
            strong = self._try_strong_bi_break(n1)
            if strong is not None:
                return ("confirm", strong)
        if n2 is not None:
            return ("confirm", n2)
        # ③ 确认未成 + **双证据**击破 (实时生长防误判, 用户 2026-06-26): ① N1 起点被严格击破 +
        #    ② 后续已反向走回 N1 方向 (创越 N1 终点极值)。仅有击破不够 (刚击破时确认序列仍在生长)。
        if brk is not None and rev is not None:
            new_end, new_key = self._extend_extreme(sm.n0, rev[0])  # N0 延伸到反转点前真实极值
            # 守护: 延伸后 N0 仍须 B5 自洽。若 N1 已**越过 N0 起点** (上涨 N0 段内现更低 low / 下跌
            # 现更高 high) → 延伸会造 B5 反画。此时 N1 是真强反向、N0 已完结 → T6 转接 (冻结 N0,
            # N1 升 N0), 不作废 N1。否则 N1 是假反向 (第五种) → T4+T5 作废+延伸。
            if self._extreme_problem(sm.n0.start_bi, new_end, sm.n0.direction) is not None:
                return ("rollover",)
            return ("break", new_end, new_key)
        # ④ 缺口第二种反向确认 (§16 v10, **末端卡住缺口段兜底**): N2 未成形 + 无 break/rollover 时,
        #    缺口候选从 peak+2 起第二特征序列 (GAP_REVERT 合并值) 出反向分型 → gap_revert 原子冻结
        #    N0+N1 + G-a 链式 seed。仅救 N2 不成形而卡 pending 的末端缺口段 (锚点 bi416-424)。
        if n1.rule == "gap":
            rc = self._revert_confirm(n1.direction, n1.end_bi)
            if rc is not None and (brk is None or rc[0] <= brk):
                return ("gap_revert", rc[0], rc[1])
        # ⑤ 未决 (确认序列仍在生长 / 无击破): N0 soft + N1 pending, 等后续数据生长。
        return ("none",)

    def _first_break(self, n1: _XianduanCand, begin: int, limit: int) -> int | None:
        """[begin, limit] 内**严格击破** N1 起点关键价位的首笔下标 (触平不算; None=未破)。

        上涨 N1: 后续笔 low < 起点 low → 破; 下跌 N1: 后续笔 high > 起点 high → 破。
        """
        up = n1.direction is BiDir.UP
        for i in range(begin, min(limit, len(self.bis) - 1) + 1):
            b = self.bis[i]
            if (up and b.low < n1.start_key) or (not up and b.high > n1.start_key):
                return i
        return None

    def _extend_extreme(self, n0: _XianduanCand, limit: int) -> tuple[int, float]:
        """N0 延伸目标 = [N0.end, limit] 内本段方向真极值笔 (下跌取最低 low / 上涨取最高 high)。

        N1 作废后 N0 吞掉假反弹+击破区到新极值; 终点取本段方向笔, 保证延伸后端点仍为方向极值。
        """
        lo, hi = n0.end_bi, min(limit, len(self.bis) - 1)
        rng = [i for i in range(lo, hi + 1) if self.bis[i].direction is n0.direction]
        if not rng:
            rng = list(range(lo, hi + 1))
        if n0.direction is BiDir.DOWN:
            e = min(rng, key=lambda i: self.bis[i].low)
            return e, self.bis[e].low
        e = max(rng, key=lambda i: self.bis[i].high)
        return e, self.bis[e].high

    def _gate_ok(self, n0: _XianduanCand) -> bool:
        """冻结硬闸: 标准段须过 `_basic_valid` (≥3笔/奇数/首尾同向/首三笔重合) **且** B5 端点极值;
        `pen_break_absorb` 段 (T7 笔破坏失败吸收) **豁免 B5**, 只查 `_basic_valid`。"""
        if n0.rule == "strong_bi":
            # 单笔 strong_bi 段 (实战变体, 用户确认非原文≥3; xianduan-practical-v1 §16): 豁免
            # B1/B3 (≥3/单数) 与 B2 (首三重合) 与 B5 —— 只需是那根反向破坏单笔 (start==end, 方向
            # 正确)。破坏 N0 起点 + 反向 N2 前置已在 _try_strong_bi_n1 校验。
            return (n0.start_bi == n0.end_bi
                    and self.bis[n0.start_bi].direction is n0.direction)
        if not self._basic_valid(n0.start_bi, n0.end_bi, n0.direction):
            return False
        if n0.rule == "pen_break_absorb":  # 吸收段允许内部越点, B5 不作硬闸
            return True
        return self._extreme_problem(n0.start_bi, n0.end_bi, n0.direction) is None

    def _pen_break_bi(self, n0: _XianduanCand, begin: int, end: int) -> int:
        """吸收段内部**越过 N0 起点**最极端的笔下标 (失败笔破坏点; 上取最低/下取最高)。"""
        up = n0.direction is BiDir.UP
        best_i, best_v = begin, None
        for i in range(begin, end + 1):
            b = self.bis[i]
            v = b.low if up else b.high
            broke = (v < n0.start_key) if up else (v > n0.start_key)
            if broke and (best_v is None or (v < best_v if up else v > best_v)):
                best_i, best_v = i, v
        return best_i

    # ── 首段定向 (暖机头 B5 锁定; 候选制) ────────────────────────────────────────

    def _first_xianduan(self) -> tuple[int, BiDir] | None:
        """首段起点+方向: 跳过暖机头, 取**首个能成 (合法候选 + 合法反向候选) 对**的起点。

        暖机头常有单笔强势/方向不定 (第五种"中间地带"), 无法成稳定链 → 右移起点直到一个段及其
        反向段都成合法候选 (链能继续生长)。其前的暖机笔留空 (用户允许)。返回 (begin, dir) 或 None。
        """
        n = len(self.bis)
        for begin in range(n):
            d = self.bis[begin].direction
            c = self._candidate(begin, d)
            if c is None:
                continue
            rev = self._candidate(c.end_bi + 1, _opposite(d))
            if rev is not None:
                return begin, d
        return None

    def _basic_valid(self, start: int, end: int, xianduan_dir: BiDir) -> bool:
        """基础硬约束 (第77课): ≥3 笔 (B1) + 含笔数单数 (B3) + 首尾同向 + 首三笔重合 (B2)。"""
        cnt = end - start + 1
        if cnt < 3 or cnt % 2 == 0:
            return False
        if (
            self.bis[start].direction is not xianduan_dir
            or self.bis[end].direction is not xianduan_dir
        ):
            return False
        three = self.bis[start : start + 3]
        return max(b.low for b in three) <= min(b.high for b in three)

    def _extreme_problem(self, start: int, end: int, xianduan_dir: BiDir) -> str | None:
        """端点极值校验 (第77课 B5 / 第八种情况): 上升线段段内不得有低于起点的 low、终点须为
        段内最高; 下降线段段内不得有高于起点的 high、终点须为段内最低。

        返回 ``"start"`` (起点不是段内极值) / ``"end"`` (终点不是段内极值) / ``None`` (合法)。
        """
        xianduan = self.bis[start : end + 1]
        if xianduan_dir is BiDir.UP:
            if any(b.low < self.bis[start].low for b in xianduan):
                return "start"  # 段内有更低 low → 起点不是真底
            if any(b.high > self.bis[end].high for b in xianduan):
                return "end"  # 段内有更高 high → 终点不是真顶
        else:
            if any(b.high > self.bis[start].high for b in xianduan):
                return "start"
            if any(b.low < self.bis[end].low for b in xianduan):
                return "end"
        return None

    # ── 输出: frozen(实线) / soft N0(软实线) / pending N1(虚线) + 末尾兜底 (方案 A) ──

    def _emit(self, sm: _XianduanFreezeMachine) -> list[_WorkXianduan]:
        """状态机 → _WorkXianduan 列表 (方案 A 显示口径)。

        frozen → FROZEN(实线 confirmed); soft N0 → SOFT_N0(软实线, 未冻结); pending N1 →
        PENDING_N1(虚线)。无 N1 时 N0 之后的反向边出一条 forming 虚线 (终点取该向极值笔)。
        连续性: 各段起点恒 = 上段 end+1, 无内部 gap; 左侧暖机头允许留空。
        """
        n = len(self.bis)
        out: list[_WorkXianduan] = []
        for fz in sm.frozen:
            out.append(_WorkXianduan(fz.start_bi, fz.end_bi, fz.direction, fz.rule, fz.dep,
                                XianduanFreezeState.FROZEN, pen_break_at=fz.pen_break_at,
                                confirmation_ts=fz.confirmation_ts, frozen_by=fz.frozen_by))
        if sm.n0 is not None:
            out.append(_WorkXianduan(
                sm.n0.start_bi, sm.n0.end_bi, sm.n0.direction, sm.n0.rule,
                sm.n0.dep, XianduanFreezeState.SOFT_N0, pen_break_at=sm.n0.pen_break_at,
            ))
        if sm.n1 is not None:
            # pending N1 (唯一右缘 forming): 终点延伸到该向**最新极值** (覆盖到右缘附近, driver 在
            # 震荡区提前停时不留大段空白; 仍是单条 forming 虚线, 满足"最右最多一条 forming")。
            fe = self._forming_end(sm.n1.start_bi, sm.n1.direction)
            n1_end = max(sm.n1.end_bi, fe)
            out.append(_WorkXianduan(
                sm.n1.start_bi, n1_end, sm.n1.direction, "forming",
                sm.n1.dep, XianduanFreezeState.PENDING_N1,
            ))
        elif sm.n0 is not None and sm.n0.end_bi + 1 < n:  # 无 N1 → N0 之后反向边一条 forming 虚线
            start = sm.n0.end_bi + 1  # N0 收在末笔时无尾段可画 (start < n 守护)
            d = _opposite(sm.n0.direction)
            end = self._forming_end(start, d)
            if end >= start:
                out.append(_WorkXianduan(
                    start, end, d, "forming", n - 1, XianduanFreezeState.PENDING_N1
                ))
        elif sm.n0 is None and sm.n1 is None and sm.frozen and sm.frozen[-1].end_bi + 1 < n:
            # gap_revert 后无新 N0 候选 (末段反向段尚未成候选) → 从最后 frozen 段后画一条 forming
            # (反向方向), 保证连续覆盖到末笔、右缘不留空档。
            start = sm.frozen[-1].end_bi + 1
            d = _opposite(sm.frozen[-1].direction)
            end = self._forming_end(start, d)
            if end >= start:
                out.append(_WorkXianduan(
                    start, end, d, "forming", n - 1, XianduanFreezeState.PENDING_N1
                ))
        if not out and n >= 1:  # 完全无法定向 → 整窗一条 forming
            d = self.bis[0].direction
            end = self._forming_end(0, d)
            out.append(_WorkXianduan(0, end, d, "forming", n - 1, XianduanFreezeState.PENDING_N1))
        return out

    def _forming_end(self, start: int, xianduan_dir: BiDir) -> int:
        """forming 末段终点笔 = 暂定极值的**同向笔** (上涨段取最高 high 的上涨笔 / 下跌段取最低
        low 的下跌笔)。保证 forming 终点落在本段方向的极值上 (用户 2026-06-21), 而非末笔。"""
        same = [i for i in range(start, len(self.bis)) if self.bis[i].direction is xianduan_dir]
        if not same:
            return start  # 无同向笔 (退化) → 起点自身
        if xianduan_dir is BiDir.UP:
            return max(same, key=lambda i: self.bis[i].high)
        return min(same, key=lambda i: self.bis[i].low)


# ── _WorkXianduan → Xianduan (含轻量 trace, source/merged_range 从构成笔聚合) ──────────────

_RULE_FSEQ = {BiDir.UP: RULE_XIANDUAN_UP_FSEQ, BiDir.DOWN: RULE_XIANDUAN_DOWN_FSEQ}
_RULE_GAP = {BiDir.UP: RULE_XIANDUAN_UP_GAP, BiDir.DOWN: RULE_XIANDUAN_DOWN_GAP}
_RULE_TAIL = {BiDir.UP: RULE_XIANDUAN_UP_TAIL, BiDir.DOWN: RULE_XIANDUAN_DOWN_TAIL}
_RULE_EXTREME_SPLIT = {
    BiDir.UP: RULE_XIANDUAN_UP_EXTREME_SPLIT, BiDir.DOWN: RULE_XIANDUAN_DOWN_EXTREME_SPLIT
}
_RULE_NONSTANDARD_REPAIR = {
    BiDir.UP: RULE_XIANDUAN_UP_NONSTANDARD_REPAIR, BiDir.DOWN: RULE_XIANDUAN_DOWN_NONSTANDARD_REPAIR
}
_RULE_TAIL_EXTEND = {
    BiDir.UP: RULE_XIANDUAN_UP_TAIL_EXTEND, BiDir.DOWN: RULE_XIANDUAN_DOWN_TAIL_EXTEND
}
_RULE_FORMING = {BiDir.UP: RULE_XIANDUAN_UP_FORMING, BiDir.DOWN: RULE_XIANDUAN_DOWN_FORMING}

_RULE_MAP = {
    "gap": _RULE_GAP,
    "tail": _RULE_TAIL,
    "extreme_split": _RULE_EXTREME_SPLIT,
    "nonstandard_repair": _RULE_NONSTANDARD_REPAIR,
    "tail_extend": _RULE_TAIL_EXTEND,
    "forming": _RULE_FORMING,
    "pen_break_absorb": {
        BiDir.UP: RULE_XIANDUAN_UP_PEN_BREAK_ABSORB, BiDir.DOWN: RULE_XIANDUAN_DOWN_PEN_BREAK_ABSORB
    },
    "strong_bi": {
        BiDir.UP: RULE_XIANDUAN_UP_STRONG_BI_BREAK, BiDir.DOWN: RULE_XIANDUAN_DOWN_STRONG_BI_BREAK
    },
}


def _rule_for(direction: BiDir, rule_kind: str) -> str:
    return _RULE_MAP.get(rule_kind, _RULE_FSEQ)[direction]


def _finish(
    bis: list[Bi], work: list[_WorkXianduan], *, profile_id: str, config_hash: str
) -> list[Xianduan]:
    out: list[Xianduan] = []
    for w in work:
        first, last = bis[w.start_bi], bis[w.end_bi]
        members = bis[w.start_bi : w.end_bi + 1]
        high = max(b.high for b in members)
        low = min(b.low for b in members)
        # source/merged_range 从构成笔 trace 聚合 (§1.7); 端点笔无 trace 时回退端点 ts。
        src_from = _src_from(first)
        src_to = _src_to(last)
        merged_from = first.trace.merged_from_index if first.trace else None
        merged_to = last.trace.merged_to_index if last.trace else None
        trace = StructTrace(
            algo_card_id=_ALGO_CARD_ID,
            rule_id=_rule_for(w.direction, w.rule_kind),
            profile_id=profile_id,
            config_hash=config_hash,
            source_from_ts=src_from,
            source_to_ts=src_to,
            merged_from_index=merged_from,
            merged_to_index=merged_to,
            dep_to_index=w.dep_index,
            freeze_state=w.freeze_state.value,
            pen_break_at=w.pen_break_at,
            confirmation_ts=w.confirmation_ts,
            frozen_by=w.frozen_by,
        )
        out.append(
            Xianduan(
                period=first.period,
                direction=w.direction,
                start_ts=first.start_ts,
                end_ts=last.end_ts,
                start_price=first.start_price,
                end_price=last.end_price,
                high=high,
                low=low,
                trace=trace,
            )
        )
    return out


def _src_from(bi: Bi) -> int:
    if bi.trace and bi.trace.source_from_ts is not None:
        return bi.trace.source_from_ts
    return bi.start_ts


def _src_to(bi: Bi) -> int:
    if bi.trace and bi.trace.source_to_ts is not None:
        return bi.trace.source_to_ts
    return bi.end_ts


# ══════════════════════════════════════════════════════════════════════════════
# 特征序列显示层 (只读调试; 纯显示, 不进算法口径 / config_hash / 信号 / 回测)
# ──────────────────────────────────────────────────────────────────────────────
# UI「显示特征序列」用: 复用线段特征序列内核 (_Eigen / _XianduanBuilder) 只读产出每个线段的特征
# 元素, 供前端画矩形框。**不改 build_xianduans 输出语义 / 不改 get_xianduans 结构结果** —— 只重跑
# 同一 _XianduanBuilder 拿各段笔下标区间, 再对每段按第65课包含处理把反向笔合并成特征元素。
#
# 语义 (第65/67课, xianduan-v1 §6): 特征序列 = 线段的**反向笔**当特征 K 线 —— 上涨线段看**下降**
# 特征序列、下降线段看**上涨**特征序列 (feature_direction = 线段方向的反向)。这是「特征序列」原
# 定义, **不是新线段口径**; UI 名仍叫「特征序列」, 不引入新 profile / 不动 chan JSON。
#
# **三类显示单元 (xianduan-v1 §16 v10 显示层根因修复, 用户 2026-07-10 Commit C)**: 早期把「第二
# 特征序列」与「tail 同向临时探测」都叫 ttz、语义混用, 曾导致排查时把 tail 滑动编号误读为"有效
# 反向分型"。现彻底分名、三类互不复用前缀:
# - ``PRIMARY``    tz{n}: 每段(含当下未完成段)的**反向笔**特征序列 (第65/67课标准定义), 编号跨
#                  完整序列连续稳定。
# - ``SECOND``     ttz{n}: **缺口第二种反向确认用的第二特征序列**, 与算法 `_revert_confirm` 同源
#                  (复用同一 `_EigenFX(GAP_REVERT)` 驱动, 非重新实现合并规则) —— 只对 frozen 且
#                  `rule_kind=="gap"` 的段产出 (即 `test_all_frozen_gap_segments_have_second_
#                  sequence_backing` 保证非空的段)。编号**每个缺口事件局部从 0 起**(ttz0=e0/
#                  ttz1=e1/ttz2=e2), 多个缺口事件的 ttz0/1/2 会重复出现——用 id (ts 派生) 区分,
#                  不靠编号唯一 (对齐 tz/tp 的"id 稳定、编号仅显示便利"惯例)。
# - ``TAIL_PROBE`` tp{n}: 右缘尚未画出线段虚线的**同向笔**临时探测 (归属假想的下一段), 仅调试、
#                  不参与任何确认判定; 画出虚线后本轮作废重算 (不稳定)。**不再叫 ttz**, 与第二
#                  特征序列彻底分开、避免重蹈两者语义混用的根因。
# ══════════════════════════════════════════════════════════════════════════════


class FeatureSeqKind(StrEnum):
    """特征序列显示单元类别 (纯显示, 不进算法/hash; 见上方模块banner「三类显示单元」)。"""

    PRIMARY = "primary"        # tz: 每段标准反向特征序列
    SECOND = "second"          # ttz: 缺口第二种第二特征序列 (与 _revert_confirm 同源)
    TAIL_PROBE = "tail_probe"  # tp: 右缘同向笔临时探测 (原误称 ttz, 已分名)


@dataclass(frozen=True, slots=True)
class FeatureSeqUnit:
    """单个特征元素 (经包含合并) 的只读显示单元 —— 一个矩形框。

    ``direction``          所属线段方向 (上涨段 / 下降段)。
    ``feature_direction``  特征元素的笔方向 (= 线段方向的反向; 上涨段看下降特征、下降段看上涨特征)。
    ``start_bi_index/end_bi_index``  该特征元素合并所含的首/末笔下标 (完整笔序列中的位置)。
    ``start_ts/end_ts``    首笔起点 ts / 末笔终点 ts (矩形横跨, 绘图点)。
    ``source_from_ts/source_to_ts``  构成笔实际依据的原始 K 线 ts 跨度 (从构成笔 trace 聚合, 同
                           线段/笔): 供 D4-A valid 整体落入判定 (来源跨左缘暖机区的框不画, 不能用
                           绘图点保守回退 —— 特征序列是笔/线段派生的结构化项, 非合并 K 线原始框)。
    ``high/low``           特征元素 (合并后) 的高/低 (矩形纵跨)。
    ``global_index``       序内生成顺序编号: ``PRIMARY`` 跨完整序列连续稳定 → tz{n}; ``SECOND``
                           每个缺口事件局部从 0 起 → ttz{n} (id 才是跨事件唯一锚); ``TAIL_PROBE``
                           自成一套局部计数 → tp{n} (不稳定, 后续可作废重排)。
    ``kind``               三类之一, 见 ``FeatureSeqKind`` (模块 banner「三类显示单元」)。
    """

    direction: BiDir
    feature_direction: BiDir
    start_bi_index: int
    end_bi_index: int
    start_ts: int
    end_ts: int
    high: float
    low: float
    source_from_ts: int
    source_to_ts: int
    global_index: int
    kind: FeatureSeqKind = FeatureSeqKind.PRIMARY


def _feature_elements(
    bis: list[Bi], start_bi: int, end_bi: int, seg_dir: BiDir, feat_dir: BiDir
) -> list[_Eigen]:
    """段内特征序列的特征元素 (标准包含处理, 复用 ``_Eigen``; 只读, 不参与冻结判定)。

    只取段内**反向笔** (``feat_dir``) 当特征 K 线, 按第65课包含处理顺序合并: 相互包含即合并
    (``combine``), 非包含处成新元素分界。合并取值随**线段方向** (上升取高高 / 下降取低低, 与
    ``_EigenFX`` 一致)。相比 ``_EigenFX`` 只保留标准三元素分型窗口的差别: 这里为展示遍历整段所有
    反向笔, 不做 exclude / 前看 / 分型判定 —— 显示的是「特征序列」本身, 非线段确认逻辑。
    """
    elements: list[_Eigen] = []
    cur: _Eigen | None = None
    for i in range(start_bi, end_bi + 1):
        if bis[i].direction is not feat_dir:
            continue
        if cur is None:
            cur = _Eigen.of(seg_dir, i, bis[i])
            continue
        if cur.test_combine(bis[i], exclude_included=False, allow_top_equal=None) == "combine":
            cur.merge(i, bis[i])
        else:
            elements.append(cur)
            cur = _Eigen.of(seg_dir, i, bis[i])
    if cur is not None:
        elements.append(cur)
    return elements


def build_feature_sequence_overlays(bis: list[Bi], cfg: ChanConfig) -> list[FeatureSeqUnit]:
    """只读调试: 每条线段(含当下未完成段)+右缘未画段区的特征序列元素 (供前端画框); 稳定全局编号。

    与 ``build_xianduans`` 共用同一 ``_XianduanBuilder`` (同 cfg → 同分段), 故特征序列与图上显示
    的线段严格对应。覆盖三类区域 (用户 2026-07-08), 产三种单元 (``FeatureSeqKind``, 模块 banner
    「三类显示单元」):
    - ``PRIMARY`` (tz): 已完成 (frozen) 线段内 + 当下未完成线段 (soft_n0/pending_n1/forming) 的
      段内反向笔特征序列; 最后一个 work item 延伸到 ``len(bis)-1`` 覆盖右缘 tail。
    - ``SECOND`` (ttz): frozen 且 ``rule_kind=="gap"`` 的段, 与 ``_revert_confirm`` 同源产出的
      第二特征序列 (每缺口事件局部编号 0 起)。
    - ``TAIL_PROBE`` (tp): 没有画线段虚线的当下 (最后一个 work item 之后到最新笔) 的**同向笔**
      临时探测。左侧暖机头(首个 work item 之前)无段, 不显示(非"当下")。

    ``global_index``: ``PRIMARY`` 按 (线段顺序, 段内特征元素顺序) 基于**完整** engine 笔序列连续
    赋值, 调用方随后窗口裁剪只影响返回哪些框、不重排编号 (对齐 ``attach_bi_labels`` 纪律);
    ``SECOND``/``TAIL_PROBE`` 各自局部计数 (见 ``FeatureSeqUnit.global_index`` 字段说明)。

    cutoff / 回放下天然安全: ``bis`` 只含 ``<= cutoff_ts`` 的 K 线派生结果, 不偷看未来。
    """
    if len(bis) < 3:
        return []
    cfg = cfg.normalize()
    builder = _XianduanBuilder(
        bis,
        nonstandard=cfg.xianduan_nonstandard_policy is XianduanNonstandardPolicy.REPAIR,
        oscillation=cfg.xianduan_oscillation_policy is XianduanOscillationPolicy.THREE_BI,
    )
    work = builder.run()
    n = len(bis)
    out: list[FeatureSeqUnit] = []
    gi = 0
    last_wi = len(work) - 1
    for wi, w in enumerate(work):
        feat_dir = _opposite(w.direction)
        # 最后一段延伸到最新笔: 覆盖当下未画线段虚线的 tail (正在生长的反向特征序列 tz)。
        span_end = n - 1 if wi == last_wi else w.end_bi
        for e in _feature_elements(bis, w.start_bi, span_end, w.direction, feat_dir):
            first_bi, last_bi = bis[e.idxs[0]], bis[e.idxs[-1]]
            out.append(
                FeatureSeqUnit(
                    direction=w.direction,
                    feature_direction=feat_dir,
                    start_bi_index=e.idxs[0],
                    end_bi_index=e.idxs[-1],
                    start_ts=first_bi.start_ts,
                    end_ts=last_bi.end_ts,
                    source_from_ts=_src_from(first_bi),
                    source_to_ts=_src_to(last_bi),
                    high=e.high,
                    low=e.low,
                    global_index=gi,
                    kind=FeatureSeqKind.PRIMARY,
                )
            )
            gi += 1
        # 第二特征序列 ttz (§16 v10, 用户 2026-07-10): 只对 frozen 且 rule_kind=="gap" 的段产出
        # (test_all_frozen_gap_segments_have_second_sequence_backing 保证非空), 与 _revert_confirm
        # 同一 _EigenFX(GAP_REVERT) 驱动同源。每缺口事件局部编号 0 起 (跨事件用 id 区分, 不靠编号)。
        if w.freeze_state is XianduanFreezeState.FROZEN and w.rule_kind == "gap":
            for si, e in enumerate(builder._second_sequence_elements(w.direction, w.end_bi)):
                first_bi, last_bi = bis[e.idxs[0]], bis[e.idxs[-1]]
                out.append(
                    FeatureSeqUnit(
                        direction=_opposite(w.direction),  # 第二序列方向 = 下一段方向 (反向)
                        feature_direction=w.direction,  # 特征元素笔方向 = 被确认段方向 (seg_dir)
                        start_bi_index=e.idxs[0],
                        end_bi_index=e.idxs[-1],
                        start_ts=first_bi.start_ts,
                        end_ts=last_bi.end_ts,
                        source_from_ts=_src_from(first_bi),
                        source_to_ts=_src_to(last_bi),
                        high=e.high,
                        low=e.low,
                        global_index=si,
                        kind=FeatureSeqKind.SECOND,
                    )
                )
    # tail-probe (原误称 ttz, 已按 §16 v10 分名, 用户 2026-07-08/2026-07-10): 未画线段虚线的
    # tail —— 从当前 (末) 段虚线终点的下一笔起, 额外画**同向笔**临时序列 (归属假想的下一段)。
    # 仅调试、不参与任何确认判定; 自成一套 tp{n} 计数, 一旦后续画出虚线定型即作废重算 (不保稳定)。
    if work:
        last = work[-1]
        tail_start = last.end_bi + 1
        if tail_start <= n - 1:
            d = last.direction  # 同向 d (反向 tz 用 opposite(d))
            ti = 0
            for e in _feature_elements(bis, tail_start, n - 1, _opposite(d), d):
                first_bi, last_bi = bis[e.idxs[0]], bis[e.idxs[-1]]
                out.append(
                    FeatureSeqUnit(
                        direction=_opposite(d),  # 假想下一段方向
                        feature_direction=d,  # 特征元素笔方向 = 同向 d → 取 d 的 K 线涨跌色
                        start_bi_index=e.idxs[0],
                        end_bi_index=e.idxs[-1],
                        start_ts=first_bi.start_ts,
                        end_ts=last_bi.end_ts,
                        source_from_ts=_src_from(first_bi),
                        source_to_ts=_src_to(last_bi),
                        high=e.high,
                        low=e.low,
                        global_index=ti,
                        kind=FeatureSeqKind.TAIL_PROBE,
                    )
                )
                ti += 1
    return out
