# memo0027_class_bi_series

[class design] [chan] [bi] [series first]

## 0. Scope And Purpose

> [purpose] Implement the first experimental `BiSeries` / 笔序列: define what it
> receives, what the result stores, and how callers calculate and inspect it.
> Preserve every original K-line and add Bi membership and endpoint tags.

```text
FenxingSeries + BiConfig -> BiSeries
```

- **Input:** an existing `FenxingSeries`. Follow `source_series` to its
  merged series and original rows; do not detect Fenxing again or pass a second,
  potentially different copy of the upstream data.
- **Result:** every original row, with merge/Fenxing fields unchanged and added
  Bi tags and endpoint indices. Shared endpoints can belong to two strokes.
- **Classes:** `BiSeries` holds the result and exposes the calculation;
  `BiBar` describes one original Fenxing row with added Bi information;
  series-owned `BiConfig` holds the calculation settings.
- **Implementation:** members, methods, validation, sample use, and tests.
  Row-aligned storage and the first algorithm option `kwx` are selected;
  the runnable KWX snapshot and bi_5k preset are pinned in `_kwx/provenance.json`.

> [scope] [memo0026](memo0026_algo_of_bi.md) covers what Bi represents and how
> CC's algorithm selects it. This memo covers the row-aligned class design,
> the `kwx` option reuses CC's calculation rather than rewriting its rules.
> Source and parameter verification are recorded in chapter 2. The external `Bi` in Appendix B is a
> whole-stroke result; it is not the row object defined below.

[non-goals] This implementation remains in experiments. CSV, charts, Xianduan,
incremental live updates, and moving code into `src/` remain separate tasks.

## 1. Class Design

### 1.a BiBar: Members And Methods

> [decision] **`BiBar` 是一行 `Fenxing` 加上笔信息，不是一整笔的独立容器。**
> 保留原始 Kbar、所属 M、合并高低价和分型标签，只增加它属于哪笔、
> 该笔从哪根 Kbar 开始、在哪根 Kbar 结束。不再另设 `BiKline`。
>
> [naming] 原拟议行类 `Bi` 改名为 `BiBar`；类名用 PascalCase，模块名为
> `bi_bar.py`。这里只更正名称，不改变逐行存储和标签设计，也不创建一整笔的类。

**Inherited Members / 继承成员。** 使用不可变 dataclass `BiBar(Fenxing)`。
以下是从 `Fenxing` 及其父类 `MergedKline` 继承的完整字段，不需要在 BiBar 中重复声明：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `symbol` | `str` | 标的代码 |
| `period` | `str` | 原始 Kbar 周期，不是笔的级别 |
| `source` | `str` | 原始数据来源 |
| `timestamp` | `datetime` | 当前原始 Kbar 的时间 |
| `open`, `high`, `low`, `close` | `float` | 当前原始 Kbar 的 OHLC，不替换为合并价格 |
| `volume` | `float` | 当前原始 Kbar 的成交量 |
| `raw_index` | `int` | 当前原始行下标 |
| `merged_tag` | `str` | 当前行所属 M，例如 `"M2"` |
| `merged_low`, `merged_high` | `float` | 所属 M 的合并低价、高价 |
| `merged_direction` | `Literal["up", "down"] \| None` | 合并方向；未建立时为 None，不是笔的方向 |
| `merge_state` | `Literal["resolved", "direction_unresolved"]` | 合并方向是否已确定 |
| `is_group_first` | `bool` | 当前行是否为所属 M 的第一根原始 Kbar |
| `is_group_extreme` | `bool` | 当前行是否为合并算法选定的组极值行；不自动等于笔端点 |
| `fx_type` | `Literal["top", "bottom"] \| None` | 所属 M 的分型标签，默认 None；同组各行重复此标签 |

**Inherited Properties And Methods / 已有属性与方法。**

- `k_low / k_high -> float`：原始 `low / high` 的别名，不是合并价。
- `is_top / is_bottom -> bool`：所属 M 是否标为顶/底分型；不表示当前原始行就是价格锚点。
- `fenxing_price -> float | None`：顶返回 `merged_high`，底返回 `merged_low`，
  无分型返回 None；同一 M 各行的值相同。
- `to_merged_kline() -> MergedKline`：返回只保留原始及合并字段的新对象，去掉分型和笔字段。
- `to_raw_kline() -> Kline`：返回只保留原始行情字段的新对象。
- `from_merged_kline(row: MergedKline, fx_type=None)`：现有类方法，复制合并行并加分型标签；
  不检测分型。按现有 `cls(...)` 写法，从 BiBar 调用时将创建 BiBar，新增笔字段取空元组。
- `from_kline(*, kline: Kline, raw_index: int, merged_tag: str, merged_low: float,
  merged_high: float, merged_direction: ChanDirection | None, merge_state: MergeState,
  is_group_first: bool, is_group_extreme: bool)`：继承的底层构造方法，手动提供合并信息；
  不执行合并或分型计算。返回调用类的对象，未提供的分型和笔字段取默认值。

后两个工厂保留在继承接口中，但 BiBar 的正常入口使用下面的 `from_fenxing()`，
避免跳过已有分型数据。`Fenxing.__post_init__()` 会调用 `self.validate()`；
BiBar 必须扩展校验并保留父类检查，不能只验证笔字段。

> [note] 继承关系是 `BiBar -> Fenxing -> MergedKline`；
> `MergedKline` 保存 Kline 的字段，但不是 Kline 子类。因此 `body_size`、
> `upper_shadow`、`lower_shadow`、`is_bullish`、`is_bearish`、`is_flat` 和 `to_dict()`
> 不会自动成为 BiBar 的方法或属性；需要时先调用 `row.to_raw_kline()`。

**New Members / 新增成员。** 三个元组默认均为 `()`：

```python
bi_tags: tuple[str, ...] = ()
bi_start_raw_indices: tuple[int, ...] = ()
bi_end_raw_indices: tuple[int, ...] = ()
```

三个元组按位置对应：第一个标签配第一个起点和终点，第二个标签配第二组端点。
下标是 `source_series.klines` 中的原始行位置，不是 M 下标，也不是分型序号。
`B0`、`B1` 按本次结果的笔顺序编号；重算后不保证原标签仍表示同一笔。

**Example / 例子。** 假设已选出 `B0: K1 -> K5`、`B1: K5 -> K9`。
这只说明存储形式，不证明这两笔通过了某组成笔规则。完整输入为 K0-K10：

| 原始行 | `bi_tags` | `bi_start_raw_indices` | `bi_end_raw_indices` |
| --- | --- | --- | --- |
| K0 | `()` | `()` | `()` |
| K1 | `("B0",)` | `(1,)` | `(5,)` |
| K2 | `("B0",)` | `(1,)` | `(5,)` |
| K3 | `("B0",)` | `(1,)` | `(5,)` |
| K4 | `("B0",)` | `(1,)` | `(5,)` |
| K5 | `("B0", "B1")` | `(1, 5)` | `(5, 9)` |
| K6 | `("B1",)` | `(5,)` | `(9,)` |
| K7 | `("B1",)` | `(5,)` | `(9,)` |
| K8 | `("B1",)` | `(5,)` | `(9,)` |
| K9 | `("B1",)` | `(5,)` | `(9,)` |
| K10 | `()` | `()` | `()` |

每一行原有的 `merged_tag`、`fx_type` 等字段仍在，表中只是省略显示。
K3 可以没有分型标签，但仍属于 B0。K5 同时是 B0 终点和 B1 起点。

**New Properties / 新增属性。** 不重复存储能从三个元组算出的标记：

- `bi_start_tags -> tuple[str, ...]`：筛选起点下标等于本行 `raw_index` 的笔。
- `bi_end_tags -> tuple[str, ...]`：筛选终点下标等于本行 `raw_index` 的笔。
- `is_bi_start / is_bi_end -> bool`：对应标签元组是否非空；可以同时为真。

例如 K3 的 `bi_start_tags=()`，但所属笔的起点仍是 K1；
K5 的 `bi_start_tags=("B1",)`、`bi_end_tags=("B0",)`。

**New Or Overridden Methods / 新增或重写的方法。**

- `from_fenxing(row, *, bi_tags=(), bi_start_raw_indices=(), bi_end_raw_indices=()) -> BiBar`：
  复制一行 Fenxing 的全部字段，附加笔信息并校验；不在这里计算成笔。
- `validate() -> None`（重写）：先调用父类检查继承字段，再检查三个元组等长、标签非空且不重复、
  下标为非负整数（不接受 bool），每组端点满足 `start < end` 且
  `start <= raw_index <= end`。不一致时抛出 `TypeError` 或 `ValueError`。
- `to_fenxing() -> Fenxing`：去掉笔字段，恢复与来源完全相同的 Fenxing 行。

> [boundary] 单行只能检查自己的信息。端点是否存在、是否对应正确分型、
> 其他行是否也记录了同一组端点，由 `BiSeries` 检查。`BiBar` 不读写文件、不画图。

### 1.b BiSeries: Members And Methods

> [concept] **`BiSeries` 在完整 Fenxing 序列上选笔，再把结果标回每一根原始 Kbar。**
> 不删除无分型、未成笔或位于首尾之外的行；没有成笔时，行数仍保持不变。

**Members / 成员。** 使用不可变 dataclass：

```python
klines: tuple[BiBar, ...]
config: BiConfig
source_series: FenxingSeries
```

`klines[i]` 对应 `source_series.klines[i]`。构造器接收已算好的结果并校验；
显式调用 `derive_from(...)` 才进行选笔，不让构造器偷偷重算。

`BiConfig` 放在 `bi_series.py`，由序列持有；只保存规则设置，不保存候选或工作状态。
首个算法选项为 `algorithm="kwx"`，详见1.c。KWX版本和参数预设已固定，
不能用本机随版本变化的默认值。配置自身拒绝未实现或非法的选项。

**Properties / 派生属性。**

- `count / raw_count`：原始行数；`bi_count`：不同笔标签的数量，不是标签出现次数。
- `merged_count / fenxing_count`：从来源序列读取，不重复识别。
- `symbol / period / start_timestamp / end_timestamp`：完整来源的数据标识和时间范围。

**Methods / 方法。**

- `derive_from(source_series, config=None) -> BiSeries`：从给定完整输入重新计算全部笔，
  返回新对象。先按 M 去重读取分型中心，再选端点并回填行标签；不把同一 M 的重复标签
  当成多个分型。不修改输入，也不接续上一次调用的内部候选状态。
- `validate() -> None`：检查来源类型、配置、行数、顺序及所有继承字段完全一致；
  对每个 B 标签检查所有行的端点相同、覆盖区间完整且恰为 `[start, end]`。
  检查端点对应相反类型分型的价格锚点，邻笔共享端点并上下交替。
  不允许区间外多贴、区间内漏贴，或非共享端点出现多笔重叠。
- `raw_indices_for_bi_tag(tag) -> tuple[int, ...]`：返回该笔覆盖的全部原始行下标，包含两端。
- `endpoint_raw_indices_for_bi_tag(tag) -> tuple[int, int]`：返回该笔的 `(start, end)`。
  以上两个查询找不到标签时抛出 `KeyError`，不返回容易误解的空结果。
- `to_list() -> list[BiBar]`：返回完整标记行列表；`raw_klines()`、`timestamps()`、
  `closes()` 沿用前面序列的接口含义，不改变原始时间轴。

```python
bis = BiSeries.derive_from(fenxings, config=selected_config)
row = bis.klines[5]                              # 原始 K5，保留全部上游字段
row.bi_tags                                     # ("B0", "B1")，按上面的存储例子
bis.endpoint_raw_indices_for_bi_tag("B0")         # (1, 5)
bis.raw_indices_for_bi_tag("B0")                  # (1, 2, 3, 4, 5)
```

> [decision] 笔区间按两个实际价格锚点之间的原始行计算，不扩展到整个端点 M 组，
> 也不把判断时向后查阅的证据行算入笔内。锚点沿用来源的
> `turning_raw_index(merged_index)`；顶价取 `merged_high`，底价取 `merged_low`。
> 锚点不一定是 M 的第一行，也不能用本行原始 high/low 替换合并价格。

[open] 当前端点不代表永久确认。确认状态、判断依赖和拒绝/修正过程记录的接口，
需在选定算法规则后补充；三个标签元组不能还原这些过程，本次不伪造对应字段或结果。

### 1.c Derive From: KWX Specification

> [purpose] **调用一次 `BiSeries.derive_from()`，让 KWX 代码计算整个输入序列的笔，
> 再由包装层把结果标回原始 Kbar。调用者不需要操作 KWX 的类型或手动衔接步骤。**

**Reference / 对照网页和0026。** 2026-09-11核对
[CC笔定义](https://www.kwx.me/cc/#stroke-definition)、
[笔执行流程与代码](https://www.kwx.me/cc/#stroke-recipe)、
[公共模型和配置](https://www.kwx.me/cc/#foundation-recipe)。网页标示源码快照
`b1348795d25d282aa769bce2f14fb366df269d7d`。
网页 `manual_rebuild/algo/bi.py` 共453行；将本备忘录附录开头缺少的一个引号补齐后，
两份代码除末尾空白外一致。附录原文不修改，也不把整个CC项目搬进来。

> [concept] 网页给出复现目标和可运行代码；[memo0026](memo0026_algo_of_bi.md)
> 1.2解释这段代码的十二步，1.4解释标准检查。这里把它们接到我们的对象接口上。
> 0026第2章的几何解释、矩形覆盖设想不作为额外过滤条件，避免悄悄改变KWX输出。

**Preset / kwx具体按哪套规则算。** 首版包装规格采用网页默认的 `bi_5k`，
而不是只写一个不明确的“使用CC默认”。对外暂时仍只有 `algorithm="kwx"` 一个选项：

```text
bi_profile        = bi_5k
bi_formation_mode = standard
bi_span_mode      = merged_center
bi_min_span       = 4
bi_gap_as_bar     = True
bi_endpoint_check = half
bi_require_peak   = True
bi_fractal_repair = True
bi_strength_ratio = 0.9   (standard不使用此值)
```

以上已与网页 `ChanConfig`、`_PROFILE_CONFIGS`、`DEFAULT_CONFIG` 及0026第二步核对。
`bi_strong` 的比例才是0.95，不能把它混进这个预设。包装层先取得规范化配置，
从同一配置读取 `profile_id` 和 `config_hash`，再交给 `build_bis()`；不手填旧manifest的hash。
`normalize()`会按命名预设重新确定参数，不是价格归一化。
例如 `bi_5k + bi_min_span=6` 仍会变回4；以后若开放自定义才另行设计 `custom`，当前不开放。

**Algorithm / 先找第一笔，再逐个判断：续接、延长，还是重画末端。**

> [workflow] 以下按实际执行顺序展开选定的 `kwx / bi_5k`，不是重新设计规则。
> 对应0026步骤1-12：准备、首笔、同型处理、标准续笔、失败修正、输出。
> **同型看能否延长；反型先看能否成新笔；失败后才考虑吸收最近一次反弹。**
> 原算法一次看得到整份输入，但主循环按时间先后读取；修正分支会提前查看后续分型。

**贯穿例子。** 沿用0026：每根原始K对应一根M，无包含、无价格缺口。
输入分型已经存在，Bi算法不重新识别。`F0=A`、`F1=B`等是分型顺序；
`M1`、`M5`等是它们在完整合并序列中的位置，两种下标不能混用。

```text
M序号   M0  M1  M2  M3  M4  M5  M6  M7  M8  M9 M10 M11 M12 M13 M14 M15 M16
高价    19  20  18  16  14  12  13  14  16  17  14  10  11  13  16  19  18
低价    15  16  14  12  10   8   9  10  12  13  10   6   7   9  12  15  14
分型     .   A   .   .   .   B   .   .   .   C   .   D   .   .   .   E   .

输入分型：A顶20@M1，B底8@M5，C顶17@M9，D底6@M11，E顶19@M15
```

> **第一步：固定配置，建立两个空工作列表。**
>
> `build_bis()`先调用 `cfg.normalize()`，再建立候选池 `P=[]` 和笔列表 `S=[]`。
> 输入分型列表仍是完整的 `[A,B,C,D,E]`，空的是工作列表，不是输入。
> 此后每建立一笔都继续使用同一个S；只有重新调用整个方法才清空重算。
> 输入没有分型时，不补数据，直接以空笔列表进入第七步输出。

> **第二步：取下一个分型，决定找首笔还是接着已有笔处理。**
>
> 第一次取A，以后依次取B、C、D、E，当前分型记为 $F_i$。
> S为空去第三步；S非空去第四步。读完全部分型去第七步。
> 第三步换旧候选、或第六步查看未来，都不会改变当前 $F_i$。

> **第三步：没有笔时，从第一个旧候选开始找第一笔。**
>
> 当前 $F_i$固定，按入池顺序逐个试 $P_0,P_1,\ldots$。
> 旧候选与当前同为顶或同为底：跳过这次配对，不删除旧候选，继续试下一个旧候选。
> 一顶一底：把旧候选作为起点、当前作为终点，执行下面的三项标准检查。
> 失败仍试下一个旧候选；**第一个通过的配对**加入S，清空整个P，回第二步。
> 所有旧候选都试完仍不成功，才把当前分型加到P末尾，回第二步；不进入修正分支。
>
> 主例：读A时P为空，留下 `P=[A]`。读B时试A→B，通过检查，
> 变为 `S=[A→B], P=[]`。独立分支：若池里有三个旧候选，前两个失败而第三个通过，
> 就采用第三个；不是第一个失败后立即换下一个输入分型。

**Standard Check / 一对起终点怎样算通过。** 起点中心为 $M_s$，终点中心为 $M_e$；
$H_j,L_j$是合并M的高、低价。按下面顺序检查，任一失败立即返回“不成笔”，不改S。

> **① 距离：中心间隔，加上可折算缺口，至少为4。**
>
> 先算 $d=e-s$；若 $d\ge4$直接通过。否则检查从 $M_s$ 到 $M_e$ 的每一对相邻M。
> 对每个M，回到它包含的全部原始K，取原始最低价 $rL_j$ 和原始最高价 $rH_j$。
> 相邻两组满足 `max(rL[j], rL[j+1]) > min(rH[j], rH[j+1])`，才记一个缺口。
> 价区间刚好接触不算缺口；这里不能用合并后的H/L代替原始包络。
> 缺口总数为G，最终检查 $d+G\ge4$。例如d=3、G=1通过，d=3、G=0失败。
> 通过缺口折算后，不再额外要求未折算的d也达到4。
>
> 主例A→B：5−1=4，通过；C→D：11−9=2且G=0，失败，后两项不再检查。

> **② half端点关系：两端必须真正拉开，而不只是顶底类型相反。**
>
> 向下，顶→底，两个条件必须同时成立：
> `H[s] > max(H[e-1], H[e])`，且 `L[e] < min(L[s], L[s+1])`。
> 向上，底→顶，两个条件必须同时成立：
> `L[s] < min(L[e-1], L[e])`，且 `H[e] > max(H[s], H[s+1])`。
> 都是严格比较；任一相等也失败。half只使用这里列出的半侧窗口，不能换成全部三根。
>
> A→B向下：`20 > max(14,12)=14`，且 `8 < min(16,14)=14`，通过。
> B→C向上：`8 < min(12,13)=12`，且 `17 > max(12,13)=13`，通过。
> 独立边界情况：若右侧计算结果恰为20，`20 > 20`不成立，返回失败。

> **③ 区间极值：终点不能被笔内更极端的价格盖过。**
>
> 逐根检查 $j=s+1,\ldots,e-1$，不含起终点中心。
> 向上要求每根 `H[j] <= H[e]`；向下要求每根 `L[j] >= L[e]`。
> 允许同价极值，不额外要求起点也是整个区间的最高/最低点。
>
> A→B内部最低价为10，`10 >= 8`，通过；B→C内部最高价为16，`16 <= 17`，通过。
> 独立边界情况：向上终点17，内部高点17可以；内部高点18则失败。
> 三项全部通过才返回“成笔”。本检查只回答是否合格，不自行追加笔。

> **第四步：已有笔，先与最后一笔的终点比较顶底类型。**
>
> 比较对象不是输入里的上一个分型，而是S中最后一笔已经接受的终点T。
> 当前与T同为顶：当前顶价严格高于T，才把末笔终点移到当前；相等或更低不改。
> 同为底：当前底价严格低于T，才移动；相等或更高不改。
> 移动后依赖下标取旧值与当前M下标的较大值。以上同型情况均回第二步，
> **不增加笔数，也不再检查距离、half或修正。**
>
> 主例读C时，末端B是底、C是顶，去第五步。
> 独立同型分支：若末端是顶17，当前也是顶，价格18则延长，17或16则保持原笔。
> 当前与T一顶一底，才进入第五步。

> **第五步：反型先尝试接一笔；标准失败才去修正。**
>
> 以T为候选起点、当前分型为候选终点，执行三项标准检查。
> 全部通过：在S末尾追加T→当前，原有笔不删，依赖下标设为当前M下标，回第二步。
> 任一失败：本预设standard不调用strong的幅度例外，直接去第六步。
>
> 主例读C：B→C通过，`S=[A→B, B→C]`。
> 读D：C→D距离不足，不能追加，但此时还不能说“D被忽略”，要继续检查能否修正。

> **第六步：尝试吸收最近一次反弹，把前一笔延长到更有代表性的极值。**
>
> 先检查S至少有两笔；不足两笔，保持S并回第二步。
> 将最后两笔写为 `U→V→W`，当前反型分型为X。这里U、V、W是已接受的端点，
> 不要求它们在输入分型中相邻。按顺序检查以下三道关，失败即保持原笔列表并回第二步。
>
> **先看前面的价格：反弹是否可被吸收。**
> 末笔V→W向上：V与X都是底，要求 `X.low <= V.low`，且 `W.high <= U.high`。
> 末笔向下：V与X都是顶，要求 `X.high >= V.high`，且 `W.low >= U.low`。
> 这里的high/low是CC分型的三M窗口边界，定义见后面的输入转换，不是一律取中心M两端。
> 再对U→X执行上述③区间极值检查；失败则不修正。
> 这一分支不会另外对U→X重做①距离或②half。
>
> **再看后面的分型：哪一种证据先出现。** 当前X不动，先看输入中的下一个分型G，
> 不满足下面任一种情况，就继续看再下一个G；比较基准始终是旧末端W。
> 若旧末笔向上：先遇到顶G且 `G.high > W.high`，允许进入重画；
> 若先遇到底G且W→G通过全部标准检查，则保留原笔，不重画。
> 若旧末笔向下：先遇到底G且 `G.low < W.low`，允许进入重画；
> 若先遇到顶G且W→G通过全部标准检查，则保留原笔。
> 价格仅相等不是突破。一直查到输入末尾仍无结果，也不重画，不能当作默认通过。
>
> **最后才修改S；没有真正延长就恢复。** 暂时取走最后一笔V→W，
> 按第四步的严格同型规则，把前一笔U→V延长为U→X。
> 若X与V价格相等，前面的非严格门槛虽通过，此处却不能延长，必须把取走的末笔放回原位。
> 成功则 `U→V→W` 变为 `U→X`，笔数减少一笔；
> U→X的依赖下标取原依赖、X位置、未来证据G位置的最大值。随后回第二步。
> 提前查看G不消耗主循环的输入；G以后仍会按正常顺序处理。
>
> 主例取 `U=A, V=B, W=C, X=D`：`D.low=6 <= B.low=8`，
> `C.high=17 <= A.high=20`，A→D内部最低价8也不低于D的6，前两道关通过。
> 查看下一个分型E，`E.high=19 > C.high=17`，后续证据允许修正。
> 取走B→C，把A→B延长为A→D，得到 `S=[A→D]`，依赖位置记到M15。
> A→D的终点仍是M11，不是证据M15。
> 若另一次调用只给截至M12的数据，D后没有E可查，则此次不修正，仍保留两笔。

> **第七步：读完输入，输出最终笔，再映射到原始行。**
>
> 主例修正后继续正常读取E；D→E距离4，half为 `6 < min(12,15)`、
> `19 > max(10,11)`，内部最高价16也不超过19，追加成功。
> 最终 `S=[A→D, D→E]`。`finish()`按S的顺序输出整笔，
> 顶端价格用顶分型high，底端价格用底分型low，保留中心M下标和依赖记录。
> 包装层最后才生成BiBar标签，不把中途被删除的B→C残留在行上。
> 若始终找不到第一笔，KWX输出空列表；包装层仍保留全部原始行，只是不贴笔标签。

```text
读到的分型       A             B                 C                    D              E
处理后的笔列表   []            [A→B]             [A→B, B→C]           [A→D]          [A→D, D→E]
主要判断         留作候选      首笔标准通过      续笔标准通过         借E证据修正    续笔标准通过
```

> [boundary] **算出了端点，不等于当时就能知道或以后不再改变。**
> 原代码另有 `bi_confirmed_flags()`：最后一笔总是forming；某笔依赖缺失或
> `dep >= merged_count-2`也未确认；若末笔依赖缺失或落在该尾部范围，倒数第二笔也未确认。
> 这套标记不参与选笔。主例N=17，A→D依赖M15，落在尾部阈值15，不能标成已确认。
> 未来证据、确认状态和原始行覆盖是三件不同的事，不能仅靠B标签混为一谈。

**Interface / 对外接口。** 以下省略实现体，只展示签名；可运行调用见2.b：

```python
@dataclass(frozen=True)
class BiConfig:
    algorithm: Literal["kwx"] = "kwx"

@classmethod
def derive_from(
    cls, source_series: FenxingSeries, config: BiConfig | None = None
) -> BiSeries:
    ...

bis = BiSeries.derive_from(fenxings, config=BiConfig(algorithm="kwx"))
```

`config=None` 时创建 `BiConfig()`。`kwx` 是算法选项的值，不是布尔开关；
现在只支持这一项，其他名称报 `ValueError`，不偷偷换成另一套算法。
它选择“由谁计算”，不等同于 KWX 的 `standard/strong/secondary` 成笔模式。
当前输入已经有合并和分型结果；选择kwx不会重新执行上游合并或分型。

**Wrapper / 包装类。** 内部 `KwxBiAdapter`，模块为
`experiments/chan_theory/kwx_bi_adapter.py`。它把我们的对象转换为 KWX 对象、调用算法、
把输出转换为 `tuple[BiBar, ...]`；不自行改写成笔、延长或修正规则。

```text
BiSeries.derive_from(fenxings, config)
    -> KwxBiAdapter(config).derive_rows(fenxings)
    -> tuple[BiBar, ...]
    -> BiSeries(klines=rows, config=config, source_series=fenxings)
```

`KwxBiAdapter` 持有不可变 `config`；`derive_rows(source_series)` 每次建立独立工作状态。
KWX 特有的数据类型和导入仅出现在适配模块及隔离的参考代码中，不进入 BiBar 的公开接口。

**Workflow / 执行顺序。**

1. **核对输入与配置。** 验证 FenxingSeries，保留全部原始行。由
   `source_series.source_series` 取得合并信息；检查算法选项和固定的 KWX 依赖可用。
   方向未确定的 M 不能伪造方向后送入 KWX；首版遇到这类输入明确报错，后续另定兼容策略。
2. **转换三组输入。** 原始 Kbar 按时间顺序逐行转换；每个 M 只生成一个 KWX MergedKline，
   保留合并高低价、原始起止下标及时间。每个有分型的 M 只生成一个 KWX Fenxing；
   `fx.index` 使用它在完整 M 序列中的下标，不是它在分型列表中的序号。
   CC Fenxing 的 `high=max(H[i-1], H[i], H[i+1])`、
   `low=min(L[i-1], L[i], L[i+1])`，不能直接复制中心M的两端价格；
   `timestamp` 使用中心 M 的 `start_ts`。原始 datetime 必须明确时区并能无损转为UTC整数秒，
   未指定时区或有不能表示的亚秒精度时拒绝，不猜时区、不截断。
   转换价格、时区和时间单位必须有明确对应，不能通过字符串截断或排序重新编号。
3. **调用原算法。** 适配类构造固定预设对应的 `ChanConfig`，调用附录 B 的
   `build_bis(merged, fenxings, raw_klines, cfg, profile_id=..., config_hash=...)`。
   整个输入在本次调用中可见，保留 KWX 的向后查阅行为；这不是逐根实时、无未来数据的承诺。
4. **将笔端点映射回来。** 按返回的时间顺序给整笔编号 B0、B1 等。以每笔
   `trace.merged_from_index/merged_to_index` 找到端点 M，再通过来源的
   `turning_raw_index()` 找到原始价格锚点。核对分型类型、方向、价格及CC代表时间；
   不以“最接近的时间”猜测下标。缺 trace、非法索引或无法保持同一端点含义时明确报错。
5. **填回所有行。** 每笔在原始 `[start, end]` 闭区间填入标签和起终点下标。
   共享端点填两组；区间外为空。即使 KWX 返回空笔列表，也返回完整的无笔标签行序列。
6. **校验并返回。** 构造 BiSeries，验证来源字段和跨行标签一致。不修改输入或旧结果，
   不读写 CSV、不画图、不保留跨调用候选状态。

**Example / 下标映射。** 假设完整 M 序列有 M0-M12，分型列表中的第一个、第二个
分型分别位于 M2、M7。KWX 输入的 `fx.index` 应为 2、7，而不是 0、1。
若它返回一笔 M2->M7，来源锚点分别是 K4、K12，则 B0 标记 K4-K12 全部九行；
哪怕 M2 的组首是 K3，也不能把 B0 起点改成 K3。其余原始行照常保留。

> [mapping] **CC代表时间和我们的价格锚点时间要分开。** 若M2从K3开始、底价由K4贡献，
> CC起点时间仍是K3的时间；BiBar端点索引仍是4。先核对CC输出时间等于转换输入的M2起始时间，
> 再按M2映射到K4。这是明确的坐标转换，不是找最近时间，也不能声称两个时间完全一致。

例如一个顶分型的完整三M窗口为：

```text
M:     M1  M2  M3
high:  11  14  12
low:    7   9   8
```

CC Fenxing记录 `high=14, low=7`；中心M2是 `[9,14]`。
顶端点价格两者都取14，但另一个边界7不能误写成9，因为修正分支也会读分型的另一侧价格。
这只是转换例子，不是独立成笔样本。

**Source And Limits / 代码来源与限制。**

- 使用附录 B 保存的 KWX 代码作为基线，不在运行时从网页下载或执行代码。
  原文开头少一个引号，且依赖 `manual_rebuild.algo.config/models/trace` 和
  `manual_rebuild.data`；网页共同基础已提供这些模型、配置和trace代码，
  本次已连同额外的 `keys.py` 依赖隔离到 `_kwx/`，可以导入，不需要安装外部包。
  原样附录保持不变；六个网页文件仅改本地导入路径及末尾换行。来源、校验值及许可限制见2.a。
- 已固定源文件校验值及完整参数预设，特别是距离模式/阈值、缺口计数、
  端点比较、极值检查、成笔模式、强势比例和修正开关。现有 manifest 的
  `profile_id="bi_5k"` 与 config hash 本身不包含完整参数；此次已从网页配置代码补齐上面的
  笔层预设。运行后配置指纹为 `ffb2448b188c`，不扩展多个配置旋钮。
- 正常结果返回空列表与依赖缺失/算法失败必须区分；后者报出具体原因，不能包装成“没有笔”。
  不启用尚未实现的 `secondary` 预设，也不自动退回我们自己重写的算法。
- `trace.dep_to_index` 是判断证据位置，不是笔终点。映射不得用它扩张笔区间。
  KWX 的 trace/确认信息应在适配验证中保留并比较；持久化及公开查询接口仍待设计。
  当前标签结果只描述选定端点，不能据此宣称它们已永久确认。

[verification] 网页 `check_02_stroke.py` 的参考目标是502笔、501 confirmed、1 forming，
并检查14笔的依赖位置晚于终点（网页称14次修正）及逐对象摘要。
这些只适用于网页锁定的完整CSV、合并/分型结果和配置；同样行数或同样502笔不能证明复现。
先逐对象比较传给KWX的三组输入，再比较原始KWX输出，最后单独验证BiBar的锚点映射。
网页的250根窗口只用于展示，不能先截成250根来冒充完整历史计算。

[status] 2026-09-11已完成实验实现及测试，见第2、3章。这里保留算法说明供逐步检查；
CSV、图表、增量更新及公开确认状态接口不在本次实现中。

### 1.d Test Methods

> [verification plan] **先验证每行的信息能完整保留并互相对上，再验证成笔算法。**
> 以下是测试目标；实际测试文件、已验证结果与未验证范围见第3章。

- **原始数据不变。** 对每个 i 比较 `bis.klines[i].to_fenxing()` 与输入行；
  OHLCV、时间、source、M 标签、合并高低价、首行/极值标记和分型标签必须全部相同。
- **完整行与共享端点。** 先手工构造 1.a 的十一行结果，单独测试存储与查询：
  `count=11`、`bi_count=2`，K0/K10 无标签，K3 只有 B0，K5 同属 B0/B1。
  K5 的起点标记仅 B1、终点标记仅 B0；内部行不能被误标为端点。
- **错误数据必须报错。** 分别制造元组长度不等、重复标签、bool/负数下标、
  起终点倒置、越界端点、同一 B 的端点不一致、区间漏行、多贴标签、断开的邻笔、
  错误锚点和继承字段被改动；分别确认行级或序列级校验拒绝。未知标签查询应报 `KeyError`。
- **合并组与原始行不能混淆。** 使用一个包含多根原始行的 M，令价格锚点不在组首。
  验证继承的分型标签仍在整个 M 重复，而笔端点只落在锚点行；另测并列极值，
  结果应与 `FenxingSeries.turning_raw_index()` 一致，不另定选第一/最后行的规则。
- **没有笔也保留数据。** 使用有效但不足以成笔的来源；输出行数不变，所有新增元组为空、
  `bi_count=0`。覆盖不足两个相反分型以及有候选但全部配对失败的情况。
- **重算不污染旧结果。** 相同输入与配置应产生相同结果；增加数据后重新计算，
  检查新结果标签自洽，同时原 Fenxing 输入和旧 BiSeries 不变。若选定规则允许延长或修正，
  用数值例子验证旧端点标签在新结果中被移除、新端点被正确标出。
- **算法另有预期答案。** 规则选定后，为距离、端点比较、区间极值、同型延长和启用的
  强势/修正规则分别写最小数值样本，断言具体端点和行标签；不能只检查总笔数，
  也不能把 1.a 的手工标签表当作算法测试通过的证据。
- **KWX 包装必须透明。** 同一份转换输入和固定配置，直接调用保存的 KWX 代码与经适配类
  调用，比较全部端点 M 下标、价格、方向、规则及依赖，再检查映射后的全部 BiBar 标签。
  这验证包装没有改变参考结果，不代表已经证明 KWX 规则正确。
- **配置及映射边界。** 检查默认选择 kwx、未知算法拒绝、多行 M 分型去重、M 下标与分型
  序号分离、时区/单位转换、并列极值锚点，以及无 trace/未确定方向/缺依赖明确失败。
- **网页契约回归。** 用1.c三M例子断言CC分型区间为 `[7,14]` 而不是中心的 `[9,14]`；
  分开断言M组首代表时间和原始价格锚点下标。核对规范化后的bi_5k参数，确认没有错误启用
  strong，并将网页逐对象验收与本项目BiBar映射验收分开报告。

[source] 接口沿用现有 `experiments/chan_theory/fenxing.py` 和
`experiments/chan_theory/fenxing_series.py`；算法研究见 memo0026。
本次已实现Python类及测试；没有新增Bi CSV或图表类。

## 2. Implementation Result

### 2.a 实现了什么

> [execution] 2026-09-11，阶段7.4.61.1-3：**保留每根原始Kbar，在已有Fenxing行上加笔标签。**
> KWX负责选笔，本项目负责输入转换、原始价格锚点映射和跨行校验；两者不混写。

- `experiments/chan_theory/bi_bar.py`：`BiBar(Fenxing)`，新增三个元组及起终点属性。
- `experiments/chan_theory/bi_series.py`：`BiConfig`、`BiSeries`，显式计算、保存来源、校验及查询。
- `experiments/chan_theory/kwx_bi_adapter.py`：内部`KwxBiAdapter`，只转换、调用和映射，不重写KWX判断。
- `experiments/chan_theory/_kwx/`：网页的六个依赖文件，隔离导入；`provenance.json`保存各文件SHA-256。
  除导入路径和末尾换行外，与解码后的网页源码一致。没有安装新依赖、改动`.venv`或修改附录原文。
- `experiments/chan_theory/__init__.py`：公开`BiBar`、`BiConfig`、`BiSeries`，不公开KWX类型。

固定配置为1.c的`bi_5k`，实际配置指纹`ffb2448b188c`。原参考依赖中的其他模式不代表
本项目已经支持它们。网页未发现明确许可声明，来源归属保留在`_kwx/README.md`；
发布或迁入正式源码前，仍需确认使用和分发许可。

> [implementation] 端点定位一次读取`FenxingSeries.evidence_table()`中的
> `turning_raw_index`，复用Fenxing已有的价格贡献行及并列极值规则。
> 与逐笔调用`turning_raw_index()`含义相同，但不为每个端点重新扫描全部M组。
> `BiSeries`构造只校验已给结果，不再次调用选笔算法。

### 2.b Sample Use

在仓库根目录运行，输入使用现有完整参考CSV：

```python
from pathlib import Path
from tradinglab.data_io import CsvFileKlineTSeries
from experiments.chan_theory import (
    MergedKlineSeries, FenxingSeries, BiConfig, BiSeries,
)

raw = CsvFileKlineTSeries(
    Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv")
).read()
merged = MergedKlineSeries.derive_from(raw)
fenxings = FenxingSeries.derive_from(merged)
bis = BiSeries.derive_from(fenxings, BiConfig(algorithm="kwx"))

print(bis.count, bis.bi_count)                 # 10060 502
start, end = bis.endpoint_raw_indices_for_bi_tag("B0")
print(start, end, bis.raw_indices_for_bi_tag("B0"))
row = bis.klines[start]
print(row.merged_tag, row.fx_type, row.bi_tags, row.bi_start_tags)
assert row.to_fenxing() == fenxings.klines[start]
```

找不到的笔标签抛出`KeyError`；未确定方向的M、不能无损转为UTC整数秒的时间、
损坏的KWX端点或配置记录均报错，不包装为“没有笔”。正常未成笔则保留全部行及空元组。

## 3. Test Session

### 3.a 测试在哪里，如何运行

[verification] 测试文件：`experiments/chan_theory/test_bi_series.py`，共29项。
在仓库根目录执行：

```zsh
.venv/bin/python -m unittest experiments.chan_theory.test_bi_series
.venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

### 3.b 具体检查什么

- **原始行与共享端点。** 1.c主例应得到`B0: K1→K11`、`B1: K11→K15`；
  K11同时结束B0并开始B1，首尾未覆盖行仍存在。逐字段核对原始价格、时间、来源、M及分型信息。
- **对象契约。** 冻结对象、元组长度、重复/空标签、bool/负数/倒序下标、继承工厂与转换。
  构造结果不触发算法；列表输入转换为元组后，修改原列表不影响结果。
- **跨行校验。** 缺行、漏贴标签、同标签端点冲突、越界/错误价格锚点、同型两端、
  断开的相邻笔、非端点重叠、共享标签顺序错误均被拒绝。
- **首笔与同型。** 旧候选按顺序尝试；同型候选保留，全部配对失败才追加当前候选。
  同型延长要求严格新高/新低，相等不延长，也不误做距离检查。
- **三项标准检查。** 中心距离、原始包络缺口折算、相接不算缺口；
  half的两个严格条件分别测相等失败；区间极值允许同价，但拒绝越点。上下方向均覆盖。
- **失败与修正。** 两笔不足、修正关闭、前后极值门槛不满足、区间极值失败、
  没有未来证据、先出现有效反向笔、同价突破失败、延长不成功时回滚。
  主例及上下镜像均得到预期端点；截短输入与完整输入不同，但旧结果不被修改。
- **输入和坐标转换。** 分型下标用完整M位置，high/low用三M窗口；
  多行M只算一个分型，组首时间与价格锚点分开，并列极值服从来源的first/last设置。
  未定方向、缺时区/亚秒精度、错误算法名称和损坏参考输出均有失败测试。
- **参考代码。** 六个文件校验值与附录一致性测试防止意外改写；
  完整CSV逐笔摘要与网页固定摘要相同，再独立逐行验证每个BiBar的标签和起终点。

局部分支测试有些通过手工状态或mock隔离检查顺序；它们不是独立合法市场序列的证明。
完整数值主例、镜像例和完整CSV测试不替换KWX判断。

### 3.c 本机结果与产物

2026-09-11：Bi专项29项通过；全部实验202项通过（约29.7秒）；`src`回归42项通过（约2.7秒）。
第一轮发现测试调用了错误的参考方法名，已改为`_repair_sub_peak`后完整重跑。

> [evidence] 完整链：**10,060 Kbar → 6,200 M → 3,027 Fenxing → 502 Bi**。
> 原始10,060行全部保留。KWX参考标记为501 confirmed、1 forming；14笔的依赖晚于终点。
> 这些是KWX的状态输出，不是本项目对实时可知性或历史永不重画的保证。

逐笔摘要（包括方向、时间、价格、规则、M端点及依赖）与网页`check_02_stroke.py`一致：

```text
ca0276fd6440ba7bd2d1913852a03197cdb51f253fc6c45e2824f86eeec16381
```

Bi派生含转换、映射及结果校验约0.33秒；完整样本测试含上游计算、直接参考计算和逐行核对约3.5秒。
这是本机观察值，不是性能承诺。报告由完整样本测试重新生成，保存在：

```text
artifacts/experiments/chan_theory/bi_series_verification.json
```

报告记录时间、输入校验值、配置指纹、数量、摘要和耗时，不是Bi CSV导出文件。
完整实验回归会重新生成原有CSV/图表测试产物；本次没有新增Bi图表。

[boundary] 尚未验证或实现：strong/secondary/custom对外选项、逐根增量/回补接口、
CSV读写和Bi绘图。确认状态及完整推断过程的公开存储仍待后续设计。

## Appendix A. Reference Map

- [memo0026](memo0026_algo_of_bi.md): Bi interpretation, CC's step-by-step
  calculation, standard checks, and preserved reference code.

- [memo0020](memo0020_class_merged_kline_series.md): chapter structure, raw-aligned
  shape, rules/examples first, then members/methods and verification.
- [memo0019](memo0019_InterfaceChan.md), sections 1.f and 1.f.2: stage-owned
  config and Bi's dependency on Fenxing plus merged/raw evidence.
- [memo0023](memo0023_class_fenxing_series.md): repeated group labels, true
  price-contributor anchors, and source/config preservation.
- [memo0015](memo0015_oop_trading_architecture.md), Fenxing To Bi: previous local
  summary of the KWX gates, repair, and 502-Bi checkpoint.
- [KWX, definition topics A-E](https://www.kwx.me/cc/#stroke-definition),
  reread and expanded in the browser on 2026-09-10. The current page advertises
  source snapshot `b1348795d25d282aa769bce2f14fb366df269d7d`; the initial draft
  recorded `e86f2dd92920f9c36678d6b859fd4405dde8df85`. This is a source-version
  change, not evidence that every algorithm or fixture changed.
- Lessons [62](https://chzhshch.org/2007/06/30/0567-教你炒股票62/) and
  [65](https://chzhshch.org/2007/07/16/0593-教你炒股票65/): read the linked
  archived lesson texts, not only KWX's descriptions. Separation, alternating
  joints, and same-type handling support the discussion; the CC candidate pool,
  HALF formulas and repair guards are not verbatim lesson definitions.
- User-supplied KWX text: attachment
  `b39ac1e8-7d3b-4b6b-a33a-58744c4398f5/pasted-text.txt`, lines 2219-2708.
  Read `_try_first_bi`, `_extend_same_fx`, distance/HALF/peak checks,
  `_repair_sub_peak`, `_confirm_reverse_break`, and `bi_confirmed_flags`.
  This is **reference code from others**, not a Project 009 implementation.
- `records/cc/kline-to-zoushi-001/dce-kqm-m-15m-manifest.json`: recorded profile
  and count expectations. Website and saved CSV hashes differ; investigate
  normalized content before claiming reproducibility.


## Appendix B. External Bi Reference Code

[source] User-supplied KWX/CC code, received 2026-09-10. Attachment:
`45d5b910-33bf-4675-a026-9d8bde364849/pasted-text.txt`.

[reference] Quoted verbatim below, including comments and imports. This is
code from others, not Project 009 implementation or an adopted rule profile.
References to project decisions or user approvals inside the quote belong to
that source project. No code was installed or executed.

[note] The pasted opening docstring has two quotation marks, not three;
it is preserved as supplied. The `manual_rebuild` imports require the external
project. This quotation is not a standalone runnable module.

```python
""笔（Bi）— 在分型序列上派生 (算法说明卡 bi-v1 v4)。

统一参数化引擎：一套底层参数 + 成笔模式 (standard/strong/secondary)；profile 只是预设名。
口径优先链 (§1.1 / decision-0001 v1.4 §12.3：原文 > 用户确认的本项目口径 > 本项目自主实现；
参考项目 chan.py-main / czsc / chanlun-pro 无固定优先级，只作对照/启发/差异发现来源)；
分型恒在合并序列识别 (PR-3)。

成笔判定 (standard)：距离(bi_span_mode) → 端点检查(bi_endpoint_check) → 端点极值(bi_require_peak)。
- 距离 merged_center：分型中心合并下标差 (+缺口折算) ≥ bi_min_span。
- 距离 raw_extreme：①不共用 K（三元窗口无公共合并单元，内建）②极值原始 K 索引差 ≥ bi_min_span。
强势笔 (strong)：标准失败时，候选幅度 ≥ ratio × 相邻反向笔幅度（前一笔或后一笔）则成笔。
次笔 (secondary)：第一反向分型不成笔(pending)，第二同型处成笔；中间夹相反成笔则回退标准。

**纯函数**：合并/分型由引擎批量重派生 (版本缓存)，本模块无跨调用状态。strong_next「后一笔」
在单次派生内 = 向分型数组后方有界 look-ahead；回补由「dep 依赖水位线 + provisional」承载
(每笔记成笔实际查阅的最大分型下标 dep_to_index，serializer 据此判 confirmed，保证 strong_next
不在 confirmed 区插删笔)。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from manual_rebuild.algo.config import (
    BiEndpointCheck,
    BiFormationMode,
    BiSpanMode,
    ChanConfig,
)
from manual_rebuild.algo.models import Bi, BiDir, Fenxing, FxType, MergedKline
from manual_rebuild.algo.trace import (
    RULE_BI_DOWN_4K,
    RULE_BI_DOWN_5K,
    RULE_BI_DOWN_SECONDARY,
    RULE_BI_DOWN_STRONG_NEXT,
    RULE_BI_DOWN_STRONG_PREV,
    RULE_BI_UP_4K,
    RULE_BI_UP_5K,
    RULE_BI_UP_SECONDARY,
    RULE_BI_UP_STRONG_NEXT,
    RULE_BI_UP_STRONG_PREV,
    StructTrace,
)
from manual_rebuild.data import Kline

_ALGO_CARD_ID = "bi-v1"

# rule_kind → (up rule_id, down rule_id)。standard 再按 span_mode 细分 5k/4k (见 _rule_for)。
_RULE_STRONG_PREV = (RULE_BI_UP_STRONG_PREV, RULE_BI_DOWN_STRONG_PREV)
_RULE_STRONG_NEXT = (RULE_BI_UP_STRONG_NEXT, RULE_BI_DOWN_STRONG_NEXT)
_RULE_SECONDARY = (RULE_BI_UP_SECONDARY, RULE_BI_DOWN_SECONDARY)
_RULE_STD_MERGED = (RULE_BI_UP_5K, RULE_BI_DOWN_5K)
_RULE_STD_RAW = (RULE_BI_UP_4K, RULE_BI_DOWN_4K)


def bi_dep_index(bi: Bi) -> int | None:
    """笔依赖水位（与既有 overlay confirmed 判定同一事实来源）。"""
    if bi.trace is None:
        return None
    return bi.trace.dep_to_index if bi.trace.dep_to_index is not None else bi.trace.merged_to_index


def bi_confirmed_flags(bis: Sequence[Bi], n_merged: int) -> list[bool]:
    """返回每笔是否 confirmed；逐字保持 bi-v1 §10 的既有三条末端规则。"""
    n_bis = len(bis)
    last_dep = bi_dep_index(bis[-1]) if n_bis else None
    last_unstable = last_dep is None or last_dep >= n_merged - 2
    flags: list[bool] = []
    for i, bi in enumerate(bis):
        dep = bi_dep_index(bi)
        provisional = (
            i == n_bis - 1
            or dep is None
            or dep >= n_merged - 2
            or (i == n_bis - 2 and last_unstable)
        )
        flags.append(not provisional)
    return flags


@dataclass(slots=True)
class _WorkBi:
    """构建期可变笔。rule_kind ∈ standard/strong_prev/strong_next/secondary；dep = 依赖水位。"""

    start_fx: Fenxing
    end_fx: Fenxing
    direction: BiDir
    rule_kind: str
    dep_index: int


def build_bis(
    merged: list[MergedKline],
    fenxings: list[Fenxing],
    raw_klines: list[Kline],
    cfg: ChanConfig,
    *,
    profile_id: str,
    config_hash: str,
) -> list[Bi]:
    """从分型序列派生笔序列（纯函数，按 cfg 统一参数 + 成笔模式判定）。"""
    cfg = cfg.normalize()
    builder = _BiBuilder(merged, fenxings, raw_klines, cfg)
    builder.run()
    return builder.finish(profile_id, config_hash)


class _BiBuilder:
    """单次派生的内部状态机（不跨调用持久）。"""

    def __init__(
        self,
        merged: list[MergedKline],
        fenxings: list[Fenxing],
        raw_klines: list[Kline],
        cfg: ChanConfig,
    ) -> None:
        self._merged = merged
        self._fxs = fenxings
        self._raw = raw_klines
        self._cfg = cfg
        self._bis: list[_WorkBi] = []
        self._candidates: list[Fenxing] = []  # standard/strong 首笔候选

    def run(self) -> None:
        if self._cfg.bi_formation_mode is BiFormationMode.SECONDARY:
            # 次笔 = 高一级别一笔 = 老笔的线段(特征序列法)。**暂搁置不输出**(用户 2026-06-17)：
            # 旧"破坏式合并"在长趋势上过度合并 → 已回退；待特征序列法线段草案确认后实现 (§5.8)。
            self._bis = []
        else:
            for i, fx in enumerate(self._fxs):
                self._feed_std_strong(i, fx)

    # ── standard / strong 主循环 ─────────────────────────────────────────
    def _feed_std_strong(self, i: int, fx: Fenxing) -> None:
        if not self._bis:
            self._try_first_bi(fx)
            return
        last = self._bis[-1]
        if fx.fx_type is last.end_fx.fx_type:
            self._extend_same_fx(fx)
            return
        if self._try_standard_form(last.end_fx, fx):
            self._append(last.end_fx, fx, "standard", fx.index)
            return
        # 标准失败 → 强势 (前/后一笔)
        if self._cfg.bi_formation_mode is BiFormationMode.STRONG and self._try_strong(
            i, last.end_fx, fx
        ):
            return
        if self._cfg.bi_fractal_repair:
            self._repair_sub_peak(i, fx)

    def _try_first_bi(self, fx: Fenxing) -> None:
        for cand in self._candidates:
            if cand.fx_type is fx.fx_type:
                continue
            if self._try_standard_form(cand, fx):
                self._append(cand, fx, "standard", fx.index)
                self._candidates = []
                return
        self._candidates.append(fx)

    # ── 强势笔 (前一笔 / 后一笔；前优先) ─────────────────────────────────
    def _try_strong(self, i: int, start_fx: Fenxing, end_fx: Fenxing) -> bool:
        cand_amp = _bi_amplitude(start_fx, end_fx)
        ratio = self._cfg.bi_strength_ratio
        # 前一笔 (实时，已构建的相邻反向笔)
        prev = self._bis[-1]
        prev_amp = _bi_amplitude(prev.start_fx, prev.end_fx)
        if prev_amp > 0 and cand_amp >= ratio * prev_amp:
            self._append(start_fx, end_fx, "strong_prev", end_fx.index)
            return True
        # 后一笔 (有界 look-ahead: 从 end_fx 起首个 standard 反向笔；禁递归强势)
        nxt = self._lookahead_next_std_bi(i, end_fx)
        if nxt is not None:
            next_amp, dep_fx_index = nxt
            if next_amp > 0 and cand_amp >= ratio * next_amp:
                self._append(start_fx, end_fx, "strong_next", dep_fx_index)
                return True
        return False

    def _lookahead_next_std_bi(
        self, i: int, from_fx: Fenxing
    ) -> tuple[float, int] | None:
        """从 from_fx 起，按 standard 规则形成的下一条反向笔的 (幅度, 其端点分型下标)。

        只认 standard（不递归强势，已定 2）；取首个 standard 成笔的反向分型（有界）。
        """
        for q in range(i + 1, len(self._fxs)):
            nf = self._fxs[q]
            if nf.fx_type is from_fx.fx_type:
                continue
            if self._try_standard_form(from_fx, nf):
                return _bi_amplitude(from_fx, nf), nf.index
        return None

    # 次笔(=老笔线段, 特征序列法) 暂搁置, 见 run()。实现待线段草案确认 (用户 2026-06-17)。

    # ── 同型延伸 / sub_peak 修正 (与 standard 共用) ──────────────────────
    def _extend_same_fx(self, fx: Fenxing) -> None:
        # 同型分型永远取更极值 (两顶取更高 / 两底取更低, 第 65 课)。原 first 变体 v7 删除。
        last = self._bis[-1]
        if last.direction is BiDir.UP:
            if fx.high > _top_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)
        else:
            if fx.low < _bottom_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)

    def _repair_sub_peak(self, i: int, fx: Fenxing) -> bool:
        """笔破坏修正 (bi_fractal_repair, 项目变体)：反弹笔起点被反向更极值 fx 击穿时，
        仅当**反向确认守卫**通过 (fx 为真极值、反弹是假反弹) 才吸收反弹笔、把前一笔延伸到 fx。
        守卫见 ``_confirm_reverse_break``；吸收笔 dep_index = 确认处下标 (确认前恒 provisional)。
        """
        if len(self._bis) < 2:
            return False
        last, prev = self._bis[-1], self._bis[-2]
        if last.direction is BiDir.DOWN:
            if fx.high < _top_value(last.start_fx):
                return False
            if _bottom_value(last.end_fx) < _bottom_value(prev.start_fx):
                return False
        else:
            if fx.low > _bottom_value(last.start_fx):
                return False
            if _top_value(last.end_fx) > _top_value(prev.start_fx):
                return False
        if not self._is_peak(prev.start_fx, fx, _direction_of(fx)):
            return False
        confirm_index = self._confirm_reverse_break(i, fx, last)
        if confirm_index is None:
            return False
        popped = self._bis.pop()
        before = self._bis[-1].end_fx
        self._extend_same_fx(fx)
        if self._bis[-1].end_fx is before:
            self._bis.append(popped)
            return False
        self._bis[-1].dep_index = max(self._bis[-1].dep_index, confirm_index)
        return True

    def _confirm_reverse_break(self, i: int, fx: Fenxing, last: _WorkBi) -> int | None:
        """反向确认守卫 (bi-v1 笔破坏修正小节，项目变体)。

        fx 击穿反弹笔 ``last`` 起点后，从 fx 在分型序列向后**有界扫描**：
        - 若价格在「从反弹笔顶/底 T 形成有效反向笔」**之前**先**越过 T 的极值** →
          反弹是假反弹、fx 是真极值 → 返回确认处合并下标 (供 dep 水位线，确认前恒 provisional)。
        - 若先形成「T→反向有效笔」 → 反弹是真实摆动、T 成立 → 返回 ``None`` (不吸收)。
        - 扫到末尾两者皆无 (数据不足) → ``None`` (保守不吸收，随回补再判)。
        """
        t = last.end_fx
        up = last.direction is BiDir.UP
        for q in range(i + 1, len(self._fxs)):
            g = self._fxs[q]
            if up:
                if g.fx_type is FxType.TOP and g.high > t.high:
                    return g.index
                if g.fx_type is FxType.BOTTOM and self._try_standard_form(t, g):
                    return None
            else:
                if g.fx_type is FxType.BOTTOM and g.low < t.low:
                    return g.index
                if g.fx_type is FxType.TOP and self._try_standard_form(t, g):
                    return None
        return None

    def _append(
        self, start: Fenxing, end: Fenxing, rule_kind: str, dep_index: int
    ) -> None:
        self._bis.append(_WorkBi(start, end, _direction_of(end), rule_kind, dep_index))

    # ── 标准成笔判定 (距离 → 端点检查 → 端点极值) ───────────────────────
    def _try_standard_form(self, start: Fenxing, end: Fenxing) -> bool:
        if start.fx_type is end.fx_type:
            return False
        if not self._check_distance(start, end):
            return False
        if not self._check_endpoint(start, end):
            return False
        if self._cfg.bi_require_peak and not self._is_peak(
            start, end, _direction_of(end)
        ):
            return False
        return True

    # ── 距离 (bi_span_mode 分派) ─────────────────────────────────────────
    def _check_distance(self, start: Fenxing, end: Fenxing) -> bool:
        if self._cfg.bi_span_mode is BiSpanMode.MERGED_CENTER:
            return self._check_center_span(start, end)
        return self._check_raw_extreme(start, end)

    def _check_center_span(self, start: Fenxing, end: Fenxing) -> bool:
        base_span = end.index - start.index
        if base_span >= self._cfg.bi_min_span:
            return True
        if not self._cfg.bi_gap_as_bar:
            return False
        gap_count = sum(
            1
            for i in range(start.index, end.index)
            if self._has_gap(self._merged[i], self._merged[i + 1])
        )
        return base_span + gap_count >= self._cfg.bi_min_span

    def _check_raw_extreme(self, start: Fenxing, end: Fenxing) -> bool:
        # ① 不共用 K (三元窗口无公共合并单元，内建)
        if start.index + 1 >= end.index - 1:
            return False
        # ② 极值原始 K 索引差 ≥ bi_min_span
        if end.fx_type is FxType.TOP:
            start_raw = self._extreme_raw_index(start, want_high=False)
            end_raw = self._extreme_raw_index(end, want_high=True)
        else:
            start_raw = self._extreme_raw_index(start, want_high=True)
            end_raw = self._extreme_raw_index(end, want_high=False)
        return end_raw - start_raw >= self._cfg.bi_min_span

    def _has_gap(self, a: MergedKline, b: MergedKline) -> bool:
        a_lo, a_hi = self._raw_extremes(a)
        b_lo, b_hi = self._raw_extremes(b)
        return max(a_lo, b_lo) > min(a_hi, b_hi)

    def _raw_extremes(self, u: MergedKline) -> tuple[float, float]:
        members = self._raw[u.start_index : u.end_index + 1]
        return min(k.low for k in members), max(k.high for k in members)

    def _extreme_raw_index(self, fx: Fenxing, *, want_high: bool) -> int:
        u = self._merged[fx.index]
        members = self._raw[u.start_index : u.end_index + 1]
        if want_high:
            best = max(range(len(members)), key=lambda i: (members[i].high, -i))
        else:
            best = min(range(len(members)), key=lambda i: (members[i].low, i))
        return u.start_index + best

    # ── 端点有效性 (bi_endpoint_check；none 跳过) ───────────────────────
    def _check_endpoint(self, start: Fenxing, end: Fenxing) -> bool:
        method = self._cfg.bi_endpoint_check
        if method is BiEndpointCheck.NONE:
            return True
        s_pre, s_mid, s_next = self._fx_units(start)
        e_pre, e_mid, e_next = self._fx_units(end)
        if start.fx_type is FxType.TOP:  # 向下笔: 顶 → 底
            if method is BiEndpointCheck.HALF:
                item2_high = max(e_pre.high, e_mid.high)
                self_low = min(s_mid.low, s_next.low)
            elif method is BiEndpointCheck.LOSS:
                item2_high = e_mid.high
                self_low = s_mid.low
            else:
                item2_high = max(e_pre.high, e_mid.high, e_next.high)
                self_low = min(s_pre.low, s_mid.low, s_next.low)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.low > item2_high
            return s_mid.high > item2_high and e_mid.low < self_low
        else:  # 向上笔: 底 → 顶
            if method is BiEndpointCheck.HALF:
                item2_low = min(e_pre.low, e_mid.low)
                cur_high = max(s_mid.high, s_next.high)
            elif method is BiEndpointCheck.LOSS:
                item2_low = e_mid.low
                cur_high = s_mid.high
            else:
                item2_low = min(e_pre.low, e_mid.low, e_next.low)
                cur_high = max(s_pre.high, s_mid.high, s_next.high)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.high < item2_low
            return s_mid.low < item2_low and e_mid.high > cur_high

    def _is_peak(self, start: Fenxing, end: Fenxing, direction: BiDir) -> bool:
        if direction is BiDir.UP:
            thr = _top_value(end)
            return all(u.high <= thr for u in self._merged[start.index + 1 : end.index])
        thr = _bottom_value(end)
        return all(u.low >= thr for u in self._merged[start.index + 1 : end.index])

    def _fx_units(self, fx: Fenxing) -> tuple[MergedKline, MergedKline, MergedKline]:
        return (
            self._merged[fx.index - 1],
            self._merged[fx.index],
            self._merged[fx.index + 1],
        )

    # ── 输出 ─────────────────────────────────────────────────────────────
    def finish(self, profile_id: str, config_hash: str) -> list[Bi]:
        out: list[Bi] = []
        for wb in self._bis:
            up = wb.direction is BiDir.UP
            start_price = _bottom_value(wb.start_fx) if up else _top_value(wb.start_fx)
            end_price = _top_value(wb.end_fx) if up else _bottom_value(wb.end_fx)
            rule_id = _rule_for(wb, self._cfg.bi_span_mode)
            trace = StructTrace(
                algo_card_id=_ALGO_CARD_ID,
                rule_id=rule_id,
                profile_id=profile_id,
                config_hash=config_hash or None,
                source_from_ts=self._merged[wb.start_fx.index - 1].start_ts,
                source_to_ts=self._merged[wb.end_fx.index + 1].end_ts,
                merged_from_index=wb.start_fx.index,
                merged_to_index=wb.end_fx.index,
                dep_to_index=wb.dep_index,
            )
            out.append(
                Bi(
                    period=wb.end_fx.period,
                    direction=wb.direction,
                    start_ts=wb.start_fx.timestamp,
                    end_ts=wb.end_fx.timestamp,
                    start_price=start_price,
                    end_price=end_price,
                    high=end_price if up else start_price,
                    low=start_price if up else end_price,
                    trace=trace,
                )
            )
        return out


def _rule_for(wb: _WorkBi, span_mode: BiSpanMode) -> str:
    """rule_id 按成笔实际规则派生 (bi-v1 §7)。standard 再按 span_mode 分 5k/4k。"""
    up = wb.direction is BiDir.UP
    if wb.rule_kind == "strong_prev":
        return _RULE_STRONG_PREV[0 if up else 1]
    if wb.rule_kind == "strong_next":
        return _RULE_STRONG_NEXT[0 if up else 1]
    if wb.rule_kind == "secondary":
        return _RULE_SECONDARY[0 if up else 1]
    # standard
    pair = _RULE_STD_MERGED if span_mode is BiSpanMode.MERGED_CENTER else _RULE_STD_RAW
    return pair[0 if up else 1]


def _bi_amplitude(start_fx: Fenxing, end_fx: Fenxing) -> float:
    """笔幅度 = abs(端点价差)（绝对价差，本轮锁定）。方向由 end_fx 决定。"""
    if end_fx.fx_type is FxType.TOP:  # 向上笔: 底→顶
        return abs(_top_value(end_fx) - _bottom_value(start_fx))
    return abs(_bottom_value(end_fx) - _top_value(start_fx))  # 向下笔: 顶→底


def _direction_of(end_fx: Fenxing) -> BiDir:
    return BiDir.UP if end_fx.fx_type is FxType.TOP else BiDir.DOWN


def _top_value(fx: Fenxing) -> float:
    return fx.high


def _bottom_value(fx: Fenxing) -> float:
    return fx.low
```
