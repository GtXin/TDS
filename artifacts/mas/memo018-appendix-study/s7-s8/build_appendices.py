"""Build source-grounded S7/S8 appendices; no CC imports or execution."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[4]
FOLDER = ROOT / "docs/memo"
ARTIFACT = Path(__file__).parent
CC = "../../references/cc_algo/local_snapshot/374268381a3e"
records = []


class Study:
    def __init__(self, filename):
        self.path = FOLDER / filename
        self.asset = FOLDER / self.path.stem
        self.refs = []
        self.quotes = []
        self.images = []

    def cite(self, label, target):
        entry = (label, target)
        if entry not in self.refs:
            self.refs.append(entry)
        return f"[{self.refs.index(entry) + 1}]"

    def source(self, lesson):
        return self.cite(f"缠中说禅：《教你炒股票{int(lesson)}》，本地整理本 {lesson}.md", f"../../references/chan_theory/{lesson}.md")

    def quote(self, lesson, start, stop, title, note):
        source = ROOT / f"references/chan_theory/{lesson}.md"
        lines = source.read_text().splitlines()
        raw = "\n".join(lines[start - 1:stop])
        # Remove only HTML span styling, retain attribution/content and Markdown.
        normalized = re.sub(r"</?span\b[^>]*>", "", raw)
        def image_link(match):
            old = match.group(2)
            src = source.parent / old
            assert src.is_file(), src
            name = f"lesson{lesson}-{src.name}"
            dest = self.asset / name
            self.asset.mkdir(exist_ok=True)
            data = src.read_bytes()
            if dest.exists():
                assert dest.read_bytes() == data
            else:
                dest.write_bytes(data)
            self.images.append({"source": str(src.relative_to(ROOT)), "copy": str(dest.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "viewed": True})
            return f"![{match.group(1)}]({self.path.stem}/{name})"
        normalized = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_link, normalized)
        self.quotes.append({"lesson": lesson, "start_line": start, "end_line": stop, "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(), "normalization": "Remove span markup only; rewrite copied figure paths; retain source wording/annotations."})
        quoted = "\n".join("> " + line if line else ">" for line in normalized.splitlines())
        return f"### {title}\n\n{note} 本快照 L{start}–{stop}。{self.source(lesson)}\n\n{quoted}\n\n"

    def write(self, text):
        before = self.path.read_bytes()
        head = before.decode().split("## Appendix A —", 1)[0]
        bibliography = "## References\n\n" + "\n\n".join(f"[{i}] [{label}]({target})。" for i, (label, target) in enumerate(self.refs, 1)) + "\n"
        content = head + text.rstrip() + "\n\n" + bibliography
        stamp = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
        backup = FOLDER / "backups" / f"{self.path.stem}__{stamp}.md"
        with backup.open("xb") as stream:
            stream.write(before)
        assert backup.read_bytes() == before
        assert self.path.read_bytes() == before, "Concurrent memo change detected"
        self.path.write_text(content)
        assert self.path.read_text().split("## Appendix A —", 1)[0] == head
        for target in re.findall(r"\]\(([^)]+)\)", content):
            assert (FOLDER / target).is_file(), target
        records.append({"memo": str(self.path.relative_to(ROOT)), "backup": str(backup.relative_to(ROOT)), "main_sections_preserved": True, "quotes": self.quotes, "images": self.images, "references": len(self.refs), "checks": "All extracted quotes created directly from stated source ranges; all local links exist, copied image bytes/hash match; every selected source image viewed before copy. No CC execution."})


def intro(concept, matching):
    return f"""## Appendix A — Quotes from ChanOriginal

本附录研究{concept}。2026-11-09 对全部 108 篇编号课程（001–108）作关键词检索；目录共 109 个 Markdown 文件，另一个是 README，不能计为课程。本概念关键词命中 {matching} 篇，随后阅读下列候选段落及其上下文；不是逐字通读全部课程。检索清单见[批次证据](../../artifacts/mas/memo018-appendix-study/corpus_keyword_inventory.json)。

引文来自本地带批注整理本，保留原措辞、Markdown 强调、问答与“娇注”；仅去除 HTML span 样式并重写复制图片的相对路径。“娇注”、未署名“注”和图上其他作者署名不当作缠中说禅正文。图是整理本所收录的原文件，未认证为作者首发配图。原文论断不等于 TDS 已验证的结果。

"""


s7 = Study("memoWX_024_Chan_beichi.md")
text = intro("趋势背驰、盘整背驰、背驰段与多级别定位，包含早期力度定义的历史语境", 99)
text += s7.quote("037", 16, 24, "A.1 — 第37课：完整的 a+A+b+B+c 前提与 c 内部结构", "核心连续正文；保留级别、趋势、新极值、比较段和内部结构的全部条件，括号内娇注仍属整理者。")
text += "阅读提示（非引文）：这里比较进入最后中枢 B 的 b 与离开 B 的 c；a 是整个趋势的起始背景。不能把任意两段价格新高／新低加指标减弱直接命名为同级趋势背驰。\n\n"
text += s7.quote("024", 14, 44, "A.2 — 第24课：MACD 辅助判断的连续论述", "正文连续保留方法定位、级别、A/B/C 前提、历史例子、盘整分支及局限性；本课 A/B/C 记号与第37课 a/A/b/B/c 不能机械逐字对应。")
text += "图像缺口：本地024.md 的 images 为空，正文却要求查看人寿5分钟、上海5分钟、万科15分钟图。对应图没有保存在该课文件中；保留日期／时段文字，未以其他行情图代替。第37课 L32–42 的编者“例图”“下图”提示也没有对应嵌入图片。\n\n"
text += s7.quote("027", 14, 44, "A.3 — 第27课：背驰段、盘整背驰与逐级收缩", "连续正文，保留第一个中枢／趋势的边界、两个盘整可比较力度、背驰段命名与区间套的有限精度。原文中比例数字与历史推断照录，不是本次统计。")
text += "图像缺口：027.md 也没有嵌入图；L26 的季度图和 L48–52 的个股图示提示不能视为已取得的图片证据。\n\n"
text += s7.quote("029", 33, 63, "A.4 — 第29课：背驰后转折的三种分类与历史算例图", "正文连续保留定理、三种结果、最弱反弹与盘整背驰的区分，以及2007-02-06后的实际例子。文中的“注”“娇注”和图片上的说明独立于作者正文。")
text += "图像核对：图中可见最后一个5分中枢、其后1分走势与后续30分中枢，图上另有“禅师分段前……”的补充说明，不能将所有后加标记都认作首发标注。第29课 L41 对离开段级别的措辞与第37课 L20–24 的 c 条件须结合分解对象／发表语境继续核对，本附录保留差异，未改写成一条统一程序规则。\n\n"
text += s7.quote("015", 44, 58, "A.5 — 第15课：早期均线力度定义及其历史边界", "早期正文，保留均线“吻”、总面积／平均力度及判断时滞。末尾娇注明确提醒早期趋势口径与后来的中枢口径不同。")
text += "阅读提示（非引文）：本段用于追溯“力度”概念，不把均线面积公式直接设为 TDS 背驰默认算法。前文配图015/image001.gif对应早期高低点／盘整说明，并含已标明错误；未将其挪用为后期中枢背驰图。\n\n"
text += s7.quote("017", 247, 255, "A.6 — 第17课答疑：结构先于指标", "读者问题与作者答复成组保留；不是正文定义的新公式。")
text += s7.quote("064", 39, 57, "A.7 — 第64课：比较对象错误、未完成结构与实际图示", "连续保留108–109的线段上下文、110–111两个红箭头的解释及两张后续图；此处笔／线段内容是理解背驰段尚未完成的前提。夹注和张大山习作均另属整理资料。")
text += "图像核对：064/image001.jpg含104–111编号、红绿箭头及MACD；image002.gif保留更长历史及矩形标记；image003.jpg署“张大山习作”，仅作奔走型结构的整理者示意。第64课先前L33的image021是同段行情更长视窗，已查看，但本条从L39开始且原图001/002已覆盖论证所指对象，没有另加重复视窗。\n\n"
text += s7.quote("064", 369, 373, "A.8 — 第64课答疑：预先判断不等于结构确认", "保留作者标签、日期与完整问题／答复；与上文主要图示相互补充。")
text += s7.quote("064", 539, 543, "A.9 — 第64课答疑：背驰段与背驰的区别", "读者质疑大级别柱子缩小而价格继续新高，作者要求区分背驰段与背驰；保留完整问答而不以指标阈值补写答案。")
text += s7.quote("037", 82, 86, "A.10 — 第37课答疑：盘整背驰的方法边界", "保留答复所针对的问题及读者提问中的娇注。")
text += """### A.11 — 后续定义／算法研究需要保留的问题

- 固定研究级别、同级中枢身份和比较的两段来源；价格幅度、用时、均线面积、MACD面积及内部结构不是可随意互换的单一数值。
- 区分已进入背驰段、MACD辅助信号、次级别定位与本级结构完成；第24课的“已出现面积乘2”是正文中的经验性辅助说法，尚无本项目确认的实时终止／误差规则。
- 盘整背驰可转化为中枢外的第三类点；与趋势背驰后转折的三种分类分别保存。缺少前提时不能仅凭一张柱状图补全结论。
- 第15课均线语境与第37课中枢语境、第29课与37课关于比较段的措辞差异保留为研究问题，不能默默选一套当作已确认规范。

## Appendix B — Notes from CC's implementation

### B.1 — 实现证据缺口：配对研究尚未完成

"""
snapshot = s7.cite("CC 当前选定源码快照与逐文件哈希（HEAD 374268381a3eaeee4d220e67d63364b3907405f4）", CC + "/manifest.json")
search = s7.cite("S7/S8 检测器全 src/cc 检索记录（80个Python文件、路径与哈希）", "../../artifacts/mas/memo018-appendix-study/s7-s8/cc_detector_search.json")
text += f"2026-11-09 只读检查本机 CC 当前干净工作树，保存实际源码快照，版本与2026-11-08网站快照分开。{snapshot} 对 `src/cc` 全部80个Python文件作 `beichi|divergen|背驰|背弛|macd` 检索，命中0处；文件清单和哈希已保留。{search} 此结论限于本次工作树／Python源码，不能扩展成整个 CC 历史从未实现背驰。\n\n"
engine = s7.cite("CC engine.py：ChanEngine.get_level_zoushi_result/get_zoushis，L467–477", CC + "/src/cc/algo/engine.py")
models = s7.cite("CC models.py：CompletedZouShi，L351–414", CC + "/src/cc/algo/models.py")
text += f"""### B.2 — 已有的上游结构输出

`ChanEngine.get_zoushis(level)` 在 L474–477 取对应结构级别构建结果，再返回 `result.zoushis` 的列表拷贝；该调用没有比较力度或发出背驰事件。{engine}

```python
result = self.get_level_zoushi_result(level)
return list(result.zoushis)
```

`CompletedZouShi` 保存级别、来源、类型、趋势方向、端点、成员ID、中枢ID及 forming/frozen 的关闭证据。L369–406 的校验涉及非空成员、位置／时间顺序、类型与方向、关闭证据约束；这些校验没有计算MACD或背驰强弱。类名中的 `Completed` 也不能抹掉字段实际允许 forming 的事实。{models}

这些对象可能为以后的背驰研究提供来源与状态事实，但现有接口没有规定取哪个 b/c、如何比较力度、何时确认背驰或怎样回撤事件。它们与 TDS memo009 所提 Beichi 系列也不是已接通的同一接口。

### B.3 — 缺少的执行步骤与检查

| 项目 | 本次可核对的证据 | 状态 |
|---|---|---|
| 中枢、走势及形成／冻结状态 | 实际结构模型与引擎取数代码 | 已静态检查 |
| 背驰输入约束、b/c选择及方向／级别检查 | 未找到检测器 | 待取得源码 |
| 力度计算、MACD预热及数值单位 | 未找到计算实现 | 待取得源码 |
| 背驰段→确认点、实时更新／撤销 | 未找到事件状态机 | 待取得源码 |
| 来源成员、事件锚点、稳定性与规则解释 | 上游有trace，不等于背驰已有trace | 待取得源码 |
| 连续数值逐步推演及金融图 | 缺少可追踪的背驰执行分支 | 配对研究尚缺此项 |

仅执行了文件／哈希／文本／语法层检查，没有导入或运行 CC，没有生成所谓 CC 背驰测试结果。附录 A 是已整理的理论证据，附录 B 当前记录源码边界与待补证据；尚不能据此宣布完整的双来源研究或背驰算法完成。
"""
s7.write(text)

s8 = Study("memoWX_025_Chan_buysellpoint.md")
text = intro("同一级别第一、二、三类买卖点，兼顾其多级别定位、重合、小转大和中枢关系", 97)
text += s8.quote("017", 51, 79, "A.1 — 第17课：第一／二类点与走势完成的连续论证", "正文连续保留盘整／趋势定义、完成／分解前提、第一类与第一次回调的第二类点、次级别第一类点及转折定律。")
text += "阅读提示（非引文）：这里的“第一次次级别回调”不是任意两根K线的回落；第53课对小级别转大级别时第二类点的补充见A.4。\n\n"
text += s8.quote("020", 62, 84, "A.2 — 第20课：中枢边界、第三类点、首次回试与原配图", "连续正文及全部五张所嵌入的整理本图片，保留公式、次级别离开／回试、ZG/ZD、第一次和其后两种走向；“娇注”属于整理者。")
text += "图像核对：image005是中枢指标／关系的整理示意；image001/002是北辰30分／日线、image003/004是工行30分／日线，均能看到第三类买点标注。它们并非本次运行图。正文同时举000803第三类卖点，但这五图没有该股对应图；不补造卖点行情。图和正文的边界取等／不触及措辞保留，源码未找到前不擅定浮点容差或等号处理。\n\n"
text += s8.quote("018", 50, 66, "A.2 补充 — 第18课：中枢维持／破坏及离开回抽的组合", "连续保留中枢定理一、二到三的推导与三种组合原话；后面第92课的具体解盘按其自身分解语境阅读，差异不由整理者代为抹平。")
text += s8.quote("021", 16, 40, "A.3 — 第21课：按中枢关系分类及第二／三类重合", "连续保留转折／延续、中枢上下、三个类别的分工、第二类点位置及第二／第三类重合条件。")
text += s8.quote("021", 52, 56, "A.3 补充 — 第21课：完备性定理的作者表述", "原文论断，未把后面的网络选载或读者思考题答案并入作者证明。")
text += s8.quote("053", 16, 36, "A.4 — 第53课：观察级别、三类点与小转大补充", "本课连续正文到操作讨论结束，保留观察级别与次级别的压缩、盘整背驰、第一类点例外、第二类补充和第三类结束中枢。L38以后为另外的说明／转载，未混入此段。")
text += "归属核对：053.md L48–76 的“转载／思考贴9”及2009年整理讨论不是2007年第53课正文；本附录引用第二类点的小转大说明来自正文L30，没有把后来的转载解释代成作者结论。第二类点因此不能被程序限定为“同级第一类点必须已出现”。\n\n"
text += s8.quote("037", 130, 134, "A.5 — 第37课答疑：低级别第一类点与盘整结束的确认", "完整读者提问及作者答复；保留用户对次级别回抽／盘整延伸的疑问，答复没有提供通用预测软件。")
text += s8.quote("036", 62, 66, "A.6 — 第36课答疑：回试盘整的 A/C 比较与内部背驰", "完整问答，补充第37课答疑所涉及的次级别定位；提问中的娇注保留身份。")
text += s8.quote("092", 210, 218, "A.7 — 第92课解盘：次级别趋势／盘整两种离开路径", "作者解盘连续三项分类与对应行情图；其中第二种明确说离开只是盘整。此处是具体当下分析，未将其泛化为任意盘整+盘整组合均成立。")
text += "图像核对：原图image024绘有三类分解路径与实际后续线；图上补画和结果展示不等于当时每个节点均已确认。此例与第18课早期组合枚举的关系仍需在定义阶段核对，不能让编者转载替代原始语境。\n\n"
text += s8.quote("086", 27, 37, "A.8 — 第86课整理本图页：大级别结构中的小级别点", "本地该课开头以图为主，六张图全部查看后原字节复制。前五张图署“张大山习作”，是整理本所收的解释图，不能认证为缠中说禅首发原图；第六张为铜陵有色行情标记。")
text += "图页导读（非引文）：图001/002分别讨论小级别第三类卖点相对大级别中枢上移／震荡的意义；003/004画大买点后的较小结构与后续买点；005把大中枢内的小买卖点单列；006的行情图标有“1买”“3买类2买”，图中文字是来源标记，尚未逐笔核验其规则。多级别同屏不意味着各标记属于同一观察级别或强制按1→2→3排序。\n\n"
text += """### A.9 — 后续定义／算法研究需要保留的问题

- 各事件必须带同一解释下的级别、买／卖方向、类别与相关中枢／走势；不能将图形外观相似直接当作同级买卖点。
- 第二类与第三类可能重合；小转大时可没有该级别第一类点。存储是否允许同一锚点多个类别，须另行设计，不能因现有类别字段而删掉原文情况。
- 第三类点要求适当级别的离开及第一次回试；原文“不跌破／不升破”与“不触及”的操作措辞、等号、容差和实时确认时点仍待针对性核对。
- 第三类之后可能中枢上移或形成更大级别盘整；“出现三买”不能替代对后续路径的实际确认。
- 第92课的具体盘整离开示例、第37课的走势分解语境与第53课转载中的疑问分别保留来源身份。定义阶段再统一适用条件，未在此形成默认实现约定。

## Appendix B — Notes from CC's implementation

### B.1 — 当前配对研究缺少买卖点检测器

"""
snapshot = s8.cite("CC 当前选定源码快照与逐文件哈希（HEAD 374268381a3eaeee4d220e67d63364b3907405f4）", CC + "/manifest.json")
search = s8.cite("S7/S8 检测器全 src/cc 检索记录（80个Python文件）", "../../artifacts/mas/memo018-appendix-study/s7-s8/cc_detector_search.json")
text += f"2026-11-09 只读检查并保存当前 CC 干净工作树的选定源码，HEAD 与早先网站版分别标明。{snapshot} 全部80个Python源码文件的买卖点词汇／常用标识检索命中4处，分别是接口范围说明、API占位函数及通用通知字段；没有找到可供追踪第一／二／三类点的检测函数。{search}\n\n"
protocol = s8.cite("CC protocols.py：阶段与输出边界，L9–17及查询接口", CC + "/src/cc/algo/protocols.py")
api = s8.cite("CC udf.py：UDFMarks L142–154与marks L527–536", CC + "/src/cc/api/routes/udf.py")
notify = s8.cite("CC notify/models.py：NotifyLevel/NotifyMessage，L10–28", CC + "/src/cc/notify/models.py")
engine = s8.cite("CC engine.py：结构查询 L467–477", CC + "/src/cc/algo/engine.py")
text += f"""### B.2 — 源码逐处核对：接口说明、空标记与通知字段

1. `ChanEngineProtocol` 文件L16–17声明当前引擎不产买卖点信号；其查询接口返回分型、笔、线段、中枢、走势等结构。声明可指示阶段意图，仍须检查具体函数。{protocol}
2. `udf.py` 的 `/marks` 函数L527–536接收symbol、resolution和时间区间，仅把参数赋给 `_`，然后构造空 `UDFMarks()`；它没有调用类别判断器。文档字符串写着“阶段5起接通”，而执行体仍为空占位，不能用注释替代实际行为。{api}

```python
_ = (symbol, resolution, from_, to)
return UDFMarks()
```

3. `NotifyLevel` 含 `"buy_sell"`，`NotifyMessage.payload` 是可为空的通用字典。字段和注释表示通知容器的设计用途，没有从走势／背驰生成一、二、三类点的判断分支，也没有类别、确认或撤销状态机。{notify}
4. `ChanEngine.get_zoushis` 返回上游结构列表，源码没有在这个出口生成点位事件。它可以提供未来研究所需的成员、级别、时间和状态事实，但不能据此反推出已实现的买卖点规则。{engine}

### B.3 — 证据边界与下一步需要的源码

| 需要解释的步骤 | 当前源码可核对什么 | 未取得的证据 |
|---|---|---|
| 第一类点 | 可取走势／中枢对象 | 背驰检测、方向反转与确认锚点 |
| 第二类点 | 上游来源与形成／冻结字段 | 第一次回试、小转大分支及类别条件 |
| 第三类点 | 中枢边界与结构查询 | 离开／首次回试级别验证、取等与无效化规则 |
| 同点多类别 | 通用通知载荷占位 | 类别重合的实际数据结构与去重策略 |
| 实时增量与修订 | 上游具有末端更新接口 | 买卖点确认／撤销／重算范围与稳定ID |
| 数值逐步推演／金融图 | 已有来源理论图 | 买卖点可执行分支及可验证的CC运行样本 |

配对研究尚未完成：附录 A 已整理理论及原文件图示，附录 B 当前是代码边界与实现缺口记录。后续取得实际检测器及其调用链后，再按输入、状态、分支、更新、输出补充连续数值手工推演与图示。本次仅静态读源码及核对文件，没有运行 CC、没有将图上标签当作测试结果。
"""
s8.write(text)
(ARTIFACT / "evidence.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"memos": [r["memo"] for r in records], "quote_blocks": [len(r["quotes"]) for r in records], "image_copies": [len({im["copy"] for im in r["images"]}) for r in records]}, ensure_ascii=False))
