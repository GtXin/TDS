# Bi algorithm study — pure selection logic

Scope: derive an algorithm tree from memo020 version2's six conditions and version3's endpoint-subset interpretation. User explicitly invoked Computer Scientist, requested an algo tree, then narrowed the explanation to pure algorithm before data structures. This is a conversational design study, not a memo edit or production Bi implementation. No CC code was executed.

## Established predicate

Use every complete strict fractal from the unchanged merged sequence. A fractal's center is its three-bar window start plus one. Do not use the raw anchor or the ordinal of a fractal to measure old-stroke spacing.

For earlier endpoint A and later endpoint B:

1. They must have opposite types.
2. Their merged-center distance must be at least four, leaving at least one merged bar outside both endpoint windows.
3. The top-center high must exceed the bottom-center high, and the bottom-center low must be below the top-center low.
4. Every bar between their centers, including the endpoint centers, must have high no greater than the top's high and low no smaller than the bottom's low.

Shared endpoint selection then provides continuity; opposite-type consecutive endpoints provide alternating directions. Under strict fractals and condition4, the two strict inequalities in condition3 follow from the interior-facing neighbors. They remain explicit diagnostic checks but cannot decide which of several valid endpoint subsets to choose.

## Pure algorithm tree: complete finite candidate baseline

This baseline enumerates the possibilities permitted by the six conditions. It deliberately does not silently introduce an earliest-turn, latest-turn or maximum-count preference.

```text
2.1 从已处理包含关系的K线中，识别全部完整分型，按时间排列
├── 少于两个分型 → 没有完整笔；保留未决范围，结束
└── 至少两个分型 → 转2.2

2.2 依次尝试每个可能的起点A
→ 尚未选入的前部不强行连笔；转2.3检查A之后的分型

2.3 读取后续候选B
├── 没有后续候选
│   → 已有完整笔则保存这一候选划分；未完成尾部单独说明
│     回到尚未检查的选择分支／起点
└── 仍有B → 转2.4

2.4 检查A与B能否成笔
├── 同型 → 这一对不能连接；继续检查下一个B，转2.3
├── 两中心距离不足4 → 这一对不能连接；转2.3
├── 两端中心K线不满足区间关系 → 这一对不能连接；转2.3
├── 中间任一K线高于顶端点或低于底端点 → 这一对不能连接；转2.3
└── 全部通过 → A→B是合法候选笔；转2.5

2.5 检查两种选择
├── 选B作端点
│   → 接上A→B，以B作为下一笔起点，继续2.3
└── 暂不选B作端点
    → 仍以A作为起点，继续检查更晚的分型，转2.3

2.6 在同一起终点的候选划分之间检查结果
├── 没有合法划分 → 明示该范围无法按六条件连通，不能补造笔
├── 恰好一个 → 得到该固定范围内唯一的合法划分
└── 多个 → 六条件未决定取舍；需要另行明确端点选择原则
```

No rejected A/B pair permanently deletes either fractal. A later same-kind extreme is independently examined: replacing an existing endpoint must preserve all affected old/new pairs. A skipped short opposite turn can lie outside the proposed endpoint envelope and make a replacement invalid. A chain that remains legal on its old interval is not retroactively invalid just because a different tail becomes available; deciding to reorganize it requires a coverage/selection policy.

Enumeration can be exponential in fractal count; this is a correctness baseline, not the final efficient implementation. Once a single-output policy is stated, it can be optimized and checked against this baseline. The current isolated oracle stores legal pair relationships and cross-checks all small-case paths; that implementation detail is not required for explaining the pure tree.

## Nonuniqueness is substantive

The 21 continuous bars in `oracle-results.json` and `ambiguity.json` have intervals `[x,x+1]`, with x:

`8,9,8,7,5,3,4,5,6,7,4,2,3,4,5,6,5,3,1,0,1`.

All adjacent pairs are strictly up/down in both bounds; no adjacent inclusion. The exact full fractal list is:

`A=top@1, B=bottom@5, C=top@9, D=bottom@11, E=top@15, F=bottom@19`.

Both `A→B→C→F` and `A→D→E→F` satisfy every condition, have no equal same-kind endpoint prices, and cover the identical center interval. Both have the maximum possible three strokes; C→D has distance2 and cannot be inserted to combine them. There is also a valid coarse A→F path. Thus maximum count, absence of ties and nonrefinability do not by themselves repair the missing selection principle. This says nothing against a fuller original-source convention that adds a selection rule.

## Boundary and replacement failures

`boundary-case.json` contains a 13-bar inclusion-free example with exact extrema bottom1,top5,bottom7,top11. The pairs1→5 and7→11 are valid, but there is no valid path1→11: direct1→11 contains a low below endpoint1, while5→7 violates distance. Full coverage of arbitrary fixed first/last fractals is therefore not guaranteed.

`state_model.md/json` gives a continuous example where replacing a prior top by a later higher top violates the bottom endpoint's minimum, an arbitrarily extensible construction requiring deep rollback if covering the newest extreme is imposed, and FIRST/LAST endpoint-preselection failures. The existing raw-anchor FIRST option is unrelated to these distinct-fractal choices.

## Actual checks

- Root `python3 artifacts/mas/bi-algorithm-study/oracle.py`: 40,949 processed-interval sequences, 694,020 direct-versus-incremental pair comparisons, 448,549 fixed-boundary path-DP versus exhaustive comparisons passed; seed20261110. Includes exhaustive nonflat four-level sequences of lengths3..9, 1,200 longer seeded equal-width inputs, 400 variable-width inputs and the explicit21-bar witness.
- Independent `ambiguity.py`: bounded24-assignment family, five strict zigzags and two multiple-maximum examples; all returned paths independently revalidated.
- Independent `state_model.py`: five continuous examples and comparison with76 enumerated paths passed.
- Root boundary-case check: exact four-fractal list and no fixed-boundary full path verified.
- Protected memo020/019, memo009 and current merged/fractal source hashes remained unchanged during the oracle run. Final static preservation is recorded in `verification.json`.

These are finite arithmetic/model checks, not a proof of a greedy selector, market-data validation, a production benchmark or a CC-equivalence test. Input snapshot completion and live confirmation are separate unresolved contracts; this study does not invent confirmation timestamps.

## Source boundaries and next action

Original077:65–69 contains conditional same-kind selection, temporary retention of equals, and connection only after filtering. Original069:35–37 permits provisional choice and later revision. Neither passage should be replaced by an untested claim that any more-extreme same-kind endpoint can always replace the last one. The next design step is to specify which admissible turns to preserve, with explicit finite-history boundaries, equal extrema and tail reorganization behavior, then derive an efficient single-result tree. No such new rule was adopted by this study.
