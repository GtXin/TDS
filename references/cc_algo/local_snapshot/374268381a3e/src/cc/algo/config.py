"""ChanConfig / AlgorithmProfile 契约 (stage-05-execution-plan.md §1.6 / §4.4)。

阶段 5 PR-5 (v3): **统一参数化画笔引擎** — 一套底层参数 + 多个一键 preset; custom 自由组合;
profile 只是预设名, 真正决定画笔的是参数。build_bis 按参数线性判定。
口径优先链 (§1.1 / decision-0001 v1.4 §12.3): 缠论原文 > 用户确认的本项目口径 > 本项目自主
实现; 参考项目 (chan.py-main / czsc / chanlun-pro) 无固定优先级, 只作对照 / 启发 / 差异发现来源。

**preset (bi-v1 §16 用户锁定; v3 重命名 + 强势笔/次笔)**:
- ``bi_5k``        老笔(严格笔) = 原文老笔严格 + chan strict (merged_center, 中心差 ≥4)。默认。
- ``bi_4k``        新笔(宽松笔) = 原文新笔 (raw_extreme, 极值原始 K 间距)。
- ``bi_strong``    强势笔 = **老笔 bi_5k 基础**(含 fractal_repair) + 相邻反向笔幅度判定。待完善。
- ``bi_secondary`` 次笔 = **老笔 bi_5k 线段代理**(特征序列法)。**待完善, 当前搁置不输出**。
- ``custom``       自由组合全部底层参数。
- 变体默认仅图上对照 / 人工分析, 不进信号回测 (§1.6-5)。

**config_hash = 后端单一权威** (用户拍板): 前端只发归一化参数、**不自算 hash**。
canonical **semantic** payload (动态生效字段): 只哈希当前 ``bi_span_mode``/``bi_formation_mode``
下**生效**的字段 (inactive 不进 hash, 避免「图形不变而 hash 变」); 排除 ``bi_profile`` 标签
与 ``trace_*``。custom 配成 named preset 生效参数 ⇒ 同 hash 同几何, 但 EngineKey 含 profile_id
→ 不同实例隔离。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum

from cc.algo.keys import EngineKey
from cc.algo.models import ZhongShuMode

# wire schema 版本 (API chan JSON 的 config_version; 仅接受当前值, 旧值 → 400)。
# v3: 字段改名 + 删 czsc + 强势/次笔。v4: allow_sub_peak → bi_fractal_repair(带反向确认守卫)。
# v5: 线段两层口径 (xianduan_preset + 4 策略, xianduan-v1 §5 / decision-0028)。
# v6: seg → xianduan 全仓命名统一 (字段 seg_*→xianduan_*; 命名契约升级, 算法几何不变)。
# v7: 删 bi_same_fx_policy wire 字段 (同型延伸固定 extreme; 仅删无用变体/UI 参数,
#     几何不变 → BI_ALGO_VERSION 不升, 只升 wire schema 版本)。
# v8: 新增 zhongshu_mode；它改变中枢成员、边界与稳定 id，必须进入配置指纹/EngineKey。
CONFIG_VERSION = 8

# 笔口径**语义版本** (后端常量, 非客户端可传; 注入 config_hash payload)。
# 几何算法身份标记: 仅几何变化才升。v7 删 same_fx 字段属"删变体不改几何", **保持 4**。
BI_ALGO_VERSION = 4

# 线段口径**语义版本** (后端常量, 注入 config_hash payload)。v1 = 两层 (严格标准 + 实战变体);
# v2 = 缺口第二种情况 find_revert_fx 反向确认 (gap_revert_confirmed, xianduan-v1 §16 v10) —— 改变
# 严格 standard 几何 (部分缺口段由 pending 提前 confirmed) → standard config_hash 随版本变化。
XIANDUAN_ALGO_VERSION = 2

# 距离阈值边界 (前后端一致校验)。
MIN_DISTANCE_VALUE = 1
MAX_DISTANCE_VALUE = 1000
# 强势比例边界 (0 < r ≤ 2; >1 = 要求当前笔比相邻还大, 更严)。
MIN_STRENGTH_RATIO = 0.0  # 排他下界 (0 < r)
MAX_STRENGTH_RATIO = 2.0


class BiProfile(StrEnum):
    """笔口径套餐 (UI 五选一; UI 显中文, 代码用此值)。"""

    BI_5K = "bi_5k"  # 老笔(严格笔)
    BI_4K = "bi_4k"  # 新笔(宽松笔)
    BI_STRONG = "bi_strong"  # 强势笔
    BI_SECONDARY = "bi_secondary"  # 次笔
    CUSTOM = "custom"  # 自定义参数


class BiFormationMode(StrEnum):
    """成笔模式 (决定候选反向分型对如何接受/成笔)。"""

    STANDARD = "standard"  # 标准: 距离 + 端点检查 + 端点极值
    STRONG = "strong"  # 强势: 标准失败时按相邻反向笔幅度 ≥ ratio 成笔
    SECONDARY = "secondary"  # 次笔: 第一反向分型不成笔, 第二同型处成笔


class BiSpanMode(StrEnum):
    """成笔距离计数模式 (只控制 base_span 怎么数; 分型仍在合并序列识别)。"""

    MERGED_CENTER = "merged_center"  # 分型中心合并单元下标差 (+缺口折算)
    RAW_EXTREME = "raw_extreme"  # 两端极值原始 K 索引差 (+不共用 K 内建)


class BiEndpointCheck(StrEnum):
    """分型作为笔端点的有效性检查 (chan check_fx_valid; **非分型识别本身**)。"""

    NONE = "none"  # 跳过端点有效性检查
    LOSS = "loss"  # 只比中间根
    HALF = "half"  # 比前两根 (chan 默认)
    STRICT = "strict"  # 三根全用
    TOTALLY = "totally"  # 价区完全分离


class TraceLevel(StrEnum):
    """trace 详细程度 (§1.7; 观测开关, 不进 config_hash)。"""

    OFF = "off"
    LIGHT = "light"  # 默认
    FULL = "full"  # 按需端点 / 调试脚本


# ── 线段两层口径 (xianduan-v1 §5 / decision-0028; 缠论语义命名, 不用参考项目名) ──────


class XianduanPreset(StrEnum):
    """线段口径预设 (UI 三选; UI 显中文, 代码用此值)。

    **默认 = STANDARD (严格标准)**。standard_strong / practical 启用实战变体:
    - **强势笔破坏 strong_bi 已实现** (用户 2026-07-10, xianduan-practical-v1 §16): 改线段几何 →
      `xianduan_break_policy=strong_bi` 生效时进 config_hash (动态字段); standard (line_only) 不进 →
      默认几何/hash 不变。
    - 非标准补齐 / 横向震荡三笔 **仍未实现** (§5.2 低优先级 / §5.3 降级), build_xianduans 不消费其
      策略、不进 hash。
    """

    STANDARD = "standard"  # 严格标准 (原文特征序列, 作根) — 默认
    STANDARD_STRONG = "standard_strong"  # 标准 + 强势笔 (未来变体, 未实现)
    PRACTICAL = "practical"  # 标准 + 强势笔 + 非标准补齐 + 横向震荡三笔 (未来变体, 未实现)


class XianduanBreakPolicy(StrEnum):
    """线段破坏策略。"""

    LINE_ONLY = "line_only"  # 仅反向线段破坏 (严格标准, 原文)
    STRONG_BI = "strong_bi"  # + 强势笔破坏 (项目实战变体)


class XianduanNonstandardPolicy(StrEnum):
    """非标准线段补齐策略。"""

    OFF = "off"  # 严格标准: 不补齐 (未确认处虚线兜底)
    REPAIR = "repair"  # 实战: 非标准连续拆分补齐 (项目实战变体)


class XianduanOscillationPolicy(StrEnum):
    """横向震荡三笔成段策略。"""

    OFF = "off"  # 严格标准: 不做
    THREE_BI = "three_bi"  # 实战: 三笔重合成震荡段 (项目实战变体)


class XianduanLeftMethod(StrEnum):
    """末段未闭合处理 (chan left_method)。"""

    PEAK = "peak"  # 取已现方向极值笔 (默认)
    ALL = "all"  # 取全部已现笔


@dataclass(frozen=True, slots=True)
class ChanConfig:
    """缠论笔层口径配置 (统一底层参数; §1.6 算法口径总规则的工程载体)。

    named profile 由 ``normalize`` 派生完整参数, custom 自由组合。数值字段经 ``__post_init__``
    校验边界。
    """

    bi_profile: BiProfile = BiProfile.BI_5K
    bi_formation_mode: BiFormationMode = BiFormationMode.STANDARD
    bi_span_mode: BiSpanMode = BiSpanMode.MERGED_CENTER
    bi_min_span: int = 4
    bi_gap_as_bar: bool = True  # 仅 merged_center 有效
    bi_endpoint_check: BiEndpointCheck = BiEndpointCheck.HALF
    bi_require_peak: bool = True
    # 同型分型延伸固定取更极值 (两顶取更高 / 两底取更低, 第 65 课); 原 bi_same_fx_policy
    # 的 first 变体于 v7 删除 (无正确用途, 三项目 + 原文均只用 extreme, §16 v11)。
    # 笔破坏修正 (取代旧 allow_sub_peak): 反弹笔起点被反向更极值击穿、且"新低/高之后价格反向
    # 确认真极值"时, 吸收该反弹笔、把前一笔延伸到新极值 (bi-v1 笔破坏修正小节, 项目变体)。
    # 默认 True = bi_5k 开启; strong/secondary 继承老笔 bi_5k 基底(同为 True); 仅 bi_4k 显式 False。
    bi_fractal_repair: bool = True
    bi_strength_ratio: float = 0.9  # 仅 strong 有效
    # ── 线段两层口径 (xianduan-v1 §5 / decision-0028) ──
    # xianduan_preset = 用户可见预设; 4 策略由 preset 派生 (normalize)。默认 = 严格标准。
    # xianduan_break_policy=strong_bi **已实现** (强势笔破坏, 用户 2026-07-10): build_xianduans
    # 消费、改线段几何 → 生效时动态进 config_hash (见 _hash_payload)。nonstandard/oscillation 策略
    # 仍未实现 (build_xianduans 不消费、不进 hash)。
    xianduan_preset: XianduanPreset = XianduanPreset.STANDARD  # 默认严格标准 (用户 2026-06-30)
    xianduan_break_policy: XianduanBreakPolicy = XianduanBreakPolicy.LINE_ONLY
    xianduan_nonstandard_policy: XianduanNonstandardPolicy = XianduanNonstandardPolicy.OFF
    xianduan_oscillation_policy: XianduanOscillationPolicy = XianduanOscillationPolicy.OFF
    xianduan_left_method: XianduanLeftMethod = XianduanLeftMethod.PEAK
    # 中枢结构口径与输入来源正交：默认延伸；同级分解不吸收延伸成员。
    zhongshu_mode: ZhongShuMode = ZhongShuMode.EXTEND
    # 观测 (不进 config_hash)
    trace_enabled: bool = True
    trace_level: TraceLevel = TraceLevel.LIGHT

    def __post_init__(self) -> None:
        v = self.bi_min_span
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"bi_min_span must be int, got {v!r}")
        if not MIN_DISTANCE_VALUE <= v <= MAX_DISTANCE_VALUE:
            raise ValueError(
                f"bi_min_span={v} out of range [{MIN_DISTANCE_VALUE},{MAX_DISTANCE_VALUE}]"
            )
        r = self.bi_strength_ratio
        if isinstance(r, bool) or not isinstance(r, int | float):
            raise ValueError(f"bi_strength_ratio must be number, got {r!r}")
        if not (MIN_STRENGTH_RATIO < r <= MAX_STRENGTH_RATIO):
            raise ValueError(
                f"bi_strength_ratio={r} out of range ({MIN_STRENGTH_RATIO},{MAX_STRENGTH_RATIO}]"
            )

    def normalize(self) -> ChanConfig:
        """归一化: named profile 派生笔参数 (保留 trace_*); 线段 4 策略由 ``xianduan_preset`` 派生。

        线段策略恒由 ``xianduan_preset`` 派生 (3 预设固定组合, xianduan-v1 §5),
        不暴露 custom 自由组合 (避免不合理组合; 将来需要再开)。
        ``xianduan_left_method`` 随 preset (当前均 peak)。
        """
        bp = XIANDUAN_PRESET_POLICIES[self.xianduan_preset]
        base = self if self.bi_profile is BiProfile.CUSTOM else _PROFILE_CONFIGS[self.bi_profile]
        return replace(
            base,
            xianduan_preset=self.xianduan_preset,
            xianduan_break_policy=bp[0],
            xianduan_nonstandard_policy=bp[1],
            xianduan_oscillation_policy=bp[2],
            xianduan_left_method=bp[3],
            zhongshu_mode=self.zhongshu_mode,
            trace_enabled=self.trace_enabled,
            trace_level=self.trace_level,
        )

    @property
    def profile_id(self) -> str:
        """人读 profile 标签 = profile 名 (不进 config_hash)。"""
        return self.bi_profile.value

    @property
    def config_hash(self) -> str:
        """后端单一权威指纹 (前 12 hex; canonical semantic payload)。"""
        return compute_config_hash(self)

    def engine_key(self, symbol: str, period: str) -> EngineKey:
        """据本配置生成 ``EngineKey(symbol, period, profile_id, config_hash)``。"""
        cfg = self.normalize()
        return EngineKey(symbol, period, cfg.profile_id, cfg.config_hash)


# named profile = **完整归一化配置** (custom 不在此表; trace_* 由调用方覆写)。
_PROFILE_CONFIGS: dict[BiProfile, ChanConfig] = {
    # bi_5k = 类默认值 (老笔严格 / chan strict)。
    BiProfile.BI_5K: ChanConfig(),
    BiProfile.BI_4K: ChanConfig(
        bi_profile=BiProfile.BI_4K,
        bi_formation_mode=BiFormationMode.STANDARD,
        bi_span_mode=BiSpanMode.RAW_EXTREME,
        bi_gap_as_bar=False,
        bi_endpoint_check=BiEndpointCheck.NONE,
        bi_require_peak=False,
        bi_fractal_repair=False,
    ),
    # 强势笔/次笔基底 = 老笔 bi_5k 几何 (merged_center/min4/gap/half/peak/fractal_repair)，
    # 仅覆写成笔模式 (+强势比例)，其余继承类默认(=bi_5k)。用户 2026-06-14 拍板。
    BiProfile.BI_STRONG: ChanConfig(
        bi_profile=BiProfile.BI_STRONG,
        bi_formation_mode=BiFormationMode.STRONG,
        bi_strength_ratio=0.95,  # 老笔失败时，候选幅度 ≥ 0.95×前笔/后笔 则保留
    ),
    BiProfile.BI_SECONDARY: ChanConfig(
        bi_profile=BiProfile.BI_SECONDARY,
        bi_formation_mode=BiFormationMode.SECONDARY,
        # secondary 循环不经笔破坏修正，继承的 fractal_repair 对其无效。
    ),
}

# 线段预设 → (break, nonstandard, oscillation, left_method)。3 预设固定组合 (xianduan-v1 §5)。
# 注: standard_strong/practical 的 break_policy=strong_bi **已实现且改几何** (进 hash); 其
# nonstandard/oscillation 策略仍未实现 (build_xianduans 不消费、不进 hash, 用户 2026-06-30 方案A)。
XIANDUAN_PRESET_POLICIES: dict[
    XianduanPreset,
    tuple[
        XianduanBreakPolicy,
        XianduanNonstandardPolicy,
        XianduanOscillationPolicy,
        XianduanLeftMethod,
    ],
] = {
    XianduanPreset.STANDARD: (
        XianduanBreakPolicy.LINE_ONLY, XianduanNonstandardPolicy.OFF,
        XianduanOscillationPolicy.OFF, XianduanLeftMethod.PEAK,
    ),
    XianduanPreset.STANDARD_STRONG: (
        XianduanBreakPolicy.STRONG_BI, XianduanNonstandardPolicy.OFF,
        XianduanOscillationPolicy.OFF, XianduanLeftMethod.PEAK,
    ),
    XianduanPreset.PRACTICAL: (
        XianduanBreakPolicy.STRONG_BI, XianduanNonstandardPolicy.REPAIR,
        XianduanOscillationPolicy.THREE_BI, XianduanLeftMethod.PEAK,
    ),
}

# 始终进 hash 的语义字段 (当前真正影响几何者 = 笔)。
# 线段几何身份由 ``xianduan_algo_version`` (见 _hash_payload) 表示。线段策略字段:
# - ``xianduan_break_policy`` = strong_bi **已改几何** → 动态进 hash (仅 STRONG_BI 时, 见
#   _hash_payload; line_only 不进 → 默认 standard hash 不变, 用户 2026-07-10)。
# - ``xianduan_nonstandard_policy`` / ``xianduan_oscillation_policy`` / ``xianduan_left_method``
#   **当前不影响几何** (未实现 / left_method 均 peak) → 不进 hash, 否则伪造不存在的几何差异
#   (用户 2026-06-30 方案A; "hash 只纳入当前生效字段"原则)。实现后按生效字段纳入。
_HASH_FIELDS_ALWAYS = (
    "bi_formation_mode",
    "bi_span_mode",
    "bi_min_span",
    "bi_endpoint_check",
    "bi_require_peak",
    "bi_fractal_repair",
    "zhongshu_mode",
)

# chan JSON 允许字段 (API 白名单; 多余键 → INVALID_CHAN_CONFIG)。不含 config_version。
CHAN_WIRE_FIELDS = (
    "bi_profile",
    "bi_formation_mode",
    "bi_span_mode",
    "bi_min_span",
    "bi_gap_as_bar",
    "bi_endpoint_check",
    "bi_require_peak",
    "bi_fractal_repair",
    "bi_strength_ratio",
    "xianduan_preset",  # 线段预设 (派生4策略; strong_bi 已实现动态进 hash, 见 _HASH_FIELDS_ALWAYS)
    "zhongshu_mode",
    "trace_enabled",
    "trace_level",
)


def _to_jsonable(value: object) -> object:
    return value.value if isinstance(value, StrEnum) else value


def _hash_payload(cfg: ChanConfig) -> dict[str, object]:
    """canonical semantic payload: bi_algo_version + 始终字段 + 当前模式生效字段。

    动态生效 (用户 2026-06-12 #9): ``bi_gap_as_bar`` 仅 merged_center 纳入;
    ``bi_strength_ratio`` 仅 strong 纳入。
    """
    payload: dict[str, object] = {
        "bi_algo_version": BI_ALGO_VERSION, "xianduan_algo_version": XIANDUAN_ALGO_VERSION
    }
    for name in _HASH_FIELDS_ALWAYS:
        payload[name] = _to_jsonable(getattr(cfg, name))
    if cfg.bi_span_mode is BiSpanMode.MERGED_CENTER:
        payload["bi_gap_as_bar"] = cfg.bi_gap_as_bar
    if cfg.bi_formation_mode is BiFormationMode.STRONG:
        payload["bi_strength_ratio"] = cfg.bi_strength_ratio
    # 线段实战变体: strong_bi 单笔破坏 (xianduan-practical-v1 §16) **改变线段几何** → 生效时进 hash
    # (动态字段, 对齐 bi_strength_ratio 只在 strong 时进; line_only 不进 → 默认 standard hash 不变,
    # 无需升 XIANDUAN_ALGO_VERSION, 用户 2026-07-10 Q5「默认 standard 不受影响」)。
    if cfg.xianduan_break_policy is XianduanBreakPolicy.STRONG_BI:
        payload["xianduan_break_policy"] = cfg.xianduan_break_policy.value
    return payload


def compute_config_hash(cfg: ChanConfig) -> str:
    """归一化配置的 semantic payload → canonical JSON → sha256 → 前 12 hex (后端单一权威)。"""
    payload = _hash_payload(cfg.normalize())
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def make_profile(profile: BiProfile) -> ChanConfig:
    """据 profile 名生成归一化配置 (custom 用 ``ChanConfig(bi_profile=CUSTOM, ...)`` 自构造)。"""
    return ChanConfig(bi_profile=profile).normalize()


# 默认主线配置 = bi_5k (进 golden / API 默认 / 后续信号回测)。
DEFAULT_CONFIG = ChanConfig()
