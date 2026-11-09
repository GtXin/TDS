"""Apply evidence-backed S6 appendix supplements, without executing CC."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
MEMO = ROOT / 'docs/memo/memoWX_023_Chan_zoushi.md'
before = MEMO.read_bytes()
text = before.decode()
assert '### A.8 —' not in text
prefix = text.split('## Appendix A —', 1)[0]
new_quotes = []

def quote(lesson, start, stop, heading, note, citation):
    path = ROOT / f'references/chan_theory/{lesson:03d}.md'
    raw = '\n'.join(path.read_text().splitlines()[start-1:stop])
    rendered = re.sub(r'</?span\b[^>]*>', '', raw).replace('==', '\\=\\=')
    assert '![' not in rendered, 'Review/copy every new selected figure before adding it'
    body = '\n'.join('> '+line if line else '>' for line in rendered.splitlines())
    new_quotes.append({'lesson': lesson, 'start_line': start, 'stop_line': stop,
                       'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                       'source_text': raw, 'rendered_text': rendered})
    return f'### {heading}\n\n{note} 本地快照 {lesson:03d}.md，{start}–{stop}行。[{citation}]\n\n{body}\n\n'

# Add six theory sources before the implementation references; preserve AMA order.
def shift(match):
    first = int(match[1]); last = match[3]
    first = first+6 if first >= 7 else first
    if last:
        end = int(last); end = end+6 if end >= 7 else end
        return f'[{first}{match[2]}{end}]'
    return f'[{first}]'
text = re.sub(r'\[(\d+)(?:([–-])(\d+))?\]', shift, text)

extra = quote(36,16,26,'A.8 — 第36课：同一历史在不同分解视角下的完成状态',
    '连续正文，保留结合律、多级别分解、5分钟已完成而30分钟未完成，以及中枢震荡可由更小级别组成的上下文。这里的多义性依赖明确规则，不能解读成随意分段。',7)
extra += quote(43,20,48,'A.9 — 第43课：小级别转折与出现更大中枢后的重新归类',
    '连续正文，保留两类背驰／转折关系直到走势分解原则和B、C重叠／不重叠的两个结果；“注／娇注”仍属于整理者。正文并未说任一小级别转折都已经结束本级走势。',8)
extra += quote(63,23,27,'A.10 — 第63课：基本图表、递归级别与显示载体分开',
    '连续正文，说明先选最低图表，再递归构成走势；把完成走势标到5分钟或30分钟图上是显示／记忆选择，不把图表周期直接当作结构级别。所选正文没有嵌入或指向需复制的行情图。',9)
extra += quote(42,108,112,'A.11 — 第42课答疑：多个同级中枢与六段延伸的分解区别',
    '保留作者标签、回复时间和完整读者问题／答复，补足第38课规则的一个直接边界例：多个不延伸中枢仍可组成趋势，单个延伸中心的拆分是另一件事。',10)
extra += quote(52,278,284,'A.12 — 第52课答疑：连接点的极值与观察级别重组',
    '保留连续两问两答，作者将共同高低点的标准形式归于结合律，并解释不同级别分解可得不同中枢。提问里的娇注保留，不把几何端点与每个成员生命周期极值混同。',11)
extra += quote(80,462,466,'A.13 — 第80课答疑：更大中枢出现后采用新级别视角',
    '完整问题／作者答复：原先已有两个1分钟中枢，不足以无视后来已形成的5分钟中枢而继续套旧级别标签。本段是具体场景，不补造机械“九根K线自动升级”规则。',12)
boundary = '以上证据支持随后讨论定义与算法，但本次不填写001–005'
assert text.count(boundary) == 1
text = text.replace(boundary,extra+boundary)

same_level = '''
**SAME_LEVEL 还需保留的执行条件。** 这些条件属于本版本的工程分解规则，不由模式名称自动推出。[19]

1. **左缘相位只可试移一次。** `_segment_projection_plan()` 在1859–1869行先找从run起点0的实际离开；仅当其始终没有离开、右移起点1已有离开，才让首段从1开始。内部已经建立的分界仍从旧终点后一部件原位重启，不能随意丢掉中途来源。
2. **左侧X与未确认右侧X的复核水位不同。** `first_exit()` 和 `exit_is_valid_for_final_cores()`（1405–1471行）用X出现当时的延伸中枢判断端点是否严格离开；后一函数明确不让 `observed_to_position` 改写这个几何判断。`exit_survives_internal_extension()`（1473–1511行）则只对尚未确认的右侧候选，允许用其自身后续延伸判断早先X是否被吸收。不能把“左侧防未来回写”扩大成“所有活动候选都不再复核”。
3. **保守基线与最终相位细分分开。** 内部 `valid_exit_through()` 仍有 `observed_to_position >= position+2` 的延迟检查（1515–1555行），因此不能声称整个文件从未使用固定两部件等待。最终 `refine_complete_phase_partitions()`（1681–1857行）只有找到至少两条从旧区间左缘连续开始、各自在其区间内拥有正式中枢及E同向实际离开的相位走势，才细分保守基线；左段冻结还取决于后一有效且已冻结相位，最右未确认部分保留forming。前述“不再X2后固定等待两部件”说的是最终发布裁决，不是删除了所有旧基线检查。
4. **类别与独占中枢检查独立于端点连线。** `_reproject_segment_local()` 的2140–2158行比较本段所有有序中枢对，收集严格方向集合；仅集合恰有一个方向才给 `TREND`，没有方向或同时含上／下严格关系均给 `CONSOLIDATION`。它不是简单“中枢数大于1就趋势”，也不是只比较最后相邻一对。最终 `_validate_result_invariants()`（770–916行）要求每个正式中枢恰有一个走势归属、同一run中的frozen都在forming之前，已发布分界具有实际离开且不切穿完整／延伸中枢，右段进入证据不得来自分界左侧；这与extend可共享中枢的上下文关联有明确区别。

'''
anchor = '第38课允许同级别规则下的“盘整＋盘整”'
assert text.count(anchor) == 1
text = text.replace(anchor,same_level+anchor)

recursive = '''
递归来源与trace还有两个约束不能省略。`recursive_leg_runs_from_level_result()`（291–400行）遇到forming或起终点价相同的来源时，先结束当前run再跳过，而不是删掉该项后把两侧已冻结走势自动接成一条连续run；跨来源run或不连续的下一项也另起run。`_trace_for_zoushi()`（476–588行）在内核提供共享 `trace_horizon_position` 时，以实际选中正式成员的时间和合并坐标截断旧走势范围，不借关联中枢右侧仍在延伸的完整trace补齐；正式成员都没有 `merged_to_index` 时就保留 `None`。只有显式关闭证据可以再扩大依赖水位，且缺失依赖不会从整个中枢猜一个值。递归输出的 `logical_level` 由origin与depth计算，不是将分钟周期乘一个常数（605–667行）。[20]

'''
anchor = '### B.11 — 更新方式、成本与本次验证边界'
assert text.count(anchor) == 1
text = text.replace(anchor,recursive+anchor)
text = text.replace('实际完成：108课程关键词扫描；上述原文连续范围对照；2张源图查看并逐字节复制；',
    '实际完成：108课程关键词扫描；13组原文连续范围对照；2张源图查看并逐字节复制；')

old_refs = text.index('\n[13] CC本机选定源码快照.')
refs = '''
[7] 缠中说禅. [教你炒股票36：走势类型连接结合性的简单运用](../../references/chan_theory/036.md). 正文16–26行。

[8] 缠中说禅. [教你炒股票43：有关背驰的补习课](../../references/chan_theory/043.md). 正文20–48行，保留整理者夹注。

[9] 缠中说禅. [教你炒股票63：替各位理理基本概念](../../references/chan_theory/063.md). 正文23–27行。

[10] 缠中说禅. [教你炒股票42：有些人是不适合参与市场的](../../references/chan_theory/042.md). 108–112行，2007-04-04 16:34:54作者答疑及读者提问。

[11] 缠中说禅. [教你炒股票52：炒股票就是真正的学佛](../../references/chan_theory/052.md). 278–284行，2007-05-21 16:27:11作者答疑及连续追问。

[12] 缠中说禅. [教你炒股票80：市场没有同情、不信眼泪](../../references/chan_theory/080.md). 462–466行，2007-09-17 17:12:00作者答疑及读者提问。
'''
text = text[:old_refs]+refs+text[old_refs:]
text = text.replace('136–231、291–400、670–757行，递归中枢、来源投影与 `depth=1` 走势入口。',
                    '136–231、291–400、476–667、670–757行，递归中枢、来源投影、共享trace范围与 `depth=1` 走势入口。')

assert text.split('## Appendix A —',1)[0] == prefix
stamp = datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
backup = ROOT/'docs/memo/backups'/f'{MEMO.stem}__{stamp}.md'
with backup.open('xb') as f:f.write(before)
assert backup.read_bytes()==before and MEMO.read_bytes()==before
MEMO.write_text(text)
for q in new_quotes:
    body='\n'.join('> '+line if line else '>' for line in q['rendered_text'].splitlines())
    assert body in text
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
    if not target.startswith(('http://','https://','#')):
        assert (MEMO.parent/target).exists(), target
assert re.findall(r'^\[(\d+)\]\s', text, re.M)==[str(x) for x in range(1,21)]
baseline=json.loads((HERE.parent/'baseline.json').read_text())
expected=next(r['main_prefix_sha256'] for r in baseline if r['memo']==str(MEMO.relative_to(ROOT)))
assert hashlib.sha256(prefix.encode()).hexdigest()==expected
(HERE/'added_quotes.json').write_text(json.dumps(new_quotes,ensure_ascii=False,indent=2)+'\n')
(HERE/'write_check.json').write_text(json.dumps({'memo':str(MEMO.relative_to(ROOT)),'backup':str(backup.relative_to(ROOT)),'old_sha256':hashlib.sha256(before).hexdigest(),'main_prefix_sha256':expected,'added_quote_blocks':len(new_quotes),'total_quote_blocks':13,'new_original_figures':0,'new_code_numerical_cases':0,'checks':['source ranges directly extracted after disclosed span/equality normalization','new quotes exactly contained in written appendix','20 sequential references and relative links pass','main prefix exactly matches task-start baseline','no source/CC imports or execution']},ensure_ascii=False,indent=2)+'\n')
print('Added6 continuous source blocks and targeted SAME_LEVEL/recursive source constraints; main prefix, backup, links and references passed.')
