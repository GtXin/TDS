"""标准 K 线数据模型 — 全项目唯一 (stage-04-execution-plan.md §2)。

阶段 4 验收硬标准: 图表 / 算法 / 回放 / 回测共用本模型, 不允许各模块各自维护格式。

设计要点:
- 时间统一 **Unix 秒 (UTC)**, 对齐 TV 显示层 (阶段 3 已建)。各 adapter 在边界把
  源单位 (ccxt 毫秒 / tqsdk datetime) 转成秒。
- 市场扩展字段 (持仓量 / 结算价 / 成交额) 用**可空显式字段**, 不用 dict/JSON:
  DuckDB 列存下可直接查询、类型明确。期货填 open_interest/settlement, 数字货币填 amount。
- symbol 在 Kline 内存为**规范串** "market:code" (存储/传输友好);
  结构化构造/解析由 `Symbol` 负责。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Market(StrEnum):
    """支持的市场 / 交易所标识 (规范 symbol 串的前缀)。"""

    # 数字货币 (ccxt, decision-0023)
    BINANCE = "binance"
    # 国内期货交易所 (tqsdk / pytdx, decision-0024)
    SHFE = "shfe"  # 上海期货交易所
    DCE = "dce"  # 大连商品交易所
    CZCE = "czce"  # 郑州商品交易所
    CFFEX = "cffex"  # 中国金融期货交易所
    INE = "ine"  # 上海国际能源交易中心
    GFEX = "gfex"  # 广州期货交易所 (工业硅/碳酸锂/多晶硅)


@dataclass(frozen=True, slots=True)
class Symbol:
    """结构化标的 = 市场 + 代码。

    规范串形式 "market:code" 用于 Kline 存储、TV widget symbol、跨层传输。
    """

    market: Market
    code: str  # "BTCUSDT" / "rb2401"

    @property
    def canonical(self) -> str:
        """规范串 "market:code"。"""
        return f"{self.market.value}:{self.code}"

    @classmethod
    def parse(cls, s: str) -> Symbol:
        """从规范串解析。``"binance:BTCUSDT"`` → ``Symbol(BINANCE, "BTCUSDT")``。

        Raises:
            ValueError: 格式非 "market:code" 或 market 不在 ``Market`` 内。
        """
        parts = s.split(":", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(f"invalid symbol (expect 'market:code'): {s!r}")
        market_str, code = parts
        try:
            market = Market(market_str)
        except ValueError:
            raise ValueError(f"unknown market: {market_str!r}") from None
        return cls(market=market, code=code)


@dataclass(frozen=True, slots=True)
class Kline:
    """单根 K 线 — 标准模型。

    timestamp 为**开盘时间 Unix 秒 (UTC)**。OHLCV 为通用字段;
    market-specific 字段可空 (见模块 docstring)。
    """

    symbol: str  # 规范串 "market:code"
    period: str  # 规范周期码, 见 cc.data.periods (如 "1m" / "1h" / "1d")
    timestamp: int  # 开盘时间, Unix 秒 (UTC)
    open: float
    high: float
    low: float
    close: float
    volume: float  # 成交量
    # ── 市场扩展 (可空) ──
    amount: float | None = None  # 成交额 (数字货币 quote volume)
    open_interest: float | None = None  # 持仓量 (期货专有)
    settlement: float | None = None  # 结算价 (期货专有)
