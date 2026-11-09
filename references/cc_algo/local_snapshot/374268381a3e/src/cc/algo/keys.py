"""EngineKey — ChanEngine 实例标识 (stage-05-execution-plan.md §4.4 / §1.6-6)。

key = `(symbol, period, profile_id, config_hash)` 四元结构化标识, **不再硬编码二元 tuple**。
- `profile_id` = 人读 profile 标签 (bi_5k / bi_4k / bi_strong / bi_secondary / custom)。
- `config_hash` = 后端单一权威算出的口径指纹 (cc.algo.config, PR-4 接入)。
  同 preset 名但不同自定义参数 (profile_id="custom") 靠 config_hash 区分; 不同 config_hash
  天然落到不同实例、状态隔离, 杜绝串口径污染。
- 默认 `config_hash=""` 保旧路径兼容 (PR-3 snapshot 仍走 profile_id="default"/hash="");
  生产默认路径切到 default_strict 配置走 PR-5 (本 PR 只加能力)。
"""

from __future__ import annotations

from dataclasses import dataclass

from cc.algo.trace import DEFAULT_PROFILE_ID


@dataclass(frozen=True, slots=True)
class EngineKey:
    """ChanEngine 实例 key (frozen, 可作 dict key)。"""

    symbol: str
    period: str
    profile_id: str = DEFAULT_PROFILE_ID
    config_hash: str = ""
