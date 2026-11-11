# CC 数据对接与 ChanTable 转换

## 000 — 范围

从 CC 冻结本批行情，计算原生结构，再生成并回读 ChanTable。主表沿用 WX009 的41列、原始行、结构 ID、来源和缺失值约定。[1]

## 001 — 起点与参数

在同一个 PowerShell 窗口依次执行001至004。先填写本次输入，查询包含 UTC 开始时间，排除 UTC 结束时间。

| 参数 | 填写或核对 |
|---|---|
| `$ccDb` | CC 实际行情库路径，使用库中已存的行情。需要补齐时先在 CC 加载所需范围 |
| `$symbol`、`$period` | CC 使用的标的代码与周期 |
| `$fromUtc`、`$untilUtc` | 带 `Z` 或 `+00:00` 的 UTC 时间，精确到秒 |
| `$view` | `base` 导出 MK、FX、BI、XD。需要中枢和走势时选择 `recursive_l0_d1` 或 `recursive_l1_d1` |
| `$ccPython`、`$tdsPython` | CC Python 3.12 环境含 DuckDB，TDS 使用 Python 3.11 环境 |
| `$workRoot` | 实施使用 TDS_CN。隔离试走填任务目录内的试验工作根 |

```powershell
$ErrorActionPreference = 'Stop'
$tdsRoot = 'D:/Codex/TDS_CN'
$ccRoot = 'D:/Codex/CC'
$ccPython = Join-Path $ccRoot '.venv/Scripts/python.exe'
$tdsPython = 'D:/Codex/TDS/artifacts/localization-update-49ec5f4/runtime-audit/environment/.venv/Scripts/python.exe'
$ccDb = Join-Path $env:USERPROFILE '.cc/klines.duckdb'
$workRoot = $tdsRoot
$symbol = ''
$period = ''
$fromUtc = ''
$untilUtc = ''
$view = ''

Set-Location -LiteralPath $tdsRoot
if (-not $symbol -or -not $period -or -not $fromUtc -or -not $untilUtc) {
    throw 'Fill symbol, period, fromUtc and untilUtc'
}
if ($view -notin @('base', 'recursive_l0_d1', 'recursive_l1_d1')) {
    throw 'Select a ChanTable view'
}
foreach ($file in @($ccDb, $ccPython, $tdsPython)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing file $file" }
}
git -C $ccRoot rev-parse --verify HEAD
if ($LASTEXITCODE -ne 0) { throw 'CC Git checkout is unavailable' }
& $ccPython -B -X utf8 -c 'import sys, duckdb; assert sys.version_info >= (3, 12); print(sys.version, duckdb.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'CC Python check failed' }
& $tdsPython -B -X utf8 -c 'import sys; assert sys.version_info[:2] == (3, 11); print(sys.version)'
if ($LASTEXITCODE -ne 0) { throw 'TDS Python check failed' }

$env:PYTHONPATH = Join-Path $tdsRoot 'src'
$batch = 'cc-chantable-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,8)
$rawDir = Join-Path $workRoot "data/raw/cc/$batch"
$runDir = Join-Path $workRoot "artifacts/mas/$batch"
New-Item -ItemType Directory -Path $rawDir,$runDir | Out-Null
$rawCsv = Join-Path $rawDir 'klines.csv'
$provenance = Join-Path $rawDir 'provenance.json'
$native = Join-Path $runDir 'cc_native_snapshot.json'
$sourceLabel = 'CC DuckDB ' + [IO.Path]::GetFileName($ccDb)
$memoFile = Join-Path $tdsRoot 'docs/memo/memoKWX_004_CCToChanTable.md'
$memoSha = (Get-FileHash -LiteralPath $memoFile -Algorithm SHA256).Hash.ToLowerInvariant()
```

## 002 — 只读导出并冻结行情

从 `klines` 按标的、周期和 UTC 区间查询，按开始时间升序写出采集器要求的12列。查询或校验失败时按005处理，成功后得到冻结 CSV 和来源清单。

```powershell
@'
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import duckdb

from chanlab.data.cc_snapshot import CC_CSV_FIELDS, load_frozen_csv

db, csv_path, info, symbol, period, start, end, label, view, memo_sha = sys.argv[1:]
raw = Path(csv_path)
provenance = Path(info)
if raw.exists() or provenance.exists():
    raise FileExistsError("Use a new batch directory")

def utc_seconds(value):
    dt = datetime.fromisoformat(value)
    if dt.utcoffset() != timedelta(0) or dt.microsecond:
        raise ValueError("Use UTC timestamps at whole-second precision")
    return int(dt.timestamp())

start_ts, end_ts = utc_seconds(start), utc_seconds(end)
if not 0 <= start_ts < end_ts:
    raise ValueError("The UTC interval must have a valid start and end")

with duckdb.connect(str(Path(db).resolve()), read_only=True) as conn:
    rows = conn.execute(
        "SELECT symbol, period, timestamp, open, high, low, close, volume, "
        "amount, open_interest, settlement FROM klines "
        "WHERE symbol = ? AND period = ? AND timestamp >= ? AND timestamp < ? "
        "ORDER BY timestamp",
        [symbol, period, start_ts, end_ts],
    ).fetchall()
if not rows:
    raise ValueError("No CC bars matched the selected input")

with raw.open("x", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(CC_CSV_FIELDS)
    for row in rows:
        writer.writerow((*row[:3], datetime.fromtimestamp(row[2], UTC).isoformat(), *row[3:]))
frozen = load_frozen_csv(raw)
receipt = {
    "database": str(Path(db).resolve()),
    "source": label,
    "symbol": symbol,
    "period": period,
    "from_utc": start,
    "until_utc_exclusive": end,
    "first_utc": frozen[0]["datetime_utc"],
    "last_utc": frozen[-1]["datetime_utc"],
    "rows": len(frozen),
    "csv_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
    "exported_at_utc": datetime.now(UTC).isoformat(),
    "cc_python": sys.version.split()[0],
    "duckdb": duckdb.__version__,
    "volume_unit": "unverified",
    "provider": "unverified",
    "timestamp_semantics": "UTC bar start in Unix seconds",
    "view": view,
    "memo_sha256": memo_sha,
}
with provenance.open("x", encoding="utf-8") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
print(raw, len(frozen), receipt["csv_sha256"])
'@ | & $ccPython -B -X utf8 - $ccDb $rawCsv $provenance $symbol $period $fromUtc $untilUtc $sourceLabel $view $memoSha
if ($LASTEXITCODE -ne 0) { throw 'CC data export failed' }
$provenanceSha = (Get-FileHash -LiteralPath $provenance -Algorithm SHA256).Hash.ToLowerInvariant()
```

## 003 — 计算并保存 CC 原生档案

采集器使用已冻结的 CSV 和 CC 归一化默认配置，保存原生结构、代码身份、实际配置及状态。输出为本批 `cc_native_snapshot.json`。

```powershell
& $ccPython -B -X utf8 -m chanlab.data.cc_snapshot $rawCsv $native --cc-root $ccRoot --source-label $sourceLabel --symbol $symbol --period $period
if ($LASTEXITCODE -ne 0) { throw 'CC snapshot calculation failed' }
$nativeSha = (Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash.ToLowerInvariant()
```

| 范围 | 执行条件 |
|---|---|
| 计算 | 采集器使用 `extend` 配置，递归导入还要求 `standard` 线段口径 |
| 状态 | 保存选定输入结束时的原生结果和形成中状态，确认时间随来源记录 |
| 级别 | `recursive_l0_d1` 输出逻辑 L1，`recursive_l1_d1` 输出逻辑 L2，各自选同一 origin 和 depth 的中枢与走势 |

## 004 — 生成、回读和验收 ChanTable

TDS 按 WX013 的 KlineTSeries 约定校验原始 K 线，再生成选定视图。[2] 参照 WX011 的读写接口回读主表和背景。[3] 同时核对原始行与特征档案，通过后写 verification.json。

```powershell
@'
import csv
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from chanlab.algo.chan_table import COLUMNS, ChanTable
from chanlab.data.cc_import import available_cc_views, build_cc_view, import_cc_snapshot, write_import_report
from chanlab.data.cc_snapshot import load_frozen_csv, read_snapshot

raw, provenance, native, out, memo = map(Path, sys.argv[1:6])
provenance_sha, native_sha = sys.argv[6:]

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

require(sha(provenance) == provenance_sha, "Provenance changed after export")
require(sha(native) == native_sha, "Archive changed after calculation")
meta = json.loads(provenance.read_text(encoding="utf-8"))
frozen = load_frozen_csv(raw)
snapshot = read_snapshot(native)
raw_sha = sha(raw)
require(sha(memo) == meta["memo_sha256"], "Memo changed during the batch")
require(raw_sha == meta["csv_sha256"] == snapshot["input"]["sha256"], "Input SHA mismatch")
require(snapshot["raw_rows"] == list(frozen), "Archive rows differ from frozen CSV")
require(snapshot["source_label"] == meta["source"], "Source label mismatch")
require(len(frozen) == meta["rows"], "Provenance row count mismatch")
require(all(snapshot["input"][key] == meta[key] for key in ("symbol", "period")), "Provenance identity mismatch")
require(frozen[0]["datetime_utc"] == meta["first_utc"] and frozen[-1]["datetime_utc"] == meta["last_utc"], "Provenance time bounds mismatch")

template = Path("docs/memo/memoWX_009_designPatternForChanFeatures/chan_table_template.csv")
with template.open(encoding="utf-8-sig", newline="") as stream:
    require(tuple(next(csv.reader(stream))) == COLUMNS and len(COLUMNS) == 41, "WX009 header mismatch")

imported = import_cc_snapshot(snapshot)
views = available_cc_views(imported)
view = meta["view"]
require(view in views, f"Requested view unavailable. Available: {', '.join(views)}")
table = build_cc_view(imported, view=view)
require(len(table) == len(frozen), "ChanTable row count mismatch")
require(dict(table.selection) == views[view], "ChanTable selection mismatch")
for index, (row, src) in enumerate(zip(table.rows, frozen, strict=True)):
    expected = {key: src[key] for key in ("symbol", "period", "open", "high", "low", "close", "volume")}
    expected["timestamp"] = datetime.fromtimestamp(int(src["timestamp"]), UTC).isoformat()
    expected["raw_index"] = str(index)
    expected["source"] = meta["source"]
    require(all(row[k] == v for k, v in expected.items()), f"Raw data mismatch at index {index}")

main = out / "ChanTable.csv"
context = out / "context.csv"
features = out / "features.json"
report = out / "import_report.json"
done = out / "verification.json"
outputs = (main, context, features, report, done)
require(not any(path.exists() for path in outputs), "Use a new output directory")
table.write_csv(main, context, feature_path=features)
write_import_report(imported, report)
loaded = ChanTable.read_csv(main, context, feature_path=features)
require(loaded.rows == table.rows, "CSV round-trip mismatch")
require(loaded.to_feature_dict() == table.to_feature_dict(), "Context or source graph mismatch")
expected_inputs = {raw: raw_sha, provenance: provenance_sha, native: native_sha, memo: meta["memo_sha256"]}
require(all(sha(path) == digest for path, digest in expected_inputs.items()), "Input changed during conversion")
receipt = {
    "status": "verified",
    "memo_sha256": meta["memo_sha256"],
    "template_sha256": sha(template),
    "view": view,
    "selection": dict(table.selection),
    "rows": len(loaded),
    "columns": len(COLUMNS),
    "cc_source": snapshot["cc_source"],
    "cc_config": snapshot["config"],
    "sha256": {str(path.resolve()): sha(path) for path in (raw, provenance, native, *outputs[:-1])},
}
with done.open("x", encoding="utf-8") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2, allow_nan=False)
print(done, receipt["rows"], receipt["columns"], view)
'@ | & $tdsPython -B -X utf8 - $rawCsv $provenance $native $runDir $memoFile $provenanceSha $nativeSha
if ($LASTEXITCODE -ne 0) { throw 'ChanTable conversion or verification failed' }
```

## 005 — 交付与失败处理

以 `verification.json` 的 `status=verified` 和文件 SHA 为本批通过依据。交付冻结行情及来源清单、CC 原生档案、ChanTable 主表、背景、特征档案和导入报告。

| 检查点 | 通过条件或处理 |
|---|---|
| 行情库无法只读打开或查不到数据 | 核对库路径、占用、标的和时间范围，恢复可读输入后重新冻结 |
| 采集或来源校验失败 | 核对原始 CSV、档案身份、配置及报错来源链，修正对应步骤 |
| 所选递归视图不可用 | 查看实际可用视图，核所选级别和递归来源后重试 |
| 产物部分写入或核验失败 | 保留失败目录及报错。原窗口仍保有输入路径和 SHA 时，可将 `$runDir` 改为新目录并创建后重做004。会话已结束时从001开新批次 |
| 特征列语义 | 回读校验覆盖成员区间、起止点和锚点。未加载组为 `NA`，已加载 ID 列在本行无匹配为 `[]` |
| 来源与级别 | 导入报告可追溯原生 ID、来源和未映射项，递归中枢和走势配对，背驰和买卖点目前为 `NA` |

## 006 — 交叉验证

按 KWX003 第007节完成独立接手、隔离试走和交叉复核。[4] 核对执行证据与覆盖范围，引用集中列在文末。[5,6] 项目状态和下一步记入 CodexMemory。[7]

| 环节 | 通过条件 |
|---|---|
| 独立接手 | 无聊天前文的接手者仅凭 memo、列明的输入和本机环境执行001至005 |
| 隔离试走 | 将 `$workRoot` 和 `$ccDb` 指向新试验目录和合成库，核对导出边界、输入库 SHA、41列、成套回读和错误分支 |
| 交叉复核 | 另一位审阅者对照命令、输入、产物与验收记录，回修缺口后复验受影响的步骤 |

合成库试走已生成并回读321行、41列的 base 主表，重复写出与来源清单变更均被拒绝。[8,9] 另以真实焦煤主连1分钟行情验收了44,375行、41列的递归 L1 主表。[10]

## References

1. [WX009 缠论特征设计 · 002.u ChanTable](memoWX_009_designPatternForChanFeatures.md#002u--chantable)
2. [WX013 Kline 类族 · Kline 与 KlineTSeries](memoWX_013_klineFamily.md#003a--kline-and-klinetseries)
3. [WX011 ChanTable 实现 · 读写接口](memoWX_011_chanTableImplementation.md#003--implemented-chantable-interface)
4. [KWX003 流程 memo 的交叉验证](memoKWX_003_sync_en2cn.md#007--流程-memo-的交叉验证)
5. [WX005 信息工作流 · 核对证据与完成状态](memoWX_005_informationWorkflow.md#004--check-evidence-and-completion)
6. [WX006 Memo 写作指南 · 证据与决定](memoWX_006_memoWritingGuide.md#004--evidence-and-decisions)
7. [WX007 项目记忆 · 实现方式](memoWX_007_codexMemory.md#001--implementation)
8. [KWX004 独立接手与隔离试走](../../artifacts/mas/kwx004-executable-20261111/handoff.md)
9. [KWX004 交叉复核记录](../../artifacts/mas/kwx004-executable-20261111/cross-review.md)
10. [KWX004 真实行情递归 L1 验收记录](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/verification.json)
