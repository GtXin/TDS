"""Notify message model + level type alias (`decision-0015`)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

NotifyLevel = Literal["info", "warning", "buy_sell"]


class NotifyMessage(BaseModel):
    """通用通知消息 — 各 Notifier 实现据此渲染各自渠道的 payload。

    阶段 5 起 ``payload`` 字段填入买卖点事件结构化数据
    （标的 / 级别 / 价格 / 信号类型 / 笔结构等），渲染端可按渠道选择简单文本或富文本。
    """

    title: str
    body: str
    level: NotifyLevel = "info"
    timestamp: datetime
    payload: dict[str, Any] | None = Field(
        default=None,
        description="原始事件 (标的/级别/价格/信号类型),用于结构化展示,阶段 5/6 起接入",
    )
