### 002.a — Algorithm Tree

本树采用001版本二的三根几何定义，按[memo015的树格式](memoWX_015_Chan_mergedkline.md#002a--algorithm-tree)展开。数据沿用[memo009的Fenxing／FenxingSeries](memoWX_009_designPatternForChanFeatures.md#002f--fenxing)，输入衔接[memo026的已实现合并序列](memoWX_026_MergedKlineFamily.md#003c--mergedklineseries)。以下是分型算法设计，尚未实现；本层保存全部几何分型，笔的距离、结合律及端点取舍留给笔层。

**入口与数据归属**

拟议入口为 `FenxingSeries.derive_from(source_series, config, rule_tree_ref)`，其中source_series必须是一个完整的MergedKlineSeries。只使用Fenxing和FenxingSeries两个类；扫描、锚点定位和校验封装在FenxingSeries的私有方法中，不新增工作状态类。

- 输入若来自ChanTable，先用memo026已有的 `MergedKlineSeries.from_chan_table(table, series_key)` 取出确切对象，再传入本入口。原始KlineTSeries、ChanTable或切片tuple不能直接充当本层source_series。
- 上游返回 `kind="pending"` 时尚无完整输入；返回 `kind="dual"` 时，由调用方明确选取main或comparison中的完整序列，分别计算，不把两路混合。已经完成的MergedKlineSeries即使配置为UNSET，或首单元direction为None，也可在校验通过后进入。
- 分型结果保留同一merged对象；原始数据通过 `merged.source_series` 回查。分型config和rule_tree_ref记录本层规则，不覆盖上游的初始化配置及memo015规则版本。

**变量与位置**

| 变量 | 含义与约定 |
|---|---|
| `merged` | 输入的确切MergedKlineSeries对象；记录位于 `merged.klines`，不修改输入。 |
| `raw` | `merged.source_series`，同一个不可变KlineTSeries。 |
| `N` | 合并单元数，即 `len(merged)`；有效完整序列至少有1根。 |
| `i` | 本轮中心合并单元的零基下标，从1开始，最后可检查到N−2。 |
| `A、B、C` | `merged[i−1]、merged[i]、merged[i+1]`；B为中心，不是 `raw[i]`。 |
| `d_left、d_right` | 根据高低点重新计算的A→B、B→C方向；不直接读取单元的direction。 |
| `R` | 已保存分型的工作列表；最终冻结为FenxingSeries.items。 |
| `T、P` | 本层执行依据列表、每条分型对应的trace下标元组列表；最终分别冻结为trace、trace_by_point。 |
| `next_id` | 本次分型结果的下一个整数ID，从0开始；仅保存成功时增加，不等于i或MergedKline.id。 |
| `J` | 中心B的原始成员中，与price对应的原始下标集合；只作逻辑记号，实际累计匹配数量及首尾下标。 |

每次进入2.3时，小于i的完整中心均已检查，R恰好包含这些中心检出的分型；`len(R)=len(P)=next_id`。source_start／source_stop必须结合所属对象理解：MergedKline指向raw，Fenxing指向merged，均为左闭右开范围。

**判断树：判断结果 → 行动 → 下一步**

```text
2.1 输入与规则检查
├── 2.1.a 输入不是完整MergedKlineSeries，或校验失败
│   → 报错，停止；不能把待定、双路包装或无效输入当成空分型结果
└── 2.1.b 输入校验通过
    → merged=source_series；raw=merged.source_series；
      检查本层config及非空的规则位置／版本rule_tree_ref；
      规则选项无效则报错，不修改上游；
      N=len(merged)；R、T、P为空；next_id=0；i=1
    └── 2.2 合并单元数量检查
        ├── 2.2.a N<3
        │   → 记录“没有完整三根窗口”；转2.8组装空结果
        └── 2.2.b N≥3
            → 转2.3

2.3 中心位置检查
├── 2.3.a i≥N−1，完整窗口已耗尽
│   → 转2.8；不读取merged[N]，不为末根补造分型
└── 2.3.b i<N−1，仍有完整窗口
    → A=merged[i−1]；B=merged[i]；C=merged[i+1]
    └── 2.4 相邻区间方向检查
        → 由A、B计算d_left；由B、C计算d_right
        ├── 任一对不能得到严格向上或严格向下
        │   → 报错，指出对应位置；不能作为普通“无分型”跳过
        └── 两对方向均有效
            └── 2.5 三根结构分类
                ├── 2.5.a 向上→向下
                │   → 顶分型：kind="top"；price=B.high；转2.6
                ├── 2.5.b 向下→向上
                │   → 底分型：kind="bottom"；price=B.low；转2.6
                ├── 2.5.c 向上→向上
                │   → 连续上升，不保存分型；记录判断依据，转2.7
                └── 2.5.d 向下→向下
                    → 连续下降，不保存分型；记录判断依据，转2.7

2.6 定位原始锚点并保存
→ 只遍历原始下标j∈[B.source_start,B.source_stop)，逐项读取raw[j]，不创建切片；
  顶分型以原始high=price匹配，底分型以原始low=price匹配，得到J
├── 2.6.a J为空
│   → 分型价格与原始来源不一致，报错停止
├── 2.6.b J只有一个下标
│   → anchor_raw_index取该下标；转2.6.d
└── 2.6.c J有多个下标
    ├── 已明确选择最早匹配 → anchor_raw_index=min(J)；转2.6.d
    ├── 已明确选择最晚匹配 → anchor_raw_index=max(J)；转2.6.d
    └── 尚未选择同价锚点规则
        → 报告规则待定并停止；不返回完整FenxingSeries；
          明确config后，对同一merged重新计算

2.6.d 保存本轮Fenxing
→ id=next_id；kind、price沿用2.5；
  source_start=i−1；source_stop=i+2；
  anchor_raw_index沿用2.6；status="unconfirmed"；confirmed_at=None；
  保存本轮分类／锚点依据到T，构造并校验不可变Fenxing，追加到R；
  将其相关trace下标元组追加到P；next_id=next_id+1；转2.7

2.7 推进窗口
→ i=i+1；回2.3；有分型、无分型都只前进一根

2.8 组装并校验结果
→ FenxingSeries.source_series=merged；items=tuple(R)；
  保存本层config、rule_tree_ref；trace=tuple(T)；trace_by_point=tuple(P)；
  冻结嵌套配置与依据数据，校验通过后返回；失败则报错
```

2.4的方向判断沿用memo015的非包含前提：后一根high、low都严格较高为向上，都严格较低为向下。等边或高低点反向变化意味着仍有包含或输入异常；不能使用开收盘、阴阳线或上一次方向补判。

2.6的同价取舍是本层config中的显式选项，不新增Fenxing成员；最早、最晚均为待选择方案，未设项目默认值。价格按输入的原有精度严格比较，不在本层临时取整或加容差。memo026现有validate检查结构与来源范围，并不复算全部合并价格，因此2.6.a仍须保留。

**保存字段与结果校验**

Fenxing沿用memo009的8个成员，不存独立的中心下标、时间戳、方向对或三根窗口high／low包络：

| 成员 | 本树赋值与检查 |
|---|---|
| `id` | 本结果内唯一的非负整数；FX只作显示前缀。 |
| `kind` | top或bottom，由2.5确定。 |
| `price` | 顶取中心B.high，底取中心B.low；有限且符合三根严格比较。 |
| `anchor_raw_index` | 位于B的原始半开范围内，且对应原始high／low等于price。 |
| `source_start` | i−1，指向merged中的左邻，不是原始下标。 |
| `source_stop` | i+2，指向merged窗口右端之外；与source_start之差为3。 |
| `status` | 本树统一为unconfirmed；表示已检出几何结构但尚无确认规则。 |
| `confirmed_at` | None；不把中心时间、右邻时间或EOF当成确认时间。 |

FenxingSeries沿用6个成员：`source_series、items、config、rule_tree_ref、trace、trace_by_point`。其中：

1. `source_series is merged`；items可为空。各来源窗口满足 `0≤source_start<source_stop≤N`，中心由source_start＋1得到，按中心顺序保存，允许窗口重叠。
2. 每个保存结果复核顶／底四项严格不等式、原始锚点及选定同价规则；ID唯一，状态及确认字段一致。首根、末根不作为中心。
3. trace保存执行过的分类及锚点依据，每个完整窗口都须有分类记录，包括没有输出分型的窗口。锚点依据只保留来源范围、匹配数量、首尾匹配下标及选取结果，不复制原始成员或整个J；具体DecisionStep结构仍按memo009留待设计，不在本节新增类或字段。
4. `len(trace_by_point)=len(items)`；每条结果对应非空、合法的trace下标元组。没有分型的事件可只留在trace中；空items对应空trace_by_point，但trace仍可非空。不能照搬memo026“每条trace都必须归属某个输出记录”的检查。

**推进、结束与原始行映射**

| 情况 | 中心下标i | R／ID与下一步 |
|---|---|---|
| 检出顶／底，锚点确定且保存成功 | 增加1 | R和P各追加1项，ID增加1，再检查下一中心。 |
| 连续上升／连续下降 | 增加1 | 只记录依据，R、P和ID不变。 |
| 同价锚点规则待定，或发生校验错误 | 不推进 | 停止，不把部分R返回为完整结果或计算为空。 |
| i=N−1，完整窗口耗尽 | 不变 | 组装现有结果；无需像合并算法那样再保存末端工作单元。 |
| N=1或2 | 保持1 | 返回经校验的空分型结果，保留确切来源与不足三根的依据。 |

未来投影到ChanTable时，Fenxing窗口的原始覆盖为 `[A.source_start,C.source_stop)`：fx_ids覆盖该范围，fx_start_ids在A.source_start，fx_end_ids在C.source_stop−1，fx_anchor_ids和fx_kind位于anchor_raw_index。MergedKline自身仍按memo015／026放在首个原始成员处，不能把该显示位置当作分型极值位置。本树不调用文件读写或表格投影；memo026已有MK适配，FX适配尚未实现。

窗口扫描只读当前快照；上游末端修订后应针对新的完整merged重算，不承诺本次结果永久稳定。仅三根窗口分类为O(N)；锚点逐中心扫描，其原始范围互不重叠，累计不超过O(M)，M为raw长度。含本层trace的计算为O(N+M)、保存空间O(N+F)，F为分型数；锚点定位只累计匹配数量及首尾下标，不物化J。上游完整校验的开销另计。

