"""WebSocket endpoints for realtime push (decision-0011).

依据:
- decision-0011 (WebSocket)
- stage-03-execution-plan.md §5.6 (dispose 硬纪律)
- stage-04-execution-plan.md §3.3 (数据流: subscribe_realtime → /ws/quote)

/ws/quote/{symbol}:
  接受 period 查询参数 (默认 "1m")。
  连接后推 hello; 若 symbol 为规范串且 adapter 可用，异步轮询推增量 K 线。
  非规范 symbol 或 adapter 不可用时仅保持连接（不推数据）。

/ws/signal:
  阶段 5 起替换为算法层事件广播; 当前 keep-alive + pong。

§5.6 dispose 纪律: 每个 accept/register 必有 finally 块的 aclose + unregister。
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from cc.data.models import (
    Kline,  # noqa: F401 — for type annotation in _push_klines
    Market,
    Symbol,
)
from cc.data.periods import is_valid
from cc.data.service import get_adapter, get_ccxt_adapter

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Track active WebSocket connections.

    Thread-safe via asyncio.Lock。每个连接 lifecycle 必须 register → unregister 配对。
    """

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def register(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.add(ws)

    async def unregister(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)

    def count(self) -> int:
        return len(self._connections)


_manager = ConnectionManager()


def get_active_count() -> int:
    """Expose for /metrics endpoint."""
    return _manager.count()


def _safe_period(period: str) -> str:
    """period 若非合法内部码，降级为 '1m'。"""
    return period if is_valid(period) else "1m"


def _resolve_adapter(symbol_str: str) -> tuple:  # (Symbol|None, adapter|None)
    """解析 symbol 字符串并返回 (Symbol, adapter) 或 (None, None)。"""
    try:
        sym = Symbol.parse(symbol_str)
        adapter = get_ccxt_adapter() if sym.market == Market.BINANCE else get_adapter()
        return sym, adapter
    except ValueError:
        return None, None


async def _push_klines(websocket: WebSocket, it: AsyncGenerator[Kline, None]) -> None:
    """从 subscribe_realtime 迭代器逐根推送 K 线 JSON。"""
    async for kline in it:
        try:
            await websocket.send_json({
                "type": "kline",
                "data": {
                    "symbol": kline.symbol,
                    "period": kline.period,
                    "timestamp": kline.timestamp,
                    "open": kline.open,
                    "high": kline.high,
                    "low": kline.low,
                    "close": kline.close,
                    "volume": kline.volume,
                },
            })
        except Exception:  # noqa: BLE001 — WS 已关闭时停止推送
            break


@router.websocket("/ws/quote/{symbol:path}")
async def ws_quote(websocket: WebSocket, symbol: str, period: str = "1m") -> None:
    """K 线实时推送 WebSocket (stage-04 PR-7).

    查询参数 period: 内部周期码 (默认 "1m")；非法值降级为 "1m"。
    连接后推 hello; 规范 symbol + adapter 可用时启动轮询推增量 bar。
    §5.6: finally 强制 aclose(async iterator) + unregister(manager)。
    """
    await websocket.accept()
    await _manager.register(websocket)

    period_code = _safe_period(period)
    realtime_iter: AsyncGenerator[Kline, None] | None = None
    push_task: asyncio.Task[None] | None = None

    try:
        await websocket.send_json({"type": "hello", "symbol": symbol, "period": period_code})

        sym, adapter = _resolve_adapter(symbol)
        if sym is not None and adapter is not None:
            realtime_iter = adapter.subscribe_realtime(sym, period_code)
            push_task = asyncio.create_task(_push_klines(websocket, realtime_iter))

        # 保持连接，接收任意消息以检测客户端断开
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        logger.info("ws_quote disconnect: symbol=%s period=%s", symbol, period_code)
    finally:
        # §5.6 dispose: 嵌套 try/finally 确保 unregister 即使 aclose() 抛异常也必达
        try:
            if push_task is not None:
                push_task.cancel()
                try:
                    await push_task
                except asyncio.CancelledError:
                    pass  # 预期：task 因 cancel() 被中断
                except Exception:  # noqa: BLE001 — 其他异常记录后继续清理
                    logger.warning("push_task ended with unexpected error", exc_info=True)
            if realtime_iter is not None:
                await realtime_iter.aclose()  # §5.6: CancelledError 修复后可靠执行
        finally:
            await _manager.unregister(websocket)


@router.websocket("/ws/signal")
async def ws_signal(websocket: WebSocket) -> None:
    """信号事件推送 WebSocket (阶段 3 桩，阶段 5 接算法层事件广播)。"""
    await websocket.accept()
    await _manager.register(websocket)
    try:
        await websocket.send_json({"type": "hello", "channel": "signal"})
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong", "received": data})
    except WebSocketDisconnect:
        logger.info("ws_signal disconnect")
    finally:
        await _manager.unregister(websocket)
