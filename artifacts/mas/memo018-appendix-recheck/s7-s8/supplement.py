"""Evidence-backed second-pass additions; never imports CC or rewrites main text."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent
records = []


class Supplement:
    def __init__(self, number, name):
        self.path = ROOT / f"docs/memo/memoWX_{number:03d}_Chan_{name}.md"
        self.before = self.path.read_bytes()
        self.body, bibliography = self.before.decode().split("## References\n", 1)
        self.refs = {int(m[1]): m[2] for m in re.finditer(r"^\[(\d+)\] (.+)$", bibliography, re.M)}
        self.quotes = []
        self.figures = []

    def cite(self, label, path):
        entry = f"[{label}]({path})。"
        for n, existing in self.refs.items():
            if existing == entry:
                return f"[{n}]"
        n = max(self.refs, default=0) + 1
        self.refs[n] = entry
        return f"[{n}]"

    def quote(self, lesson, start, stop, title, context):
        source = ROOT / f"references/chan_theory/{lesson}.md"
        raw = "\n".join(source.read_text().splitlines()[start - 1:stop])
        normalized = re.sub(r"</?span\b[^>]*>", "", raw)
        def copy_image(m):
            origin = source.parent / m[2]
            target = self.path.parent / self.path.stem / f"lesson{lesson}-{origin.name}"
            data = origin.read_bytes()
            if target.exists():
                assert target.read_bytes() == data
            else:
                target.write_bytes(data)
            assert target.read_bytes() == data
            self.figures.append({"source": str(origin.relative_to(ROOT)), "copy": str(target.relative_to(ROOT)), "sha256": hashlib.sha256(data).hexdigest(), "source_viewed_before_copy": True})
            return f"![{m[1]}]({self.path.stem}/{target.name})"
        normalized = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", copy_image, normalized)
        block = "\n".join("> " + line if line else ">" for line in normalized.splitlines())
        citation = self.cite(f"缠中说禅：《教你炒股票{int(lesson)}》，本地整理本{lesson}.md，L{start}–{stop}", f"../../references/chan_theory/{lesson}.md")
        self.quotes.append({"lesson": lesson, "start": start, "stop": stop, "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(), "normalized_block_sha256": hashlib.sha256(block.encode()).hexdigest(), "block": block})
        return f"### {title}\n\n{context} 本次快照 L{start}–{stop}。{citation}\n\n{block}\n\n"

    def write(self):
        # Re-number all evidence citations by first body appearance after insertion.
        order = []
        for n in re.findall(r"\[(\d+)\](?!\()", self.body):
            n = int(n)
            assert n in self.refs
            if n not in order:
                order.append(n)
        assert set(order) == set(self.refs), (order, self.refs.keys())
        mapping = {old: i for i, old in enumerate(order, 1)}
        body = re.sub(r"\[(\d+)\](?!\()", lambda m: f"[{mapping[int(m[1])]}]", self.body)
        bibliography = "## References\n\n" + "\n\n".join(f"[{mapping[n]}] {self.refs[n]}" for n in order) + "\n"
        text = body.rstrip() + "\n\n" + bibliography
        before_prefix = self.before.decode().split("## Appendix A", 1)[0]
        assert text.split("## Appendix A", 1)[0] == before_prefix
        for q in self.quotes:
            assert q["block"] in text
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            assert (self.path.parent / target).exists(), target
        stamp = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
        backup = self.path.parent / "backups" / f"{self.path.stem}__{stamp}.md"
        with backup.open("xb") as stream:
            stream.write(self.before)
        assert backup.read_bytes() == self.before
        assert self.path.read_bytes() == self.before, "Concurrent memo edit"
        self.path.write_text(text)
        records.append({"memo": str(self.path.relative_to(ROOT)), "backup": str(backup.relative_to(ROOT)), "main_prefix_sha256": hashlib.sha256(before_prefix.encode()).hexdigest(), "new_quotes": self.quotes, "new_figures": self.figures, "references": len(order), "checks": "Main prefix unchanged; every new quote directly extracted and checked; images pre-viewed/copied/hash-checked; all local links resolve; first-appearance citations renumbered."})


s7 = Supplement(24, "beichi")
addition = s7.quote("025", 18, 38, "A.11 — 二次补查：第25课的指标适用范围与连续涨停例外", "完整连续论述；补回均线／MACD仅辅助、急促走势、连续一字涨停的正弦式指标失真与观察级别。源文件开头sg_trans.gif未取得，且本段没有嵌入对应行情图片，不以其作为图证。")
addition += "阅读提示（非引文）：不能把第24课柱面积比较推广成对所有急涨、连续涨停都成立的唯一检测器。第25课保留了特定场景下柱高、面积和黄白线的不同用法；这些观察尚不是已选定的TDS量化阈值。\n\n"
addition += s7.quote("043", 18, 48, "A.12 — 二次补查：第43课的同级与小级别转折分类", "连续正文；补回背驰级别与当前走势级别的关系、背驰段可被延伸否定、未有本级背驰的小转大，以及出现更大中枢后的重新分解。含署名娇注与未署名注，不将其改成作者规则。")
addition += s7.quote("044", 18, 36, "A.13 — 二次补查：第44课小背驰—大转折的必要条件", "完整保留由30分钟／5分钟／1分钟例子到必要而非充分条件的论证。源文件L16日期写2010-08-11，后附2007年答疑，不能据此当作已认证首发日期；开头sg_trans.gif也未取得。")
addition += "条件边界（非引文）：末个次级别中枢出现反向第三类点，只是此定理所列大转折的必要条件，不能反向写成充分条件，也不能将任何小级别背驰直接标为本级趋势结束。第43课的本级未背驰路径与第37课已具备本级背驰条件的路径需要分别保留。\n\n"
addition += s7.quote("061", 32, 60, "A.14 — 二次补查：第61课区间套的否定条件、四重定位与来源图", "连续保留比较对象、65／69／71各层背驰段与72定位，继续保留74同时属于第二／第三类点及其确切中枢归属。编者的“买卖／第一买点／第二买点”标签照录，但正文此例明确讨论卖点，不能按编者小标题倒转方向。")
addition += "图像核对：同一源图重复出现在本段，复用一份逐字节副本。图上55–74点及MACD箭头可见；正文所用中枢为69–72，而非看起来更近的70–73。原有理论概括因此增加了可回指的具体区间套案例，而不是另造一组价格。\n\n"
marker = "### A.11 — 后续定义／算法研究需要保留的问题"
assert s7.body.count(marker) == 1
s7.body = s7.body.replace(marker, addition + "### A.15 — 后续定义／算法研究需要保留的问题")
s7.body = s7.body.replace("## Appendix B —", "- 二次补查进一步要求保留急涨／连续涨停的指标适用边界、区间套的否定条件，以及小级别转大级别仅有必要条件的方向，见A.11–A.14。\n\n## Appendix B —", 1)

s8 = Supplement(25, "buysellpoint")
addition = s8.quote("101", 18, 48, "A.9 — 二次补查：第101课第二类点的最强／最弱／一般情形", "连续保留定义、三种强弱情形、中阴阶段与第二／第三类之间可以间隔更多震荡。L46已明示下图来自网络且严格讲有缺项，警示连同图一起保留。")
addition += "重要边界（非引文）：L34明确允许第二类买点低于第一类买点，不能把“二买不破一买”作为覆盖所有原文情形的必要条件。L40的1→2→3价位依次抬高只属于所列一般情形；L42又说明2→3未必紧邻。图是有已知缺项的网络整理图，不能反过来充当独立定义证据。第53课的小转大补充仍保留，未将第101课常规开头扩成程序强制已有同级一买的约束。\n\n"
addition += s8.quote("056", 50, 76, "A.10 — 二次补查：第56课突发缺口、现实第二类卖点与个股差异", "连续保留530事件图解、指数与个股类别可不同、缺口段的最低级别处理、第二类卖点内部结构、盘整背驰和实际配图；不是当前交易建议或本次运行结果。")
addition += "图像核对：image001有A/B/C、绿箭头和红色MACD箭头；指标参数显示24/52/9。image002为附文字的后续讲解图，指标显示12/26/9；两图不能被当作同参数、同范围的量化面积样本。image007是15分钟更长背景，既不能用它代替1分钟的确认细节，也不能把全部后加标注当作首发标记。\n\n"
addition += s8.quote("061", 48, 60, "A.11 — 二次补查：第61课第二／第三类卖点重合必须用正确的中枢", "保留从72后的操作级别说明到74重合及中枢归属的连续原段和相关原图；72的四重区间套前提详见本课L32–46及memo024A.14。编者“买点”标签与作者正文卖点表述分开阅读。")
addition += "归属边界（非引文）：第三类点至少需要先有三段构成的中枢，再有离开和回试；本例74归于69–72而非70–73。不能在任意滚动三段里任挑一个中枢来替买卖点类别作证；第二／第三类可以同点，理论出处和结构来源仍需分别保存。\n\n"
marker = "### A.9 — 后续定义／算法研究需要保留的问题"
assert s8.body.count(marker) == 1
s8.body = s8.body.replace(marker, addition + "### A.12 — 后续定义／算法研究需要保留的问题")
s8.body = s8.body.replace("## Appendix B —", "- 二次补查补回二买可低于一买、2→3可以不紧邻，以及突发缺口下现实可操作点／不同品种类别不同的原文边界；这些条件不能被简化为固定的三点上升序列，见A.9–A.11。\n\n## Appendix B —", 1)

for study in [s7, s8]:
    transport = study.cite("CC二次复核信号传输源码副本与出处（同一HEAD374268381a3e）", "../../references/cc_algo/recheck_signal_boundary/374268381a3e/README.md")
    audit = study.cite("S7/S8二次复核：候选覆盖、源码与缺图核对", "../../artifacts/mas/memo018-appendix-recheck/s7-s8/coverage.md")
    study.body += f"""### B.4 — 二次复核：信号面板／WebSocket与实现缺口

补查了Python算法目录之外的前端信号路径。`useSignalStream.ts` L16–36只建立 `/ws/signal` 连接、解析收到的JSON并维护连接状态；`SignalPanel.vue` L1–20仅展示最后一条消息或占位文字。后端 `ws.py` L151–163发送hello，对收到的文本回送 `{{"type":"pong","received":data}}`，没有在这个函数里消费结构、判断背驰或生成买卖点。注释中的未来接通计划不等于已有检测分支。三份源码原字节保存在单独补充快照，没有改写原19文件快照。{transport}

另外检索到CC研究图脚本中的 `beichi_line/pz/qs` 名称，但它们出现在讲解 chanlun-pro 的图中文字和索引中，属于参考项目说明，不能拿来冒充当前CC检测器。现有MACD图表配置、通知类型、测试通知载荷、传输占位分别核对后，仍未定位到本概念的CC可执行检测器。因此B的连续CC算例／金融输出证据缺口继续保留；本次新增原图仍属于A的理论证据。候选取舍与缺图恢复检查见二次复核记录。{audit}

"""
    study.write()

(OUT / "additions.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"new_source_blocks": sum(len(r["new_quotes"]) for r in records), "new_source_figure_copies": sum(len({im['copy'] for im in r['new_figures']}) for r in records), "main_sections_preserved": True}, ensure_ascii=False))
