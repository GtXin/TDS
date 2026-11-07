# memo0037_class_csv_file_xianduan_series

[class design] [data_io] [chan] [xianduan] [implemented interface]

## 0. Scope And Purpose

**`CsvFileXianduanSeries`把已经计算好的线段序列保存为CSV，并从basic文件恢复同一份结果及其上游来源。** 调用者提供[memo0036](memo0036_class_xianduan_series.md)的`XianduanSeries`；文件类负责读写，不负责选择线段。

```text
XianduanSeries <-> CsvFileXianduanSeries <-> basic CSV
XianduanSeries  -> CsvFileXianduanSeries  -> human_table CSV

读取后来源链：XianduanSeries -> BiSeries -> FenxingSeries
                         -> MergedKlineSeries -> KlineTSeries
```

[status] 用户批准依据接口先写后，CSV类已实现并通过接口测试。当前工作区已存在0036数据类，本类直接对接其构造、校验及查询接口；7.4.116已完成，本篇现已补齐两种算法的sample／CC集成测试。本篇沿用[memo0024](memo0024_class_csv_file_fenxing_series.md)与[memo0028](memo0028_class_bi_series_csv_chart.md)的CSV模式。

[boundary] 当前实现保存原始行、各层标注和计算配置。内部确认状态、证据时刻及KWX trace不在当前公开数据接口内；以下字段不能无损保存这些信息，不能用X标签冒充已确认。基础类若新增这些必需字段，须先补齐本篇格式再实施，不得静默丢弃。图表、中枢、算法修改、增量恢复及`src/`迁入不在本篇范围。

## 1. Design Ideas

### 1.a 一行保存什么

一份文件对应一份线段结果；每一行对应一根原始Kbar。原始OHLCV、合并、分型和笔字段全部保留，再附加线段归属。没有线段标签的首尾行也保存。

沿用0036的存储例：假设X0覆盖K1–K7，X1覆盖K7–K13，完整来源为K0–K14。以下只是列值摘录，不是证明算法会产生这两段：

| 原始行 | xianduan_tags | xianduan_start_raw_indices | xianduan_end_raw_indices |
| --- | --- | --- | --- |
| K0 | `[]` | `[]` | `[]` |
| K1–K6（每行） | `["X0"]` | `[1]` | `[7]` |
| K7 | `["X0","X1"]` | `[1,7]` | `[7,13]` |
| K8–K13（每行） | `["X1"]` | `[7]` | `[13]` |
| K14 | `[]` | `[]` | `[]` |

K7同时保留X0终点和X1起点，文件仍有15行；不能把它压成两条线段记录。下标是原始行位置，不是笔序号或合并K线序号。

### 1.b 文件设置与计算设置

```text
file.config                                      CsvFileXianduanSeriesConfig
series.config                                    XianduanConfig
series.source_series.config                      BiConfig
series.source_series.source_series.config        FenxingConfig
series.source_series.source_series.source_series.config
                                                 KlineMergeConfig
```

文件配置只选择输出格式；四层计算配置记录结果使用的规则，必须保存且逐行一致。读取缺配置时拒绝文件，不以当前默认值补齐。

`config_xianduan_algorithm`只接受`kwx`或`options0033memo`。后者是用户指定的选项名，规则来自memo0032；不能因名字含0033而转用笔算法。此列描述保存结果的来源，读取时不调用相应算法。

### 1.c Basic CSV字段

保留`CsvFileBiSeries.BASIC_FIELDNAMES`现有30列及顺序，追加四列，形成当前实现的**34列**：

```text
xianduan_tags                 JSON字符串数组，例如 ["X0","X1"]
xianduan_start_raw_indices    JSON整数数组，例如 [1,7]
xianduan_end_raw_indices      JSON整数数组，例如 [7,13]
config_xianduan_algorithm     kwx / options0033memo
```

前三个数组位置一一对应；无标签写`[]`。数组使用`json`编码，CSV转义交给`csv`模块，不使用`eval()`、Python元组字符串或手动逗号拆分。下标排除bool和小数。

已有30列包含原始、合并、分型和笔字段，以及合并/分型配置与`config_bi_algorithm`、`config_bi_profile`、`config_bi_hash`。沿用现有Bi规则标识校验，不能把线段算法名称填入笔配置。

- 数值保持有限且不作显示舍入；时间使用ISO 8601并保留UTC offset，不承诺保留IANA时区名称。
- 可空的上游方向/分型字段仍用`NA`；数组不使用`NA`或空白。
- 标签和端点以文件原值恢复，不重新编号；所有行须通过0036的行级和跨行校验。
- 方向不增加basic字段。读取后用来源笔端点的分型价格推导；原始Kbar涨跌不能替代段方向。
- 只有表头、没有数据行的文件拒绝读取；有Kbar但没有任何线段时合法。初版也拒绝写入零行序列，避免丢失无法附着到数据行的配置。

[boundary] 34列可以往返当前公开对象的全部字段、配置与来源链，不保存算法内部状态。后续若公开对象增加规则版本、确认/证据等字段，本格式必须同步扩充并验证；当前CSV不是算法检查点。算法名称本身不能证明未来重算结果相同。

### 1.d Human Table导出

人读表是检查每行归属的最终结果表，只导出、不读取。保留Bi人读表的20列，再追加：

```text
xianduanTags, xianduanStartRawK, xianduanEndRawK,
xianduanStartHere, xianduanEndHere, xianduanDirections
```

多值按标签顺序用` | `分隔，无值为`NA`。方向由序列按标签查询，一次导出先建立查询表，避免每行重复扫描全部线段。

[example] 若上述K1、K7、K13的来源端点价分别为100、130、110，K7新增列显示为：

```text
X0 | X1, K1 | K7, K7 | K13, X1, X0, up | down
```

这里每个逗号表示一列；实际转义仍由csv模块完成。方向一一对应X0/X1，不给共享行一个单独方向。human_table不表示确认过程或搜索日志。

## 2. Class Proposal

### 2.a 成员与位置

以下签名已实现，并从`experiments.chan_theory`导出：

```python
@dataclass(frozen=True)
class CsvFileXianduanSeriesConfig:
    output_profile: Literal["basic", "human_table"] = "basic"

@dataclass(frozen=True)
class CsvFileXianduanSeries:
    path: Path
    encoding: str = "utf-8"
    config: CsvFileXianduanSeriesConfig = field(
        default_factory=CsvFileXianduanSeriesConfig)
```

两类放在`experiments/chan_theory/csv_file_xianduan_series.py`，测试放同目录的`test_csv_file_xianduan_series.py`。复用现有实验目录，不新建通用持久化框架。

配置构造时拒绝未知profile；文件对象规范化Path，通过`codecs.lookup()`验证encoding，并检查配置类型。类常量固定`BASIC_FIELDNAMES`、`HUMAN_TABLE_FIELDNAMES`、三个数组字段及上游空值/布尔值约定。通过组合复用现有解析与安全写入能力，不继承Bi文件类的公开接口；复用私有方法前检查其假设与耦合。

### 2.b 方法

```text
exists() -> bool
read() -> XianduanSeries
write(series: XianduanSeries) -> None
write_human_table(series: XianduanSeries) -> None
```

- `read()`只接受basic，独立于配置的写出profile。
- `write()`先验证序列，再按profile写出。
- `write_human_table()`明确向当前路径写人读表。
- 两种输出使用两个文件对象和不同路径；同一路径写第二次会替换第一次结果。

### 2.c 读取：恢复保存对象

1. 读取表头；拒绝重复、缺少或额外列，拒绝human_table与旧Bi-only文件。basic表头顺序可不同，但字段集合必须正确。
2. 逐行检查缺单元格、多单元格、空必填值和非法编码值；解析四层配置，要求每行一致。错误报告路径、CSV记录行号及字段；跨行错误包含文件路径及序列校验原因；具体下标/标签信息取决于基础类的错误消息。
3. 将上游列恢复成BiBar，三个线段数组恢复成元组，通过`XianduanBar.from_bi_bar()`构造保存行。此工厂只复制字段，不运行算法。
4. 从保存行逐层取得原始、合并、分型和笔对象，依次构造`KlineTSeries`、`MergedKlineSeries`、`FenxingSeries`、`BiSeries`。
5. 用保存的线段行、线段配置和恢复的BiSeries构造`XianduanSeries`并验证；成功返回，失败拒绝整份文件。

所有层均不调用`derive_from()`，不查找另一份源CSV，不用重算修复标签。构造校验能发现字段与来源不一致，但不能单靠CSV格式证明线段算法正确，也不能恢复尚未保存的内部搜索状态。

### 2.d 写入：成功后才替换

1. 检查输入类型、非空原始行和完整序列；非法输入在触碰旧文件前报错。
2. basic格式化全部保存字段与配置；human_table先建立上游证据和线段查询表，再输出各行。
3. 按需创建父目录，在目标同目录写临时文件，使用指定编码和CSV换行规则。
4. 完整写入成功后替换目标；失败时清理临时文件并保留原目标。

沿用本地原子替换，不承诺断电持久性；初版无追加、部分保存或自动读回API。

### 2.e Sample Use

以下接口可以运行，`segments`是调用者提供的XianduanSeries：

```python
from pathlib import Path
from experiments.chan_theory import CsvFileXianduanSeries

folder = Path("artifacts/experiments/chan_theory")
basic = CsvFileXianduanSeries(folder / "xianduan_series_basic_kwx_sample.csv")
basic.write(segments)
loaded = basic.read()
assert loaded.klines == segments.klines
assert loaded.config == segments.config
assert loaded.source_series == segments.source_series
human = CsvFileXianduanSeries(folder / "xianduan_series_human_kwx_sample.csv")
human.write_human_table(loaded)
```

例中`segments.config.algorithm`应为`kwx`；另一个算法使用不同文件名，避免覆盖。方向查询与整笔成员查询应在保存前后保持一致。

## 3. Implementation Result

[status] 2026-09-16完成接口先行实现，已用现有数据类直接验证，无测试替身、无算法改动。

- `experiments/chan_theory/csv_file_xianduan_series.py`：文件类及配置，34列basic与26列human_table。
- `experiments/chan_theory/test_csv_file_xianduan_series.py`：20项测试（18项接口测试、2项真实输入集成测试），两个算法配置分别往返。
- 包导出已添加；沿用现有Fenxing/Bi字段解析与本地原子替换，没有安装依赖。

测试用原始数据构造有效上游对象，人工指定六笔与两段的归属，明确标为接口存储样本。它验证保存与恢复，不证明线段算法产生这些结果。新增集成测试从sample／CC原始CSV调用各层真实入口，再检查保存与恢复；不再以人工标签代替完整链路。

## 4. Test Session

### 4.a 验证范围

- 两个算法各做basic往返，比较全部行、四层配置、完整来源链、端点/方向/整笔成员查询。共享端点、无段、无标签首尾、多原始行合并组均覆盖。
- mock所有派生入口为报错，证明读取仍成功，且不会偷偷重算上游或线段。
- 拒绝坏表头、旧Bi文件、未知算法、混合配置、损坏JSON、bool/小数下标、重复标签、错位端点、漏贴/多贴和越界。
- 检查中文、逗号、引号、换行和时间偏移；校验CSV固定写出列序、可重排行头读取及human_table的共享端点方向顺序。
- 写入/替换失败保留已有目标并清理临时文件；拒绝零行序列，正常无段结果保留全部原始行。
- [已验证] 从sample与CC原始CSV依次执行合并、分型、笔及两种线段算法，保存basic并恢复后逐项比较整个对象、来源链、所有段的端点／方向／整笔成员；human_table逐行比较线段标签、起终点、端点角色和方向。读取与human导出时禁用全部四层派生入口。

### 4.b 命令与产物

在仓库根目录运行：

```zsh
PYTHONPATH=src .venv/bin/python -m unittest experiments.chan_theory.test_csv_file_xianduan_series
```

本次生成四份接口样本：`artifacts/experiments/chan_theory/xianduan_series_{basic|human}_{kwx|options0033memo}_interface.csv`。花括号表示命名选项；每份15行，人工指定2段，共享端点K7。测试比较完整恢复对象，并检查human表方向。真实输入另生成八份`sample`／`cc`后缀文件，和人工接口样本分开。

真实输入集成与相关回归命令：

```zsh
PYTHONPATH=src .venv/bin/python -m unittest \
  experiments.chan_theory.test_csv_file_xianduan_series \
  experiments.chan_theory.test_csv_file_bi_series \
  experiments.chan_theory.test_csv_file_fenxing_series \
  experiments.chan_theory.test_xianduan_series \
  experiments.chan_theory.test_kwx_xianduan_adapter \
  experiments.chan_theory.test_memo0032_xianduan
```

2026-09-16：**113项通过，耗时36.691秒**。线段CSV共20项，其中2项集成测试各运行两个算法选项；其余为上游CSV和线段类／适配器回归。

| 原始输入 | 原始行数 | 笔数 | kwx段数 | options0033memo段数 |
| --- | ---: | ---: | ---: | ---: |
| `data_samples/kline/kline_15m_minimal.csv` | 2 | 0 | 0 | 0 |
| `records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv` | 10,060 | 502 | 69 | 14 |

真实产物：`artifacts/experiments/chan_theory/xianduan_series_{basic|human}_{kwx|options0033memo}_{sample|cc}.csv`，共八份；每份保留对应输入的全部原始行。段数按0036当前样本检查点核对，算法之间不要求一致。KWX包含临时区间，0032选项输出已确认区间；CSV不会额外赋予确认含义。

### 4.c 本次验证边界

本次已通过真实数据对象的CSV往返、禁用派生入口读取、多行合并组、首末极值锚点配置、格式损坏及写失败保护等可执行检查。零行数据在现有上游对象中不能构造；CSV仍保留写入拒绝的防御检查。本次补齐真实算法到CSV的输入—输出集成；相关算法回归也通过，但有限输入不证明所有算法分支，仍不保存或验证内部状态恢复。

## 5. References And Next Step

- [memo0036](memo0036_class_xianduan_series.md)：来源对象、字段与方向查询；本次按当前数据类接口实现。
- [memo0028](memo0028_class_bi_series_csv_chart.md)及[Bi CSV实现](../../experiments/chan_theory/csv_file_bi_series.py)：现有30列basic、20列human与JSON数组依据。
- [memo0024](memo0024_class_csv_file_fenxing_series.md)：不重算读取、来源链恢复与安全替换。
- [memo0034](memo0034_memoguidance.md)：写作与验证边界。
- [阶段子计划7.4.117](../phases/phase-01-warmup/7.4-reproduce-ke-drawing-line-strategy.md#74117--memo0037-xianduan-csv)：实施依赖、审批与验收步骤。

真实线段算法到CSV的集成已完成。后续若公开对象接口扩展，先更新保存字段及往返测试；不把当前结果文件当作内部算法状态检查点。
