"""缠论算法引擎接口 (Protocol) — 阶段 5 PR-1 锁定接口语义。

依据:
- decision-0001 v1.4 §12.3 (口径优先链 = 缠论原文 > 用户确认的本项目口径 > 本项目自主实现;
  参考项目 chan.py-main / czsc / chanlun-pro 无固定优先级, 只作对照 / 启发 / 差异发现来源)
- stage-05-execution-plan.md §4.2 (ChanEngine 接口语义) / §8.1-C (非单调 ts 抛错)
- docs/05 §3.3 (全量重算被悄悄引入风险)

**接口设计层防御** (§1.4 / §4.2 硬纪律):
只暴露**增量** API (``add_kline`` / ``update_last_kline``) + 批量冷启动 (``add_klines``,
内部走逐根一致流水线) + 显式 ``reset()``;**不**暴露任何隐式全量重算入口。

**Kline 来源** (阶段 4 起): 算法层不自定义 Kline, 统一 import 标准模型
``cc.data.models.Kline`` (timestamp = Unix 秒)。验收硬标准: 图表/算法/回放/回测共用一套。

具体实现见 ``cc.algo.engine.ChanEngine``;阶段 5 仅单周期独立计算 (§8.1-H),
**不产买卖点信号** (买卖点归阶段 6, §1.5)。
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from cc.algo.models import (
    Bi,
    CompletedZouShi,
    Fenxing,
    MergedKline,
    RecursiveOrigin,
    RecursiveZhongShu,
    RecursiveZouShi,
    Xianduan,
    ZhongShu,
    ZhongShuRelation,
    ZhongShuSource,
    ZouShiCandidate,
    ZouShiLevel,
)
from cc.data.models import Kline

__all__ = ["ChanEngineProtocol", "Kline"]


class ChanEngineProtocol(Protocol):
    """缠论算法引擎接口 (增量优先)。

    喂数据语义 (§4.2):

    - ``add_kline(k)``: 仅 timestamp **严格更大**的新 K 线追加;非单调 → ``ValueError`` (§8.1-C)。
    - ``update_last_kline(k)`` / ``upsert_kline(k)``: **同 timestamp** 末端更新 (周期内变动)。
    - ``add_klines(seq)`` / ``initialize(seq)``: 冷启动批量, 内部走逐根一致流水线;
      **不得**作隐式全量重算入口。
    - ``reset()``: **唯一**允许的全量清空入口。

    查询方法返回当前结构视图 (read-only)。
    """

    def add_kline(self, kline: Kline) -> None:
        """末端追加一根 timestamp 严格更大的新 K 线 (非单调 → ``ValueError``)。"""
        ...

    def update_last_kline(self, kline: Kline) -> None:
        """同 timestamp 末端更新 (timestamp 不一致 → ``ValueError``)。"""
        ...

    def upsert_kline(self, kline: Kline) -> None:
        """``update_last_kline`` 别名。"""
        ...

    def add_klines(self, klines: Iterable[Kline]) -> None:
        """冷启动批量加载 (内部逐根一致流水线, 非全量重算入口)。"""
        ...

    def initialize(self, klines: Iterable[Kline]) -> None:
        """``add_klines`` 别名。"""
        ...

    def reset(self) -> None:
        """显式清空所有状态 (唯一允许的全量入口)。"""
        ...

    def get_merged_klines(self) -> list[MergedKline]:
        """当前合并 K 线序列视图。"""
        ...

    def get_fenxings(self) -> list[Fenxing]:
        """当前分型序列视图。"""
        ...

    def get_bis(self) -> list[Bi]:
        """当前笔序列视图。"""
        ...

    def get_xianduans(self) -> list[Xianduan]:
        """当前线段序列视图。"""
        ...

    def get_zhongshus(self, source_type: ZhongShuSource) -> list[ZhongShu]:
        """按笔或线段来源返回当前中枢序列视图。"""
        ...

    def get_zhongshu_relations(self) -> list[ZhongShuRelation]:
        """返回正式段中枢的相邻关系视图。"""
        ...

    def get_zoushi_candidates(self) -> list[ZouShiCandidate]:
        """返回走势类型结构候选（不表示完成）。"""
        ...

    def get_zoushis(self, level: ZouShiLevel) -> list[CompletedZouShi]:
        """返回指定结构级别的 v2 走势。"""
        ...

    def get_recursive_zhongshus(
        self, origin_level: RecursiveOrigin, depth: int
    ) -> list[RecursiveZhongShu]:
        """返回指定底座与深度的高一级递归中枢。"""
        ...

    def get_recursive_zoushis(
        self, origin_level: RecursiveOrigin, depth: int
    ) -> list[RecursiveZouShi]:
        """返回指定底座与深度的高一级递归走势。"""
        ...
