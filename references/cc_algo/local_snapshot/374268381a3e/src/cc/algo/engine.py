"""ChanEngine — 缠论算法引擎 (PR-1 接口骨架 → PR-3 合并/分型 → PR-5 笔)。

架构 (bi-v1 §11): 合并层 (KlineCombiner) 是**真增量**状态机; 分型/笔为合并序列上的
**纯函数派生** (答案唯一, golden 自洽 §1.4), 由版本缓存避免重复推导 — 每次状态变更
至多重派生一次 (O(单元数), 不承诺全链 O(1); 性能指标 PR-9 实测)。
线段/中枢由 PR-6+ 接入, 当前返回空序列。

硬纪律 (stage-05-execution-plan.md §4.2 / §8.1):
- ``add_kline``: 仅 timestamp **严格更大**的新 K 线追加;非单调 → 抛 ``ValueError`` (§8.1-C)。
- ``update_last_kline`` / ``upsert_kline``: **同 timestamp** 末端更新, 禁止误 append 成假 K 线。
- ``add_klines`` / ``initialize``: 冷启动批量, 内部逐根走与 ``add_kline`` 一致流水线;
  **不得作隐式全量重算入口** (§1.4)。
- ``reset``: **唯一**允许的全量清空入口。
- 入口统一 ``_validate_kline`` 校验 (§8.2-G, 2026-06-07 用户锁定)。
"""

from __future__ import annotations

import logging
import math
import os
import threading
from collections.abc import Iterable
from dataclasses import dataclass

from cc.algo.bi import build_bis
from cc.algo.combiner import KlineCombiner
from cc.algo.config import DEFAULT_CONFIG, ChanConfig
from cc.algo.fenxing import detect_fenxings
from cc.algo.models import (
    Bi,
    CompletedZouShi,
    Fenxing,
    LevelBuildResult,
    MergedKline,
    RecursiveLevelKey,
    RecursiveOrigin,
    RecursiveZhongShu,
    RecursiveZouShi,
    Xianduan,
    ZhongShu,
    ZhongShuMode,
    ZhongShuRelation,
    ZhongShuSource,
    ZouShiCandidate,
    ZouShiLevel,
)
from cc.algo.xianduan import build_xianduans
from cc.algo.zhongshu import (
    build_same_level_level_result,
    build_zhongshus,
    legs_from_bis,
    legs_from_xianduans,
)
from cc.algo.zoushi import build_l0_zoushis, build_l1_zoushis, build_zoushi_candidates
from cc.algo.zoushi_recursion import (
    build_recursive_zhongshus_from_level_result,
    build_recursive_zoushis,
    recursive_leg_runs_from_level_result,
)
from cc.data.models import Kline

logger = logging.getLogger(__name__)

# ── 冷启动根数 (工程参数, 非缠论原文口径; kline-merge-v1 §8 / §16-3 用户锁定) ──
# 按周期分级 + 环境变量 CC_COLD_START_MAX_KLINES 覆盖。
_COLD_START_TIERS: dict[str, int] = {
    "1m": 3000, "2m": 2500, "3m": 2200, "5m": 2000, "15m": 1500, "30m": 1000,
    "1h": 1000, "4h": 500, "1d": 250, "1w": 200, "1M": 200,
}
CC_COLD_START_DEFAULT = 1000  # 未知周期回退保守默认 (取 30m/1h 档, §16-3)
_COLD_START_ENV = "CC_COLD_START_MAX_KLINES"


def cold_start_max_klines(period: str) -> int:
    """解析某周期冷启动最大根数 (§16-3)。

    优先级：合法 env 覆盖 > 周期分级默认 > 未知周期回退 ``CC_COLD_START_DEFAULT``。
    非法 env (非整数 / ≤0) → 忽略 env、退回分级默认 + warning。
    """
    raw = os.getenv(_COLD_START_ENV)
    if raw is not None:
        try:
            val = int(raw)
        except ValueError:
            logger.warning("invalid %s=%r (not int); fall back to tier", _COLD_START_ENV, raw)
        else:
            if val > 0:
                return val
            logger.warning("invalid %s=%r (<=0); fall back to tier", _COLD_START_ENV, raw)
    tier = _COLD_START_TIERS.get(period)
    if tier is None:
        logger.warning(
            "unknown period %r for cold start; fall back to default %d",
            period, CC_COLD_START_DEFAULT,
        )
        return CC_COLD_START_DEFAULT
    return tier


@dataclass(frozen=True, slots=True)
class EngineConfig:
    """ChanEngine L1 固定口径配置容器 (stage-05-execution-plan.md §8.1-D)。

    L1 默认**不开放**从文件/环境变量加载, 仅作各层默认值容器;resample / 回测阶段再开放。
    合并/分型 (PR-3) 口径无独立可配置常量 (原文唯一定义); 冷启动根数为工程参数, 见
    模块级 ``cold_start_max_klines``。后续各层 (笔/线段/中枢) 在此追加锁定默认值。
    """


class ChanEngine:
    """单 ``(symbol, period)`` 缠论引擎 (增量优先, 串行喂数据)。

    每实例自带 per-engine 锁 (单实例串行喂数据, §4.4);跨实例并发由 ``EngineRegistry``
    的 registry 级锁管理。
    """

    def __init__(
        self,
        symbol: str,
        period: str,
        config: EngineConfig | None = None,
        *,
        profile_id: str | None = None,
        config_hash: str | None = None,
        chan_config: ChanConfig | None = None,
    ) -> None:
        self.symbol = symbol
        self.period = period
        self.config = config or EngineConfig()
        # 算法口径配置 (PR-5): 笔层起可配置, build_bis 按此分支; 默认 default_strict。
        self.chan_config = (chan_config or DEFAULT_CONFIG).normalize()
        # 口径标识 (供笔层 trace 回溯 §1.7): 与 EngineKey 一致的实例身份。registry 显式传入;
        # 未显式传 (直接构造/测试/调试入口) 则由归一化 chan_config 派生, 保证 trace 身份与口径
        # 一致 (Codex ⚠: 否则 ChanEngine(chan_config=BI_4K) 会产 bi.4k 笔却报 profile_id=default)。
        self.profile_id = (
            profile_id if profile_id is not None else self.chan_config.profile_id
        )
        self.config_hash = (
            config_hash if config_hash is not None else self.chan_config.config_hash
        )
        self._lock = threading.Lock()
        # decision-0030 §7.B P3: 构建时的 DB 结构版本 (该引擎基于哪个 kline_revision 构建)。
        # 与 data_revision(= last_timestamp, 末端游标, 语义不变) **是两件事**: kline_revision 是
        # DB 持久结构版本, data_revision 是末端 K 线 timestamp。overlay_snapshot 用
        # engine.kline_revision != 库.kline_revision 判是否精确失效重建 (§7.B-3)。默认 None:
        # 未打戳的引擎 (直接构造/测试) 视为「未知版本」, snapshot 只对**非 None 且不等**重建,
        # 不误判 None 为 stale。纯末端追加不改本字段 (末端不升 revision, §7.B 矩阵)。
        self.kline_revision: int | None = None
        # 原始 K 线序列 (引擎侧记录 + 状态机校验)
        self._klines: list[Kline] = []
        # 增量合并器 (PR-3): 串行喂数据, 维护合并单元 + 首段方向。
        self._combiner = KlineCombiner(period)
        # 末端稳定点 (§4.3): 该原始 K 线下标及之前结构已 confirmed, 之后为 provisional。
        self.last_sure_index = -1
        # 派生结构版本缓存 (PR-5, bi-v1 §11): 合并层真增量, 分型/笔为纯函数派生;
        # 每次状态变更 (add/update/reset) bump 版本 → 派生**至多重算一次** (非 O(1), 如实标注),
        # 同版本重复查询 O(1) 返回拷贝。内部存 tuple (不可变), 对外返回 list 拷贝 —
        # 外部修改返回值不污染缓存。reset 也 bump 不清零 (防 ABA)。
        self._version = 0
        self._cache_version = -1
        self._cached_merged: tuple[MergedKline, ...] = ()
        self._cached_fenxings: tuple[Fenxing, ...] = ()
        self._cached_bis: tuple[Bi, ...] = ()
        self._cached_xianduans: tuple[Xianduan, ...] = ()
        # 中枢不进入 _ensure_derived 首屏热路径；按 source_type 独立惰性派生。
        self._zhongshu_cache_versions: dict[ZhongShuSource, int] = {}
        self._cached_zhongshus: dict[ZhongShuSource, tuple[ZhongShu, ...]] = {}
        # 走势关系与候选同一次惰性派生；同样不进入首屏热路径。
        self._zoushi_cache_version = -1
        self._cached_zhongshu_relations: tuple[ZhongShuRelation, ...] = ()
        self._cached_zoushi_candidates: tuple[ZouShiCandidate, ...] = ()
        # v2 走势按结构 level 独立惰性派生；PR-20 同内核接入 L1。
        self._level_zoushi_cache_versions: dict[ZouShiLevel, int] = {}
        self._cached_level_zoushi: dict[ZouShiLevel, LevelBuildResult] = {}
        # 高一级中枢递归按底座来源+深度隔离；Gate B1 只启用 depth=1。
        self._recursive_zhongshu_cache_versions: dict[RecursiveLevelKey, int] = {}
        self._cached_recursive_zhongshus: dict[
            RecursiveLevelKey, tuple[RecursiveZhongShu, ...]
        ] = {}
        self._recursive_zoushi_cache_versions: dict[RecursiveLevelKey, int] = {}
        self._cached_recursive_zoushis: dict[
            RecursiveLevelKey, tuple[RecursiveZouShi, ...]
        ] = {}

    @property
    def kline_count(self) -> int:
        """已喂入的原始 K 线根数 (供冷启动判定: 0 = 空引擎, §5 不重复喂)。"""
        return len(self._klines)

    @property
    def last_timestamp(self) -> int | None:
        """末根原始 K 线 timestamp (供增量刷新到最新; 空引擎返回 None)。"""
        return self._klines[-1].timestamp if self._klines else None

    def raw_klines(self) -> list[Kline]:
        """当前原始 K 线序列拷贝 (供分型 extreme 锚点序列化; 不暴露内部引用)。"""
        with self._lock:
            return list(self._klines)

    def runtime_object_count(self) -> int:
        """返回当前实际驻留的缠论结构缓存对象数，不触发任何惰性派生。

        原始 ``Kline`` 不属于本指标；版本变化后尚未重派生的旧缓存仍占内存，因此照实计入。
        """
        with self._lock:
            return (
                len(self._cached_merged)
                + len(self._cached_fenxings)
                + len(self._cached_bis)
                + len(self._cached_xianduans)
                + sum(len(items) for items in self._cached_zhongshus.values())
                + len(self._cached_zhongshu_relations)
                + len(self._cached_zoushi_candidates)
                + sum(
                    len(result.legs) + len(result.zoushis)
                    for result in self._cached_level_zoushi.values()
                )
                + sum(len(items) for items in self._cached_recursive_zhongshus.values())
                + sum(len(items) for items in self._cached_recursive_zoushis.values())
            )

    # ── mutation: 增量喂数据 ──────────────────────────────────────────────

    def add_kline(self, kline: Kline) -> None:
        """末端追加一根 timestamp 严格更大的新 K 线。

        Raises:
            ValueError: K 线字段非法 (§8.2-G), 或 timestamp ≤ 末根 (非单调, §8.1-C)。
        """
        self._validate_kline(kline)
        with self._lock:
            if self._klines and kline.timestamp <= self._klines[-1].timestamp:
                raise ValueError(
                    f"non-monotonic timestamp: {kline.timestamp} "
                    f"<= last {self._klines[-1].timestamp} "
                    f"(use update_last_kline for same-ts update; reset to restart)"
                )
            self._klines.append(kline)
            self._combiner.append(kline)
            self.last_sure_index = self._combiner.stable_index()
            self._version += 1

    def update_last_kline(self, kline: Kline) -> None:
        """同 timestamp 末端更新 (周期内 OHLC 实时变动)。

        空序列时等价于首根 ``add_kline``。

        Raises:
            ValueError: K 线字段非法 (§8.2-G), 或 timestamp 与末根不一致
                (防止把同 timestamp 误 append 成多根假 K 线)。
        """
        self._validate_kline(kline)
        with self._lock:
            if not self._klines:
                self._klines.append(kline)
                self._combiner.append(kline)
            else:
                last = self._klines[-1]
                if kline.timestamp != last.timestamp:
                    raise ValueError(
                        f"update_last_kline timestamp mismatch: {kline.timestamp} "
                        f"!= last {last.timestamp} (use add_kline for new bar)"
                    )
                self._klines[-1] = kline
                # 回退末端原始 K 线影响, 再以新值重判 — 不产假 K 线 (§11)。
                self._combiner.pop_last_kline()
                self._combiner.append(kline)
            self.last_sure_index = self._combiner.stable_index()
            self._version += 1

    def upsert_kline(self, kline: Kline) -> None:
        """``update_last_kline`` 别名 (§4.2): 同 timestamp 末端更新。"""
        self.update_last_kline(kline)

    def add_klines(self, klines: Iterable[Kline]) -> None:
        """冷启动批量加载历史 K 线。

        内部逐根走与 ``add_kline`` **完全一致**的流水线, 保证逐根增量与批量初始化结果
        一致 (golden 自洽, §1.4); **不是**隐式全量重算入口。
        """
        for k in klines:
            self.add_kline(k)

    def initialize(self, klines: Iterable[Kline]) -> None:
        """``add_klines`` 别名 (§4.2): 冷启动批量加载。"""
        self.add_klines(klines)

    def reset(self) -> None:
        """显式清空全部状态 (唯一允许的全量入口, §4.2)。"""
        with self._lock:
            self._klines.clear()
            self._combiner = KlineCombiner(self.period)
            self.last_sure_index = -1
            self._version += 1  # bump 不清零, 防 ABA

    # ── query: 当前结构视图 (read-only, 版本缓存) ─────────────────────────

    def _ensure_derived(self) -> None:
        """版本未变直接命中缓存; 变了重派生一次 (合并 → 分型 → 笔)。须持锁调用。"""
        if self._cache_version == self._version:
            return
        merged = self._combiner.to_merged_klines()
        fenxings = detect_fenxings(merged)
        bis = build_bis(
            merged,
            fenxings,
            self._klines,
            self.chan_config,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        xianduans = build_xianduans(
            bis,
            self.chan_config,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        self._cached_merged = tuple(merged)
        self._cached_fenxings = tuple(fenxings)
        self._cached_bis = tuple(bis)
        self._cached_xianduans = tuple(xianduans)
        self._cache_version = self._version

    def get_merged_klines(self) -> list[MergedKline]:
        """当前合并 K 线序列视图（含轻量 trace; 返回拷贝, 修改不污染缓存）。"""
        with self._lock:
            self._ensure_derived()
            return list(self._cached_merged)

    def get_fenxings(self) -> list[Fenxing]:
        """当前分型序列视图（合并序列上严格识别, 含轻量 trace; 返回拷贝）。"""
        with self._lock:
            self._ensure_derived()
            return list(self._cached_fenxings)

    def get_bis(self) -> list[Bi]:
        """当前笔序列视图（按 chan_config 口径派生, 含轻量 trace; 返回拷贝）。"""
        with self._lock:
            self._ensure_derived()
            return list(self._cached_bis)

    def get_xianduans(self) -> list[Xianduan]:
        """当前线段序列视图（笔序列上特征序列法派生, 含轻量 trace; 返回拷贝）。"""
        with self._lock:
            self._ensure_derived()
            return list(self._cached_xianduans)

    def _ensure_zhongshus(self, source: ZhongShuSource) -> None:
        """按来源惰性派生中枢；须持有 ``self._lock`` 调用。"""
        self._ensure_derived()
        mode = self.chan_config.normalize().zhongshu_mode
        level = (
            ZouShiLevel.L0
            if source is ZhongShuSource.BI
            else ZouShiLevel.L1
        )
        zhongshu_fresh = self._zhongshu_cache_versions.get(source) == self._version
        level_fresh = self._level_zoushi_cache_versions.get(level) == self._version
        if zhongshu_fresh and (mode is not ZhongShuMode.SAME_LEVEL or level_fresh):
            return
        if source is ZhongShuSource.BI:
            legs = legs_from_bis(self._cached_bis, len(self._cached_merged))
        else:
            legs = legs_from_xianduans(self._cached_xianduans, self.chan_config)
        if mode is ZhongShuMode.SAME_LEVEL:
            result = build_same_level_level_result(
                legs,
                source_type=source,
                period=self.period,
                profile_id=self.profile_id,
                config_hash=self.config_hash,
            )
            self._cached_zhongshus[source] = result.zhongshus
            self._zhongshu_cache_versions[source] = self._version
            self._cached_level_zoushi[level] = result
            self._level_zoushi_cache_versions[level] = self._version
            return
        items = build_zhongshus(
            legs,
            source_type=source,
            mode=mode,
            period=self.period,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        self._cached_zhongshus[source] = tuple(items)
        self._zhongshu_cache_versions[source] = self._version

    def get_zhongshus(self, source_type: ZhongShuSource) -> list[ZhongShu]:
        """按输入来源惰性返回当前中枢序列视图（返回拷贝）。"""
        source = ZhongShuSource(source_type)
        with self._lock:
            self._ensure_zhongshus(source)
            return list(self._cached_zhongshus.get(source, ()))

    def _ensure_zoushi(self) -> None:
        """按当前 Engine 版本惰性派生关系与候选；须持锁调用。"""
        if self._zoushi_cache_version == self._version:
            return
        if self.chan_config.zhongshu_mode is not ZhongShuMode.EXTEND:
            # PR-18 正式段中枢关系固定使用阶段 5 已验收的延伸口径；同级分解供
            # B1-B 新走势链消费，不能经直接 Engine 调用悄悄污染旧正式候选。
            self._cached_zhongshu_relations = ()
            self._cached_zoushi_candidates = ()
            self._zoushi_cache_version = self._version
            return
        # 正式走势固定消费段中枢；直接复用须持锁的内部派生入口，避免普通 Lock 重入。
        source = ZhongShuSource.XIANDUAN
        self._ensure_zhongshus(source)
        zhongshus = self._cached_zhongshus.get(source, ())
        result = build_zoushi_candidates(
            zhongshus,
            period=self.period,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        self._cached_zhongshu_relations = result.relations
        self._cached_zoushi_candidates = result.candidates
        self._zoushi_cache_version = self._version

    def get_zhongshu_relations(self) -> list[ZhongShuRelation]:
        """返回正式段中枢的相邻关系视图（返回拷贝）。"""
        with self._lock:
            self._ensure_zoushi()
            return list(self._cached_zhongshu_relations)

    def get_zoushi_candidates(self) -> list[ZouShiCandidate]:
        """返回走势类型结构候选；不表示走势已经完成（返回拷贝）。"""
        with self._lock:
            self._ensure_zoushi()
            return list(self._cached_zoushi_candidates)

    def _ensure_level_zoushi(self, level: ZouShiLevel) -> None:
        """按结构 level 惰性派生 v2 走势；须持锁调用。"""
        if self._level_zoushi_cache_versions.get(level) == self._version:
            return
        source = (
            ZhongShuSource.BI
            if level is ZouShiLevel.L0
            else ZhongShuSource.XIANDUAN
        )
        self._ensure_zhongshus(source)
        if self._level_zoushi_cache_versions.get(level) == self._version:
            return
        if level is ZouShiLevel.L0:
            result = build_l0_zoushis(
                self._cached_bis,
                len(self._cached_merged),
                self._cached_zhongshus.get(source, ()),
                period=self.period,
                profile_id=self.profile_id,
                config_hash=self.config_hash,
            )
        else:
            result = build_l1_zoushis(
                self._cached_xianduans,
                self._cached_zhongshus.get(source, ()),
                cfg=self.chan_config,
                period=self.period,
                profile_id=self.profile_id,
                config_hash=self.config_hash,
            )
        self._cached_level_zoushi[level] = result
        self._level_zoushi_cache_versions[level] = self._version

    def get_level_zoushi_result(self, level: ZouShiLevel) -> LevelBuildResult:
        """返回不可变的 v2 同级别完整构建结果。"""
        resolved = ZouShiLevel(level)
        with self._lock:
            self._ensure_level_zoushi(resolved)
            return self._cached_level_zoushi[resolved]

    def get_zoushis(self, level: ZouShiLevel) -> list[CompletedZouShi]:
        """返回指定结构级别的 frozen 历史及各连续 run 的 forming 尾项拷贝。"""
        result = self.get_level_zoushi_result(level)
        return list(result.zoushis)

    def _ensure_recursive_zhongshus(self, key: RecursiveLevelKey) -> None:
        """按递归身份惰性派生中枢；须持锁调用。"""
        if self._recursive_zhongshu_cache_versions.get(key) == self._version:
            return
        if key.depth != 1 or self.chan_config.zhongshu_mode is not ZhongShuMode.EXTEND:
            self._cached_recursive_zhongshus[key] = ()
            self._recursive_zhongshu_cache_versions[key] = self._version
            return
        level = (
            ZouShiLevel.L0
            if key.origin_level is RecursiveOrigin.L0
            else ZouShiLevel.L1
        )
        self._ensure_level_zoushi(level)
        items = build_recursive_zhongshus_from_level_result(
            self._cached_level_zoushi[level],
            origin_level=key.origin_level,
            depth=key.depth,
            zhongshu_mode=self.chan_config.zhongshu_mode,
            period=self.period,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        self._cached_recursive_zhongshus[key] = tuple(items)
        self._recursive_zhongshu_cache_versions[key] = self._version

    def get_recursive_zhongshus(
        self, origin_level: RecursiveOrigin, depth: int
    ) -> list[RecursiveZhongShu]:
        """返回指定底座与深度的递归中枢视图（返回拷贝）。"""
        key = RecursiveLevelKey(RecursiveOrigin(origin_level), depth)
        with self._lock:
            self._ensure_recursive_zhongshus(key)
            return list(self._cached_recursive_zhongshus.get(key, ()))

    def _ensure_recursive_zoushis(self, key: RecursiveLevelKey) -> None:
        """按递归身份惰性派生走势；与递归中枢共享同一低层结果和版本。"""
        if self._recursive_zoushi_cache_versions.get(key) == self._version:
            return
        self._ensure_recursive_zhongshus(key)
        if key.depth != 1 or self.chan_config.zhongshu_mode is not ZhongShuMode.EXTEND:
            self._cached_recursive_zoushis[key] = ()
            self._recursive_zoushi_cache_versions[key] = self._version
            return
        level = (
            ZouShiLevel.L0
            if key.origin_level is RecursiveOrigin.L0
            else ZouShiLevel.L1
        )
        result = self._cached_level_zoushi[level]
        legs = tuple(
            leg
            for run in recursive_leg_runs_from_level_result(
                result, origin_level=key.origin_level
            )
            for leg in run
        )
        items = build_recursive_zoushis(
            legs,
            self._cached_recursive_zhongshus.get(key, ()),
            origin_level=key.origin_level,
            depth=key.depth,
            zhongshu_mode=self.chan_config.zhongshu_mode,
            period=self.period,
            profile_id=self.profile_id,
            config_hash=self.config_hash,
        )
        self._cached_recursive_zoushis[key] = tuple(items)
        self._recursive_zoushi_cache_versions[key] = self._version

    def get_recursive_zoushis(
        self, origin_level: RecursiveOrigin, depth: int
    ) -> list[RecursiveZouShi]:
        """返回指定底座与深度的递归走势视图（返回拷贝）。"""
        key = RecursiveLevelKey(RecursiveOrigin(origin_level), depth)
        with self._lock:
            self._ensure_recursive_zoushis(key)
            return list(self._cached_recursive_zoushis.get(key, ()))

    # ── internal ─────────────────────────────────────────────────────────

    def _validate_kline(self, kline: Kline) -> None:
        """入口校验 (stage-05-execution-plan.md §8.2-G, 2026-06-07 用户锁定)。

        - symbol / period 必须与本引擎实例一致 → 否则抛 ``ValueError``
          (§4.4 一实例一 ``(symbol, period)``;§7 多 symbol/period 不串状态)。
        - NaN / Inf / 负价 / low > high → 拒绝抛 ``ValueError``。
        - 零成交量 / 跳空缺口 → 放行 (合法行情)。
        - timestamp 倒退不在此处理, 由 ``add_kline`` / ``update_last_kline`` 各自判 (§8.1-C)。

        Raises:
            ValueError: K 线归属不符或字段非法。
        """
        if kline.symbol != self.symbol:
            raise ValueError(
                f"kline symbol {kline.symbol!r} != engine {self.symbol!r} "
                f"(one engine per (symbol, period), §4.4)"
            )
        if kline.period != self.period:
            raise ValueError(
                f"kline period {kline.period!r} != engine {self.period!r} "
                f"(one engine per (symbol, period), §4.4)"
            )
        for name, value in (
            ("open", kline.open),
            ("high", kline.high),
            ("low", kline.low),
            ("close", kline.close),
            ("volume", kline.volume),
        ):
            if math.isnan(value) or math.isinf(value):
                raise ValueError(f"invalid kline: {name} is NaN/Inf ({kline.symbol})")
        if min(kline.open, kline.high, kline.low, kline.close) < 0:
            raise ValueError(f"invalid kline: negative price ({kline.symbol})")
        if kline.low > kline.high:
            raise ValueError(
                f"invalid kline: low {kline.low} > high {kline.high} ({kline.symbol})"
            )
