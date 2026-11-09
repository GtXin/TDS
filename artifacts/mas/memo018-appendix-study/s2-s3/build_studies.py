"""Author S2/S3 appendices from preserved sources; no CC imports/execution."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import hashlib
import html
import json
import os
import re
import shutil

ROOT = Path(__file__).resolve().parents[4]
ART = Path(__file__).resolve().parent
CC = "../../references/cc_algo/local_snapshot/374268381a3e"
MEMOS = ROOT / "docs/memo"
os.environ.setdefault("MPLCONFIGDIR", "/tmp/tds-memo018-s2-s3-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

source_records: list[dict] = []
image_records: list[dict] = []


def normalize(s: str) -> str:
    s = re.sub(r"</?span\b[^>]*>", "", s)
    s = html.unescape(s)
    # Preserve literal comparison formulas safely in Obsidian Markdown.
    s = re.sub(r"(?<![A-Za-z0-9_`])(?:gn[<>]=?gn-1|dn[<>]=?dn-1|D1[<>]=D2|G1[<>]=G2)(?![A-Za-z0-9_`])", lambda m: "`" + m[0] + "`", s)
    s = re.sub(r"\[(?:di,gi|maxdi,maxgi|mindi,mingi)\]", lambda m: "`" + m[0] + "`", s)
    return s.replace("==", r"\=\=")


def excerpt(lesson: str, first: int, last: int, stem: str) -> str:
    p = ROOT / "references/chan_theory" / f"{lesson}.md"
    raw = "\n".join(p.read_text().splitlines()[first - 1:last])
    text = normalize(raw)
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        src = p.parent / target
        dst = MEMOS / stem / f"lesson{lesson}-{Path(target).name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert dst.read_bytes() == src.read_bytes()
        else:
            shutil.copy2(src, dst)
        image_records.append({"source": str(src.relative_to(ROOT)), "copy": str(dst.relative_to(ROOT)), "sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "viewed": True})
        text = text.replace(f"({target})", f"({stem}/{dst.name})")
    source_records.append({"memo": stem, "lesson": lesson, "first": first, "last": last, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "normalized_excerpt": text})
    return "\n".join("> " + line if line else ">" for line in text.splitlines())


def copy_figure(lesson: str, name: str, stem: str) -> str:
    src = ROOT / "references/chan_theory" / lesson / name
    dst = MEMOS / stem / f"lesson{lesson}-{name}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)
    assert src.read_bytes() == dst.read_bytes()
    image_records.append({"source": str(src.relative_to(ROOT)), "copy": str(dst.relative_to(ROOT)), "sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "viewed": True})
    return f"{stem}/{dst.name}"


def draw_candles(ax, values):
    for i, (low, high) in enumerate(values):
        op = low + .3 * (high - low)
        close = low + .7 * (high - low)
        if i % 2:
            op, close = close, op
        color = "#bd3d41" if close > op else "#248075"
        ax.vlines(i, low, high, color=color, lw=1.3)
        ax.add_patch(Rectangle((i - .22, min(op, close)), .44, abs(close - op), facecolor=color, edgecolor=color, alpha=.8))
    ax.grid(axis="y", alpha=.22)
    ax.set_ylabel("Price")


def raw_fractals(values):
    """Arithmetic cross-check of the displayed manual comparisons, not CC execution."""
    out = []
    for i in range(1, len(values) - 1):
        l, h = values[i]
        a, c = values[i - 1], values[i + 1]
        if h > a[1] and h > c[1] and l > a[0] and l > c[0]:
            out.append((i, "T", h))
        elif h < a[1] and h < c[1] and l < a[0] and l < c[0]:
            out.append((i, "B", l))
    return out


def charts():
    s2 = [(8, 11), (6, 9), (9, 12), (7, 10), (10, 13), (8, 11), (11, 14), (13, 16), (10, 13)]
    revised = s2[:-1] + [(14, 17), (12, 15)]
    assert raw_fractals(s2) == [(1, "B", 6), (2, "T", 12), (3, "B", 7), (4, "T", 13), (5, "B", 8), (7, "T", 16)]
    assert raw_fractals(revised) == raw_fractals(s2)[:-1] + [(8, "T", 17)]
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, sharey=True)
    for ax, values, title in zip(axes, [s2, revised], ["A. Base snapshot: all raw fractal candidates (overlapping windows retained)", "B. Revise R8, then append R9: T7 disappears and T8 appears"]):
        draw_candles(ax, values)
        for i, kind, price in raw_fractals(values):
            ax.scatter(i, price, marker="v" if kind == "T" else "^", s=75, color="#6445a5", zorder=4)
            ax.annotate(f"{kind}{i}", (i, price), xytext=(0, 9 if kind == "T" else -16), textcoords="offset points", ha="center", fontsize=10)
        ax.set_title(title, loc="left", fontsize=11)
        ax.set_xlim(-.6, 9.6)
        ax.set_ylim(4.2, 19)
    axes[-1].set_xticks(range(10), [f"R{i}=M{i}" for i in range(10)])
    axes[-1].set_xlabel("Ordered source index; each merged unit has one raw member")
    fig.suptitle("S2 / Code-derived manual teaching trace — not CC runtime output", fontsize=13)
    fig.text(.5, .015, "Synthetic O=L+0.3(H-L), C=L+0.7(H-L), alternating colors; detection uses H/L only.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .95))
    fig.savefig(MEMOS / "memoWX_019_Chan_fenxing" / "cc-fractal-manual-trace.png", dpi=150)
    plt.close(fig)

    s3 = [(8,11),(6,9),(9,12),(11,14),(13,16),(12,15),(10,13),(8,11),(5,8),(7,10),(10,13),(12,15),(14,17),(12,15),(11,14.5),(10,14),(12,18),(8,12),(6,10),(4,8),(3,7),(5,9)]
    revision = s3[:-1] + [(2,6)]
    assert raw_fractals(s3) == [(1,"B",6),(4,"T",16),(8,"B",5),(12,"T",17),(15,"B",10),(16,"T",18),(20,"B",3)]
    assert raw_fractals(revision) == raw_fractals(s3)[:-1]
    assert all(max(a[0],b[0]) <= min(a[1],b[1]) for a,b in zip(s3,s3[1:]))  # no price gap
    # Explicit arithmetic behind the standard gates and tail extension.
    assert 4-1 < 4 and 8-4 == 4 and 12-8 == 4 and 15-12 < 4 and 20-16 == 4
    assert 16 > max(s3[7][1],s3[8][1]) and s3[8][0] < min(s3[4][0],s3[5][0])
    assert 5 < min(s3[11][0],s3[12][0]) and 17 > max(s3[8][1],s3[9][1])
    assert 18 > 17
    assert 18 > max(s3[19][1],s3[20][1]) and 3 < min(s3[16][0],s3[17][0])
    assert min(v[0] for v in s3[5:8]) >= 5
    assert max(v[1] for v in s3[9:12]) <= 17
    assert min(v[0] for v in s3[17:20]) >= 3
    base_pens = [(4,16),(8,5),(16,18),(20,3)]
    revised_pens = base_pens[:-1]
    fig, axes = plt.subplots(2, 1, figsize=(13.2, 8), sharex=True, sharey=True)
    for ax, values, pens, title in zip(axes, [s3, revision], [base_pens, revised_pens], ["A. Base snapshot: first DOWN 4→8; UP extends 8→12 to 8→16; then DOWN 16→20", "B. Same R21 revised to [2,6]: B20 vanishes; re-derivation has no 16→20 pen"]):
        draw_candles(ax, values)
        ax.plot([p[0] for p in pens], [p[1] for p in pens], color="#1c4b8a", lw=2.2, marker="o", zorder=4)
        for i, kind, price in raw_fractals(values):
            ax.annotate(f"{kind}{i}", (i, price), xytext=(0, 9 if kind=="T" else -15), textcoords="offset points", ha="center", fontsize=9)
        ax.set_title(title, loc="left", fontsize=10)
        ax.set_ylim(.5,21)
        ax.set_xlim(-.7,21.7)
    axes[0].plot([8,12],[5,17],ls="--",color="#b46a15",lw=1.6,label="Earlier endpoint T12, replaced by T16")
    axes[0].legend(loc="upper left",fontsize=9)
    axes[-1].set_xticks(range(22), [f"{i}" for i in range(22)])
    axes[-1].set_xlabel("Ordered raw/merged singleton index i (Ri=Mi)")
    fig.suptitle("S3 / CC default bi_5k manual teaching trace — not CC runtime output",fontsize=13)
    fig.text(.5,.015,"H/L are specified teaching inputs. Synthetic open/close use 30%/70% of each range; they do not drive the rule.",ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.95))
    fig.savefig(MEMOS / "memoWX_020_Chan_bi" / "cc-stroke-manual-trace.png",dpi=150)
    plt.close(fig)
    (ART / "manual-example-inputs.json").write_text(json.dumps({"nature":"Manual code-derived examples; arithmetic assertions only, no CC execution", "s2_base":s2,"s2_revised_then_appended":revised,"s3_base":s3,"s3_tail_revision":revision},indent=2)+"\n")


def write_memo(stem: str, appendix: str):
    p=MEMOS/f"{stem}.md"
    old=p.read_bytes()
    head=old.decode().split("## Appendix A —",1)[0]
    assert "## 005 — Gaps and Pending Items" in head
    stamp=datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
    backup=MEMOS/"backups"/f"{stem}__{stamp}.md"
    with backup.open("xb") as f:f.write(old)
    assert backup.read_bytes()==old
    p.write_text(head+appendix)
    assert p.read_bytes().split(b"## Appendix A",1)[0]==old.split(b"## Appendix A",1)[0]
    return str(backup.relative_to(ROOT))


def main():
    s2="memoWX_019_Chan_fenxing"
    s3="memoWX_020_Chan_bi"
    for stem in [s2,s3]:(MEMOS/stem).mkdir(exist_ok=True)
    intro="本附录以本地108篇编号课程（001–108，另有README）作关键词全库扫描，再连续阅读候选段落；并非逐字通读108课或查看全部图片。检索词与命中记录见[批次证据](../../artifacts/mas/memo018-appendix-study/s2-s3/corpus-keyword-hits.txt)。引文保留正文、读者问题、作者答复及整理本夹注的区别；仅去除HTML样式、为比较公式加行内代码及转义问答分隔符，未改原文措辞。课号文件是带整理材料的本地副本，不宣称已认证作者首发版本。\n\n"
    a2="## Appendix A — Quotes from ChanOriginal\n\n"+intro
    a2+="### A.1 — 第62课：连续定义、图形与包含处理的先后\n\n正文28–42行。[1] 此处保留从三K线分型到笔及包含处理的连续论述；笔、线段的出现是上下文，不把它们混成分型识别条件。原图1/2给顶底，3–5给成笔间隔，6/7给包含及三K线分类；原文两次使用同一图版，均保留。\n\n"+excerpt("062",28,42,s2)+"\n\n"
    a2+="### A.2 — 第65课：包含顺序、既有方向与已形成K线\n\n正文29–45行。[2] 连续保留包含关系不传递、按时间逐次处理、方向判定的非包含前提，以及分型可见性的论述。`娇注`和“注：应去掉等于号”属整理本注语，不能当成独立作者答复；这里不据此决定数据窗口开头的初始化。\n\n"+excerpt("065",29,45,s2)+"\n\n"
    a2+="### A.3 — 第75课答疑：相等应先归入包含\n\n作者答疑72–80行；保留读者问题及署名时间。[3]\n\n"+excerpt("075",72,80,s2)+"\n\n补充同课120–124行的完整问题与作者答复：包含前提消除了通常的相等比较，但作者同时区分绝对相等与测量相等，并给出一字涨停无法形成分型的例子。[3]\n\n"+excerpt("075",120,124,s2)+"\n\n"
    a2+="### A.4 — 第77课：用于笔的有效分型与结合律\n\n正文43–49行。[4] 原文要求结合律和一顶一底；附录B将明确区分CC检测器的全部原始候选与笔层最终取舍，不能因候选窗口重叠就宣称原文允许有效端点任意共用K线。\n\n"+excerpt("077",43,49,s2)+"\n\n"
    a2+="### A.5 — 第79课：形成分型不等于延续成笔\n\n正文81–107行，连续保留不同周期、包含与无包含、形成笔与中继的五个原例及图片。[5] 均线操作是作者辅助判断上下文，不是下列纯几何检测器的输入，也不是本批次新增交易规则。\n\n"+excerpt("079",81,107,s2)+"\n\n"
    a2+="### A.6 — 第82课：三次较量、力度与中继\n\n正文26–54行。[6] 保留“分型不是分形”、三根K线的心理解释及两个原图；原文“几乎100%”等措辞仅是作者论述，本附录未作统计验证。36行`娇注`以及48行归属未明的“注”按整理本标识保留，不升级为作者规则。\n\n"+excerpt("082",26,54,s2)+"\n\n"
    a2+=f'''## Appendix B — Notes from CC's implementation

### B.1 — 代码版本、输入与本层边界

本次主要依据实际CC仓库的只读快照：HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，2026-11-09复制，捕获时工作区clean；哈希与原路径在快照清单。[7] 这与既存网站旧版本`b1348795…`分开保存，没有把网站说明或注释当作运行证据，也未导入、执行CC代码。

可执行入口是`detect_fenxings(merged)`（fenxing.py:26–62）。它接收已消除包含的有序合并单元列表，输出**所有原始顶／底分型候选**；不做成笔距离、同型取舍、有效端点或买卖点判断。[8] 这一区分来自实际循环：满足条件便直接`append`，不查看上一条输出。因此候选窗口可以重叠；与A.4关于最终有效结构的结合律要求不是同一输出层次。

该函数没有校验输入排序、周期一致、OHLC合法性或确已去包含；这些是调用链的前提。少于3个单元时循环为空，直接返回空列表。不能把空列表一概解释为“数据已足够且市场没有转折”。

### B.2 — 三根比较与记录构造

1. 只遍历中心下标`i=1…len(merged)-2`，取`a=merged[i-1]、b=merged[i]、c=merged[i+1]`；两端没有完整窗口，不产生候选（26–30行）。
2. 顶要求`b.high>a.high`、`b.high>c.high`、`b.low>a.low`、`b.low>c.low`全部成立；底同时反向严格比较四项。四项之一相等即不能走该分支。两种都不成立便跳过（31–38行）。这是CC明确使用严格比较的实现事实；A.3说明有效去包含序列中通常不应留下相邻等边。
3. 输出的`index`是**中心合并单元下标**，`timestamp=b.start_ts`是中心代表时间，不是右侧出现后的确认时间。该对象没有另存`confirmed_at`字段（51–60行；models.py:146–161）。[8][9]
4. `high=max(a.high,b.high,c.high)`、`low=min(a.low,b.low,c.low)`是整个三根窗口的外包络。顶的high等于中心高点，但low通常不是中心low；底则low等于中心低点，high通常不是中心high。不能把两字段误读成中心K线自己的价格范围。
5. `trace`保存算法卡、顶／底rule ID、**含两端**的合并范围`[i-1,i+1]`和`a.start_ts…c.end_ts`原始来源时间包络。稳定显示ID为`fx-{{timestamp}}`，不是本项目memo009拟议的整数ID方案。[8][9]

这是一遍纯函数扫描，没有持久候选或回退栈。同型候选不被去重，也没有“前一个顶已经确认就永不改变”的承诺。

### B.3 — 一组连续数值推演：全部候选而非已成笔端点

以下为**手工代码推演**。原始`R0…R8`与合并`M0…M8`一一对应，来源成员均为单根`{{Ri}}`，已无相邻包含；只给定`[low,high]`，周期相同，代表时间依次`t0…t8`。未运行CC检测器。

| i | Mi的[low,high] | 中心窗口判断 | 候选／价格 | 输出窗口high/low；来源 |
|---|---|---|---|---|
| 0 | [8,11] | 无左邻 | 无 | — |
| 1 | [6,9] | 6<8、7? 此轮右邻M2.low=9；9<11、12 | 底B1，价格6 | 12/6；R0–R2 |
| 2 | [9,12] | 12>9、10；9>6、7 | 顶T2，价格12 | 12/6；R1–R3 |
| 3 | [7,10] | 10<12、13；7<9、10 | 底B3，价格7 | 13/7；R2–R4 |
| 4 | [10,13] | 13>10、11；10>7、8 | 顶T4，价格13 | 13/7；R3–R5 |
| 5 | [8,11] | 11<13、14；8<10、11 | 底B5，价格8 | 14/8；R4–R6 |
| 6 | [11,14] | 高低都位于M5与M7之间 | 无 | — |
| 7 | [13,16] | 16>14、13；13>11、10 | 顶T7，价格16 | 16/10；R6–R8 |
| 8 | [10,13] | 此快照无右邻 | 无 | — |

表中B1的完整四项是`6<8`、`6<9`、`9<11`、`9<12`；每个候选要四项同时成立，不能只按三根high排名。B1/T2等窗口相互重叠仍被原始检测器输出；是否可以作为笔端点须再进入memo020所述取舍及门禁。

![分型手工代码推演：原始K线与全部候选，以及末根修订后候选移动](memoWX_019_Chan_fenxing/cc-fractal-manual-trace.png)

图按同一来源轴和价格刻度绘制两次快照；本例原始与合并单元重合。蜡烛open/close仅为教学构造：`O=L+0.3(H-L)`、`C=L+0.7(H-L)`，奇数位置交换二者以便辨认，既非真实行情也不参与规则。紫色符号才是三根窗口的候选。

### B.4 — 相等、未闭合右端与末根修订

**相等边界（另一个输入场景）。** 向函数直接送入`[8,11]、[10,14]、[10,13]`，中间high虽最高，low与右邻相等，四项顶判断不全成立，也不构成底，故无输出。这里后两根存在包含，是刻意绕过上游前提的helper输入探针；合法流水线应先归并，不能把该三根说成已正确去包含的反例。

**同时间末根修订。** 主例中M8若从`[10,13]`修订为`[14,17]`，在`M6,M7,M8`中M7不再是共同极大，T7消失；此时M8仍在末端，不能单凭创新高就生成T8。再追加M9=`[12,15]`，M8满足顶的四项，才产生T8，价格17、窗口high/low为17/12、来源R7–R9。上图第二行合并展示修订后再追加的最终快照。

调用链由engine.py:244–270先替换同timestamp末根，经合并器回退／重加并增加版本；299–323行在版本变化后重新运行分型和笔派生。[10] 分型函数本身不负责这些回退操作。这里区分了几何位置t8与最早具备右侧信息t9；代码没有独立确认时间字段，不能用t8代替“当时已可知”。

### B.5 — 已核对的范围与未验证事项

- 静态核对：入口、四项严格比较、窗口包络、中心时间／下标、来源范围及引擎修订调用链；原文摘录按本地行区间生成并核对，已查看所用原图，图片复制哈希相同。
- 算术核对：图表脚本只对上述手算比较、候选列表及修订结果作独立断言，未调用CC函数。脚本与具体输入保存在[本批证据目录](../../artifacts/mas/memo018-appendix-study/s2-s3/)。
- 由循环可得：M个合并单元的一次检测时间O(M)，输出F个候选所需额外存储O(F)；这不等于合并／笔／引擎全链耗时。
- 尚未执行CC引擎、与原CC测试集比较、证明不同源数据／测量误差下等价，或决定TDS最终的有效分型／确认机制。正文000–005保持空白，本附录是证据而非已采纳的实现规范。

## References

[1] 缠中说禅. 教你炒股票62：分型、笔与线段. [本地整理本](../../references/chan_theory/062.md)，正文28–42行，图062/image001.jpg。

[2] 缠中说禅. 教你炒股票65：再说说分型、笔、线段. [本地整理本](../../references/chan_theory/065.md)，正文29–45行；内含标明的整理者注语。

[3] 缠中说禅. 教你炒股票75：逗庄家玩的一些杂史1. [本地整理本](../../references/chan_theory/075.md)，答疑72–80、120–124行。

[4] 缠中说禅. 教你炒股票77：一些概念的再分辨. [本地整理本](../../references/chan_theory/077.md)，正文43–49行。

[5] 缠中说禅. 教你炒股票79：分型的辅助操作与一些问题的再解答. [本地整理本](../../references/chan_theory/079.md)，正文81–107行，原图003–007。

[6] 缠中说禅. 教你炒股票82：分型结构的心理因素. [本地整理本](../../references/chan_theory/082.md)，正文26–54行，原图001／002。

[7] [CC实际仓库选定快照与来源说明]({CC}/README.md)，HEAD `374268381a3eaeee4d220e67d63364b3907405f4`；[逐文件哈希清单]({CC}/manifest.json)。

[8] CC. [fenxing.py]({CC}/src/cc/algo/fenxing.py)，26–62行，`detect_fenxings`完整可执行实现。

[9] CC. [models.py]({CC}/src/cc/algo/models.py)，123–161行，MergedKline与Fenxing字段／ID。

[10] CC. [engine.py]({CC}/src/cc/algo/engine.py)，244–270、299–323行，末根替换与版本缓存后的派生顺序。
'''
    # Keep the comparison ledger concise and unambiguous.
    a2=a2.replace("6<8、7? 此轮右邻M2.low=9；9<11、12", "6<8、9；9<11、12")
    a3="## Appendix A — Quotes from ChanOriginal\n\n"+intro
    a3+="### A.1 — 第62课：相邻顶底、结合律与老笔最小间隔\n\n正文28–42行。[1] 连续保留分型、笔、包含处理及上升／下降笔的上下文。原图3、4、5分别展示共用K线、无独立K线、具有独立K线的差别；相邻合并单元不等于原始K线根数。\n\n"+excerpt("062",28,42,s3)+"\n\n"
    a3+="### A.2 — 第65课：一顶一底与同型分型的取舍\n\n正文47–53行。[2] 原文先区分同型分型之间有没有其他顶底，后说明交替连接；不可只摘“忽略第一个”便改写为无条件删除任意较早分型。53行`娇注`为整理者注。\n\n"+excerpt("065",47,53,s3)+"\n\n"
    a3+="### A.3 — 第77课：有效端点、唯一性论证与完整三步划笔\n\n正文43–71行。[3] 这是老笔口径的连续论述，保留作者的唯一性论证，而非只摘最后三条步骤。对“相等的，都可以先保留”和后续同型选取须连读；55行“不低于”等措辞按本地原貌保留，没有代作者修订证明。\n\n"+excerpt("077",43,71,s3)+"\n\n"
    a3+="### A.4 — 第81课所收后续文章：新笔条件及同软件数据前提\n\n本地081.md还收有2007-09-18《忽闻台风可休市，聊赋七律说〈风灾〉》；以下连续取111–121行，不误标成第81课正文当日规则。[4] 117行`娇注`仍按整理者注标识；条件一的合并后不共用窗口，与条件二的不计包含原始根数是两种计数。\n\n"+excerpt("081",111,121,s3)+"\n\n"
    arrow=copy_figure("081","image004.jpg",s3)
    a3+=f"![081整理本中、风灾文章前的绿箭头示意图]({arrow})\n\n图来自同文件103行，位于上述文章之前，实际可见绿箭头及106／107标注，能帮助定位作者讨论的区域；整理本未把它直接嵌入117行之后，不能仅凭临近关系认证为作者该句的唯一配图。图中文字与小K线不足以独立核验原始根数；保留这一图文边界。\n\n"
    a3+="同文件161–171行作者答疑，连续保留提问与回答：新标准的动机是减少不同软件之间的微小数据差异，作者表示可以用新标准，并说明自己仍用同一软件和老标准。[4]\n\n"+excerpt("081",161,171,s3)+"\n\n"
    a3+="### A.5 — 第78课答疑：端点与更高顶的语境\n\n作者答疑256–260行。[5] 读者问题与“当然。顶上如果还有顶……”的回答一并保留；不把这个简短问答单独演绎为放弃一顶一底或距离前提的通用规则。\n\n"+excerpt("078",256,260,s3)+"\n\n"
    a3+=f'''## Appendix B — Notes from CC's implementation

### B.1 — 实际代码、版本与配置边界

本次依据CC实际仓库的只读快照，HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，2026-11-09复制，捕获时clean，来源与SHA-256已保存。[6] 不沿用旧网站快照的版本声明，不把CC项目变体写成缠论作者原话，也不据此替TDS选择口径。没有导入或执行CC代码。

`build_bis(merged,fenxings,raw_klines,cfg,profile_id,config_hash)`先`cfg.normalize()`，创建仅在本次调用存活的`_BiBuilder`，执行`run()`后`finish()`（bi.py:93–106）。输入同时需要合并单元、全部原始分型候选和原始K线：前者做几何／距离，原始K线用于缺口与极值原始位置计数。[7] 原始分型的识别及四项比较见memo019；本层才取舍候选、决定成笔。

| CC口径 | 实际可执行含义 | 与作者来源的边界 |
|---|---|---|
| `bi_5k`默认 | `standard`；中心合并下标差至少4；缺口可折算；`half`端点检查；要求端点极值；启用带确认守卫的笔修正 | 不是“原文老笔的全部唯一实现”；缺口折算、half细节和修正是CC参数／项目选择 |
| `bi_4k` | `raw_extreme`；三元窗口不能共用合并单元；极值原始下标差至少4；关闭缺口折算、端点有效性、peak及repair | 对应A.4两套计数的程序表达，不把参数名自身当成证明 |
| `bi_strong` | 先走标准；失败才用前笔／后笔幅度，预设ratio=0.95，其余继承5k | CC“强势笔”扩展，不是以上原文所明定的新笔条件 |
| `bi_secondary` | `run()`直接置空`self._bis=[]`，不输出 | **暂未实现**；虽然枚举注释／模块前言叙述了次笔意图，不能报告已有次笔算法 |

以上以config.py:146–170、240–264及bi.py:126–133的可执行分支为准。[7][8] 普通`ChanConfig`字段ratio默认0.9，而命名`BI_STRONG`归一化预设为0.95，必须说清实际生效配置，不能混用。

### B.2 — 首笔候选、标准三道门与同型延伸

**首笔不是随便连接最早两分型。** 内部保存`_bis`和`_candidates`。尚无笔时，每来一个分型，按候选保存顺序扫描所有异型候选；首个通过标准三门的配对成为首笔并清空候选。都不通过便把当前分型也存入候选（155–163行）。首笔只尝试标准，未调用强势补救或repair。

**已有笔时的分支优先级。** 若新分型与末笔终点同型，直接尝试更极值延伸并返回；否则先尝试标准成反向笔，失败才试强势模式，再失败才在开关开启时试修正（136–153行）。同型顶只在更高时替换，底只在更低时替换；相等不替换，不重跑距离／端点门，也不回查修正（202–212行）。这说明“看到相反分型”与“已形成有效反向笔”不同。

标准三道门按顺序短路（277–288行）；下列前两项是距离门的两种模式，之后才是端点门与极值门：

1. **类型／距离。** 同型直接失败。`merged_center`用`end.index-start.index`；不足阈值且允许缺口折算，才遍历中心之间的相邻合并单元。缺口按每个单元对应的原始成员高低外包络算，严格满足`max(a_lo,b_lo)>min(a_hi,b_hi)`才加1，不按跳空金额加根数（291–329行）。
2. **新笔原始极值计数。** `raw_extreme`先要求`start.index+1 < end.index-1`（三根窗口不共用），再在起终中心单元的原始成员中找极值下标，相同极值取最早成员，检查原始下标差至少阈值（309–338行）。它不是简单把中心合并下标差改成3，也不在此路叠加缺口。
3. **端点有效性。** `none`跳过；`loss/half/strict/totally`选择不同的分型窗口部分。以向上`half`为例：起点中心low必须小于终点前根／中心low之min，终点中心high必须大于起点中心／后根high之max；向下用对应反向条件。`totally`要求相应价区完全分离（341–372行）。这些参数细节不是分型识别本身。
4. **端点极值。** 若`bi_require_peak`开启，向上要求起终中心之间所有high不超过终点顶；向下要求所有low不低于终点底，比较允许相等（374–379行）。实现没有在此额外检查起点是否也是整段最极值，不能扩大为“两端所有极值都已检验”。

### B.3 — 强势、修正、依赖水位与输出

**强势补救（166–197行）。** 幅度为两端选定顶底价的绝对差。先比当前候选幅度是否至少ratio×前一笔幅度；成功便追加。否则沿后方分型有界查找首条从当前终点起可标准成笔的反向笔，再比该后笔幅度；不会递归用强势笔验证后笔。依赖下标分别记当前终点或实际查到的后方端点，这一look-ahead不能伪装成候选当时已知的信息。

**项目修正（214–269行）。** 要至少已有两笔；先检查当前反向分型是否击穿反弹笔起点、反弹终点是否未反越前笔起点，以及前笔起点到该新极值的peak条件。通过后仍需向后扫描确认：若先越过反弹终点的极值，才视作假反弹并吸收；若先从反弹终点形成标准反向笔，或扫到末尾仍不充分，则保留旧结构。实际处理是弹出末笔并延伸前笔；若延伸没有改变端点，就把弹出的笔放回。最终依赖水位包含后方确认位置。不能只根据docstring“修正”二字就宣称能即时稳定回退所有历史。

**confirmed与provisional（57–79行）。** `bi_confirmed_flags`以每笔trace依赖水位、合并单元总数和末两笔位置计算：末笔恒provisional；缺依赖或`dep >= n_merged-2`者provisional；若末笔依赖仍不稳定，倒数第二笔也provisional。这是CC工程稳定性判据，不是作者对完成一笔的原文定义，也不是单看终点时间。

**finish与追溯（389–419行）。** 工作状态转为不可变Bi：由终点分型定方向；向上价为起底→终顶，向下起顶→终底；trace记录实际成笔rule ID、profile、config hash、中心合并下标闭区间和dep。来源时间包络扩大到`merged[start.index-1].start_ts…merged[end.index+1].end_ts`，包含两端分型的侧翼；几何端点时间仍是中心分型timestamp。Bi显示ID为`bi-{{start_ts}}-{{end_ts}}`（models.py:164–184），和TDS拟议整数ID不同。[7][9]

### B.4 — 一组连续数值：首笔、门禁失败、延伸与反向成笔

以下是**按默认命名bi_5k手工追踪**，未运行CC。所有`Mi=Ri`为原始单根且已无包含，成员为`{{Ri}}`，时间为`t_i`。相邻区间均相交或相接，严格缺口数为0，因此默认gap开关不改变本例距离。原始分型全部依四项比较取得，列表为B1、T4、B8、T12、B15、T16、B20。

| i | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| low | 8 | 6 | 9 | 11 | 13 | 12 | 10 | 8 | 5 | 7 | 10 |
| high | 11 | 9 | 12 | 14 | 16 | 15 | 13 | 11 | 8 | 10 | 13 |

| i | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| low | 12 | 14 | 12 | 11 | 10 | 12 | 8 | 6 | 4 | 3 | 5 |
| high | 15 | 17 | 15 | 14.5 | 14 | 18 | 12 | 10 | 8 | 7 | 9 |

| 到来的原始分型 | 比较与状态 | 当前笔结果 |
|---|---|---|
| B1（底6） | 首候选保存；无异型候选 | 空 |
| T4（顶16） | 候选B1→T4中心差3<4，零缺口，失败；T4也保存 | 空；候选[B1,T4] |
| B8（底5） | 跳过同型B1；T4→B8中心差4；half检验`16>max(11,8)=11`、`5<min(13,12)=12`；中间low均≥5 | 首笔向下T4→B8，即16→5；清空候选 |
| T12（顶17） | B8→T12差4；half检验`5<min(12,14)=12`、`17>max(8,10)=10`；中间high均≤17 | 追加向上B8→T12，即5→17 |
| B15（底10） | T12→B15差3，未成反向笔；standard模式不走strong；repair首关因`10>末笔起底5`不符而退出 | 仍为前两笔，不把出现底分型当作下笔完成 |
| T16（顶18） | 与末笔终点T12同型且18>17；直接延伸，不重新跑成笔门 | 向上笔变为B8→T16，即5→18，dep更新为16 |
| B20（底3） | T16→B20差4；half为`18>max(8,7)=8`、`3<min(12,8)=8`；M17–M19.low均≥3 | 追加向下T16→B20，即18→3 |

最后有三笔：`(t4,16)→(t8,5)`、`(t8,5)→(t16,18)`、`(t16,18)→(t20,3)`。源中心范围分别`[4,8]、[8,16]、[16,20]`；含两端侧翼的原始时间包络为`t3…t9、t7…t17、t15…t21`，依赖水位为8、16、20。共享一个分型端点不等于共用两端分型的三K窗口，也不等于原始区间分区。

![笔手工代码推演：连续输入、同型延伸与同时间末根修订](memoWX_020_Chan_bi/cc-stroke-manual-trace.png)

上下两图共用价格刻度和来源轴，蜡烛open/close是`L+0.3(H-L)`／`L+0.7(H-L)`并交替交换的教学值，不参与划笔；蓝线是端点连线，不伪装成完整OHLC结果。上图虚线是早先5→17的末笔，在T16到来后延伸为5→18。

### B.5 — 相等、缺口／新笔分支与末端修订

**相等同型候选。** 将主例M16.high从18改为17，同时其他输入不变，T16仍可能作为原始顶分型（它严格高于邻根），但与较早T12顶价相等。`_extend_same_fx`要求严格更高，因此不替换T12，依赖仍12；这与A.3“相等先保留”的原文不能机械混称为完全同一实现。此处是另一个场景，不改主例数据。

**门禁分支的小例子（与主序列分开）。** 中心差3时，`merged_center`若在其间恰有1个代码所定义的严格原始价区缺口且开关开启，距离可以折算为4；这只通过距离门，端点／peak仍要继续。`raw_extreme`中，起终中心在2与5时，其三元窗口`[1,3]`及`[4,6]`不共用；若两个中心单元极值原始下标为4与8，则差4可过，若是4与7则差3失败。两个中心单元含多根原始成员时必须用成员里的极值位置，不能凭合并下标差推断结果。上述是条件算术示例，没有构造完整可达CC行情，也没有冒称运行样本。

**同时间R21修订。** 将主例最后单根R21由`[5,9]`改为`[2,6]`，原始根数仍22；M20不再是底，B20消失。引擎先更新末根、回退／重加合并器、增加版本，再从当前合并／分型列表重派生笔（engine.py:244–270、299–323）。[10] 剩余分型到T16为止，结果只剩首笔T4→B8和延伸后的B8→T16，不能保留旧的T16→B20当作已确认历史。此为下图快照；本例每根仍各自成合并单元，没有把“同时间修订”误当新追加。

**稳定性账本。** 未修订主例`n_merged=22`，dep=[8,16,20]，末dep20≥22−2，所以第三笔和倒数第二笔均provisional，第一笔confirmed。若只在末端继续上行追加M22=`[7,11]`、M23=`[9,13]`而没有新反向分型，则n=24、末dep20<22，第二笔可转confirmed，但末笔仍provisional。这仅按flags函数手算，不是运行后的引擎状态承诺。

### B.6 — 检查结论与尚未完成的验证

- 已静态跟踪标准、同型、首笔、强势前／后笔、repair与确认守卫、输出及依赖flags；尤其指出secondary实际为空，未用陈旧注释覆盖可执行分支。
- 已将核心原文连续摘录和所用原图逐项回指本地来源；源图已查看并字节／SHA-256核对。原始图与代码推导教学图分别标识；081的绿箭头图保留配图位置的局限。
- [图表和比较脚本](../../artifacts/mas/memo018-appendix-study/s2-s3/build_studies.py)检查了主例原始分型、零缺口、关键距离／half／peak算术及修订后的分型变化，没有调用CC函数；强势和repair的完整可达行情尚未动态验证。
- 一次调用临时保存候选和工作笔，额外存储随分型／笔数增长；首笔候选可反复扫描，距离、peak、原始成员与look-ahead还会重复遍历区间，不能照抄引擎旧前言宣称全链O(M)或O(1)。本批没有给出未经证实的精确最坏界或性能实测。
- 尚未运行CC测试／行情样本、证明与作者全部规则等价，或替TDS采纳配置、强势／修正、确认阈值。正文000–005保持空白；附录完整性指证据整理范围，不等于算法已实现或验证通过。

## References

[1] 缠中说禅. 教你炒股票62：分型、笔与线段. [本地整理本](../../references/chan_theory/062.md)，正文28–42行、原图001。

[2] 缠中说禅. 教你炒股票65：再说说分型、笔、线段. [本地整理本](../../references/chan_theory/065.md)，正文47–53行。

[3] 缠中说禅. 教你炒股票77：一些概念的再分辨. [本地整理本](../../references/chan_theory/077.md)，正文43–71行。

[4] 缠中说禅. [081本地整理文件](../../references/chan_theory/081.md)，收录2007-09-18《忽闻台风可休市，聊赋七律说〈风灾〉》111–121行及2007-09-19答疑161–171行；绿箭头图004位于103行。

[5] 缠中说禅. 教你炒股票78：继续说线段的划分. [本地整理本](../../references/chan_theory/078.md)，作者答疑256–260行。

[6] [CC实际仓库选定快照与来源说明]({CC}/README.md)，HEAD `374268381a3eaeee4d220e67d63364b3907405f4`；[逐文件哈希清单]({CC}/manifest.json)。

[7] CC. [bi.py]({CC}/src/cc/algo/bi.py)，57–79、93–163、166–269、277–338、341–419、423–453行。

[8] CC. [config.py]({CC}/src/cc/algo/config.py)，59–91、146–170、240–264行，参数／归一化预设。

[9] CC. [models.py]({CC}/src/cc/algo/models.py)，123–184行，来源成员、分型、Bi及显示ID。

[10] CC. [engine.py]({CC}/src/cc/algo/engine.py)，244–270、299–323行，修订与派生调用顺序。
'''
    charts()
    backups=[write_memo(s2,a2),write_memo(s3,a3)]
    (ART/"source-excerpts.json").write_text(json.dumps(source_records,ensure_ascii=False,indent=2)+"\n")
    (ART/"figure-provenance.json").write_text(json.dumps(image_records,ensure_ascii=False,indent=2)+"\n")
    (ART/"write-evidence.json").write_text(json.dumps({"backups":backups,"main_sections_preserved":True,"cc_executed":False,"keyword_match_lines":len((ART/"corpus-keyword-hits.txt").read_text().splitlines()),"numbered_lessons_scanned":108},indent=2)+"\n")
    print("Wrote S2/S3 appendices with main-section preservation, backups, source excerpts and image hashes.")


if __name__=="__main__":main()
