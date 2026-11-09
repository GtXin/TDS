"""Append evidence-backed omissions; never import or execute CC reference code."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
MEMO = ROOT / "docs/memo"
HERE = Path(__file__).parent
records = {"quotes": [], "figures": [], "memos": []}


def quote(lesson, start, stop):
    p = ROOT / f"references/chan_theory/{lesson:03d}.md"
    raw = "\n".join(p.read_text().splitlines()[start-1:stop])
    normalized = re.sub(r"</?span\b[^>]*>", "", raw)
    records["quotes"].append({"lesson": lesson, "start": start, "stop": stop,
                               "source_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                               "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                               "normalized": normalized})
    return "\n".join("> " + line if line else ">" for line in normalized.splitlines()) + "\n\n"


def figure(stem, lesson, filename):
    source = ROOT / f"references/chan_theory/{lesson:03d}/{filename}"
    target = MEMO / stem / f"lesson{lesson:03d}-{filename}"
    if target.exists():
        assert target.read_bytes() == source.read_bytes()
    else:
        target.write_bytes(source.read_bytes())
    records["figures"].append({"source": str(source.relative_to(ROOT)),
                                "copy": str(target.relative_to(ROOT)),
                                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                                "viewed_before_copy": True})
    return f"![第{lesson}课整理本所附图，原字节复制]({stem}/{target.name})\n\n"


def replace_citations(body, refs):
    # References retain prior entries, but new original evidence precedes code.
    pattern = re.compile(r"(?<![\w])\[(\d+|NEW\w+)\](?!\()")
    ids = []
    for m in pattern.finditer(body):
        key = m[1]
        if key in refs and key not in ids:
            ids.append(key)
    assert set(refs) == set(ids), (set(refs)-set(ids), set(ids)-set(refs))
    lookup = {key: str(i+1) for i, key in enumerate(ids)}
    body = pattern.sub(lambda m: f"[{lookup[m[1]]}]" if m[1] in lookup else m[0], body)
    bibliography = "## References\n\n" + "\n\n".join(f"[{i+1}] {refs[key]}" for i, key in enumerate(ids)) + "\n"
    return body.rstrip() + "\n\n" + bibliography


def save(path, old, body, refs):
    result = replace_citations(body, refs)
    prefix = old.split("## Appendix A",1)[0]
    assert result.split("## Appendix A",1)[0] == prefix
    assert path.read_text() == old, "Concurrent edit detected"
    stamp = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
    backup = MEMO / "backups" / f"{path.stem}__{stamp}.md"
    with backup.open("xb") as stream:
        stream.write(path.read_bytes())
    assert backup.read_text() == old
    path.write_text(result)
    records["memos"].append({"path": str(path.relative_to(ROOT)),
                              "backup": str(backup.relative_to(ROOT)),
                              "preserved_main_sha256": hashlib.sha256(prefix.encode()).hexdigest()})


p = MEMO / "memoWX_021_Chan_xianduan.md"
old = p.read_text()
body, old_refs = old.split("## References", 1)
refs = dict(re.findall(r"^\[(\d+)\] (.+)$", old_refs, re.M))
addition = """### A.5 — 第83课：线段作为最小中枢部件及两类破坏的心理解释

出处：作者正文19–37行，连续保留“为什么不用笔直接构造最小中枢”、偶然因素与确认、两类破坏的不同反攻过程。[NEW083] 此段是作者的结构选择与心理解释，不是新增价格判据；其中“(注：非绝对）”是未署名整理注。原文第25行“需要三个特征序列分型”的措辞照录，不能擅自转成“每次结束都必须等三个完整分型”的可执行常量；几何判定仍须回到第67/71/77/78课前提。所引正文没有相应嵌图，后面的083/image001属于另一日解盘，不移作本段理论图。

""" + quote(83,19,37)
addition += """### A.6 — 第72课解盘：暂时标记与实际完成不同

出处：2007-08-23解盘正文195行。[NEW072] 这里单独保留关于56／59暂标的完整论述；193行价格速率线与197–203行个股评论不涉及该划分论证，故不抄入。相邻前一日图181行与当日图205行同时列出，便于看到暂标变化，而不是只展示事后最终图。图是本地整理本所收录的文件，未认证首发图版。

""" + quote(72,195,195)
addition += figure(p.stem,72,"image005.jpg") + figure(p.stem,72,"image006.jpg")
addition += "图像核对：前图右侧暂标56，后图包含重新划分后的56、57、58及右缘59；本文引用作者对确认层次的说明，不从截图自行推导CC的N0/N1/N2规则。\n\n"
body = body.replace("## Appendix B", addition + "## Appendix B", 1)
body += """
### B.6 — 二次核对：包含的分支表、输出变换与显示层边界

`_Eigen.test_combine()`（300–321行）按以下顺序短路；不能只笼统写“包含都合并”。[6]

| 顺序 | 实际条件与返回 | 适用位置 |
|---|---|---|
| 1 | 旧元素包住新笔（含完全相等）直接`combine` | 第二／第三元素均如此，先于其他特例 |
| 2 | 新笔包住旧元素，且`allow_top_equal=1`、顶相等而low下降，返回`down`；对称的底相等/high上升返回`up` | 第三元素可用，第二元素传`None`没有此特例 |
| 3 | 其余“新包旧”：`exclude_included=True`返回`included`，否则`combine` | 第二元素保留分界，第三元素通常合并 |
| 4 | 无包含时比较高低方向，返回`down/up` | 仍需后续分型与实际突破检查 |

`_reset()`（479–487行）不是只丢掉一个矩形，而是取已喂反向笔`lst[1:]`，清空三个元素后逐笔重放；因此包含后的来源成员、滑窗次数及依赖位置都须按原始笔追踪。此处也不能凭“一次右移”就宣称恒定代价。

**可选strong_bi链条。** `_try_strong_bi_break()`（733–763行）只考虑前候选结束后的第一根反向笔，必须严格破前段起点，且紧接该单笔之后能从`single+1`形成反向标准段，才返回单笔候选；依赖取该标准段水位。主循环仍让它进入N1/N2裁决，而不是单笔破位立即冻结；成为strong N0后不再延伸／失败吸收，本会作废N1并延伸N0的场景改走rollover保持该单笔几何（544–659、820–888、917–930行）。这是项目变体，不是原文“至少三笔”的例外定理。

**输出和候选并非逐字段原样透传。** `_emit()`（997–1046行）把pending N1的公开`rule_kind`改成`forming`，并按`_forming_end()`选择同方向极值笔；这个形成中展示终点可能晚于原候选终点，`dep_index`仍来自原N1。几何成员水位与依赖字段因此要分别读；不能从公开forming对象反推出其内部曾是gap候选。无候选的整窗forming／尾部forming只是展示兜底，不经过冻结硬闸。`_forming_end()`用Python的`max/min`，同价时取遍历中首个极值，而非凭注释“最新”强制改成最后同价位置（1048–1056行）。

`_finish()`（1095–1137行）对全部几何成员求high/low，但来源时间两端与合并下标仅从首／末成员trace取值，缺trace时回退对应端点时间；`dep_to_index`是笔依赖位置，不是原始K线下标。正常输入下这可组成包络，函数没有另行审计所有成员的trace是否一致／完备。主循环还设`guard<4*n`防御上界，到上界后返回当前状态，不提供额外的收敛证明或终止错误报告。

**三个显示类别。** `build_feature_sequence_overlays()`（1248–1353行）另行构建显示结果：PRIMARY画每段反向笔合并元素；SECOND仅为frozen gap段重现`GAP_REVERT`确认序列，编号按每个事件重新从0开始；TAIL_PROBE画假想后段的同向临时探测，不参与确认。PRIMARY的`_feature_elements()`不运行exclude／前看／分型判定，故图上的矩形不是候选识别器三个工作元素的逐状态镜像（1220–1245行）。

此外，该显示入口创建`_XianduanBuilder`时只转发nonstandard/oscillation，未像`build_xianduans()`267–271行转发strong_bi。因此“同cfg即同分段”的注释不能无条件推广到可选STRONG_BI配置；默认standard不触发此差别。本次只记录可执行参数转发差异，未运行比较或改动源码。
"""
refs["NEW083"] = "缠中说禅. [教你炒股票83：笔-线段与线段-最小中枢结构的不同心理意义1](../../references/chan_theory/083.md)，正文19–37行；保留未署名整理注。"
refs["NEW072"] = "缠中说禅. [教你炒股票72：本ID已有课程的再梳理](../../references/chan_theory/072.md)，2007-08-23解盘195行；整理本相邻图181/205行。"
save(p,old,body,refs)

p = MEMO / "memoWX_022_Chan_zhongshu.md"
old = p.read_text()
body, old_refs = old.split("## References",1)
refs = dict(re.findall(r"^\[(\d+)\] (.+)$",old_refs,re.M))
addition = """### A.6 — 第84课：最低起始函数与递归函数、级别与时间

出处：作者正文63–71行，连续保留初始化f1、递归f2及级别／时间的明确区分。[NEW084] 第69行指标只是辅助的过渡也保留，不把结构级别替换成软件K线周期。该段没有配图；本地84课后面的“回复”图与理论段不是同一出处层次。

""" + quote(84,63,71)
addition += """### A.7 — 第66课答疑：九个走势重叠与3+3+3组合的边界

出处：读者问题及作者答复177–187行。[NEW066] 作者回答“不一定”，并要求按3+3+3组合后确定；这足以阻止把任意九条线段的共同交集直接当作更高级中枢价格。问题所设“一分钟走势类型”不等于任意九根K线，答复也未在此给出全部分组与确认算法。

""" + quote(66,177,187)
addition += """### A.8 — 第99课：延伸后的高级中枢优先与结合律

出处：作者正文27–39行，连续保留中阴未确定、a…h重组及延伸九段后的中枢确立优先。[NEW099] 原文没有授权用固定条数跳过层级／重叠／完成前提。该课图001已经查看并原字节复制，图上“CHYS20091010”和补充注释表明它是后来的整理图，不认证为作者首发配图。

""" + quote(99,27,39)
# Rewrite only the copied image location in this newly selected block.
addition = addition.replace("![](099/image001.jpg)", f"![第99课本地整理本附图]({p.stem}/lesson099-image001.jpg)")
figure(p.stem,99,"image001.jpg")
addition += "阅读提示（非引文）：第20课的延伸／新生／外围扩张与这里的高级别重组要分别保留语境。第80课462–466行另有作者答疑，明确第二中枢延伸九段形成更高级别时按高级别震荡看；与本条方向一致，列入覆盖记录而不重复整段。第92课的中轴监视器属辅助观察，未作为本次结构判定规则移入。\n\n"
body = body.replace("## Appendix B", addition + "## Appendix B", 1)
body = body.replace("若还未有离开证据，中心是OPEN并停在run末尾", "若还未有离开证据，中心是OPEN，本run的中枢扫描在此停止；几何末端仍是最后已接受的Z成员，未配对的末尾连接部件不自动加入")
body += """
### B.6 — 二次核对：输入连续性、输出方向和依赖范围

**输入校验的实际范围。** EXTEND的`_continuous()`只检查前项end_ts等于后项start_ts、方向相反（zhongshu.py133–134行），未在此比较端点价格是否相等，也不检查source_index连续。SAME_LEVEL的`_continuous()`额外检查source_index相邻，仍不比较相邻端点价格（same_level.py100–105行）。这些是可执行检查边界，不能从函数名推断整套时间／价格／来源合法性已被证明。[6][8]

SAME_LEVEL适配时，如果`ZsLeg.start_price/end_price`缺失，就用direction对应的low/high作为端点（zhongshu.py452–475行）；这是假定端点已标准化的适配兜底，不是重新追查实际原始极值的位置。随后`LevelLeg.__post_init__()`仅检查source_index非负、start_ts不晚于end_ts、low不大于high；既不把源记录自动修正成真实走势，也不证明其是完成的次级别类型（models.py324–348行）。[9]

**方向与身份。** 中枢`direction`来自核心A/C的方向，和进入E相反；`exit_direction`来自关闭Z相对核心的价格位置，允许与E方向不同，二者不能混称“中枢上涨／下跌”。对象ID还有模式前缀：EXTEND为`zs`，SAME_LEVEL为`zsd`，随后是来源类型、核心起点时间和C结束时间（models.py213–243行）。切换模式本身改变身份语境，不只是画法。[9]

**来源与末尾未完成输入。** EXTEND的`_trace()`（zhongshu.py182–197行）把E、所有已接受成员及关闭证据组合成deps，再由`_trace_for_rule()`137–179行求其来源时间min/max、存在的合并下标min/max和最大依赖水位。时间／依赖包络因此可以超出核心／成员；关闭Z不是旧中枢成员，其前面尚未接受的连接部件也不能仅因在两个时刻之间就算作成员。若末尾只来了一条连接部件而相应Z尚未到，几何end_index保持前一已接受成员，OPEN并不意味着成员已覆盖整个当前输入尾部。[6][7]

**递归升级仍有缺口。** 本层保存extend中心的member_count或CLOSED，不等于已实现“每满九条就自动升一级”。理论A.6–A.8需要固定递归来源、完成及分组；当前更高层的来源投影和允许深度属于memo023的递归路径。上层有depth=1接口，也不能倒推本层已经覆盖原文所有层级／中枢重组情况。本次保留既有主例与相切例，其手工分支未运行CC；新增的输入／trace／身份核对属于静态代码证据。
"""
refs["NEW084"] = "缠中说禅. [教你炒股票84：本ID理论一些必须注意的问题](../../references/chan_theory/084.md)，正文63–71行：初始化／递归函数及级别与时间。"
refs["NEW066"] = "缠中说禅. [教你炒股票66：主力资金的食物链](../../references/chan_theory/066.md)，2007-07-31作者答疑177–187行。"
refs["NEW099"] = "缠中说禅. [教你炒股票99：走势结构的两重表里关系3](../../references/chan_theory/099.md)，正文27–39行及整理本图image001.jpg。"
save(p,old,body,refs)

(HERE / "write_evidence.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n")
print("Added5 continuous source blocks/3 viewed figure copies; both main prefixes preserved; source data untouched.")
