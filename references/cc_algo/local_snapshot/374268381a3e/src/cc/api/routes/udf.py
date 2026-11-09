"""UDF datafeed endpoints (TradingView Charting Library 数据接口).

阶段 4 PR-4 起, /tv/symbols 和 /tv/history 接通真实 K 线:
- symbol 为规范串 "market:code" (如 "shfe:rb2501" / "binance:BTC/USDT") → 走对应 adapter + DuckDB。
- symbol 为非规范格式 (如 "TEST") → 降级返回占位响应 (向后兼容现有 smoke test)。

/tv/history 取数 = **统一 materialize-once + 纯读供数** (decision-0027):
- 期货与 Binance 共用一条路径: 每个 (symbol, period) 只物化一次 (两段式: 首触浅拉秒开 +
  后台深拉填满 TV scrollback), 之后纯读 DuckDB; 末端用右缘节流补拉追平实时。
- 不在 TV 交互级联里逐段补拉; 旧"按 get_gaps 逐段填缺"路由已退出主路径 (Binance cold-cache
  不再进 get_gaps; repo.get_gaps 方法保留但不用于本端点, decision-0027 v7)。
凭证缺失 (adapter=None) 时仅返回已缓存数据, 不崩溃; adapter 异常记录日志后降级为缓存。

UDF 协议参考: TradingView Charting Library 官方文档与 example/kline-chart/kline_app/
里的 Flask 实现 (思路借鉴, 不复用代码, decision-0001 v1.1 / decision-0016 §6)。
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from cc.data.catalog import SymbolEntry
from cc.data.models import Market, Symbol
from cc.data.periods import from_tv, to_seconds
from cc.data.repair import get_repair_manager
from cc.data.service import get_adapter, get_catalog, get_ccxt_adapter, get_repo

logger = logging.getLogger(__name__)
router = APIRouter()

# ── 期货市场集合 ─────────────────────────────────────────────────────────────

_FUTURES_MARKETS: frozenset[Market] = frozenset(
    {Market.SHFE, Market.DCE, Market.CZCE, Market.CFFEX, Market.INE, Market.GFEX}
)
_EXCHANGE_NAME: dict[Market, str] = {
    Market.SHFE: "SHFE",
    Market.DCE: "DCE",
    Market.CZCE: "CZCE",
    Market.CFFEX: "CFFEX",
    Market.INE: "INE",
    Market.GFEX: "GFEX",
    Market.BINANCE: "Binance",
}
# 任务六: 期货交易所中文全称（商品信息弹窗 exchange 字段；listed_exchange 仍用英文代码）
_EXCHANGE_CN: dict[Market, str] = {
    Market.SHFE: "上期所",
    Market.DCE: "大商所",
    Market.CZCE: "郑商所",
    Market.CFFEX: "中金所",
    Market.INE: "能源中心",
    Market.GFEX: "广期所",
    Market.BINANCE: "Binance",
}

# ── Pydantic 响应模型 ────────────────────────────────────────────────────────


class UDFConfig(BaseModel):
    """TradingView UDF config response."""

    supported_resolutions: list[str] = Field(
        # 任务七: 含 2/3 分钟、1W、1M（TV 周期菜单显示，期货受限周期 history 返回 no_data）
        default_factory=lambda: ["1", "2", "3", "5", "15", "30", "60", "240", "D", "1W", "1M"]
    )
    supports_group_request: bool = False
    supports_marks: bool = True
    supports_search: bool = True
    supports_timescale_marks: bool = False
    supports_time: bool = True
    # TV 内置「商品代码搜索」对话框的交易所筛选（用户点3）
    exchanges: list[dict[str, str]] = Field(default_factory=lambda: [
        {"value": "", "name": "全部", "desc": "全部交易所"},
        {"value": "Binance", "name": "Binance", "desc": "币安"},
        {"value": "SHFE", "name": "SHFE", "desc": "上期所"},
        {"value": "DCE", "name": "DCE", "desc": "大商所"},
        {"value": "CZCE", "name": "CZCE", "desc": "郑商所"},
        {"value": "CFFEX", "name": "CFFEX", "desc": "中金所"},
        {"value": "INE", "name": "INE", "desc": "能源中心"},
        {"value": "GFEX", "name": "GFEX", "desc": "广期所"},
    ])
    # TV 内置搜索对话框的类型筛选 tab（全部/股票/期货/指数/外汇/加密货币）
    # 当前仅期货(futures)/加密货币(crypto)有内容，股票/指数/外汇为占位预留
    symbols_types: list[dict[str, str]] = Field(default_factory=lambda: [
        {"name": "全部", "value": ""},
        {"name": "股票", "value": "stock"},
        {"name": "期货", "value": "futures"},
        {"name": "指数", "value": "index"},
        {"name": "外汇", "value": "forex"},
        {"name": "加密货币", "value": "crypto"},
    ])


class UDFSymbol(BaseModel):
    """TradingView symbol info response."""

    name: str
    ticker: str = ""
    full_name: str = ""
    description: str
    exchange: str
    listed_exchange: str = ""  # 任务六: 上市交易所（英文代码，如 CZCE）
    type: str
    timezone: str = "Asia/Shanghai"
    minmov: int = 1
    pricescale: int = 100
    has_intraday: bool = True
    visible_plots_set: Literal["ohlcv", "ohlc", "c", "hlc"] = "ohlcv"
    supported_resolutions: list[str]
    # 数据源**原生供给**的分钟级周期 (分钟数字串)。缺此字段时 TV 默认只认部分周期、把其余
    # 周期由更细周期合成 → 发错 resolution (3m→1 / 4h→60 / 1w→1D)。须列全本端点原生周期。
    intraday_multipliers: list[str] = Field(default_factory=list)
    # 周/月原生供给 (否则 TV 用日线合成周线 → 1w 发 1D)。supported_resolutions 仍决定菜单显示。
    has_weekly_and_monthly: bool = False
    session: str = "24x7"


class UDFHistory(BaseModel):
    """TradingView history response (OHLCV 列数组, 时间戳秒)."""

    s: Literal["ok", "no_data", "error"] = "ok"
    t: list[int] = Field(default_factory=list)
    o: list[float] = Field(default_factory=list)
    h: list[float] = Field(default_factory=list)
    low: list[float] = Field(default_factory=list, alias="l")
    c: list[float] = Field(default_factory=list)
    v: list[float] = Field(default_factory=list)
    # UDF no_data 协议: 请求区间无数据但更早处有数据时, 指向最近一根时间戳,
    # 官方 UDFCompatibleDatafeed 据此跳回有数据处重新请求 (避免空图 + 重试风暴)。
    nextTime: int | None = None  # noqa: N815 — UDF 协议字段名 (camelCase)

    model_config = {"populate_by_name": True}


class UDFMarks(BaseModel):
    """TradingView marks response (空数组占位)."""

    id: list[int | str] = Field(default_factory=list)
    time: list[int] = Field(default_factory=list)
    color: list[str] = Field(default_factory=list)
    text: list[str] = Field(default_factory=list)
    label: list[str] = Field(default_factory=list)
    labelFontColor: list[str] = Field(default_factory=list)
    minSize: list[int] = Field(default_factory=list)


# ── 内部辅助 ─────────────────────────────────────────────────────────────────


# ── 期货"秒开"物化层 (两段式深拉) ─────────────────────────────────────────────
# 根因: tqsdk 线程绑定 → 仅 1 worker 串行所有拉取；TV 加载一个合约会串行发 ~12 个请求，
# 每个缺缓存就触发拉取，全堵一条线 → 数十秒。
# 对策(两段式): 首触**同步**只拉一小段(_MATERIALIZE_FIRST)立刻出图=秒开, 同时**后台异步**
# 深拉到 _MATERIALIZE_BARS 补满可回溯深度。级联里后到的请求见 in-flight/READY → 纯读 DB 秒回,
# 把级联坍缩成"1 次小拉(前台) + 1 次深拉(后台)"。
_MATERIALIZE_FIRST = 960  # 首触同步浅拉根数 (够首屏+少量缓冲, ~0.3-0.5s 出图)
_MATERIALIZE_BARS = 8964  # 后台深拉满深度 (= tqsdk _MAX_BARS, 覆盖 TV 全部 scrollback)
_MATERIALIZE_RETRY_S = 30.0  # 物化失败(超时/空)退避秒数, 防失败重试风暴
# per-(canonical, period) 物化锁 / READY(深拉完) / in-flight(后台深拉中) / 失败退避到期
_materialize_locks: dict[tuple[str, str], asyncio.Lock] = {}
_materialized_ready: set[tuple[str, str]] = set()
_materialize_inflight: set[tuple[str, str]] = set()
_materialize_failed_until: dict[tuple[str, str], float] = {}
# 后台深拉任务引用 (防止被 GC; 完成后自动移除)
_bg_tasks: set[asyncio.Task[None]] = set()

_RIGHT_FILL_THROTTLE_S = 10.0  # 同 symbol+period 右补最小间隔秒; 抑制收盘期白拉, 不碍 30s 轮询
# 右缘缺口超此根数(≈ccxt 单页上限)时改走 fetch_recent 直补最新端, 不从旧 cached_end 慢慢分页补。
_RIGHT_FILL_MAX_GAP = 1000
# (canonical, step_seconds) → 上次右补 monotonic 时刻
_last_right_fill: dict[tuple[str, int], float] = {}


async def _deep_fill(adapter: Any, repo: Any, sym: Symbol, period: str, to: int) -> None:
    """后台深拉: 把 (sym, period) 补满到 _MATERIALIZE_BARS 深度并写权威标记。

    首触浅拉已让图出来; 本任务在后台补满可回溯历史。
    「深拉非空 + save + 读回确有数据」三连后才写标记并置 READY。
    深拉为空(瞬时失败)或读回为空 → 只记退避窗口、**绝不**凭浅拉数据误标 READY
    (否则后续永远纯读 960 浅缓存、不再补满)；退避到期后由下次请求重做整套两段式。
    无论成败都清 in-flight。
    """
    key = (sym.canonical, period)
    try:
        fetched = await adapter.fetch_recent(sym, period, to, _MATERIALIZE_BARS)
        if not fetched:  # 深拉空 = 瞬时失败 → 退避重试, 不凭浅拉数据标 READY (Codex ⚠1)
            _materialize_failed_until[key] = time.monotonic() + _MATERIALIZE_RETRY_S
            return
        # decision-0030 §7.B P3 (Codex P3-r1 ⚠1): 深拉经原子版本分类写入——若覆盖/补入 < max_ts 的
        # 历史 OHLC (如主连价格调整) 则升 kline_revision, overlay 重建; 纯右缘/首次全 tail 不升。
        await repo.save_klines_versioned(sym.canonical, period, fetched, insert_only=False)
        check = await repo.get_range(sym, period, fetched[0].timestamp, to)
        if check:
            await repo.mark_materialized(sym, period, fetched[0].timestamp, to)
            _materialized_ready.add(key)
        else:
            _materialize_failed_until[key] = time.monotonic() + _MATERIALIZE_RETRY_S
    except Exception:  # noqa: BLE001 — 后台任务: 失败记退避并记录, 不抛(无调用方接)
        _materialize_failed_until[key] = time.monotonic() + _MATERIALIZE_RETRY_S
        logger.warning("deep fill failed: %s %s", sym.canonical, period, exc_info=True)
    finally:
        _materialize_inflight.discard(key)


async def _ensure_materialized(
    adapter: Any, repo: Any, sym: Symbol, period: str, to: int
) -> None:
    """确保 (sym, period) 至少完成首触浅拉 (两段式秒开核心)。

    权威标记 = repo.materialized 表;内存 READY/in-flight 仅加速。判定优先级:
    ① READY(深拉完) / in-flight(后台深拉中) → 直接返回, 纯读 DB;
    ② 退避窗口内 → 返回, 读已有 DB;
    ③ 权威表命中 → 置 READY 返回;
    ④ 否则抢锁: **同步**浅拉 _MATERIALIZE_FIRST 根(快速出图), 置 in-flight + 派后台深拉任务。

    不设"按 min_ts 足够早就补标记"的迁移捷径(Codex ⚠2): 单点弱信号会被零星残留行骗过、
    误标 READY 而缓存其实不完整。统一走浅拉 + 后台深拉 + 三连写标记; 持久 materialized 表
    保证重启后不重做, 故"已深的旧缓存"至多在首次触达时多跑一次 backgrounded 深拉, 成本可忽略。
    """
    key = (sym.canonical, period)
    if key in _materialized_ready or key in _materialize_inflight:
        return
    if time.monotonic() < _materialize_failed_until.get(key, 0.0):
        return  # 退避窗口内: 不拉, 调用方降级为读已有 DB
    lock = _materialize_locks.setdefault(key, asyncio.Lock())
    async with lock:
        if key in _materialized_ready or key in _materialize_inflight:
            return  # 等锁期间已被前一个持锁者处理
        if await repo.is_materialized(sym, period):  # 权威表命中(重启后仍有效)
            _materialized_ready.add(key)
            return
        # 首触: 同步浅拉一小段, 快速出图 (显式 count, 不靠 start 推断)
        try:
            shallow = await adapter.fetch_recent(sym, period, to, _MATERIALIZE_FIRST)
        except Exception:
            _materialize_failed_until[key] = time.monotonic() + _MATERIALIZE_RETRY_S
            raise  # 由调用方 except 记录并降级为读缓存; 退避防下一批级联立刻重拉
        if not shallow:
            _materialize_failed_until[key] = time.monotonic() + _MATERIALIZE_RETRY_S
            return
        # 浅拉同经原子版本分类写入 (P3): 空库首触全 tail 不升; 若覆盖 < max_ts 历史则升版。
        await repo.save_klines_versioned(sym.canonical, period, shallow, insert_only=False)
        # 置 in-flight 后派后台深拉: 期间后到的级联请求见 in-flight → 只读 DB, 不再拉
        _materialize_inflight.add(key)
        task = asyncio.create_task(_deep_fill(adapter, repo, sym, period, to))
        _bg_tasks.add(task)
        task.add_done_callback(_bg_tasks.discard)


async def cancel_background_tasks() -> None:
    """取消并等待所有在跑的后台深拉任务 (FastAPI shutdown 调用; Codex r1 💡3 / r2 💡1)。"""
    tasks = list(_bg_tasks)
    for task in tasks:
        task.cancel()
    if tasks:  # 等待取消落定, 让关闭可观测 (CancelledError 由 return_exceptions 吞掉)
        await asyncio.gather(*tasks, return_exceptions=True)
    _bg_tasks.clear()


async def _refresh_right_edge(
    adapter: Any, repo: Any, sym: Symbol, period: str, to: int, step: int
) -> None:
    """物化后的右缘实时补拉 (节流)。

    缓存末根落后 to 一个周期以上时, 拉 [cached_end, to]：既追平新尾部，也回显校验已经
    走完一个完整周期的 cached_end。若 cached_end 仍是此前保存的形成中快照，只最终化这一根；
    cached_end 之前的旧窗口行一律丢弃，避免 TQSDK 锚定 now 的大窗口反复覆盖历史。

    同 symbol+period 在 _RIGHT_FILL_THROTTLE_S 内只补一次(收盘期 to 持续前进而末根停在
    收盘, 否则每请求白拉)。
    刚深拉完 cached_end≈to → 直接跳过, 首开不产生多余拉取。

    大缺口 (>_RIGHT_FILL_MAX_GAP 根): **Binance 不再向主表直写最新窗口**(decision-0030 §7.A /
    Codex r1-⚠1)——否则出现"旧连续段 + 最新 960、中间空"的半段岛; 保留旧连续缓存, 交后台连续修复
    staging+原子合并补齐中间。期货(tqsdk)不做 P2 修复, 保留既有秒开直补 (fetch_recent 锚定 now
    返回最近 count 根, 无内部缺口语义)。小缺口(≤上限)Binance/期货均走 fetch_history 连续追尾(无岛)。
    """
    latest = await repo.get_latest(sym, period, 1)
    if not latest:
        return
    cached_end = latest[-1].timestamp
    if to - cached_end < step:
        return
    rkey = (sym.canonical, step)
    rnow = time.monotonic()
    if rnow - _last_right_fill.get(rkey, 0.0) < _RIGHT_FILL_THROTTLE_S:
        return
    _last_right_fill[rkey] = rnow
    gap_bars = (to - cached_end) // step
    if gap_bars > _RIGHT_FILL_MAX_GAP and hasattr(adapter, "fetch_recent"):
        # decision-0030 §7.A / Codex ⚠2: Binance 大缺口**不再向主表直写最新 960 根**——否则主库
        # 出现"旧连续段 + 最新 960、中间空"的半段岛 (违反"合并前只见全旧或全新")。保留旧连续缓存,
        # 交后台连续修复 (staging + 原子合并) 补齐中间。期货不做 P2 修复 → 保留既有秒开直补。
        if sym.market == Market.BINANCE:
            return
        right = await adapter.fetch_recent(sym, period, to, _MATERIALIZE_FIRST)
    else:
        # 起点包含 cached_end：形成中末根只有在下一次右补时才能拿到最终 OHLCV。若仍从
        # cached_end+step 请求，TQSDK 虽会回显大窗口但下方裁剪又会丢掉 cached_end，导致
        # 形成中快照永久冻结在数据库（D4-C 实图：3 根重叠 OHLC 冲突）。
        right = await adapter.fetch_history(sym, period, cached_end, to)
    if right:
        # tqsdk 的 fetch_history 以 ``start`` 只计算 count，实际会返回“锚定当前时刻的最近 N 根”，
        # 其中可能夹带 < cached_end 的既有历史。右缘补拉职责只允许“最终化 cached_end + 追加
        # 尾部”；若把更早旧行一并 upsert，save_klines_versioned 会每次判成 internal 并升
        # revision，进而形成：
        # repair-status 发现升版 → 图表重载 → history 再升版 → 15 秒后再次重载 的自激闪烁。
        # 因此按真实 cached_end 二次裁剪，并先对比数据库末根：相同锚点不重写、不升版；变化锚点
        # 与新尾部在一次事务中写入并只升版一次，使依赖旧形成中快照的结构可靠失效。
        visible = {kline.timestamp: kline for kline in right if kline.timestamp >= cached_end}
        anchor = visible.get(cached_end)
        to_save = []
        if anchor is not None and anchor != latest[-1]:
            to_save.append(anchor)
        to_save.extend(visible[ts] for ts in sorted(visible) if ts > cached_end)
        if to_save:
            await repo.save_klines_versioned(
                sym.canonical, period, to_save, insert_only=False
            )


def _auto_repair_enabled() -> bool:
    """kill switch (Codex ⚠4): CC_KLINE_AUTO_REPAIR=0/false/no/off 一键关闭后台自动修复。默认开。"""
    return os.environ.get("CC_KLINE_AUTO_REPAIR", "1").strip().lower() not in (
        "0", "false", "no", "off",
    )


def _schedule_repair_bg(sym: Symbol, period: str, requested_to: int) -> None:
    """/tv/history 调度门槛 (decision-0030 §16-P2)。**完全 fire-and-forget, 不加入秒开临界路径**。

    仅默认库 Binance(7×24)自动修复; 期货休市不自动补(§5)、1M 自然月不按网格。门槛判定
    (coverage=verified + 落后 + 右缘) 与代际 +1、拉取、合并全在后台任务里做, 前台立即返回
    已有 DB K 线。单飞去重: 同作用域并发请求复用同一任务, 不重复拉取/合并。
    kill switch 关闭 → 不调度。
    """
    if not _auto_repair_enabled() or sym.market != Market.BINANCE or period == "1M":
        return

    async def _run() -> None:
        try:
            await get_repair_manager().maybe_schedule(
                get_repo(), get_ccxt_adapter(), sym, period,
                requested_to=requested_to, now=int(time.time()), is_crypto=True,
            )
        except Exception:  # noqa: BLE001 — 后台调度失败不影响供数, 记录降级
            logger.warning("repair schedule failed: %s %s", sym.canonical, period, exc_info=True)

    task = asyncio.create_task(_run())
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


async def ensure_period_data(sym: Symbol, period: str, to: int) -> None:
    """确保 (sym, period) 数据物化到 repo（两段式秒开 + 右缘节流补拉）。

    供 /tv/history 与 /api/overlay/snapshot **共用**：overlay 据此自给数据，不必依赖图表
    先加载该周期（修 PR-3 观测的 1w/3m/4h overlay 无数据）。adapter 缺失/异常时降级为仅缓存。
    """
    repo = get_repo()
    adapter = get_ccxt_adapter() if sym.market == Market.BINANCE else get_adapter()
    if adapter is None:
        return
    try:
        await _ensure_materialized(adapter, repo, sym, period, to)
        if (sym.canonical, period) not in _materialize_inflight:
            await _refresh_right_edge(adapter, repo, sym, period, to, to_seconds(period))
    except Exception:  # noqa: BLE001 — 物化失败降级为仅缓存，记录后继续
        logger.warning(
            "ensure_period_data failed: %s %s", sym.canonical, period, exc_info=True
        )


# 任务七: 全周期 TV resolution（config 全局 / 币安 symbol）
_ALL_RESOLUTIONS = ["1", "2", "3", "5", "15", "30", "60", "240", "D", "1W", "1M"]
# ⚠1: 期货(tqsdk)实际支持周期的 TV resolution，避免"可选但不可用"。
# 含 1W: tqsdk 支持日线整数倍周期(≤28 天), 周线=7×86400 在范围内, 原生返回数据(自然周口径)。
# 不含 2m(tqsdk 无 120s)、1M(=30 天>28 天上限, 需日线合成, 留后续 PR decision-0027 §5)。
# TV 按 symbol 级 supported_resolutions 覆盖 config 全局值，期货菜单仅显示这些。
_FUTURES_RESOLUTIONS = ["1", "3", "5", "15", "30", "60", "240", "D", "1W"]


def _build_symbol_info(sym: Symbol, entry: SymbolEntry | None = None) -> UDFSymbol:
    """规范 Symbol → UDFSymbol。

    任务六: 期货 description 用 catalog 中文名（红枣2609/红枣主连），exchange 用中文交易所名
    （郑商所），listed_exchange 用英文代码（CZCE）。catalog 查不到时退回 code。
    ⚠1: 期货 supported_resolutions 仅含 tqsdk 实际可用周期（含 1W；不暴露 2m/1M）。
    """
    is_futures = sym.market in _FUTURES_MARKETS
    description = entry.name if entry else sym.code
    if is_futures:
        exchange = _EXCHANGE_CN.get(sym.market, sym.market.value.upper())  # 郑商所
        listed = _EXCHANGE_NAME.get(sym.market, sym.market.value.upper())  # CZCE
        resolutions = _FUTURES_RESOLUTIONS
    else:
        exchange = _EXCHANGE_NAME.get(sym.market, sym.market.value.upper())  # Binance
        listed = exchange
        resolutions = _ALL_RESOLUTIONS
    return UDFSymbol(
        name=sym.canonical,
        ticker=sym.canonical,
        full_name=sym.canonical,
        description=description,
        exchange=exchange,
        listed_exchange=listed,
        type="futures" if is_futures else "crypto",
        timezone="Asia/Shanghai" if is_futures else "UTC",
        session="24x7",  # 近似值; 期货日盘+夜盘时段在阶段 5 细化
        supported_resolutions=resolutions,  # 期货 9(含1W) / 币安 11（⚠1）
        # 原生分钟级周期 = supported 里的纯数字码 (1/3/5/.../240); 周/月原生 = 含 1W/1M。
        # 修 3m→1 / 4h→60 / 1w→1D: 声明原生供给, TV 不再用更细周期合成。
        intraday_multipliers=[r for r in resolutions if r.isdigit()],
        has_weekly_and_monthly=any(r in ("1W", "1M") for r in resolutions),
    )


def _fallback_symbol_info(symbol: str) -> UDFSymbol:
    """非规范 symbol 降级占位 (向后兼容; 阶段 4 之前的 smoke test 依赖此路径)."""
    return UDFSymbol(
        name=symbol,
        ticker=symbol,
        full_name=symbol,
        description=symbol,
        exchange="UNKNOWN",
        type="stock",
        timezone="Asia/Shanghai",
        supported_resolutions=_ALL_RESOLUTIONS,
        intraday_multipliers=[r for r in _ALL_RESOLUTIONS if r.isdigit()],
        has_weekly_and_monthly=True,
    )


# ── 路由 ─────────────────────────────────────────────────────────────────────


@router.get("/config")
async def config() -> UDFConfig:
    """UDF datafeed config."""
    return UDFConfig()


@router.get("/symbols")
async def symbol_info(symbol: str) -> UDFSymbol:
    """UDF symbol info（TV resolveSymbol / 商品信息弹窗数据源）。

    规范串 → 真实信息（期货查 catalog 取中文名/交易所，任务六）。
    非规范串 → 降级占位响应（向后兼容）。
    """
    try:
        sym = Symbol.parse(symbol)
    except ValueError:
        return _fallback_symbol_info(symbol)
    # resolveSymbol 只读已有缓存(lookup_cached), **绝不触发 catalog 全量发现**(decision-0027 §5
    # catalog cold-start 补丁): 否则首次切品种会被 tqsdk 全合约 + ccxt load_markets(~20s)阻塞。
    # 缓存未就绪 → entry=None → _build_symbol_info 退回 code, 不阻塞; 目录由后台预热/其它端点填充。
    entry = get_catalog().lookup_cached(sym.canonical)
    return _build_symbol_info(sym, entry)


@router.get("/history")
async def history(
    symbol: str,
    resolution: str,
    from_: int = Query(0, alias="from"),
    to: int = 0,
    countback: int | None = None,
) -> UDFHistory:
    """UDF history — 统一 materialize-once + 纯读供数 (stage-04 §3.3 / decision-0027).

    1. 解析 symbol + resolution; 非规范格式或未知 resolution 返回 no_data。
    2. 取数(期货与 Binance 共用): 物化一次(两段式: 首触浅拉秒开 + 后台深拉补满) + 右缘节流补拉;
       不在交互级联里逐段补拉, 旧 get_gaps 逐段路由已退出本端点 (decision-0027 v7)。
    3. 从 DuckDB 读: 传 countback 用 get_before 截断, 否则 get_range [from_, to]; 无数据 no_data。

    adapter=None (凭证缺失) 时仅服务缓存数据, 不崩溃; adapter 异常记录日志后降级。
    """
    if to < from_:  # 输入校验 (PR-3 Codex 💡1)
        return UDFHistory(s="no_data")

    try:
        sym = Symbol.parse(symbol)
        period = from_tv(resolution)
    except ValueError:
        return UDFHistory(s="no_data")

    repo = get_repo()
    # 统一物化一次(两段式: 首触浅拉秒开 + 后台深拉填满 TV scrollback 缓冲) + 右缘节流补拉。
    # 期货与 Binance 共用此路径(decision-0027 §5)。与 overlay 共用 ensure_period_data。
    await ensure_period_data(sym, period, to)
    # decision-0030 P2: 后台连续修复调度门槛 (fire-and-forget, 不阻塞秒开; 仅 Binance/默认库)。
    _schedule_repair_bg(sym, period, to)

    # countback: TV 要"截至 to 往前 N 根"——按 countback 截断, 减少无数据区间的重复请求。
    if countback and countback > 0:
        klines = await repo.get_before(sym, period, to, countback)
    else:
        klines = await repo.get_range(sym, period, from_, to)
    if not klines:
        # 请求区间无数据：若已有更早的 bar（收盘/远月合约最后一根早于请求下界），
        # 返回 nextTime 指向最近一根，TV 据 UDF 规范跳回有数据处重新请求，避免空图 + 重试风暴。
        latest = await repo.get_latest(sym, period, 1)
        if latest and latest[-1].timestamp < from_:
            return UDFHistory(s="no_data", nextTime=latest[-1].timestamp)
        return UDFHistory(s="no_data")

    return UDFHistory.model_validate(
        {
            "s": "ok",
            "t": [k.timestamp for k in klines],
            "o": [k.open for k in klines],
            "h": [k.high for k in klines],
            "l": [k.low for k in klines],
            "c": [k.close for k in klines],
            "v": [k.volume for k in klines],
        }
    )


@router.get("/marks")
async def marks(
    symbol: str,
    resolution: str,
    from_: int = Query(0, alias="from"),
    to: int = 0,
) -> UDFMarks:
    """UDF marks (买卖点标记阶段 5 起接通)."""
    _ = (symbol, resolution, from_, to)
    return UDFMarks()


@router.get("/time")
async def server_time() -> int:
    """UDF server time (Unix seconds, TV widget 用于时区同步)."""
    return int(time.time())


_EXCHANGE_OF: dict[Market, str] = {
    Market.SHFE: "SHFE", Market.DCE: "DCE", Market.CZCE: "CZCE",
    Market.CFFEX: "CFFEX", Market.INE: "INE", Market.GFEX: "GFEX",
    Market.BINANCE: "Binance",
}


def _entry_to_udf(e: SymbolEntry) -> dict[str, str]:
    """SymbolEntry → UDF SearchSymbolResultItem。"""
    return {
        "symbol": e.canonical,
        "full_name": e.canonical,
        "ticker": e.canonical,
        "description": e.name,
        "exchange": _EXCHANGE_OF.get(e.market, e.market.value.upper()),
        "type": "futures" if e.is_futures else "crypto",
    }


@router.get("/search")
async def symbol_search(
    query: str = "",
    type: str = "",    # noqa: A002 — TV UDF 协议保留参数名
    exchange: str = "",
    limit: int = 30,
) -> list[dict[str, str]]:
    """TV 原生搜索框数据源 (UDF /search)，基于动态标的目录 (stage-04 §6).

    目录由行情源动态发现（期货 tqsdk / 数字货币 ccxt），TTL 缓存。
    按 query 关键字过滤；大小写不敏感。用户也可直接输入规范串直接加载。
    """
    q = query.strip().lower()
    entries = await asyncio.to_thread(get_catalog().all_entries)
    results = [_entry_to_udf(e) for e in entries]
    if q:
        results = [
            r for r in results
            if q in r["symbol"].lower()
            or q in r["description"].lower()
            or q in r["exchange"].lower()
        ]
    if type:
        results = [r for r in results if r["type"] == type]
    if exchange:
        results = [r for r in results if r["exchange"].lower() == exchange.lower()]
    return results[:limit]


def _build_catalog(catalog: Any) -> dict[str, Any]:
    """组装目录树 + 每源发现状态 (在 worker 线程内执行同步发现)。"""
    entries = catalog.all_entries()
    status = catalog.source_status()  # 复用缓存，不重复拉取
    futures: dict[str, list[dict[str, str]]] = {}
    crypto: list[dict[str, str]] = []
    for e in entries:
        item = _entry_to_udf(e)
        if e.is_futures:
            futures.setdefault(_EXCHANGE_OF[e.market], []).append(item)
        else:
            crypto.append(item)
    return {
        "crypto": {"Binance": crypto},
        "futures": futures,
        "total": len(entries),
        # 每源发现状态: ok=False 表示本次发现失败 (网络/账号), 前端应提示而非当作"无标的"
        "status": status,
    }


@router.get("/catalog")
async def symbol_catalog() -> dict[str, Any]:
    """市场目录树 (stage-04 §6): 数字货币 / 国内期货 → 交易所 → 合约 + 每源状态。

    前端市场目录 UI 数据源。一次返回全部标的（TTL 缓存），前端本地分组展示。
    status 字段区分"真实空目录"与"发现失败"，前端据此给可见提示。
    """
    return await asyncio.to_thread(_build_catalog, get_catalog())
