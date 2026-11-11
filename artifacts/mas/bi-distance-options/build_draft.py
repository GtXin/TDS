"""Prepare a reviewable distance-mode memo draft without editing the memo."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
old=(ROOT/'docs/memo/memoWX_020_Chan_bi.md').read_text()
active,archive=old.split('## Appendix A —',1)
active=active.replace('定义笔的六项条件，并据004原始草案','定义笔的六项条件，其中距离提供强／弱两档，并据004原始草案',1)
active=active.replace('(版本一) 笔是','(版本一，原强距离口径) 笔是',1)
start=active.index('6. **距离 （强）**');stop=active.index('\n\n**（版本三）**',start)
active=active[:start]+'''6. **距离（强／弱二选一）**：两端完整三根分型窗口不共用合并K线；本次计算固定使用以下一个档位。距离按合并中心位置计数，不按FX数量或原始K线数量计数。

| 距离档位 | `distance_mode` | `min_gap` | 两端分型窗口之间的要求 |
|---|---|---:|---|
| 强 | `"strong"` | 4 | 至少一根合并K线不属于任一端点分型。 |
| 弱 | `"weak"` | 3 | 允许窗口紧邻，中心距3时中间没有独立K线；两个窗口仍不重叠。 |

初次未指定时采用强档。强弱只改变第⑥项门槛，其余五项均不放宽；不是两项必须同时满足的条件。''' + active[stop:]
active=active.replace('第⑥项采用老笔间隔，原文见附录A.1、A.3；新笔条件另见','第⑥项强档采用原有老笔间隔，原文见附录A.1、A.3；弱档是本项目新增的可选口径，不直接等同于作者新笔条件或CC的强势笔。原文新笔条件另见',1)
active=active.replace('成笔条件采用001版本二的六项定义。','成笔条件采用001版本二的六项定义，距离使用本次选定档位。',1)
needle='**输出与续读使用同一份快照Q。**'
pos=active.index(needle)
policy='''**距离选项与续读**

`distance_mode`可显式指定`"strong"`或`"weak"`，由此唯一得到`min_gap=4`或`3`，不另开放任意距离值。`None`只表示未指定：初次处理取强档，续读继承Q中的档位。未知值、缺少档位的旧Q、档位与门槛不一致、续读显式改档均报错，即使R为空也不例外。

初次弱档写作`process(source, distance_mode="weak")`；以后可用`process(new_source, previous_state=Q)`继承弱档。要更换档位，从完整输入重新计算另一结果版本，不修改原Q或原R。距离强弱、同型端点价格强弱及附录B的`bi_strong`分别定义。

'''
active=active[:pos]+policy+active[pos:]
active=active.replace('`process(source)`返回Q；下一批调用','`process(source, distance_mode=None)`返回Q；下一批调用',1)
active=active.replace('包括原始、合并、完整分型和算法／规则、配置、精度信息。','包括原始、合并、完整分型和算法／规则、配置、精度信息；必须显式保存本次有效distance_mode与派生min_gap。',1)
active=active.replace('一个分型只记录一次，首个起点也有初始化依据。','一个分型只记录一次，首个起点也有初始化依据；距离比较记录实际中心距与本档min_gap。',1)
active=active.replace('中心距离至少4；F为','中心距离至少min_gap；F为',1)
active=active.replace('中心距离至少4；B和F','中心距离至少min_gap；B和F',1)
active=active.replace('输入无效，或旧Q来源／规则不兼容、状态被改写','输入无效，或旧Q／距离选项非法、来源不兼容、状态被改写',1)
active=active.replace('│   └── 检查通过\n│       ├── 初次处理','│   └── 检查通过，解析本次distance_mode及min_gap\n│       ├── 初次处理',1)
active=active.replace('查中心距至少4及F侧范围极值','查中心距≥min_gap及F侧范围极值',1)
active=active.replace('查中心距至少4及B、F两侧全范围极值','查中心距≥min_gap及B、F两侧全范围极值',1)
active=active.replace('按当前N计算未决范围，保存当前整个来源上下文；','按当前N计算未决范围，保存当前来源及距离档位／门槛；',1)
active=active.replace('按001复核Q.R及Q.Bi002，并核对连接、状态、位置与未决范围','按001本档复核Q.R及Q.Bi002，核对配置、连接、状态与未决范围',1)
active=active.replace('本节从有效的合并K线与全部完整分型开始，不重做包含处理。','本节从有效的合并K线与全部完整分型开始，不重做包含处理。原主例、同价例及续读表默认采用强档；明确标出的对照例比较两档。',1)
active=active.replace('先检查输入；初次扫描','先检查输入并解析距离档位；初次扫描',1)
active=active.replace('续读保留本过程返回的Q，只在','续读保留本过程返回的Q并继承其距离档位，只在',1)
active=active.replace('距离3，不成笔；范围内M2的low=0也低于候选的1','强档因距离3<4失败；弱档距离通过，但M2的low=0低于候选的1，仍不成笔',1)
# Add a genuine difference fixture after the main walkthrough, before tie examples.
marker='#### 同价取舍'
i=active.index(marker)
fixture='''#### 距离强／弱的差异例

以下11根合并K线均为`[low,low+1]`，相邻无包含：

```text
M：    0  1  2  3  4  5  6  7  8  9 10
low：  1  0  2  4  5  4  2  1  3  6  5
```

完整FX依次为底M1、顶M4、底M7、顶M9，源FX位置为0、1、2、3。M1→M4中心距3，范围low最低0、high最高6；M4→M7也距3，范围最低1、最高6，均满足其余成笔条件。M1与M4的窗口为`[0,3)`和`[3,6)`：紧邻、不共用，但中间没有独立K线。

| 档位 | 逐点取舍 | EOF已提交R | EOF未完成Bi002 |
|---|---|---|---|
| 强，min_gap=4 | M1→M4距离失败；底M7弱于起点M1而保留旧S；随后M1→M9距离8并通过全部条件 | 空 | M1→M9，即FX0→FX3 |
| 弱，min_gap=3 | M1→M4先缓存；M4→M7反向合格，提交前笔；M7→M9距离2失败 | M1→M4，即FX0→FX1 | M4→M7，即FX1→FX2 |

两档均读完4个FX。这个例子说明：弱档的单对距离门槛较宽，但更早接受端点会改变后续路线，最终R不保证包含强档R。不能在原强档Q上临时放宽后继续。

'''
active=active[:i]+fixture+active[i:]
active=active.replace('每行E均为None，Q的来源上下文保存到本行N及完整来源前缀，依据条数等于已读FX数。','每行E均为None，Q保存强档／min_gap=4以及本行N和完整来源前缀，依据条数等于已读FX数。该主例及同价例在弱档的R、缓存、S、游标和未决范围相同，但模式元数据与部分失败依据不同，不能称两个Q完全相同。',1)
active=active.replace('[分批与重复调用核验](../../artifacts/mas/bi-memo-consistency/checkpoint-checks.json)','[强／弱档与分批核验](../../artifacts/mas/bi-distance-options/mode-checks.json)',1)
active=active.replace('以下7个拟议私有辅助函数','以下8个拟议私有辅助函数',1)
# Preserve existing source validator signature; policy resolution is an explicit separate helper.
active=active.replace('前缀修订报输入修订；不静默清空R或重选起点。','前缀修订报输入修订；不静默清空R或重选起点。previous_state必须是None或完整有效Q，空字典不能当成初次运行；距离档位兼容性另由下面的_resolve_distance_mode检查，均通过后才能读新FX。',1)
i=active.index('#### 同型强弱：_compare_same_kind')
normalizer='''#### 解析距离档位：_resolve_distance_mode

**接口：** `_resolve_distance_mode(distance_mode, previous_state=None) → (mode, min_gap)`。

1. 显式值仅接受`"strong"`或`"weak"`；其他字符串、数字、布尔值及容差替代值报错。None只表示省略。
2. 初次previous_state为None：省略取strong；按固定映射strong→4、weak→3派生门槛。
3. 续读：旧Q必须显式保存合法mode及与之相符的min_gap；缺失或不一致即报错，不从旧笔中心距猜测档位。省略则继承；显式值必须等于旧mode，否则拒绝续用，即使尚无笔。

只返回有效值，不推进位置、不改Q，也不允许独立指定min_gap。

'''
active=active[:i]+normalizer+active[i:]
active=active.replace('_check_first(merged, fx, S, F) →','_check_first(merged, fx, S, F, min_gap) →',1)
active=active.replace('先查`c(F)-c(S)≥4`','先查`c(F)-c(S)≥min_gap`',1)
active=active.replace('旧A→B合格，F晚于B','旧A→B在同一距离档位下合格，F晚于B',1)
active=active.replace('_check_reverse(merged, fx, B, F) →','_check_reverse(merged, fx, B, F, min_gap) →',1)
active=active.replace('查中心距至少4，再查顶high','查中心距至少min_gap，再查顶high',1)
active=active.replace('_validate_output(source, Q, R_before)`','_validate_output(source, Q, R_before, mode, min_gap)`',1)
active=active.replace('1. 直接按001检查R及缓存各笔：','1. 核对Q中的mode／min_gap与本次解析结果完全相同，且符合strong→4、weak→3的映射。直接按001本档检查R及缓存各笔：',1)
active=active.replace('process(source, previous_state=None):','process(source, distance_mode=None, previous_state=None):',1)
active=active.replace('_validate_input(source, previous_state)           # 2.1，先验来源再看M','_validate_input(source, previous_state)           # 2.1，先验来源再看M\n    mode,min_gap ← _resolve_distance_mode(distance_mode,previous_state)',1)
active=active.replace('若previous_state不存在：','若previous_state为None：',1)
active=active.replace('_check_first(merged,fx,S,F)','_check_first(merged,fx,S,F,min_gap)')
active=active.replace('_check_reverse(merged,fx,B,F)','_check_reverse(merged,fx,B,F,min_gap)')
active=active.replace('source_context=当前整个输入及完整来源／长度／稳定上下文','source_context=当前整个输入及完整来源／长度／稳定上下文，\n                       包括本次有效mode及min_gap',1)
active=active.replace('_validate_output(source,Q,R_before)              # 2.9','_validate_output(source,Q,R_before,mode,min_gap) # 2.9',1)
# A full policy pseudocode block is separate from the one complete main process.
i=active.index('#### 三个分支的数值判断')
resolver='''#### 距离档位解析

```text
_resolve_distance_mode(distance_mode,previous_state=None):
    若distance_mode不是None且不在{"strong","weak"}：报错
    若previous_state为None：
        mode ← "strong"（省略时）或distance_mode
    否则：
        old_mode,old_gap ← 旧Q.source_context中显式保存的值
        若缺失、old_mode非法或old_gap≠映射[old_mode]：报错
        mode ← old_mode（省略时）或distance_mode
        若mode≠old_mode：报错，不能在旧Q上改档
    min_gap ← {"strong":4,"weak":3}[mode]
    返回(mode,min_gap)
```

'''
active=active[:i]+resolver+active[i:]
active=active.replace('若j−i<4：返回(False,实际距离依据)','若j−i<min_gap：返回(False,实际中心距与本档门槛依据)')
active=active.replace('返回(ok,实际端点及F侧范围极值依据)','返回(ok,实际中心距、min_gap及F侧范围极值依据)',1)
active=active.replace('返回(ok,实际距离及两侧范围极值依据)','返回(ok,实际中心距、min_gap及两侧范围极值依据)',1)
active=active.replace('_validate_output(source,Q,R_before):','_validate_output(source,Q,R_before,mode,min_gap):',1)
active=active.replace('    要求len(Q.R)≥len(R_before)，且原有前缀逐项同值','    要求mode合法，min_gap={"strong":4,"weak":3}[mode]\n    要求Q.source_context中的mode/min_gap与本次解析结果完全相同\n    要求len(Q.R)≥len(R_before)，且原有前缀逐项同值',1)
active=active.replace('中心距离至少4','中心距离至少min_gap',1)  # Remaining generic full-validator occurrence.
active=active.replace('输入校验一次保证严格完整分型及时间顺序','输入校验一次保证严格完整分型及时间顺序，距离档位在读取前解析并固定',1)
# Explain geometry, reductions and mode-dependent chosen outputs.
i=active.index('### 简化依据与边界')
why='''### 距离选项的几何意义

设两中心为i<j，d=j−i，窗口分别是`[i−1,i+2)`与`[j−1,j+2)`。两窗口不重叠等价于d≥3；二者之间独立合并K线的根数是`max(0,d−3)`。所以强档要求d≥4，弱档允许d=3时零独立间隔。弱档不能同时保留“至少一根独立K线”的文字。

下面的简化对两档均成立：首笔起点极值保证不依赖门槛4；端点区间关系只需严格分型的内侧邻线及范围极值，d≥3已满足；延伸必须沿用旧缓存相同档位，新F更晚使原距离条件继续成立。若改档，则旧选择历史和距离前提都须重算，不能只改Q中的一个数字。

'''
active=active[:i]+why+active[i:]
active=active.replace('给定连续21根合并K线','本例按强档给定连续21根合并K线',1)
active=active.replace('这里末笔未完成是允许的本批输出，','此输入弱档的选中状态也相同。这里末笔未完成是允许的本批输出，',1)
active=active.replace('距离＋F侧范围极值；起点极值由初始化保证','本档min_gap＋F侧范围极值；起点极值由初始化保证',1)
active=active.replace('旧输入前缀保持、完整FX不遗漏且按顺序时','距离档位相同、旧输入前缀保持、完整FX不遗漏且按顺序时',1)
# Do not alter user's004 note or quoted prompt: put active policy outside their text.
i=active.index('### 协作提示词')
active=active[:i]+'原note中的“成bi”按001本次选择的距离档位判定；原草案及下面提示词保留原句。\n\n'+active[i:]
active=active.replace('本文Q是算法层统一记号；本次补清的Q打包、初始化依据及完整输出复核等约定，仍须与实际返回报告逐项对照，不能直接当成已同步的生产接口。','当前检查的代码仍固定使用中心距4。本文distance_mode及Q是算法层约定，弱档配置、Q打包、初始化依据及完整输出复核等仍须与实际报告逐项对照，不能当成已同步的生产接口。',1)
active=active.replace('- 当前提交规则与作者原文唯一划分、永久确认及未来完成性的关系尚未证明。','- 已核验当前固定缓存可能永久不再更新；[A换C及待定笔链讨论](../../artifacts/mas/bi-start-reselection/README.md)涉及前一笔与提交边界，仍未采纳。本次仅增加距离选项，不改变缓存／提交规则；原已知B→C中心距1在两档均失败，不能据此宣称恢复问题已经解决。\n- 当前提交规则与作者原文唯一划分、永久确认及未来完成性的关系尚未证明。',1)
new=active+'## Appendix A —'+archive
(HERE/'draft-memo.md').write_text(new)
for name,start,end in [('001','## 001 —','## 002 —'),('002a','### 002.a —','### 002.b —'),('002b','### 002.b —','### 002.c —'),('002c','### 002.c —','### 002.d —'),('002d','### 002.d —','## 003 —'),('003','## 003 —','## 004 —'),('004','## 004 —','## 005 —'),('005','## 005 —','## Appendix A —')]:
 (HERE/f'section-{name}.md').write_text(new[new.index(start):new.index(end)])
print({'draft_lines':len(new.splitlines()),'archive_exact':new[new.index('## Appendix A —'):]==old[old.index('## Appendix A —'):]})
