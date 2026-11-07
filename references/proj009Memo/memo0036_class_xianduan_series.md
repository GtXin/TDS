# memo0036_class_xianduan_series

[class design] [chan] [xianduan] [series first] [implemented]

## 0. Scope And Purpose

**`XianduanSeries`接收已有笔序列，计算线段，再把线段归属和端点标回每根原始Kbar。** 本篇按[memo0027](memo0027_class_bi_series.md)的章节及对象关系设计；已在7.4.116实现两个类及两套独立算法，运行结果见第2、3章。

```text
FenxingSeries + BiConfig -> BiSeries
BiSeries + XianduanConfig -> XianduanSeries

行继承：XianduanBar -> BiBar -> Fenxing -> MergedKline
序列来源：XianduanSeries.source_series -> BiSeries
          -> FenxingSeries -> MergedKlineSeries -> KlineTSeries
```

- **Input：** 已有`BiSeries`，沿`source_series`访问上游；不重新选笔，也不另传一份可能不一致的K线。
- **Result：** 保留所有原始行及合并、分型、笔字段，新增线段标签与原始行端点。共享端点可属于相邻两段。
- **Classes：** `XianduanBar`是一行带线段信息的`BiBar`；`XianduanSeries`持有完整结果；`XianduanConfig`只保存计算设置。
- **Algorithm boundary：** [memo0032](memo0032_algo_of_xianduan_2nd.md#3-与-kwxcc-代码的关键差距)记录项目推导与KWX的差异。按用户指定，两套算法都作为独立选项（`options0033memo`是选项名，规则来源仍为memo0032，不是笔算法memo0033）：`kwx`包装参考算法，`options0033memo`执行0032规格；不混用两者的规则。

[scope] 本次实现Python类、配置和两个适配器。CSV、图表由后续独立任务负责；本次不包含中枢、增量更新或`src/`迁入。

## 1. Class Design

### 1.a XianduanBar: Members And Methods

**`XianduanBar`是一根原始Kbar的完整上游信息加上线段归属，不是一整条线段的容器。** 使用不可变dataclass `XianduanBar(BiBar)`，模块名为`xianduan_bar.py`。

**Inherited Members / 继承成员。** 以下字段全部保留，不在子类重复声明：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `symbol`, `period`, `source` | `str` | 原标的、Kbar周期、来源；period不改成线段级别 |
| `timestamp` | `datetime` | 当前原始Kbar时间 |
| `open`, `high`, `low`, `close`, `volume` | `float` | 原始OHLCV，不替换为线段端点价 |
| `raw_index` | `int` | 当前原始行下标 |
| `merged_tag` | `str` | 所属合并M标签 |
| `merged_low`, `merged_high` | `float` | 所属M的合并价格 |
| `merged_direction` | `Literal["up", "down"] \| None` | 合并方向，不是线段方向 |
| `merge_state` | `Literal["resolved", "direction_unresolved"]` | 合并方向状态 |
| `is_group_first`, `is_group_extreme` | `bool` | 合并组首行和选定极值行 |
| `fx_type` | `Literal["top", "bottom"] \| None` | 所属M的分型类型 |
| `bi_tags` | `tuple[str, ...]` | 本行所属笔 |
| `bi_start_raw_indices`, `bi_end_raw_indices` | `tuple[int, ...]` | 与笔标签逐项对应的原始端点下标 |

**Inherited Properties And Methods / 已有属性与方法。**

- 保留`k_low/k_high`、`is_top/is_bottom`、`fenxing_price`以及笔的起终点标签和布尔属性。
- `to_fenxing()`、`to_merged_kline()`、`to_raw_kline()`仍返回去掉后续层字段的新对象。
- 继承`from_fenxing()`、`from_merged_kline()`、`from_kline()`，但正常入口使用下面的`from_bi_bar()`：旧工厂可能不复制已有笔标签。
- 沿用父类初始化校验，并在重写`validate()`时调用`super().validate()`。
- `MergedKline`不是`Kline`子类；需要原始蜡烛属性时先`to_raw_kline()`，不虚构继承方法。[^rows]

**New Members / 新增成员。** 沿用0027的三个标签与端点元组；方向从来源端点推导，不重复存储：

```python
xianduan_tags: tuple[str, ...] = ()
xianduan_start_raw_indices: tuple[int, ...] = ()
xianduan_end_raw_indices: tuple[int, ...] = ()
```

三个元组按位置配对。`X0`、`X1`按本次结果顺序编号，重算后不保证标签身份稳定；下标始终是来源`BiSeries.klines`的位置，不是笔序号或M序号。标签表示本次选出的区间，不表示永久确认。

**方向含义。** `up`表示该线段终点价格严格高于起点，`down`表示严格低于起点；两端同价不接受为这两种方向。价格使用来源笔的端点价，不使用当前行Kbar的涨跌。方向由`XianduanSeries.direction_for_xianduan_tag()`按标签查询时计算，不在行上增加方向字段。共享端点属于两条线段，应分别查询X0、X1；单独一行的涨跌不能代表两段方向。

**Example / 例子。** 仅演示存储：假设来源笔为`B0:K1→K3`、`B1:K3→K5`、`B2:K5→K7`、`B3:K7→K9`、`B4:K9→K11`、`B5:K11→K13`，本次结果选出`X0:K1→K7`、`X1:K7→K13`。假设来源端点价为K1=100、K7=130、K13=110，则X0上升、X1下降。完整原始输入为K0–K14；这些价格与下标仅演示存储，不证明算法会选出这两段。

| 原始行 | `xianduan_tags` | 起点元组 | 终点元组 |
| --- | --- | --- | --- |
| K0 | `()` | `()` | `()` |
| K1–K6（各行相同） | `("X0",)` | `(1,)` | `(7,)` |
| K7 | `("X0", "X1")` | `(1,7)` | `(7,13)` |
| K8–K13（各行相同） | `("X1",)` | `(7,)` | `(13,)` |
| K14 | `()` | `()` | `()` |

K3是两笔的共享端点，却只是X0内部的一行；K7才是两个线段的共享端点。K0/K14仍存在，所有原有笔标签不变。

**New Properties / 新增属性。**

- `xianduan_start_tags / xianduan_end_tags -> tuple[str, ...]`：按起点/终点下标等于本行`raw_index`筛选标签。
- `is_xianduan_start / is_xianduan_end -> bool`：相应标签是否非空；共享端点可同时为真。
- 例：K7起点标签为`("X1",)`、终点标签为`("X0",)`；K3两者均为空。

**New Or Overridden Methods / 新增或重写的方法。**

- `from_bi_bar(row, *, xianduan_tags=(), xianduan_start_raw_indices=(), xianduan_end_raw_indices=()) -> XianduanBar`：复制全部BiBar字段并附加线段信息；不执行线段算法。
- `validate() -> None`：先检查父类，再检查三个元组类型、等长、非空且不重复的标签、非负整数下标（排除bool）以及`start < end`、`start <= raw_index <= end`；类型错抛`TypeError`，值不合法抛`ValueError`。
- `to_bi_bar() -> BiBar`：删除线段字段，返回与来源行相同的BiBar。

[boundary] 单行校验不能证明线段算法正确。来源端点是否存在、跨行覆盖是否一致由序列检查。行对象不读写文件、不画图。

### 1.b XianduanSeries: Members And Methods

**`XianduanSeries`保存与来源等长的标记行；没有线段时，仍保留全部Kbar。** 序列采用组合，不继承`BiSeries`；行采用继承，与0027的拓扑一致。

**Members / 成员。** 不可变dataclass：

```python
klines: tuple[XianduanBar, ...]
config: XianduanConfig
source_series: BiSeries
```

构造器只验证已给结果；`derive_from()`才计算。`XianduanConfig`放在`xianduan_series.py`中，只保存规则，不存搜索位置、候选段或特征序列状态。

**Properties / 派生属性。**

- `count / raw_count`：原始行数；`xianduan_count`：不同X标签数量，不数重复出现的行标签。
- `bi_count / merged_count / fenxing_count`：从来源读取，不重算。
- `symbol / period / start_timestamp / end_timestamp`：完整来源标识与范围。

**Methods / 方法。**

- `derive_from(source_series: BiSeries, config: XianduanConfig) -> XianduanSeries`：使用完整来源重算并返回新对象；调用者明确传入算法配置，不提供默认配置，不恢复旧调用的内部状态。
- `validate() -> None`：验证来源与配置、等长逐行对应及全部继承字段相同；每个X在所有成员行的端点一致，来源端点价格不能相等，标签恰覆盖原始闭区间`[start,end]`，端点对应来源笔边界。非共享端点不得出现段区间重叠；标签顺序按区间顺序。
- `raw_indices_for_xianduan_tag(tag) -> tuple[int, ...]`：返回闭区间原始下标；未知标签抛`KeyError`。
- `endpoint_raw_indices_for_xianduan_tag(tag) -> tuple[int,int]`：返回原始起终点；未知标签抛`KeyError`。
- `direction_for_xianduan_tag(tag) -> Literal["up", "down"]`：取该段的来源起终点价格，终点高于起点返回`up`，低于起点返回`down`；同价或无法取得合法端点价报`ValueError`，未知标签抛`KeyError`。价格沿用来源分型的`fenxing_price`（顶取`merged_high`、底取`merged_low`），不比较原始行下标大小或当前Kbar收盘价。
- `bi_tags_for_xianduan_tag(tag) -> tuple[str, ...]`：返回整笔区间被线段包含的来源笔，按时间排序。不能把端点行的全部`bi_tags`直接并入：K7也属于B3，但X0只含B0–B2。
- `to_list() -> list[XianduanBar]`、`raw_klines() -> tuple[Kline,...]`、`timestamps() -> tuple[datetime,...]`、`closes() -> tuple[float,...]`：与0027含义相同，保留完整原始时间轴。

**覆盖政策。** 两项都要求相邻输出段共享端点，内部不得留洞；未分段前缀和尾部仍保留原始行、X标签为空。`kwx`保留参考入口返回的所有区间，包括未冻结结果；`options0033memo`只输出S6.b／S7.a确认的段，不补画尾段。序列校验检查覆盖，不替代算法确认。

[decision] 线段端点沿用来源笔的原始价格锚点，不扩大到端点M整组，也不扩大到未来证据行。向上/下由来源笔的端点价判断，不能用锚点行原始high/low替代所属M的合并价格。

[open] 三个元组表达归属及区间，方向通过来源端点推导。`confirmed`、证据时刻和参考代码`freeze_state`不是同一概念；接口确定前不能用X标签承诺冻结或实时可知，也不能直接作为已确认中枢输入。

### 1.c Derive From: Algorithm And KWX Boundary

**调用者给已有笔，适配层负责整理一次笔列表、调用选定计算、映射回原始行。** 本节对应0027的KWX规格位置，扩展为两个明确选项；0032与参考代码在起点、冻结和尾部输出上不同。

**Interface / 对外接口。** 实际签名如下，类可从`experiments.chan_theory`导入：

```python
@dataclass(frozen=True)
class XianduanConfig:
    algorithm: Literal["kwx", "options0033memo"]  # 必填，调用者明确选择

@classmethod
def derive_from(cls, source_series: BiSeries,
                config: XianduanConfig) -> XianduanSeries:
    ...
```

配置只接受这两个名称，其他字符串抛`ValueError`，非字符串抛`TypeError`。两项均已实现，选中算法出错时直接报错，不切换另一项。`options0033memo`独立执行0032树图，不调用KWX线段计算。

**分型规则边界。** 按用户最新决定，项目K线分型和`options0033memo`的第一／第二特征序列分型统一严格比较，中间高低点与两侧比较有任一必要等号便不成立。现有FenxingSeries已为严格规则。`kwx`选项继续忠实包装固定外部快照，其边界差异须在结果对照中说明；不修改参考源码后仍称为原版KWX。另按用户最新决定，`options0033memo`的三笔重叠要求`max(L)<min(H)`，单点接触走S3.b／S4.b；S5的两元素接触仍按原树图算无缺口。

**Wrapper / 包装边界。** 两个适配器都是内部实现，均持有不可变配置，每次调用建立独立工作状态；不共享可变搜索状态。

| 选项 | 内部适配器 | 规则依据 |
| --- | --- | --- |
| `kwx` | `KwxXianduanAdapter` | 固定KWX快照、规范化配置，调用`build_xianduans()` |
| `options0033memo` | `Memo0032XianduanAdapter` | 已批准版本的0032步骤S1–S7；保留其起点、候选和确认政策 |

适配器分别放在`kwx_xianduan_adapter.py`和`memo0032_xianduan_adapter.py`。
0032算法内核放在同模块，`calculate()`从S1执行到输入耗尽，返回已确认的端点区间和内部调试步骤。调试步骤的`evidence`是本次判断查看的点下标，不是累计数据可用时刻，也不是公开确认元数据。

```text
XianduanSeries.derive_from(bis, config)
    -> config.algorithm == "kwx": KwxXianduanAdapter(config).derive_rows(bis)
       config.algorithm == "options0033memo": Memo0032XianduanAdapter(config).derive_rows(bis)
    -> tuple[XianduanBar, ...]
    -> XianduanSeries(klines=rows, config=config, source_series=bis)
```

**Workflow / 包装流程。** 这是接口数据流，不是重写线段算法：

1. 校验来源与配置。非法输入报错，不能伪装成空线段；保留来源所有行。
2. 汇集唯一B标签，以起终点下标按时间排序，核对同标签端点一致。不能按字符串排序把B10排在B2前，也不能每读到一行就新增一笔。
3. 建立笔序号、原始端点、M位置和端点价格的明确映射。每笔从来源读取，不重跑`BiSeries.derive_from()`。空笔输入仍保留原始行；是否有最少笔数由选定算法确定，不能混用0032的16笔与参考入口的3笔条件。
4. 每次建立新的计算工作状态，调用已选定算法。KWX固定快照和预设见下文；0032按S1–S7执行。
5. 将输出首末笔边界映射回原始锚点，对每个结果回填X标签及起终点。参考算法若返回方向，适配层应与来源端点推导值核对；不一致则报错，不新增重复字段。输出引用不存在的笔、无法唯一映射或状态政策不明时明确失败，不以最近时间猜端点。
6. 构造结果并执行跨行校验，返回新序列；源BiSeries及旧XianduanSeries均不修改。原始输入耗尽只结束本次计算，不自动确认尾段。

**Example / 下标映射。** 1.a中适配输入第0–2笔对应B0–B2；它们组成X0时，结果回填K1–K7。来源包含B3的K7标签不改变这个成员范围；证据若来自K11，也不把X0终点从K7移到K11。

**Source And Limits / 实际包装边界。**

- `BiBar`的三个元组提供笔范围，来源分型提供合并端点价；输入笔不重新计算。共用映射还核对价格方向与端点分型一致、相邻笔方向交替。[^rows]
- 保存的KWX线段决策只读笔的几何数据；`Bi.trace`仅用于汇集来源信息，并明确支持`None`。包装器据此传`trace=None`，没有伪造依赖证据或修改上游类。[^reference]
- KWX固定使用`standard / line_only / off / off / peak`，`bi_5k`来源标识；规范化配置哈希为`ffb2448b188c`。独立`_kwx_xianduan/`包保留参考算法，已有Bi的`_kwx/`不变。
- 输入参考Bi的时间取实际原始锚点时间，可能不同于完整CC引擎的M组代表时间；因此这里只保证相同几何输入的区间与方向复现，不声称恢复参考对象ID、依赖链或确认时刻。
- KWX全部输出区间均回填，包含`frozen / soft_n0 / pending_n1 / forming`。三个元组只保存成员及端点，不保存这些状态；本次样本有7段的参考`dep_to_index`小于其末笔下标，不能将该字段直接当作实时可知水位。
- 参考`Xianduan`表示整段，`XianduanBar`表示一行Kbar。参考段的`high/low`不会覆盖原始OHLC。

### 1.d Test Methods

**先验证存储契约，再验证算法与适配；手工标签正确不证明线段划分正确。** 以下是验收范围；已运行部分与暂未公开的状态接口分开记录，第3章给出测试入口：

- 逐行比较`result.klines[i].to_bi_bar() == source.klines[i]`，覆盖全部继承字段。
- 用1.a的15行例检查2段、共享端点K7、内部笔端点K3、无标签首尾行及`bi_tags_for_xianduan_tag("X0") == ("B0","B1","B2")`。
- 检查查询X0返回`up`、X1返回`down`；共享端点K7不存单一方向。覆盖同价端点拒绝、未知标签、价格取合并端点而非原始OHLC，以及适配输出方向与推导值不一致时失败。
- 行校验拒绝长度不等、重复/空标签、负数/bool下标、倒序区间；序列校验拒绝越界、漏贴、多贴、同标签冲突、非来源端点和字段改动。
- 检查未知标签`KeyError`、未知算法明确拒绝、正常无段与依赖失败分开；空笔输入保留所有行。
- 检查B2/B10数字顺序、多行M、共享端点、并列极值锚点、组首代表时间与价格贡献行的区别。
- 分派测试分别核对`kwx`只调用KWX适配器、`options0033memo`只调用0032适配器；未知值拒绝，任一算法失败不切换选项。
- 对两个选项分别验证相同输入与配置重复调用结果相同；扩大输入后重算可以改标签，但不得污染旧结果或来源。
- 对两个选项各用自己的预期答案，从真正入口覆盖上下方向、相等、起点失败、候选改写、尾部及覆盖政策。KWX直接参考输出与其适配输出逐项比较；0032逐步状态及端点按书面规格独立验收。两选项结果有差异时记录差异，不强迫一致。
- 为`options0033memo`的S3／S4各覆盖正宽度、单点接触和分离，确认接触走失败分支及其上下镜像；三笔不足不能伪装成失败。
- 为`options0033memo`的顶／底分型各覆盖四个比较的等号失败，并检查未突破时分别去S6.c／S7.d；对KWX单独记录边界差异，不要求两选项同结果。
- 确认/证据元数据接口补齐后，再测试状态及知识时刻；用未来证据产生的结果不得在更早截面标成已知。

## 2. Implementation Result

### 2.a 实现了什么

- [XianduanBar](../../experiments/chan_theory/xianduan_bar.py)：继承BiBar，保存三个线段元组，提供端点属性和可逆转换。
- [XianduanSeries与配置](../../experiments/chan_theory/xianduan_series.py)：保存来源、明确分派算法、校验完整覆盖并提供成员／端点／方向查询。
- [共用映射](../../experiments/chan_theory/xianduan_support.py)：按时间整理已有笔，读取来源合并价格，再映射回全部原始行。
- [KWX适配器](../../experiments/chan_theory/kwx_xianduan_adapter.py)与[独立0032实现](../../experiments/chan_theory/memo0032_xianduan_adapter.py)：各自使用自己的规则和尾部政策。
- 三个公开类已由`experiments.chan_theory`导出；复用现有Python环境，无新增第三方依赖。

0032的窗口状态只存活于一次完整计算：换候选回S5时，从固定段起点重放第一序列；S7.b进入S6时，从当前候选后的规定位置重放第二序列。窗口失败或忽略非候选处分型后，从第二根原始特征笔继续重放；已经读入但尚未消费的后续笔保留。具体规则及步骤映射见[memo0032第3.g节](memo0032_algo_of_xianduan_2nd.md#3g-实现与可执行验证)。

### 2.b Sample Use

已有`bis: BiSeries`时可直接运行：

```python
from experiments.chan_theory import XianduanConfig, XianduanSeries

kwx_segments = XianduanSeries.derive_from(
    bis, XianduanConfig(algorithm="kwx"))
segments = XianduanSeries.derive_from(
    bis, XianduanConfig(algorithm="options0033memo"))

assert segments.source_series is bis
assert all(row.to_bi_bar() == source
           for row, source in zip(segments.klines, bis.klines))
if segments.xianduan_count:
    print(segments.endpoint_raw_indices_for_xianduan_tag("X0"))
    print(segments.bi_tags_for_xianduan_tag("X0"))
    print(segments.direction_for_xianduan_tag("X0"))
```

两项接收同一个`bis`，端点和段数可以不同。0032少于16笔返回保留全部行的无段结果；KWX入口少于3笔无段。单独构造`XianduanSeries(rows, config, bis)`只验证已有结果，不运行算法。

## 3. Test Session

### 3.a 测试在哪里，如何运行

从仓库根目录运行：

```bash
PYTHONPATH=src .venv/bin/python -m unittest \
  experiments.chan_theory.test_bi_series \
  experiments.chan_theory.test_xianduan_series \
  experiments.chan_theory.test_kwx_xianduan_adapter \
  experiments.chan_theory.test_memo0032_xianduan
PYTHONPATH=src .venv/bin/python -m experiments.chan_theory.check_xianduan_series
```

### 3.b 具体检查什么

- **类契约15项：** 所有来源字段、共享端点、完整闭区间、无标签首尾、无内部洞、非法配置／标签、无段、分派及失败不回退。多行M和并列极值分别测试`first/last`原始锚点，方向使用合并价。
- **KWX适配9项：** 原始／本地快照指纹、固定配置、直接调用保存参考文件的独立子进程对照、几何／方向／映射失败，以及真实CSV入口逐行输出对照。
- **0032算法14项：** 从S1进入检查S2失败推进、S3／S4点接触、S6／S7确认及突破改点、S7.b合并后缺口和第二序列重放；另有严格分型等号、包含来源保留及重放不丢笔回归。固定种子100组40笔检查上下镜像、16／24／32笔前缀、连续区间和方向交替。
- **既有Bi回归29项：** 现有选笔、配置、锚点及完整CSV检查点不变。

这些分别是类契约、局部谓词、状态转换与真实入口测试。有限输入验证不证明所有价格路径；确认时间、增量状态、KWX其他配置与完整CC引擎身份元数据不在本次验收范围。

### 3.c 本机结果与产物

2026-09-16：上述**67项测试全部通过**。标准样本保持`10,060 raw → 6,200 M → 3,027 Fenxing → 502 Bi`，两项都保存全部10,060行：

| 算法选项 | 输出线段数 | 输出含义 |
| --- | ---: | --- |
| `kwx` | 69 | 参考返回全部区间；本样本包含frozen、soft_n0、pending_n1 |
| `options0033memo` | 14 | S6.b／S7.a确认区间；尾部未确认不输出 |

[检查脚本](../../experiments/chan_theory/check_xianduan_series.py)记录输入摘要、逐段原始端点和方向，便于重复对照；产物为`artifacts/experiments/chan_theory/xianduan_series_verification.json`。两项数量不同符合独立规则与不同输出政策，不按段数直接判优劣。

执行记录见[7.4.116实施总结](../phases/phase-01-warmup/7.4-execution-summary-2026-09-16-xianduan-implementation.md)。

## Appendix A. Reference Map

- [memo0027](memo0027_class_bi_series.md)：章节、行继承、序列组合及测试组织的直接模板。
- [memo0032](memo0032_algo_of_xianduan_2nd.md)：线段推导及与参考实现的六类差异。
- [memo0034](memo0034_memoguidance.md)：当前写作规范。
- [BiBar](../../experiments/chan_theory/bi_bar.py)、[BiSeries](../../experiments/chan_theory/bi_series.py)、[Bi适配器](../../experiments/chan_theory/kwx_bi_adapter.py)：现有输入接口及转换边界。
- [项目设想](memo0001_项目009设想_20260831.md#appendix-b-缠论画图)：笔到线段再到中枢的应用路径。

## Appendix B. External Xianduan Reference Code

对应0027的外部代码附录。本篇直接链接已保存的完整文件，避免再维护一份相同代码：

- [xianduan.py](../../records/cc/xianduan-study-20260912/reference/manual_rebuild/algo/xianduan.py)
- [config.py](../../records/cc/xianduan-study-20260912/reference/manual_rebuild/algo/config.py)、[models.py](../../records/cc/xianduan-study-20260912/reference/manual_rebuild/algo/models.py)、[trace.py](../../records/cc/xianduan-study-20260912/reference/manual_rebuild/algo/trace.py)
- [来源记录](../../records/cc/xianduan-study-20260912/provenance.json)

```python
# 参考入口签名；Bi、Xianduan、ChanConfig是参考包类型。
def build_xianduans(bis: list[Bi], cfg: ChanConfig, *,
                   profile_id: str, config_hash: str) -> list[Xianduan]:
    ...
```

[^rows]: 2026-09-16核对本地上游字段与原始锚点；实现及测试见第2、3章。

[^reference]: 固定快照`b1348795d25d282aa769bce2f14fb366df269d7d`；隔离副本仅修改导入命名空间和末尾换行。原始与本地SHA-256见[provenance.json](../../experiments/chan_theory/_kwx_xianduan/provenance.json)，详细边界见[README](../../experiments/chan_theory/_kwx_xianduan/README.md)。
