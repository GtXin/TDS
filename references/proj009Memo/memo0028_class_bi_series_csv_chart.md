# memo0028_class_bi_series_csv_chart

[class design] [data_io] [visualization] [chan] [bi]

## 0. Scope And Purpose

> [purpose] **把已经算好的BiSeries保存下来、读回来，并画出来检查。**
> 一份memo同时记录CSV和图表，但文件转换与绘图仍由不同类负责。

```text
BiSeries <-> CsvFileBiSeries <-> basic CSV
BiSeries  -> CsvFileBiSeries  -> human_table CSV
BiSeries  -> BiSeriesChart   -> PNG / optional window
```

沿用[memo0024](memo0024_class_csv_file_fenxing_series.md)的基本格式往返、人读表格和安全替换；
沿用[memo0025](memo0025_class_fenxing_series_chart.md)的窗口、HD、固定柱宽及图层选项。
输入契约来自[memo0027](memo0027_class_bi_series.md)：保留全部原始行，共享端点可贴两笔标签。

[boundary] 不修改合并、分型和笔算法，不新增实时确认接口。读文件和绘图不调用`derive_from()`；
构造时仍校验数据，错误就拒绝，不重算修复。全部实现和产物留在实验区域。

## 1. Design Ideas

### 1.a CSV保留什么

保留Fenxing基本CSV的24列，再追加六列，共30列：

```text
bi_tags                  JSON array of strings: ["B0","B1"]
bi_start_raw_indices     JSON array of integers: [1,11]
bi_end_raw_indices       JSON array of integers: [11,15]
config_bi_algorithm      kwx
config_bi_profile        bi_5k
config_bi_hash           ffb2448b188c
```

三个数组按位置配对，无笔用`[]`，不是空白或`NA`。CSV引用/转义交给csv模块，数组交给json模块，
不使用`eval()`、逗号拆分或Python元组字符串。所有配置列必须逐行一致，未知规则指纹拒绝读取。
最后两列记录当前固定KWX规则，不是新增可调旋钮；文件不能冒充另一套算法结果。

读回`BiSeries -> FenxingSeries -> MergedKlineSeries -> KlineTSeries`完整来源链，
无需另找原CSV或JSON文件。保留ISO时间和UTC偏移，不保存IANA时区名。
读取只恢复已保存的笔，不证明它们是该算法唯一可能的结果，也不恢复推断/修正历史。

### 1.b 人读表格

保留Fenxing人读格式15列，再加：

```text
biTags, biStartRawK, biEndRawK, biStartHere, biEndHere
```

例如主例K11：`B0 | B1`、`K1 | K11`、`K11 | K15`、`B1`、`B0`。
没有信息写`NA`。这张表解释最终归属，不是每次候选比较的执行日志；仅导出，不能读回。
同时保存两种格式时，用两个文件对象和不同路径；不暗中生成额外文件。

### 1.c 图表画什么

> [concept] **一根笔只画一条线，连接它的起点分型价与终点分型价。**
> 同一笔虽然贴在多根原始Kbar上，也只画一次；被修正掉的旧笔不再出现。

- 默认`overlay_on_raw`：原始高低价、M背景和笔折线；向上红色，向下绿色。
- `raw`：原始行情与笔；`merged_only`：沿用合并图的合成柱和M等距横轴，不是新成交OHLC。
- `fenxing_bi_only`：只画顶/底分型和笔，不画Kbar、M图层、成交量或百分比曲线。
  这是图表视图，不是CSV格式；横轴仍保留原始Kbar的等距位置，没有分型的位置不会被删掉。
- `bi_anchor="price_extreme"`默认把端点放在BiBar保存的原始价格贡献行；
  `group_first`只把显示位置移到该M首行，纵坐标始终使用合并顶/底价，数据端点不改。
- 默认不画全部分型三角形，避免与笔混淆；`show_top/show_bottom`可打开。
  `fenxing_anchor`只控制这些辅助分型；`bi_anchor`独立控制笔。
- `show_bi`控制笔线，`show_bi_labels`控制B编号，`show_bi_endpoints`控制小端点圆点；
  后两者默认关闭。`bi_line_width`为线宽，单位point，默认1.2。
- 默认1920×1080、150dpi、日期轴、signed volume，无百分比曲线。
  需要旧的M中价百分比曲线时显式打开`show_merged_mid_change`，仍与成交量零点对齐。

### 1.d 窗口与固定柱宽

原始行窗口和时间窗口都包含两端；同时给出时取交集，空窗口报错。
先用完整BiSeries计算，再限制显示范围。跨窗口笔按原直线插值得到可见部分，
两端都在窗口外也不能漏画穿过窗口的线；不在截断处制造真实端点标记。
Y轴包含窗口内行情及笔线可见部分，不被窗口外远处极值拉扁。
裁剪边界是选中数据的首尾横坐标，不是坐标轴两边的空白。

`output_mode="fixed_kbar_width", min_kbar_width_px=3`表示实际价格轴上每个可见raw/M槽至少3像素，
不是涂满3像素的柱体。全数据PNG可很宽，不降采样。`fit`为默认；`open_window=False`默认只存图。
沿用0025限制：candle或merged_only显示成交量时需`volume_mode="absolute"`；
百分比曲线只支持带成交量的high_low raw/overlay视图。

## 2. Classes And Methods

### 2.a CsvFileBiSeries

```python
CsvFileBiSeriesConfig(output_profile="basic")  # basic / human_table
CsvFileBiSeries(path, encoding="utf-8", config=CsvFileBiSeriesConfig())
```

方法：`exists()`、`read() -> BiSeries`、`write(series) -> None`、
`write_human_table(series) -> None`。类常量固定两种列名及规则指纹。
文件配置仅决定输出格式，`BiConfig`仍由序列持有。

内部使用Fenxing文件类解析和格式化已有字段，复用其临时文件替换机制；
不继承一个返回Fenxing的公开读写接口。Bi类自行检查30列表头、数组及Bi配置，
构建保存的来源链后交给BiSeries校验。错误应指出行号/字段，跨行错误保留上下文。

### 2.b BiSeriesChart

成员沿用FenxingSeriesChart的显示选项，`series`改为BiSeries，再增加1.c中的笔选项。
内部持有临时Fenxing图表协作者，取它生成的Figure再加笔；不复制完整底层绘图器。

方法：`render_to_file(path) -> Path`默认输出PNG，`show_window(block=True) -> None`用于人工查看。
保存失败或图层失败关闭Figure；非阻塞窗口由调用者关闭。绘图只读已有事实。

### 2.c 实验文件

```text
experiments/chan_theory/csv_file_bi_series.py
experiments/chan_theory/bi_series_chart.py
experiments/chan_theory/test_csv_file_bi_series.py
experiments/chan_theory/test_bi_series_chart.py
```

包入口公开CSV类/配置和图表类。没有新增顶层目录；产物放在
`artifacts/experiments/chan_theory/`。未来分别归入data_io和visualization，迁移须另行批准。

## 3. Implementation And Sample Use

[status] 2026-09-11完成。文件类及其配置、图表类已从实验包入口公开，未迁移到src。

### 3.a 保存、读回、画全数据

在仓库根目录使用项目Python运行：

```python
from pathlib import Path
from tradinglab.data_io import CsvFileKlineTSeries
from experiments.chan_theory import (
    MergedKlineSeries, FenxingSeries, BiSeries,
    CsvFileBiSeries, BiSeriesChart,
)

folder = Path("artifacts/experiments/chan_theory")
raw = CsvFileKlineTSeries(
    Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv")
).read()
merged = MergedKlineSeries.derive_from(raw)
fenxings = FenxingSeries.derive_from(merged)
bis = BiSeries.derive_from(fenxings)

basic = CsvFileBiSeries(folder / "bi_series_basic_cc.csv")
basic.write(bis)
saved = basic.read()
CsvFileBiSeries(folder / "bi_series_human_cc.csv").write_human_table(saved)

BiSeriesChart(
    saved, output_mode="fixed_kbar_width", min_kbar_width_px=3,
).render_to_file(folder / "bi_chart_full_fixed_3px.png")
```

`saved`保留10,060根原始Kbar、6,200个M、3,027个分型和502笔。
共享端点上的两组笔标签、所有原始值和上游配置均逐项验证一致。

### 3.b 只查看一个时间窗口

接着上例，默认没有分型三角形、B编号或百分比曲线：

```python
from datetime import datetime
from zoneinfo import ZoneInfo

tz = ZoneInfo("Asia/Shanghai")
BiSeriesChart(
    saved,
    window_start_timestamp=datetime(2025, 4, 7, 9, tzinfo=tz),
    window_end_timestamp=datetime(2025, 4, 21, 22, tzinfo=tz),
).render_to_file(folder / "bi_chart_window_default.png")
```

[options] 看全部分型加`show_top=True, show_bottom=True`；看笔编号加`show_bi_labels=True`；
看真实端点加`show_bi_endpoints=True`。横轴换M首行用`bi_anchor="group_first"`。
只画合并柱用`chart_mode="merged_only", volume_mode="absolute"`。
使用`show_window()`可以打开本机窗口，自动测试不打开GUI。

> [example] **Bi＋分型**是另一种可选视图：笔线保留，同时显示窗口内全部顶/底分型，
> 包括没有被选为笔端点的分型。顶分型是红色向上三角形，底分型是绿色向下三角形；
> 默认仍为仅Bi视图，不改变CSV格式或求笔算法。

```python
BiSeriesChart(
    saved,
    show_top=True,
    show_bottom=True,
    fenxing_anchor="price_extreme",
    window_start_timestamp=datetime(2025, 4, 7, 9, tzinfo=tz),
    window_end_timestamp=datetime(2025, 4, 21, 22, tzinfo=tz),
).render_to_file(folder / "bi_chart_window_fenxing.png")
```

移除两个时间参数即可显示全序列；全图需要固定间距时，加
`output_mode="fixed_kbar_width", min_kbar_width_px=3`。
三角形沿用0025的随柱间距缩放规则，底边至少5像素；`fenxing_anchor`与`bi_anchor`独立。

> [example] **只看分型＋笔，不看行情背景。** 2026-09-12新增：

```python
BiSeriesChart(
    saved,
    chart_mode="fenxing_bi_only",
    window_start_timestamp=datetime(2025, 4, 7, 9, tzinfo=tz),
    window_end_timestamp=datetime(2025, 4, 21, 22, tzinfo=tz),
).render_to_file(folder / "bi_chart_structures_window.png")
```

该模式自动显示两类分型，不必再传`show_top/show_bottom`；覆盖这些开关以及Kbar样式、
M图层、成交量和百分比曲线的显示设置。笔线、标签、端点、图例开关和两种锚点仍可设置。
Y轴只看窗口内分型价格和裁剪后的笔段，隐藏的原始高低价不参与缩放。
没有任何可见结构时保留时间轴、隐藏价格刻度，不造出笔或价格。
`output_mode="fixed_kbar_width"`仍指原始Kbar槽间距，不是分型之间的距离。

### 3.c 已生成的文件

全部在`artifacts/experiments/chan_theory/`，不提交Git；测试可重新生成。

```text
bi_series_basic_sample.csv         17行、2笔；可读回
bi_series_human_sample.csv         同一小例子的人读表
bi_series_basic_cc.csv             10,060行、502笔；可读回
bi_series_human_cc.csv             全数据的人读表
bi_csv_verification.json           行数、笔数、文件大小和耗时

bi_chart_sample.png                小例子、笔编号和真实端点
bi_chart_price_extreme.png         多行M，按价格贡献行定位
bi_chart_group_first.png           同一例子，改按M首行定位
bi_chart_window_default.png        April窗口默认图
bi_chart_window_fenxing.png        同一窗口加分型三角形
bi_chart_structures_sample.png     仅分型＋笔，小例子
bi_chart_structures_window.png     仅分型＋笔，April窗口
bi_chart_structures_full_fixed_3px.png  仅分型＋笔，全数据3px
bi_chart_window_mid_change.png     同一窗口加M中价百分比曲线
bi_chart_merged_only_window.png    同一窗口，仅合并柱与笔
bi_chart_full_fixed_3px.png         全数据，不降采样
bi_chart_verification.json         尺寸、实际槽宽、可见笔数和耗时
```

窗口包含250根原始Kbar、14条可见笔；裁剪后的笔仍算一条，不意味着两端都在窗口内。
原始叠加全图33,431×1,080像素，实测每个raw槽3.0074像素，全部502笔均已绘制。
仅结构全图33,380×1,080、槽宽3.0070像素；其余九张为1,920×1,080。
这次运行全数据basic写入约0.30秒、读回0.52秒、人读导出0.27秒；全图渲染约7.52秒。
这些是本机单次实测，不是性能保证。

## 4. Test Session

### 4.a CSV测试：20项通过

测试文件：`experiments/chan_theory/test_csv_file_bi_series.py`。

- **读回来还是原来的数据。** 小例子、共享端点、无笔、多行M和并列极值均完整往返；
  时间偏移、逗号、引号、中文和换行不会破坏字段。
- **读文件不偷偷算一遍。** 把各层`derive_from()`和KWX调用替换为报错函数，读取仍成功。
  可以保存并恢复无笔的未定向数据；这不等于允许KWX对未定向数据求笔。
- **坏文件不能蒙混过关。** 检查30列表头、缺列/重列/额外列、空数据、坏引号、
  JSON非数组、错误元素类型、规则指纹、跨行标签及来源字段。交换列顺序允许，缺少信息不允许。
- **人读表与基本表分工明确。** 人读表有20列、共享端点可辨认，不能被当成basic读入。
  文件输出配置不改变读取契约。
- **失败不能毁掉旧文件。** 非法对象、写入失败、替换失败均保留旧内容并清理临时文件。
  全数据basic逐字段往返；四个CSV产物均有数量检查。

### 4.b 图表测试：21项通过

测试文件：`experiments/chan_theory/test_bi_series_chart.py`。

- **一笔一线，不是一行一线。** 核对数量、红绿方向、端点价格、共享点去重、图例及无笔输入。
- **横轴换了，价格不能换。** 检查价格贡献行/M首行两种锚点，以及raw、candle、merged_only窗口坐标。
- **窗口只改变可见范围。** 检查首尾均在窗口外的穿越笔、线性裁剪、不伪造端点，
  时间与行号窗口取交集；Y轴只纳入可见笔段，不使用远处端点极值。
- **选项真的生效。** 分型、B编号、端点、笔线、图例和成交量开关；百分比与成交量零点对齐；
  不兼容组合或非法参数报错。
- **PNG和资源都检查。** 验证尺寸、非空像素及最终布局后的实际槽宽；
  保存/图层失败关闭Figure，窗口调用通过mock检查，不要求GUI。
- **保存的数据能直接画。** 测试完整`原CSV -> BiSeries -> basic CSV -> read -> PNG`链；
  八张产物检查可见数量和尺寸，全图检查502笔与至少3px槽宽。

### 4.c 运行结果与人工检查

```zsh
MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_csv_file_bi_series
MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_bi_series_chart
MPLBACKEND=Agg .venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
MPLBACKEND=Agg .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

[verification] 2026-09-11：20项CSV、21项图表通过；全部实验243项通过（38.018秒），
src回归42项通过（2.582秒）。依赖沿用现有环境，没有安装或修复操作。

人工查看了小例子、窗口、合并柱图和全图原生像素局部。
检查过程中修正了笔线延伸到坐标轴留白的问题：现在只到选中首尾Kbar，
避免把窗口外价格算进Y轴；修正后重跑测试、重新生成图片。

[limits] 测试证明文件往返和绘图契约，不证明交易有效性或实时无未来信息。
本次不新增推断历史/确认状态的保存接口；KWX权限问题仍在迁移前审查。
实际GUI交互未人工验证，自动验证路径是PNG。早期memos保持原样，本次变化集中记录于0028。

### 4.d 仅分型＋笔视图的补充验证

[verification] 2026-09-12新增5项测试，图表共26项通过；全部实验248项通过（40.400秒），
src回归42项通过（2.527秒）。继续使用4.c的命令，图表测试会重新生成全部11张PNG。

- **没有藏起来的行情图层。** 仅一个价格轴，实际artist只有分型与笔；没有Kbar、M矩形、
  成交量轴或百分比轴，图例也只显示当前结构。
- **窗口内价格决定范围。** 用K2—K3窗口检查穿越笔：价格18.6→17.2，隐藏Kbar的低价12
  不得进入Y轴；没有真实端点时不生成端点圆点。
- **没有结构也能输出。** 无分型/无笔输入显示空时间窗口；单根Kbar窗口保持有限坐标范围。
- **锚点与固定间距不变。** 多行M按首行定位时只移动横坐标，不改变分型价或笔端点价；
  测量最终布局后的槽间距，图例关闭仍生效。
- **失败会清理图。** 分型绘制失败关闭Figure，不留下窗口资源。

另直接核对全数据结构图：一个价格轴、3,027个分型标记、502条笔。
已人工检查窗口PNG；新增小例子、April窗口和全序列3px产物。
本次只改Bi图表类与测试，没有改Fenxing/Merged渲染器、CSV或求笔算法。

### 4.e 十张150根Kbar组合样本

[example] 2026-09-12：原始高低价柱＋M红绿背景＋顶/底分型＋笔线，同图保留成交量。
每张恰好150根原始Kbar，1920×1080像素；不是150像素，也不是150个M。
沿用高低价柱，不恢复开收盘蜡烛实体。样本图例移到价格区右侧，避免遮挡走势。

全序列先求M、分型和笔，再选十个均匀分布、互不重叠的窗口；没有按图形好坏挑选。
起点为`floor(i * (10060 - 150) / 9)`，`i = 0,...,9`，终点为起点加149。
图上的编号均为全序列原始行号；日期和时间使用保存数据的UTC（+0000）。
笔可穿过窗口边缘，边缘截断不代表真实端点。

全部位于`artifacts/experiments/chan_theory/`：

```text
bi_chart_overlay_150_sample_01.png   K0-K149
bi_chart_overlay_150_sample_02.png   K1101-K1250
bi_chart_overlay_150_sample_03.png   K2202-K2351
bi_chart_overlay_150_sample_04.png   K3303-K3452
bi_chart_overlay_150_sample_05.png   K4404-K4553
bi_chart_overlay_150_sample_06.png   K5505-K5654
bi_chart_overlay_150_sample_07.png   K6606-K6755
bi_chart_overlay_150_sample_08.png   K7707-K7856
bi_chart_overlay_150_sample_09.png   K8808-K8957
bi_chart_overlay_150_sample_10.png   K9910-K10059
bi_chart_overlay_150_samples.json   编号、范围、UTC时间、分型与可见笔数量
```

重新生成这十张图：

```zsh
MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_bi_series_chart.BiSeriesChartTest.test_ten_150_bar_overlay_samples
```

[verification] 新测试逐图检查150根原始柱、M阴影、两种分型、可见笔、双轴、HD尺寸、
非空像素和资源关闭；绘图期间禁止重新求笔。首尾样本直接看图，其余八张通过缩略总览检查。
当前Bi图表测试共27项，实验回归249项通过（49.825秒）。只增加样本测试，未改图表类API或默认行为。

### 4.f 改看200根Kbar

[example] 同日追加十张200根版本，原150根版本保留。仍为1920×1080，
原始高低价柱＋M颜色＋分型＋笔＋成交量，右侧图例；只增加每张显示的行情范围。
起点改为`floor(i * (10060 - 200) / 9)`，终点加199，仍均匀分布且互不重叠。

产物：`artifacts/experiments/chan_theory/bi_chart_overlay_200_sample_01.png`至`_10.png`；
对应`bi_chart_overlay_200_samples.json`记录准确时间、行号和结构数量。

```zsh
MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_bi_series_chart.BiSeriesChartTest.test_ten_200_bar_overlay_samples
```

150/200两个测试共享同一生成与校验方法，分别检查实际原始柱数、M/分型/笔图层、
HD尺寸和资源关闭。本次重跑这两个样本测试；未重新执行全部实验或src回归。
