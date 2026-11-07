# memo0038_class_xianduan_series_chart

[class design] [visualization] [chan] [xianduan] [implemented in experiments]

## 0. Scope And Purpose

**`XianduanSeriesChart`把已经算好的线段画在来源笔与行情上，让读者检查每段连接了哪些端点。** 调用者提供一份完整的`XianduanSeries`和显示选项，得到PNG文件，也可选择打开本地窗口。

```text
XianduanSeries ────────────────────────> XianduanSeriesChart -> PNG / window
    .source_series -> BiSeries ───────> BiSeriesChart（底图协作者）
```

输入契约来自[memo0036](memo0036_class_xianduan_series.md)，图表组织沿用[memo0028](memo0028_class_bi_series_csv_chart.md)。本篇记录图表类设计与接口实现；不实现CSV接口、线段计算、中枢或实时回放。下列显示接口与默认值已在实验模块落地。

[status] 按用户“实现代码 用接口”的要求，已完成7.4.118接口实现。使用现有`XianduanSeries`公开结果接口，组合`BiSeriesChart`；14项新测试及101项原有绘图回归通过，6张接口示例图已目视检查。构造结果的测试不证明线段算法正确，确认状态不由图表推断。

[scope] 相邻的[memo0037](memo0037_class_csv_file_xianduan_series.md)负责线段CSV设计；本篇只负责图表。两者分别使用0036的结果契约。

## 1. Class Design

### 1.a 职责、输入与对象关系

`XianduanSeriesChart`是持有序列引用与显示设置的不可变图表对象，使用`@dataclass(frozen=True)`。它组合`BiSeriesChart`，不继承一个要求`BiSeries`输入的公开构造接口。

- `series`是唯一数据入口；笔、分型、合并K线和原始行情均从它的来源链取得，不额外接收可能不一致的底图数据。
- 构造时调用`series.validate()`，检查显示参数；非法输入报错，不调用任何`derive_from()`修复。
- 每次渲染建立新的Figure和临时底图协作者，不修改序列、来源或旧图，不保存计算候选或跨调用的算法状态。
- 算法选择属于`series.config.algorithm`。图表读取`kwx`或`options0033memo`标识，不提供另一个算法开关，也不要求两种输入画出相同结果。

**[example] 延续0036的存储例。** 输入K0–K14，已存X0连接K1=100与K7=130，X1连接K7=130与K13=110；X0覆盖B0–B2，X1覆盖B3–B5。这是给定结果的显示例，不证明线段算法会选择这些端点。

```text
原始位置：K0  K1        K3        K5        K7        K9        K11       K13 K14
笔范围：      └── B0 ───┴── B1 ───┴── B2 ───┴── B3 ───┴── B4 ───┴── B5 ───┘
线段范围：    └────────── X0 ────────────────┴────────── X1 ────────────────┘
端点价格：    100                           130                           110
```

画两条X线；K7是共享端点，只画一个端点标记。K3/K5虽是笔端点，不成为线段端点。K0/K14保留在时间轴上，不自动连接成额外线段。

### 1.b Members / 成员

沿用`BiSeriesChart`现有显示选项与校验语义：原始行／时间窗口、`chart_mode`、行情样式、成交量、分型、笔、合并背景、图例、尺寸、dpi、固定柱宽和窗口显示。`series`改为`XianduanSeries`；新增下列选项：

| 成员 | 默认值 | 用途 |
| --- | --- | --- |
| `show_xianduan: bool` | `True` | 是否绘制X线段层 |
| `show_xianduan_labels: bool` | `False` | 在可见线段中部标X编号 |
| `show_xianduan_endpoints: bool` | `False` | 标出窗口内的真实线段端点 |
| `xianduan_anchor` | `"price_extreme"` | 可选`price_extreme`或`group_first`，只决定横坐标 |
| `xianduan_line_width: float` | `2.4` | 线宽，单位point；必须有限且大于0，拒绝bool |

默认底图仍为`overlay_on_raw`、原始`high_low`行情、M背景及笔；`bi_line_width=1.2`。X层统一蓝色`#1F77B4`，绘制在笔层上方，X标签与图例明确写“Xianduan / 线段”。B层保持已有向上红、向下绿，避免两级线条只靠粗细区分。蓝色及实线只标明对象层级，不代表已确认或冻结。

保留1920×1080、150dpi、`output_mode="fit"`、`open_window=False`等已有默认值。`title=""`时生成含标的、周期、Xianduan及算法名的标题；显式标题原样使用，启用图例时仍在X层图例中注明算法。

### 1.c 一条线的价格与横坐标

**每个X标签只生成一条连接起终点的直线；重复贴在原始行上的归属标签不生成重复线。** 在完整序列上收集标签与端点，校验后按起点／终点顺序画；不按字符串把X10排在X2前。

- 端点下标取`endpoint_raw_indices_for_xianduan_tag(tag)`；纵坐标取来源端点的`fenxing_price`，即所属M的合并顶／底价，不用锚点行原始high/low替代。
- `price_extreme`把横坐标放在已存原始端点；`group_first`把它移至该端点所属M的首行。两者都不改变保存的端点、成员范围和纵坐标。
- `merged_only`按完整来源M的时间顺序映射为可见窗口内的等距位置；此时两种锚点均落到同一M槽。
- raw高低价底图使用原始下标；局部等距底图使用相对可见首行的偏移。必须复用底图当前的坐标约定，不能把原始下标直接加到所有底图上。
- X、B、分型的锚点选项互相独立；若希望端点重合，调用者应对这些层使用相同锚点。

例如K7的来源分型价为130，即使该原始行high不是130，X0终点仍画在130。若K7所属M首行为K6，`group_first`只将显示端点从`(7,130)`移到`(6,130)`。

不从段内最高最低价重新找端点；不将线延长到确认它所需的后续证据行；不在相邻已存区间之间补画连接。

### 1.d 视图、窗口与边界

首版复用现有四种视图，不另建专用视图名：

- `overlay_on_raw`：行情、合并背景、笔及X层。
- `raw`：原始行情、笔及X层，其他辅助层遵守原有开关。
- `merged_only`：M等距底图、笔及X层；合成柱不是新成交数据。
- `fenxing_bi_only`：分型与结构线底图，再叠加X层；保留原始Kbar位置，无行情、M背景或成交量。`show_bi=False`可隐藏笔。

原始行窗口和时间窗口都包含两端，同时传入时取交集，空窗口报`ValueError`。来源`KlineTSeries`已拒绝空行序列，`XianduanSeries`也拒绝与来源不等长的结果；图表仍保留非空检查。有行情但无X时正常画底图，不构造占位线。`show_xianduan=False`同时隐藏X标签与端点标记。

**窗口只裁显示，不重算线段。** 完整X两端都在窗口外但穿过窗口时，仍画它的可见部分；按变换后的横坐标插值裁剪，裁剪点不成为真实端点。

沿用主例，显示K3–K5时，X0原式为`y=100+(x-1)×30/6`，可见线从`(3,110)`到`(5,120)`；两处均不标真实端点，X1不可见。X0的成员和原始端点仍是K1–K7。裁剪边界取数据窗口首尾位置，不使用坐标轴留白。

显示坐标必须严格递增；映射结果若重合或倒序，图表在创建Figure前抛`ValueError`并指出X标签，避免除以零或静默丢线。正常来源笔端点与M顺序由上游校验，图表不修复非法映射。

Y轴包含底图可见内容及X线的可见部分，不受窗口外整段极值影响。单点窗口只保留其相交位置；仅当该点本来就是真实端点时才画端点标记。标签在可见部分中点，标记按显示坐标与价格去重；图例只纳入实际可见的层。

`fixed_kbar_width`继续保证实际价格轴上的raw/M槽最小像素间距，不降采样。candle或merged_only配成交量须使用`absolute`，百分比曲线沿用原有high_low与成交量约束，不由X层放宽。

[limit] 从最终结果裁一张早期窗口图，仍可能使用未来证据；这是静态结果检查图，不能当成当时已知的线段。三个归属元组没有确认／证据信息，本版不提供`confirmed_only`、候选着色或冻结标记。

## 2. Methods And Implementation Boundary

### 2.a 对外方法与调用

- `render_to_file(path: Path) -> Path`：输出PNG，创建父目录，成功返回路径；后缀非`.png`报错。保存和图层异常均关闭本次Figure并传播错误。
- `show_window(block: bool = True) -> None`：人工查看；阻塞窗口结束后释放Figure，非阻塞窗口由调用者关闭。自动验收不依赖GUI。

`segments`是调用者已经取得的完整结果；以下图表接口现可导入使用：

```python
from pathlib import Path
from experiments.chan_theory import XianduanSeriesChart

chart = XianduanSeriesChart(
    series=segments,
    show_xianduan_labels=True,
    show_xianduan_endpoints=True,
    window_start_raw_index=0,
    window_end_raw_index=14,
    output_mode="fixed_kbar_width",
    min_kbar_width_px=3,
)
chart.render_to_file(Path("artifacts/experiments/chan_theory/xianduan.png"))
```

### 2.b 内部协作与文件

实现模块为`experiments/chan_theory/xianduan_series_chart.py`；测试位于同目录`test_xianduan_series_chart.py`，通过实验包入口导出类。此时不迁入`src/`，不新增通用绘图库或另一套数据模型。

内部方法沿用现有类的组织：`_bi_chart()`取得底图协作者，`_xianduan_segments()`整理临时绘图记录，`_draw_xianduan()`增加X层，`_build_figure()`管理本次Figure。临时记录含tag、原始起终点与显示坐标；它不是新的领域线段对象。

[implementation note] 复用现有Bi/Fenxing绘图协作方法，没有改动底层类或算法。添加X层后保留旧图例的文字与符号，再调整最终柱宽和分型标记大小；结构底图无可见分型／笔时，以可见X价替换空图的0–1占位范围。像素尺寸向上移动一个浮点表示单位，避免400px因取整变成399px。保存、图层和窗口异常均释放本次Figure。

## 3. Verification And Current Result

### 3.a 验收范围

- 主例两条X只画各一次，共享K7仅一个端点标记；不新增K0/K14连接，标签数字顺序正确。
- 检查价格来自合并分型、两种锚点及M坐标映射，覆盖一组M含多根原始行。
- 四种视图分别检查底图对齐；开关隐藏整层，X/B视觉可辨，标题／图例记录真实算法。
- 覆盖上述K3–K5裁剪、单点窗口、完全不可见、两端在外、空窗口、无行情、无段和非法参数；核对裁剪边界不产生端点。
- 检查包含X层后的Y范围和实际3px间距；异常时释放Figure，重复渲染不修改来源。保存PNG后打开检查文字、线条、端点和裁剪位置。
- 上游完成后，分别将两个算法的真实输出送入图表并对照已存端点；算法正确性在0036验收，不用画图成功代替。固定结果绘图测试与真实计算链测试分开记录。

### 3.b 本次结果与复现

新增[类实现](../../experiments/chan_theory/xianduan_series_chart.py)、[14项测试](../../experiments/chan_theory/test_xianduan_series_chart.py)和[示例生成器](../../experiments/chan_theory/render_xianduan_chart_examples.py)，并从实验包导出。复用现有Python 3.11与绘图依赖，未安装新包。

```bash
MPLCONFIGDIR=/private/tmp/proj009-mpl .venv/bin/python -m unittest experiments.chan_theory.test_xianduan_series_chart -q
MPLCONFIGDIR=/private/tmp/proj009-mpl .venv/bin/python -m experiments.chan_theory.render_xianduan_chart_examples
```

14项新测试通过；`test_bi_series_chart`、`test_fenxing_series_chart`和`test_merged_kline_series_chart`共101项回归通过。检查包括固定柱宽最终实际间距、保存尺寸、图例文字、窗口插值及异常资源释放。GUI调用以mock检查资源生命周期，没有实际弹窗验收。

6张1920×1080 PNG位于`artifacts/experiments/chan_theory/xianduan_chart_interface_*.png`，包含两个算法标签、裁剪、结构图、M图和组首锚点；均已打开检查。清单为[interface manifest](../../artifacts/experiments/chan_theory/xianduan_chart_interface_manifest.json)。图片来自明确构造的结果，不是两个算法的计算产物；标题同时注明此限制。

下一步在7.4.116算法验收后，用各算法真实结果检查整条计算链。本次只完成给定结果到图像的接口闭环，没有以图表测试替代线段算法验收，也未增加候选／冻结图层。执行详情见[实施总结](../phases/phase-01-warmup/7.4-execution-summary-2026-09-16-memo0038-chart-implementation.md)。

## 4. References

- [memo0036](memo0036_class_xianduan_series.md)：输入行、来源链、端点查询与算法配置；本篇不替它补算法政策。
- [memo0028](memo0028_class_bi_series_csv_chart.md)、[BiSeriesChart](../../experiments/chan_theory/bi_series_chart.py)：已有图表协作、窗口和资源管理。
- [memo0025](memo0025_class_fenxing_series_chart.md)：分型图层和固定柱宽。
- [memo0034](memo0034_memoguidance.md)：写作及验证边界；本次审读以本地文档和代码为依据。
