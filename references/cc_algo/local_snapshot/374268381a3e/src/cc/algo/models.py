"""缠论基础结构层公共 DTO 与枚举 (stage-05-execution-plan.md §4.1)。

阶段 5 算法层**只产结构对象**, 不碰 Web / 通知 (§1.5)。本模块定义合并 K 线 /
分型 / 笔 / 线段 / 中枢 / 走势候选五类结构的稳定字段;具体填充由各算法层负责。

设计要点:
- 全部 frozen + slots dataclass: 结构对象一旦 confirmed 即冻结, 符合「可变性」纪律
  (§4.3 confirmed 冻结 vs provisional 可变), provisional 末端对象通过整体替换更新。
- 每个结构带 ``period`` 字段: 阶段 5 仅单周期独立计算 (§8.1-H), 但为阶段 6 多级别
  联立预留来源周期标识 (§1.5)。
- 时间统一 **Unix 秒 (UTC)**, 对齐 cc.data.models.Kline 与 TV 显示层。
- ``ZhongShu`` 只保留 Gate B 已确认字段；未确认的阶段 6 演化字段不提前占位。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cc.algo.trace import StructTrace


class KlineDir(StrEnum):
    """合并 K 线方向 (处理包含关系时的局部趋势方向)。"""

    UP = "up"
    DOWN = "down"


class FxType(StrEnum):
    """分型类型。"""

    TOP = "top"  # 顶分型
    BOTTOM = "bottom"  # 底分型


class BiDir(StrEnum):
    """笔 / 线段方向 (向上为升、向下为降)。"""

    UP = "up"
    DOWN = "down"


class ZhongShuMode(StrEnum):
    """中枢结构口径：默认延伸，或第 38 课同级分解。"""

    EXTEND = "extend"
    SAME_LEVEL = "same_level"


class ZhongShuSource(StrEnum):
    """中枢输入来源；与结构口径是两个正交维度。"""

    BI = "bi"
    XIANDUAN = "xianduan"


class ZhongShuState(StrEnum):
    """中枢延伸状态；与下层 confirmed/provisional 是不同维度。"""

    OPEN = "open"
    CLOSED = "closed"


class ZhongShuRelationType(StrEnum):
    """相邻同级别段中枢关系（第 20 课中心定理二）。"""

    UP_TREND = "up_trend"
    DOWN_TREND = "down_trend"
    UP_EXPANSION = "up_expansion"
    DOWN_EXPANSION = "down_expansion"
    UNDETERMINED = "undetermined"


class ZouShiKind(StrEnum):
    """走势类型保留原文两层语义：盘整或趋势。"""

    CONSOLIDATION = "consolidation"
    TREND = "trend"


class ZouShiDirection(StrEnum):
    """仅趋势候选具有上涨/下跌方向；盘整候选方向为空。"""

    UP = "up"
    DOWN = "down"


class ZouShiClassificationState(StrEnum):
    """Gate B 只证明结构门槛满足，不声称走势已经完成。"""

    STRUCTURALLY_QUALIFIED = "structurally_qualified"


class ZouShiStability(StrEnum):
    """候选/关系是否仍依赖 open 末端中枢。"""

    STABLE = "stable"
    PROVISIONAL = "provisional"


class ZouShiBoundaryState(StrEnum):
    """v2 走势边界状态：历史已获右证据冻结，或最右仍在形成。"""

    FROZEN = "frozen"
    FORMING = "forming"


class ZouShiLevel(StrEnum):
    """项目结构级别；与自然 K 线周期严格分离。"""

    L0 = "l0"
    L1 = "l1"


class RecursiveOrigin(StrEnum):
    """递归链底座来源；与自然周期和递归深度分离。"""

    L0 = "l0"
    L1 = "l1"


@dataclass(frozen=True, slots=True)
class MergedKline:
    """合并 K 线 — 包含关系处理后的单元 (PR-3 填充)。

    一根合并 K 线对应原始 K 线序列的一个连续区间 [start_index, end_index]。
    """

    period: str  # 来源周期码 (§1.5 预留)
    dir: KlineDir  # 合并方向
    high: float
    low: float
    start_ts: int  # 区间首根原始 K 线开盘时间 (Unix 秒)
    end_ts: int  # 区间末根原始 K 线开盘时间 (Unix 秒)
    start_index: int  # 原始 K 线序列起始下标
    end_index: int  # 原始 K 线序列结束下标
    trace: StructTrace | None = None  # 轻量 trace 索引 (§1.7); 默认 overlay 不下发

    @property
    def id(self) -> str:
        """稳定 id (§1.7): ``mk-{start_ts}-{end_ts}``。"""
        return f"mk-{self.start_ts}-{self.end_ts}"


@dataclass(frozen=True, slots=True)
class Fenxing:
    """分型 — 由三根相邻合并 K 线构成, 取中间一根为代表 (PR-3 填充)。"""

    period: str  # 来源周期码 (§1.5 预留)
    fx_type: FxType
    index: int  # 中间合并 K 线在合并序列中的下标
    timestamp: int  # 中间合并 K 线代表时间 (Unix 秒)
    high: float  # 分型三根区间最高
    low: float  # 分型三根区间最低
    trace: StructTrace | None = None  # 轻量 trace 索引 (§1.7); 默认 overlay 不下发

    @property
    def id(self) -> str:
        """稳定 id (§1.7): ``fx-{timestamp}`` (与 serializer id 对齐)。"""
        return f"fx-{self.timestamp}"


@dataclass(frozen=True, slots=True)
class Bi:
    """笔 — 连接相邻顶/底分型 (PR-4 模型/契约; 增量算法 PR-5 填充)。

    端点分型可由稳定 id 反推 (起点 ``fx-{start_ts}`` / 终点 ``fx-{end_ts}``), 不存冗余引用。
    """

    period: str  # 来源周期码 (§1.5 预留)
    direction: BiDir
    start_ts: int  # 起点分型代表时间 (Unix 秒)
    end_ts: int  # 终点分型代表时间 (Unix 秒)
    start_price: float  # 起点价
    end_price: float  # 终点价
    high: float
    low: float
    trace: StructTrace | None = None  # 轻量 trace 索引 (§1.7); 默认 overlay 不下发

    @property
    def id(self) -> str:
        """稳定 id (§1.7): ``bi-{start_ts}-{end_ts}``。"""
        return f"bi-{self.start_ts}-{self.end_ts}"


@dataclass(frozen=True, slots=True)
class Xianduan:
    """线段 — 由若干笔经特征序列法构成 (PR-6 填充)。

    端点为构成线段的首/末笔端点 (起点笔起点 / 终点笔终点); 几何 high/low 为线段区间极值。
    ``trace`` 为轻量 trace 索引 (§1.7, xianduan-v1 §13), 默认 overlay 不下发; ``source_range`` /
    ``merged_range`` / ``dep_to_index`` 从构成笔的 trace 聚合 (PR-6B)。
    """

    period: str  # 来源周期码 (§1.5 预留)
    direction: BiDir
    start_ts: int  # 起点笔起点时间 (Unix 秒)
    end_ts: int  # 终点笔终点时间 (Unix 秒)
    start_price: float
    end_price: float
    high: float
    low: float
    trace: StructTrace | None = None  # 轻量 trace 索引 (§1.7); 默认 overlay 不下发

    @property
    def id(self) -> str:
        """稳定 id (§1.7): ``xianduan-{start_ts}-{end_ts}``。"""
        return f"xianduan-{self.start_ts}-{self.end_ts}"


@dataclass(frozen=True, slots=True)
class ZhongShu:
    """中枢 Gate B 结构对象（笔/线段共用）。"""

    period: str  # 来源周期码 (§1.5 预留)
    source_type: ZhongShuSource
    direction: BiDir  # 核心 A/C（Z 结构）方向；与进入方向锚点相反
    zg: float  # 中枢上沿（首两个同向 Z 结构高点最小值，延伸后冻结）
    zd: float  # 中枢下沿（首两个同向 Z 结构低点最大值，延伸后冻结）
    gg: float  # 所有已纳入同向 Z 结构高点最大值
    dd: float  # 所有已纳入同向 Z 结构低点最小值
    start_ts: int
    core_end_ts: int  # 第三个核心成员终点；稳定 id 锚点
    end_ts: int  # 最后一个已纳入成员终点（延伸时可变）
    start_index: int
    end_index: int
    core_member_ids: tuple[str, str, str]
    extended_member_ids: tuple[str, ...]
    member_count: int
    extension_state: ZhongShuState
    mode: ZhongShuMode = ZhongShuMode.EXTEND
    entry_evidence_id: str | None = None  # 核心 A 前一结构；成立必要证据但非成员
    entry_evidence_index: int | None = None
    close_evidence_id: str | None = None
    close_evidence_index: int | None = None
    trace: StructTrace | None = None

    @property
    def id(self) -> str:
        """稳定 id：成立锚点不随延伸或关闭变化。"""
        prefix = "zs" if self.mode is ZhongShuMode.EXTEND else "zsd"
        return f"{prefix}-{self.source_type.value}-{self.start_ts}-{self.core_end_ts}"


@dataclass(frozen=True, slots=True)
class ZhongShuRelation:
    """两个相邻段中枢的严格位置关系；不是走势完成证据。"""

    period: str
    source_type: ZhongShuSource
    relation: ZhongShuRelationType
    stability: ZouShiStability
    left_zhongshu_id: str
    right_zhongshu_id: str
    left_index: int
    right_index: int
    start_ts: int
    end_ts: int
    left_zg: float
    left_zd: float
    left_gg: float
    left_dd: float
    right_zg: float
    right_zd: float
    right_gg: float
    right_dd: float
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.source_type is not ZhongShuSource.XIANDUAN:
            raise ValueError("formal zhongshu relation source_type must be xianduan")

    @property
    def id(self) -> str:
        """稳定 id：由左右两个稳定中枢 id 决定。"""
        return f"zsr-{self.left_zhongshu_id}-{self.right_zhongshu_id}"


@dataclass(frozen=True, slots=True)
class ZouShiCandidate:
    """走势类型结构候选；Gate B 不表示走势已经完成。"""

    period: str
    kind: ZouShiKind
    trend_direction: ZouShiDirection | None
    classification_state: ZouShiClassificationState
    stability: ZouShiStability
    start_ts: int
    end_ts: int
    start_zhongshu_index: int
    end_zhongshu_index: int
    zhongshu_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    member_count: int
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.member_count != len(self.zhongshu_ids) or self.member_count < 1:
            raise ValueError("zoushi candidate member_count must match non-empty zhongshu_ids")
        if self.kind is ZouShiKind.CONSOLIDATION and self.trend_direction is not None:
            raise ValueError("consolidation candidate must not have trend_direction")
        if self.kind is ZouShiKind.TREND and self.trend_direction is None:
            raise ValueError("trend candidate requires trend_direction")
        if len(self.relation_ids) != max(0, self.member_count - 1):
            raise ValueError("relation_ids must connect adjacent candidate zhongshus")

    @property
    def id(self) -> str:
        """稳定 id：候选升级或同向延伸时保持首中枢成立锚点。"""
        return f"zoushi-xianduan-{self.start_ts}"

@dataclass(frozen=True, slots=True)
class ZouShiEndpoint:
    """走势显示分段的算法端点；锚定到实际下层笔/线段。"""

    source_id: str
    source_index: int
    ts: int
    price: float


@dataclass(frozen=True, slots=True)
class LevelLeg:
    """L0/L1 共用的最低输入部件；来源由薄适配器决定。"""

    period: str
    level: ZouShiLevel
    source_type: ZhongShuSource
    source_id: str
    source_index: int
    direction: BiDir
    start_ts: int
    end_ts: int
    start_price: float
    end_price: float
    high: float
    low: float
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.source_index < 0:
            raise ValueError("level leg source_index must be non-negative")
        if self.start_ts > self.end_ts:
            raise ValueError("level leg start timestamp must not exceed end")
        if self.low > self.high:
            raise ValueError("level leg low must not exceed high")


@dataclass(frozen=True, slots=True)
class CompletedZouShi:
    """v2 走势对象；历史项 frozen，右缘候选/活动项 forming。"""

    period: str
    level: ZouShiLevel
    source_type: ZhongShuSource
    kind: ZouShiKind
    trend_direction: ZouShiDirection | None
    start: ZouShiEndpoint
    end: ZouShiEndpoint
    start_source_id: str
    source_member_ids: tuple[str, ...]
    zhongshu_ids: tuple[str, ...]
    completion_state: ZouShiBoundaryState
    close_evidence_zhongshu_id: str | None = None
    close_evidence_source_id: str | None = None
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if not self.source_member_ids:
            raise ValueError("zoushi requires source members")
        if not self.zhongshu_ids and (
            self.completion_state is not ZouShiBoundaryState.FORMING
            or self.kind is not ZouShiKind.CONSOLIDATION
            or self.trend_direction is not None
        ):
            raise ValueError(
                "zoushi without official zhongshu must be a forming consolidation"
            )
        if self.start.source_index > self.end.source_index:
            raise ValueError("zoushi source range is reversed")
        if self.start.ts > self.end.ts:
            raise ValueError("zoushi timestamp range is reversed")
        if self.kind is ZouShiKind.CONSOLIDATION and self.trend_direction is not None:
            raise ValueError("consolidation must not have trend_direction")
        if self.kind is ZouShiKind.TREND and self.trend_direction is None:
            raise ValueError("trend requires trend_direction")
        evidence_count = sum(
            item is not None
            for item in (
                self.close_evidence_zhongshu_id,
                self.close_evidence_source_id,
            )
        )
        if self.completion_state is ZouShiBoundaryState.FROZEN and evidence_count != 1:
            raise ValueError("frozen zoushi requires exactly one close evidence")
        if (
            self.completion_state is ZouShiBoundaryState.FROZEN
            and self.close_evidence_zhongshu_id in self.zhongshu_ids
        ):
            raise ValueError("frozen zoushi close evidence must not be a member")
        if (
            self.completion_state is ZouShiBoundaryState.FORMING
            and evidence_count
        ):
            raise ValueError("forming zoushi must not claim close evidence")

    @property
    def id(self) -> str:
        """用户确认的稳定 id，不使用尾端、成员数量或自然周期。"""
        return (
            f"zsl-{self.level.value}-{self.source_type.value}-"
            f"{self.start_source_id}"
        )


@dataclass(frozen=True, slots=True)
class LevelBuildResult:
    """同一前缀一次构建得到的部件、正式中枢与走势对象。"""

    level: ZouShiLevel
    source_type: ZhongShuSource
    legs: tuple[LevelLeg, ...]
    zhongshus: tuple[ZhongShu, ...]
    zoushis: tuple[CompletedZouShi, ...]


@dataclass(frozen=True, slots=True)
class RecursiveLevelKey:
    """递归结构身份；相同显示级别的不同底座不得串用。"""

    origin_level: RecursiveOrigin
    depth: int

    def __post_init__(self) -> None:
        if self.depth < 1:
            raise ValueError("recursive depth must be positive")

    @property
    def logical_level(self) -> str:
        base = 0 if self.origin_level is RecursiveOrigin.L0 else 1
        return f"l{base + self.depth}"


@dataclass(frozen=True, slots=True)
class RecursiveLeg:
    """一个 frozen 低一级完成走势投影成的递归中枢输入。"""

    period: str
    origin_level: RecursiveOrigin
    source_depth: int
    source_zoushi_id: str
    source_position: int
    start: ZouShiEndpoint
    end: ZouShiEndpoint
    direction: ZouShiDirection
    high: float
    low: float
    source_member_ids: tuple[str, ...]
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.source_depth < 0 or self.source_position < 0:
            raise ValueError("recursive leg source coordinates must be non-negative")
        if not self.source_member_ids:
            raise ValueError("recursive leg requires source members")
        if len(set(self.source_member_ids)) != len(self.source_member_ids):
            raise ValueError("recursive leg source members must be unique")
        if self.start.ts > self.end.ts:
            raise ValueError("recursive leg timestamp range is reversed")
        if self.low > self.high:
            raise ValueError("recursive leg low must not exceed high")
        if not (self.low <= self.start.price <= self.high):
            raise ValueError("recursive leg start price must be inside lifecycle range")
        if not (self.low <= self.end.price <= self.high):
            raise ValueError("recursive leg end price must be inside lifecycle range")
        if self.start.price == self.end.price:
            raise ValueError("recursive leg direction cannot be inferred from equal endpoints")
        expected = (
            ZouShiDirection.UP
            if self.end.price > self.start.price
            else ZouShiDirection.DOWN
        )
        if self.direction is not expected:
            raise ValueError("recursive leg direction must match endpoint movement")


@dataclass(frozen=True, slots=True)
class ZouShiKernelExtremeRef:
    """走势生命周期极值及其低一级来源坐标。"""

    source_id: str
    source_position: int
    price: float

    def __post_init__(self) -> None:
        if self.source_position < 0:
            raise ValueError("zoushi extreme position must be non-negative")


@dataclass(frozen=True, slots=True)
class RecursiveZhongShu:
    """由低一级完成走势递归形成的高一级中枢。"""

    period: str
    origin_level: RecursiveOrigin
    depth: int
    logical_level: str
    zhongshu_mode: ZhongShuMode
    direction: ZouShiDirection
    zg: float
    zd: float
    gg: float
    dd: float
    start_ts: int
    core_end_ts: int
    end_ts: int
    start_index: int
    end_index: int
    core_member_ids: tuple[str, str, str]
    extended_member_ids: tuple[str, ...]
    member_count: int
    entry_evidence_id: str
    entry_evidence_index: int
    extension_state: ZhongShuState
    close_evidence_id: str | None = None
    close_evidence_index: int | None = None
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.depth < 1:
            raise ValueError("recursive zhongshu depth must be positive")
        expected_level = (
            0 if self.origin_level is RecursiveOrigin.L0 else 1
        ) + self.depth
        if self.logical_level != f"l{expected_level}":
            raise ValueError("recursive zhongshu logical_level does not match identity")
        if self.zhongshu_mode is not ZhongShuMode.EXTEND:
            raise ValueError("recursive zhongshu Gate B1 requires extend mode")
        if self.zd > self.zg or self.dd > self.gg:
            raise ValueError("recursive zhongshu price range is invalid")
        if self.member_count != 3 + len(self.extended_member_ids):
            raise ValueError("recursive zhongshu member_count does not match members")
        if len(self.extended_member_ids) % 2:
            raise ValueError("recursive zhongshu extensions must be reverse/Z pairs")
        if len(set(self.core_member_ids + self.extended_member_ids)) != self.member_count:
            raise ValueError("recursive zhongshu members must be unique")
        if self.entry_evidence_index + 1 != self.start_index:
            raise ValueError("recursive zhongshu core must immediately follow entry evidence")
        if not (
            self.entry_evidence_index < self.start_index <= self.end_index
            and self.start_ts <= self.core_end_ts <= self.end_ts
        ):
            raise ValueError("recursive zhongshu coordinates are invalid")
        if self.entry_evidence_id in self.core_member_ids:
            raise ValueError("entry evidence must not be a core member")
        if self.close_evidence_id is not None and (
            self.close_evidence_id in self.core_member_ids
            or self.close_evidence_id in self.extended_member_ids
        ):
            raise ValueError("close evidence must not belong to the same center")
        if self.extension_state is ZhongShuState.CLOSED:
            if self.close_evidence_id is None or self.close_evidence_index is None:
                raise ValueError("closed recursive zhongshu requires close evidence")
        elif self.close_evidence_id is not None or self.close_evidence_index is not None:
            raise ValueError("open recursive zhongshu must not claim close evidence")

    @property
    def id(self) -> str:
        """成立锚点稳定 id；延伸与 open→closed 不换号。"""
        return (
            f"rzs-{self.origin_level.value}-d{self.depth}-"
            f"{self.start_ts}-{self.core_end_ts}"
        )


@dataclass(frozen=True, slots=True)
class RecursiveZouShi:
    """由正式递归中枢构造的高一级走势；历史项 frozen，右缘项 forming。"""

    period: str
    origin_level: RecursiveOrigin
    depth: int
    logical_level: str
    zhongshu_mode: ZhongShuMode
    kind: ZouShiKind
    trend_direction: ZouShiDirection | None
    start: ZouShiEndpoint
    end: ZouShiEndpoint
    start_source_position: int
    end_source_position: int
    high: float
    low: float
    high_point: ZouShiKernelExtremeRef
    low_point: ZouShiKernelExtremeRef
    start_source_id: str
    source_member_ids: tuple[str, ...]
    zhongshu_ids: tuple[str, ...]
    member_count: int
    completion_state: ZouShiBoundaryState
    close_evidence_zhongshu_id: str | None = None
    close_evidence_source_id: str | None = None
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.depth < 1:
            raise ValueError("recursive zoushi depth must be positive")
        expected_level = (0 if self.origin_level is RecursiveOrigin.L0 else 1) + self.depth
        if self.logical_level != f"l{expected_level}":
            raise ValueError("recursive zoushi logical_level does not match identity")
        if self.zhongshu_mode is not ZhongShuMode.EXTEND:
            raise ValueError("recursive zoushi requires extend mode")
        if not self.source_member_ids or not self.zhongshu_ids:
            raise ValueError("recursive zoushi requires source and center members")
        if len(set(self.source_member_ids)) != len(self.source_member_ids):
            raise ValueError("recursive zoushi source members must be unique")
        if len(set(self.zhongshu_ids)) != len(self.zhongshu_ids):
            raise ValueError("recursive zoushi center members must be unique")
        if self.member_count != len(self.source_member_ids):
            raise ValueError("recursive zoushi member_count does not match source members")
        if self.start_source_id != self.source_member_ids[0]:
            raise ValueError("recursive zoushi start source must be its first member")
        if self.start_source_position < 0:
            raise ValueError("recursive zoushi source position must be non-negative")
        member_end_position = self.start_source_position + self.member_count - 1
        if not self.start_source_position <= self.end_source_position <= member_end_position:
            raise ValueError("recursive zoushi end must belong to its member horizon")
        if self.start.ts > self.end.ts or self.low > self.high:
            raise ValueError("recursive zoushi lifecycle range is invalid")
        if not self.low <= self.start.price <= self.high:
            raise ValueError("recursive zoushi start is outside lifecycle range")
        if not self.low <= self.end.price <= self.high:
            raise ValueError("recursive zoushi end is outside lifecycle range")
        if not self.low <= self.high_point.price <= self.high:
            raise ValueError("recursive zoushi high point is outside lifecycle range")
        if not self.low <= self.low_point.price <= self.high:
            raise ValueError("recursive zoushi low point is outside lifecycle range")
        if self.high_point.price != self.high or self.low_point.price != self.low:
            raise ValueError("recursive zoushi extreme refs must match high/low")
        for role, point in (("high", self.high_point), ("low", self.low_point)):
            if not self.start_source_position <= point.source_position <= member_end_position:
                raise ValueError(
                    f"recursive zoushi {role} point must belong to its member horizon"
                )
            member_id = self.source_member_ids[
                point.source_position - self.start_source_position
            ]
            if point.source_id != member_id:
                raise ValueError(
                    f"recursive zoushi {role} point must reference its source member"
                )
        if self.kind is ZouShiKind.CONSOLIDATION and self.trend_direction is not None:
            raise ValueError("recursive consolidation cannot have trend direction")
        if self.kind is ZouShiKind.TREND and self.trend_direction is None:
            raise ValueError("recursive trend requires direction")
        evidence = (
            int(self.close_evidence_zhongshu_id is not None)
            + int(self.close_evidence_source_id is not None)
        )
        if self.completion_state is ZouShiBoundaryState.FROZEN and evidence != 1:
            raise ValueError("frozen recursive zoushi requires one close evidence")
        if self.completion_state is ZouShiBoundaryState.FORMING and evidence:
            raise ValueError("forming recursive zoushi cannot claim close evidence")
        if self.close_evidence_zhongshu_id in self.zhongshu_ids:
            raise ValueError("recursive close evidence center must not be a member")
        if self.close_evidence_source_id in self.source_member_ids:
            raise ValueError("recursive close evidence leg must not be a member")

    @property
    def id(self) -> str:
        return (
            f"rzt-{self.origin_level.value}-d{self.depth}-"
            f"{self.start.ts}"
        )
