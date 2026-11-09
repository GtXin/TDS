"""Evidence-backed second pass; preserve existing text and concept main sections."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[4]
MEMOS=ROOT/'docs/memo'
OUT=Path(__file__).parent
changes=[]


def sha(data):return hashlib.sha256(data).hexdigest()


def quote(lesson,start,stop,memo_stem):
    src=ROOT/f'references/chan_theory/{lesson}.md'
    raw='\n'.join(src.read_text().splitlines()[start-1:stop])
    norm=re.sub(r'</?span\b[^>]*>','',raw)
    figures=[]
    def copy(m):
        source=src.parent/m[2]
        dest=MEMOS/memo_stem/f'lesson{lesson}-{source.name}'
        assert source.is_file()
        if dest.exists():assert dest.read_bytes()==source.read_bytes()
        else:dest.write_bytes(source.read_bytes())
        figures.append({'source':str(source.relative_to(ROOT)),'copy':str(dest.relative_to(ROOT)),'sha256':sha(source.read_bytes()),'viewed':True})
        return f'![{m[1]}]({memo_stem}/{dest.name})'
    norm=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',copy,norm)
    quoted='\n'.join('> '+line if line else '>' for line in norm.splitlines())
    return quoted,{'lesson':lesson,'start':start,'stop':stop,'source_block_sha256':sha(raw.encode()),'normalization':'Remove span styling and rewrite copied figure links only','figures':figures}


def renumber(text,threshold):
    return re.sub(r'\[(\d+)\]',lambda m:f'[{int(m[1])+1}]' if int(m[1])>=threshold else m[0],text)


def write(path,old,new,detail):
    assert old.split('## Appendix A')[0]==new.split('## Appendix A')[0]
    stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
    backup=MEMOS/'backups'/f'{path.stem}__{stamp}.md'
    with backup.open('xb') as f:f.write(old.encode())
    assert backup.read_bytes()==old.encode() and path.read_text()==old
    path.write_text(new)
    for target in re.findall(r'\]\(([^)]+)\)',new):
        if not target.startswith(('http://','https://','#')):assert (MEMOS/target).exists(),target
    changes.append({'memo':str(path.relative_to(ROOT)),'backup':str(backup.relative_to(ROOT)),'before_sha256':sha(old.encode()),'main_sha256':sha(new.split('## Appendix A')[0].encode()),'detail':detail})


p=MEMOS/'memoWX_019_Chan_fenxing.md';old=p.read_text()
assert '### A.7 —' not in old
s=renumber(old,7)
block,record=quote('069',25,37,p.stem)
a='''### A.7 — 第69课：原始分型与用于笔的有效端点、当下修订

第二次检索补入正文25–37行的连续原例：同一几何顶／底能被识别，不等于它最终被选为笔端点。保留月线适用性、两个约束、取舍的反证过程和当下修订语境，不能只摘“完成后不改”一句当作程序稳定性保证。[7]

'''+block+'''

图像核对：整理本原图069/image001.jpg可见红／绿箭头、X及1／2标记，未以日线示意替代月线原例；未认证各附加标注的首发归属。该段说明的是作者在笔的有效分型取舍中的完成／未完成，不把它改写成“原始三根候选以后永不失效”。CC原始检测器与笔层是否等价于这段论证，仍须按各自输入、取舍与确认约定核对。

'''
s=s.replace("## Appendix B — Notes from CC's implementation",a+"## Appendix B — Notes from CC's implementation",1)
s=s.replace('### B.5 — 已核对的范围与未验证事项','### B.6 — 已核对的范围与未验证事项',1)
b='''### B.5 — 补充核对：helper 输入前提与价格精度

`detect_fenxings()`没有配置参数；四项比较直接使用输入high/low，没有取整、容差、5周期均线或最小跳动单位分支。作者在第64课的精度说明见[memo020附录A.6](memoWX_020_Chan_bi.md)：一致精度是数据解释前提，不等于CC已经自动采用0.5点容差。若调用者预先量化价格，应对完整来源序列统一处理，不能只为了一个候选临时改比较精度；这不是本批新增的TDS默认方案。

同样，函数只按列表位置取相邻三根，不按时间重新排序，也不确认输入high/low均为有限数、来源区间正确或上游已去包含。正常引擎提供这些前提；手工直接调用helper的坏数据结果，不能反过来当作作者定义的反例。尾部价格修订后原始候选能消失，笔层有效端点还可能因新候选重新取舍；这两个变化不能用同一个“已确认”标签混淆。[9][11]

'''
s=s.replace('### B.6 — 已核对的范围与未验证事项',b+'### B.6 — 已核对的范围与未验证事项',1)
ref='[7] 缠中说禅. [教你炒股票69：月线分段与上海大走势分析、预判](../../references/chan_theory/069.md)，正文25–37行及原图069/image001.jpg；本次补查保留当下有效分型取舍的连续语境。\n\n'
s=s.replace('[8] [CC实际仓库选定快照与来源说明]',ref+'[8] [CC实际仓库选定快照与来源说明]',1)
write(p,old,s,{'new_quote':record,'code_findings':['No tolerance/rounding in detector','Caller input validation distinct from helper','Raw candidate revision distinct from effective endpoint selection']})

p=MEMOS/'memoWX_020_Chan_bi.md';old=p.read_text()
assert '### A.6 —' not in old
s=renumber(old,6)
block,record=quote('064',27,37,p.stem)
a='''### A.6 — 第64课：取整与统一精度是预设，不是任意改场景

补入正文27–37行，连续保留106–107的取整例、两张源图、0.5点的可选说明及“一路保持”的约束。[6] 图001含106／107及箭头，图021是更长视窗并有学习者说明；原文件复制，不把后加文字认证为作者首发标注。

'''+block+'''

阅读提示（非引文）：这段明确精度是可预设的，作者没有宣布取整或0.5点为所有市场统一标准。它补充A.4不同软件的数据适配语境；不能在同一例里按需要切换原始价格与取整结果。CC笔／分型的当前比较没有内置这种容差，见B.6。

'''
s=s.replace("## Appendix B — Notes from CC's implementation",a+"## Appendix B — Notes from CC's implementation",1)
s=s.replace('### B.6 — 检查结论与尚未完成的验证','### B.8 — 检查结论与尚未完成的验证',1)
b='''### B.6 — 补查实际生效配置、强势绕过、修正取等与追溯限制

**生效配置。** `build_bis()`首先调用`cfg.normalize()`；`config.py:203–222`对named profile从完整预设取笔参数，只有`CUSTOM`保留调用者自由组合。因此“给bi_5k对象另填一个ratio／min_span”不保证该值进入执行分支；原B.1表列的是归一化后的值。`profile_id`／`config_hash`仍是调用者传给`finish()`的字符串，`build_bis()`没有用实际生效配置重算这两个实参；正常引擎怎样生成它们与helper本身是否校验匹配须分开。[8][9]

**强势的实际豁免。** 标准三门失败后，`_try_strong()`只比较候选幅度与相邻反向笔幅度；满足前笔或后笔条件便直接`_append()`，没有再把失败的距离、端点或peak门重新要求一遍。前笔优先，只有前笔不够才查后笔。`_lookahead_next_std_bi()`从当前位置扫描到当前分型数组末尾，取首个异型且标准成笔的反向候选；所谓“有界”是当前有限数组边界，没有额外固定K数／时间的前看上限。不能把它说成固定时间的实时操作。[8]

**修正首关与取等。** `_repair_sub_peak()`的起点破坏检查用`<`／`>`作失败条件，因此“刚好到达旧起点”并不在首关立即排除；但最后延伸仍要求严格新极值，若对象没变就恢复弹出的笔。`_confirm_reverse_break()`确认越过反弹端点也用严格`>`／`<`，取等不确认；候选／后方证据的先后顺序不可交换。repair中的`_is_peak()`始终执行，不因自定义配置关闭普通`bi_require_peak`而跳过。[8]

**来源与原因记录。** `source_to_ts`只扩到几何终点分型的右侧翼；strong_next／repair读到更晚证据时，额外水位由`dep_to_index`保存，并不自动把时间包络一直扩到该证据。`_extend_same_fx()`只改终点和dep，没有重写原`rule_kind`；所以被修正／同型延伸的笔仍可保留最初standard或strong规则ID。这个ID不能单独重建后来修正的完整原因链。`finish()`总构造trace，未读取`cfg.trace_enabled`；关闭观测配置不等于本helper不再产生这些字段。[8]

### B.7 — 从同一来源底稿补足强势与修正的完整条件链

以下四种是**彼此独立的教学输入场景**，都从B.4原始范围表出发，未导入或运行CC。所有合并单元均只含对应原始成员`Mi=Ri`，相邻无包含，时间依次为`t_i`；未列出的下标保持B.4原值，给定终点后的右邻包含在各自输入前缀中。算术脚本独立核对所有原始分型、零缺口、距离、half与peak前提，不把人为预置的内部状态冒充完整行情输出。

| 场景 | 与B.4底稿不同的原始范围；当前最后下标 | 形成的分型（序号／极值价） |
|---|---|---|
| strong_prev | M15=[5.5,14]；输入到M16 | B1=6、T4=16、B8=5、T12=17、B15=5.5 |
| strong_next | M15=[7,12]，M16=[9,13]，M17=[10,14]，M18=[11,15]，M19=[12,16]，M20=[9,12]；到M20 | B1=6、T4=16、B8=5、T12=17、B15=7、T19=16 |
| repair接受 | M12=[14,15.5]，M15=[4,14]；到M17 | B1=6、T4=16、B8=5、T12=15.5、B15=4、T16=18 |
| repair拒绝 | M12=[14,15.5]，M15=[4,14]，M16=[12,15]，M17=[8,12]，M18=[3,9]，M19=[6,11]；到M19 | B1=6、T4=16、B8=5、T12=15.5、B15=4、T16=15、B18=3 |

**强势前笔。** 固定归一化named `bi_strong`，ratio=0.95。开始仍由标准门建立T4→B8和B8→T12；T12→B15中心差3且零缺口，标准失败。候选幅度`17−5.5=11.5`，前笔幅度`17−5=12`，`11.5>=0.95×12=11.4`成立，立即追加17→5.5，rule=`strong_prev`、dep=15，不再查后笔。原始底分型B15要到M16出现才具备右侧信息，dep下标15不是最早可知的原始时间。

**强势后笔。** 同样使用named `bi_strong`。到B15时，候选17→7的幅度10不够11.4，标准距离3仍失败；look-ahead找到首个从B15标准成笔的T19：中心差4，half为`7<min(11,12)`且`16>max(12,13)`，中间high不超过16，后笔幅度9。`10>=0.95×9=8.55`成立，追加17→7，rule=`strong_next`、dep=19；正常扫描随后到T19再按标准追加7→16。若输入只到M16而没有T19候选，strong_prev、strong_next与repair均不通过，这条17→7尚不能输出。完整M20快照中的几何终点`t15`、时间包络到右侧翼`t16`、依赖19、及T19要等右邻M20才可识别是四件事，不能都标成t15时已确认。

![强势前笔／后笔两个独立输入：同价格轴与来源轴，后笔条件明确依赖19](memoWX_020_Chan_bi/cc-stroke-strong-recheck.png)

**repair接受。** 固定默认named `bi_5k`（standard且repair开启），先得到16→5和5→15.5。B15=4到来时，15−12=3且零缺口，标准失败；`4<=5`、反弹终点`15.5<=16`，前笔起点T4到B15之间所有low≥4，修正前提成立。未来先见T16=18严格超过反弹顶15.5，守卫返回确认下标16；弹出5→15.5，原向下笔终点从B8的5延伸到B15的4，最后得到16→4、dep=max(8,15,16)=16。来源中心范围[4,15]、侧翼时间`t3…t16`，而T16候选依赖原始M17；原standard规则ID被保留，不能据它看出这次吸收动作。

**repair拒绝。** 保持相同历史到B15，后续先见T16=15，没有严格超过15.5；然后B18=3使T12→B18标准成笔：中心差6，half为`15.5>max(12,9)`及`3<min(14,12)`，中间low≥3。守卫在这条标准反向笔先成立时返回None，保留16→5和5→15.5；扫描到B18后追加15.5→3。相同的B15破起点动作，因后续证据顺序不同而结果不同，不能只看“破了5”就直接吞掉反弹。

![默认5k修正的接受／拒绝：原反弹保留或吸收取决于后方确认顺序](memoWX_020_Chan_bi/cc-stroke-repair-recheck.png)

两图共用价格刻度与来源顺序。蜡烛open/close仅按`L+0.3(H−L)`／`L+0.7(H−L)`构造并交替交换颜色，不参与规则；折线是手工结构结果，阴影显示几何终点之后所读的依赖。图与[独立算术／绘图脚本](../../artifacts/mas/memo018-appendix-recheck/s2-s3/manual_cases.py)、[完整数值清单](../../artifacts/mas/memo018-appendix-recheck/s2-s3/manual-cases.json)均是静态代码研究的辅助证据，不是CC运行测试或正确性证明。

'''
s=s.replace('### B.8 — 检查结论与尚未完成的验证',b+'### B.8 — 检查结论与尚未完成的验证',1)
ref='[6] 缠中说禅. [教你炒股票64：去机场路上给各位补课](../../references/chan_theory/064.md)，正文27–37行、图064/image001.jpg及image021.jpg；统一精度的连续语境。\n\n'
s=s.replace('[7] [CC实际仓库选定快照与来源说明]',ref+'[7] [CC实际仓库选定快照与来源说明]',1)
write(p,old,s,{'new_quote':record,'code_findings':['Named profile normalization vs CUSTOM','Strong bypasses failed standard gates; no fixed lookahead horizon','Repair equality/peak/confirmation order','Rule kind not rewritten on extension/repair; dep vs source time envelope','trace_enabled not consumed in finish'],'new_cases':4,'new_manual_charts':2})
(OUT/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print('Two source additions, three source-image copies and deeper branch cases inserted; main prefixes unchanged.')
