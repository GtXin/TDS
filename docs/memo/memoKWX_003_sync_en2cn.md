# TDS 拉取、同步与中文化流程

## 000 — 范围

同步 TDS 并增量更新中文副本。[1–7]

## 001 — 起点与输入

在 `TDS_CN` 根目录打开 PowerShell，以下命令和工作路径均从这里起算。

| 检查项 | 输入与通过条件 |
|---|---|
| 环境 | Git、PowerShell及项目目录读写权限可用，缺项按任务授权准备后继续 |
| 位置 | `../TDS/` 为上游工作副本，`./` 为中文项目，两个目录互不包含 |
| 上游 | 默认 `https://github.com/GtXin/TDS.git` 的 `main`，隔离试验可使用任务明确提供的本地 Git 上游 |
| 中文基线 `$base` | `./README.md` 的完整源提交与最近成功回执 `source_commit` 一致，回执覆盖的旧译文可核验 |
| 任务范围 | 明确本次更新目标、可写路径、覆盖授权及验证范围，既有材料作数据读取 |
| 记录位置 | `./mas/tasks/` 保存任务，`./artifacts/localization-update-<目标短号>/` 保存本轮清单、译文与回执 |

| 首次接手情况 | 处理 |
|---|---|
| 缺少 `../TDS` | 按 002 克隆已确认上游 |
| 已有目录而 Git 根、远程或分支不符 | 先定位正确工作副本，有本地内容时按授权处理，避免误用该目录 |
| CN 尚无上游派生内容 | `$base = $null`，以目标提交全部受管文件作首次导入，现存流程文档和本地文件按碰撞处理 |
| CN 已有内容而基线/回执缺失 | 先从源提交、旧交付及哈希恢复对应关系，仍缺依据时暂停增量范围判定并恢复基线，已有派生内容不得以 `null` 进入首次导入 |
| Git 中缺少 `$base` | 补取该提交或所需历史后确认可读，失败时登记原因和待办 |

## 002 — 获取与固定上游

```powershell
$tds = '../TDS'
$origin = 'https://github.com/GtXin/TDS.git' # 隔离试验替换为任务指定上游
git --version
if ($LASTEXITCODE -ne 0) { throw 'Git 不可用' }
if (-not (Test-Path $tds)) {
    git clone --branch main $origin $tds
    if ($LASTEXITCODE -ne 0) { throw '克隆失败' }
}
git -C $tds rev-parse --show-toplevel
git -C $tds remote get-url origin
git -C $tds status --short --branch
```

- 根目录、上游地址和 `main` 核对成功后获取目标
- 缺少 `origin` 时，先确认目录归属，再用 `git -C $tds remote add origin $origin` 设置

```powershell
git -C $tds fetch origin main
if ($LASTEXITCODE -ne 0) { throw '获取失败' }
$target = git -C $tds rev-parse --verify FETCH_HEAD
if ($LASTEXITCODE -ne 0) { throw '目标提交不可读' }
$tracking = git -C $tds rev-parse --verify origin/main
if ($LASTEXITCODE -ne 0 -or $target -ne $tracking) { throw '远程跟踪提交不一致' }
```

| 情况 | 同步动作 |
|---|---|
| 可快进且无冲突 | `git -C $tds merge --ff-only $target`，检查退出码 |
| 已授权覆盖 TDS | 核受影响路径后执行 `git -C $tds reset --hard $target`，检查退出码 |
| 取源条件 | `HEAD == $target`，本轮取源文件与该提交对应，工作树改动已处理 |
| 无上游增量 | `$base == $target` 且最近回执已通过时结束，有未完成回执时转入恢复 |

## 003 — 建立增量与本地保护清单

```powershell
# $base 使用 001 确认的值
if ($base) {
    git -C $tds diff --name-status -M $base $target
} else {
    git -C $tds ls-tree -r --name-only $target
}
```

| 项目 | 操作与判定 |
|---|---|
| 路径 | 脚本解析 Git 路径用 `-z`，检查重命名两端，目标解析后必须位于 CN 根目录内，遍历跳过外部及受保护目标的符号链接和目录联接 |
| 保护清单 | 写入前登记 CN 文件相对路径与 SHA-256，遍历前排除凭证、受保护区、应用状态、环境和缓存，符号链接按实际目标核对 |
| `A` | 查同名文件、正式编号和配套目录，确认来源后加入或登记冲突 |
| `M` | 比较旧上游→新上游、旧中文交付→当前 CN，分清翻译差异、本地编辑及换行/BOM差异后合并 |
| `D` | 核 CN 独有内容、引用及删除授权，确认删除的路径备份后登记 |
| `R` | 核新旧路径、编号、图片和引用，拆成新增新路径与移除旧路径两项记录 |
| 本地内容与冲突 | 保留 CN 独有文件，本地编辑的共同文件逐项合并，无法确定的取舍记 `conflict` 并保留现场 |

## 004 — 中文化与逐项覆盖

按段落、代码块和单元格判定用途，说明可译，机器字面值与原始证据原样保存。[5,8,9]

| 内容 | 处理与检查 |
|---|---|
| Markdown 人文标题、正文、图注、表格及链接显示字 | 每项记录“已译”或“原样保留及原因”，统一术语，核结论、前提、否定、数字、单位和验证状态 |
| 围栏、行内代码、命令、提示词、YAML、标识符、链接目标 | 提取受保护片段，与源逐项比对内容及出现次数，译后保持完整 |
| 源码、测试、配置、锁、原文、许可、数据、图片及生成产物 | 与选定源文件逐字节或按 SHA-256 比对 |
| CSV | 仅译 `chan_table_header.csv` 的 `meaning`、`chan_table_context.csv` 的 `note` 中人文说明，解析后比较行列顺序及其余单元格 |
| 标题与锚点 | 翻译标题时保留被引用的原锚点，例如 `<a id="execution-checks"></a>`，逐项确认链接目标与片段可达 |
| 漏译与语义 | 对照源的全部人文单元核覆盖，复查剩余英文及保留原因，由另一 Agent 对照原文审校语义 |

```text
源片段  Run `mode="UP"` for 3 bars.
译文    以 `mode="UP"` 处理 3 根 K 线。
核对    代码字面值与数字一致，事实和条件对应
```

## 005 — 暂存与逐文件写入

| 记录 | 最少字段 |
|---|---|
| 本轮 `manifest.json` | `base_commit`、`source_commit`、`state`、`files` |
| 每个文件项 | `op`、`path`、`old_path`、`source_sha256`、`before_sha256`、`planned_sha256`、`backup`、`result` |
| 字段约定 | 路径相对 CN 根目录，SHA-256 指明使用的实际字节，文件缺失或无适用值用 `null` |
| 状态 | 本轮 `staging/partial/complete`，每项 `pending/written/verified/kept/conflict`，`kept` 附保留原因 |

- 首次落盘前保存完整计划、CN 保护清单和备份，备份遵循 WX006并覆盖其他将替换的文件 [6]
- 独立待写项的暂存通过 006 逐项适用检查后写入，源提交/源哈希再次核对，目标现值须匹配写前哈希，新路径须仍为空
- 同目录临时文件替换并回读，每项即时持久保存结果，README、项目规则、索引、记忆和日志按本地内容合并

## 006 — 验收、恢复与基线

| 检查 | 通过条件 |
|---|---|
| 版本与范围 | 固定源提交可追溯，每个上游差异均有操作、保留理由或未决记录，记 `complete` 和推进基线时未决项数须为零 |
| 中文覆盖 | 人文单元全部有处理记录，剩余英文均有原因，语义审校无未修复问题 |
| 保护内容 | 受保护片段逐项相同，原样文件字节/哈希相同，CSV 非说明内容相同 |
| 链接 | 在最终目录布局核文件与锚点，新增失效引用为零，源既有缺口登记 |
| 本地成果 | 清单外受保护文件的写前/写后哈希相同，本地合并取舍有记录 |
| 写入与记录 | 计划与实际结果相符，备份可定位，收尾文件回读哈希写入最终回执 |

| 中断后实际文件哈希 | 恢复动作 |
|---|---|
| 等于 `planned_sha256` | 已落盘，补做验收并补记结果 |
| 等于 `before_sha256` | 尚未落盘，可复核来源和目标后续做 |
| 两者均不等 | 视为未知/并发改动，保留当前文件、记冲突并核查 |
| 删除/新增的空路径 | 以 `null` 表示缺失，结合操作类型和清单判断已完成或待执行 |

- 部分写入或有未决冲突时记 `partial`，保留上一完整验收基线，继续独立项或依备份恢复本轮改动
- 首次导入未完成时保留 `$base = $null`，已有未完成计划与目标一致时按计划恢复
- 全部验收通过后，将 `./README.md`、任务、`./CodexMemory.md` 和 `./logXW.md` 的收尾更新作为清单中的最后操作，先登记各自最终拟写哈希，再写入回读并记 `complete` [7–9]
- 本轮执行检查与上游历史测试结果分别记录，源码运行、安装和业务测试按当次任务授权执行

## 007 — 流程 memo 的交叉验证

| 步骤 | 交付与通过条件 |
|---|---|
| 独立接手 | 未参与编写且无聊天前文的 Agent，仅凭 memo、明确列出的输入和环境权限提出并执行步骤 |
| 隔离试走 | 用临时目录或本地测试上游验证首次准备、A/M/D/R、混合可译内容、本地冲突、部分写入恢复及无更新 |
| 交叉复核 | 另一 Agent 对照源、计划和输出核 006，复核取舍、原样内容和所有预期结果 |
| 问题回修 | 将缺失条件、错误操作或依赖聊天补充的环节回写 memo，再试走受影响路径 |
| 完成记录 | 保存所用 memo 哈希、试走输入、命令、结果、发现及复核结论，标明实际运行范围与尚待验证项 |

## References

1. [WX001](memoWX_001_folderStrucureforProj009.md)
2. [WX002](memoWX_002_MAS.md)
3. [WX003](memoWX_003_folderDecision.md)
4. [WX004](memoWX_004_projectAndMAS.md)
5. [WX005](memoWX_005_informationWorkflow.md)
6. [WX006](memoWX_006_memoWritingGuide.md)
7. [WX007](memoWX_007_codexMemory.md)
8. [5125d92 更新记录](../../mas/tasks/20261109-tds-cn-update-5125d92.md)
9. [4c806cf 更新记录](../../mas/tasks/20261110-tds-cn-update-4c806cf.md)
