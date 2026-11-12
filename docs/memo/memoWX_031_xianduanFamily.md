# Xianduan family implementation plan
## 000 — Scope and current result
参考memo028的结构与实施顺序，准备线段领域类、集成、验证和图集计划。[1] 类设计以memo009为核对依据。[2] 本稿仅完成外围计划，尚未执行实现或验证。

用户提及029作为算法依据；当前029是笔算法，030是仍在修订的线段算法稿。[3,4] 029用于上游笔与DP思路参考；线段识别、确认、状态和选择目标须等待线段规格定稿，实施前明确最终依据及版本。本稿不替用户确定这些规则，不修改029／030，不把030试算口径当作正式合同。

## 001 — Implementation plan
### 001.a — Implement the Xianduan family
1. 核对009的Xianduan／XianduanSeries设计与最终线段规格，列明成员、来源、公开方法、状态及解释合同；有冲突先记录并讨论。
2. 计划在 `src/chanlab/algo/` 实现共享算法，保持独立于API和网站。输入保留确切BiSeries及其分型、合并和原始来源链；ID、序列位置、端点锚点与确认时间分别处理。
3. 规格定稿后，逐项建立“定义／算法步骤→实现→独立检查→例子”对照；候选识别、上下文状态、DP转移、并列与回溯细节暂不补写。不直接搬用029的笔配对条件或最优子结构结论。
4. 保留逐段规则与来源证据、未覆盖区间及待确认部分；空结果与未完成识别分别记录。确认、追加、续读和历史修订语义待规格确定。
5. 先实现可直接核对的基线，再评估优化；复杂度按实际状态数、候选数和范围扫描成本推导，记录时间和内存。
6. 核对后完成explain、DataFrame、ChanTable、CSV/context和绘图集成；不改变上游已选笔路线来适配线段结果。
### 001.b — Repeat and review using Python Pro
冻结基线、输入、规则版本、共同测试及哈希；续作时实际读取共享Python Pro并记录版本与请求。两版遵守相同规格；披露既往技能接触，按顺序工程比较报告，不作技能因果结论。
### 001.c — Compare and select
独立进程核对实际导入路径，比较完整线段端点、状态、确认依据、来源和未覆盖区间；若规格采用DP，再比较全部可达状态及best／prev。依据正确性、可读性、类型与实测资源选择，保留失败版本与诊断。
### 001.d — Tests and integration
1. 规格定稿后建立手算例与边界表，覆盖已明确的定义、包含／等值／触点、破坏／延续、确认时间及未完成尾部；未决规则不预填预期答案。
2. 验证空／短输入、非法来源、ID与位置分离、不可变结果、证据一致性及上游来源保持。
3. 小输入独立穷举规格允许的候选和路线；分别检查逐段合法性、确认依据与选择目标。不能只验证最终线条看起来合理。
4. 验证表注册隔离、CSV/context往返、解释和绘图；执行相关pytest、strict mypy、Black／Ruff及覆盖检查，记录实际结果。
5. 沿用028真实CC的100／1,000／3,000完整分型前缀及两种上游笔档位，记录实际笔数和线段数；不足如实说明。各至少3次，分别记录上游、线段核心、工厂与端到端中位耗时、缓存、环境和内存口径。
### 001.e — Monte Carlo validation
1. 计划至少10,000条可复现随机原始OHLCV，经过既有合并、分型及029笔算法后进入线段算法；覆盖趋势、震荡、跳空、包含和等值，按长度及上游strong／weak分层。
2. 独立检查器不调用被测识别helper；短输入穷举，较长输入独立参考，分别报告合法性、确认和选择目标。价格镜像、平移、正比例缩放仅按最终规格所支持的不变量检验。
3. 保存种子、完整输入、来源哈希、规则版本、档位与统计；空结果、未确认、异常和资源未完成单列。
4. 差异保存最小可复现数据与问题图，向用户说明；不为通过实验擅改规格。
### 001.f — Full segmented chart validation
1. 完整真实样本从首根至末根原始K线连续分段，建议200根窗口、20根重叠；机器核对覆盖及缺页。全量结果计算一次，跨页线段保持真实端点。
2. 每页显示原始K线、合并范围、全部分型、源笔、线段及必要ID／锚点；确认与候选的显示方式待状态合同确定。不同上游档位分图保存。
3. PNG、交互HTML、窗口清单、缩略图与总索引放入 `artifacts/mas/xianduan-family/` 的独立运行目录，记录UTC范围、规则版本及来源哈希。
4. 逐页目视检查端点、跨页连续性、确认标记、遮挡和未覆盖行情；明确未绘／未查页数。必要memo图片复制到本memo同名伴随目录，不用局部例图代替全量验收。

## 002 — Implementation notes and verification reports
尚未执行；各节以后仅记录本轮实际证据，不沿用028或历史线段试算的通过数量。
### 002.a — Implement the Xianduan family → 001.a
待执行。
### 002.b — Python Pro continuation → 001.b
待执行。
### 002.c — Compare and select → 001.c
待执行。
### 002.d — Tests and integration → 001.d
待执行。
### 002.e — Monte Carlo validation → 001.e
待执行。
### 002.f — Full segmented charts → 001.f
待执行。
### 002.g — Handoff and remaining scope
下一步先明确线段算法依据及冻结版本，再补算法到代码的映射、测试预期和状态合同；本次不启动实现。
## 003 — Implemented classes, members and methods
### 003.a — Class count and scope
计划核对Xianduan／XianduanSeries两个领域类；最终成员和辅助结构待规格与009对齐，尚无本轮实现。
### 003.b — Xianduan
待补经核定的成员、类型、端点来源、状态、确认时间与validate合同。
### 003.c — XianduanSeries
待补确切来源引用、配置、规则版本、记录、解释依据及工厂／校验／访问／适配方法合同；不直接复制BiSeries字段。
### 003.d — Object workflow and implementation boundary
计划流程：原始K线→合并K线→全部完整分型→029笔路线→线段→解释／表／绘图。线段结果保留确切源笔版本，输入快照变化后的重算与确认语义待定。
### 003.e — Usage examples
待接口定稿并实际运行后补充。
### 003.f — Chart pictures and complete atlas
待本轮生成并验收后补充。
## References
1. [Memo028 — Bi family implementation plan](memoWX_028_biFamily.md)。
2. [Memo009 — Design pattern for Chan features](memoWX_009_designPatternForChanFeatures.md)。
3. [Memo029 — Chan_bi](memoWX_029_Chan_bi.md)。
4. [Memo030 — Chan_xianduan](memoWX_030_Chan_xianduan.md)。
