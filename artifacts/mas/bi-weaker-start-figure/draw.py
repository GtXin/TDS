"""Verify and render a synthetic merged-range counterexample using AppKit."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOWS = [9, 10, 0, 9, 7, 5, 3, 1, 2]
BARS = [(low, low + 1) for low in LOWS]
FRACTALS = []
for i in range(1, len(BARS) - 1):
    left, center, right = BARS[i - 1 : i + 2]
    if all(center[j] > left[j] and center[j] > right[j] for j in (0, 1)):
        FRACTALS.append((i, "top"))
    elif all(center[j] < left[j] and center[j] < right[j] for j in (0, 1)):
        FRACTALS.append((i, "bottom"))
assert FRACTALS == [(1, "top"), (2, "bottom"), (3, "top"), (7, "bottom")]
for first, second in zip(BARS, BARS[1:]):
    assert not (first[0] <= second[0] and first[1] >= second[1])
    assert not (second[0] <= first[0] and second[1] >= first[1])


def check_pair(top: int, bottom: int) -> dict[str, object]:
    checks = {
        "opposite_types": (top, "top") in FRACTALS and (bottom, "bottom") in FRACTALS,
        "time_order": top < bottom,
        "center_distance": bottom - top >= 4,
        "center_intervals": BARS[top][1] > BARS[bottom][1] and BARS[bottom][0] < BARS[top][0],
        "maximum_at_top": max(high for _, high in BARS[top : bottom + 1]) <= BARS[top][1],
        "minimum_at_bottom": min(low for low, _ in BARS[top : bottom + 1]) >= BARS[bottom][0],
    }
    return {"checks": checks, "valid": all(checks.values())}


PAIRS = {"A_to_X": check_pair(1, 2), "A_to_C": check_pair(1, 7), "B_to_C": check_pair(3, 7)}
assert [pair["valid"] for pair in PAIRS.values()] == [False, False, True]
assert set(range(4, 7)) - set(range(2, 5)) - set(range(6, 9)) == {5}

SWIFT = r'''
import AppKit
let w:CGFloat=1700, h:CGFloat=1160
let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:Int(w),pixelsHigh:Int(h),bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
let ink=NSColor(calibratedRed:0.12,green:0.17,blue:0.23,alpha:1)
let muted=NSColor(calibratedRed:0.45,green:0.49,blue:0.54,alpha:1)
let grid=NSColor(calibratedRed:0.88,green:0.90,blue:0.93,alpha:1)
let red=NSColor(calibratedRed:0.79,green:0.19,blue:0.22,alpha:1)
let green=NSColor(calibratedRed:0.03,green:0.48,blue:0.35,alpha:1)
let gold=NSColor(calibratedRed:0.82,green:0.55,blue:0.09,alpha:1)
func box(_ x:CGFloat,_ y:CGFloat,_ ww:CGFloat,_ hh:CGFloat,_ color:NSColor) {
 color.setFill();NSBezierPath(rect:NSRect(x:x,y:h-y-hh,width:ww,height:hh)).fill()
}
func text(_ s:String,_ x:CGFloat,_ y:CGFloat,_ size:CGFloat=25,_ color:NSColor=ink,_ bold:Bool=false,_ ww:CGFloat=1550,_ hh:CGFloat=80) {
 let f=NSFont(name:bold ? "PingFangSC-Semibold":"PingFangSC-Regular",size:size) ?? NSFont.systemFont(ofSize:size)
 (s as NSString).draw(in:NSRect(x:x,y:h-y-hh,width:ww,height:hh),withAttributes:[.font:f,.foregroundColor:color])
}
func line(_ x1:CGFloat,_ y1:CGFloat,_ x2:CGFloat,_ y2:CGFloat,_ color:NSColor,_ width:CGFloat=2,_ dashed:Bool=false) {
 let p=NSBezierPath();p.move(to:NSPoint(x:x1,y:h-y1));p.line(to:NSPoint(x:x2,y:h-y2));p.lineWidth=width
 if dashed {p.setLineDash([11,8],count:2,phase:0)};color.setStroke();p.stroke()
}
func dot(_ x:CGFloat,_ y:CGFloat,_ color:NSColor,_ r:CGFloat=7) {
 color.setFill();NSBezierPath(ovalIn:NSRect(x:x-r,y:h-y-r,width:2*r,height:2*r)).fill()
}
func x(_ i:Int)->CGFloat {200+165*CGFloat(i)}
func y(_ value:CGFloat)->CGFloat {790-40*value}
let lows:[CGFloat]=[9,10,0,9,7,5,3,1,2]
box(0,0,w,h,.white)
text("2.b：为什么较弱的同型起点 B 不能直接丢掉？",65,30,42,ink,true)
text("同一段连续数据：A 是更高的顶，但 A→C 失败；较低的顶 B 却能与 C 成笔。",69,100,27,muted)
box(75,176,24,24,muted.withAlphaComponent(0.35));text("合并K线高低区间",113,165,22,muted,false,300)
line(465,188,525,188,muted,3,true);text("A→X：距离不足",540,165,22,muted,false,300)
line(870,188,930,188,red,4,true);text("A→C：失败",945,165,22,red,false,270)
line(1265,188,1325,188,green,5);text("B→C：合格",1340,165,22,green,false,280)
text("价格",78,251,22,muted,false,90)
for value in stride(from:0,through:12,by:2) {
 let yy=y(CGFloat(value));line(145,yy,1580,yy,grid,1)
 text(String(value),95,yy-16,21,muted,false,50)
}
// Only the center-to-center interval defines the stroke's interior.
box(x(1)-35,y(1),x(7)-x(1)+70,40,red.withAlphaComponent(0.06))
line(x(1)-20,y(1),x(7)+20,y(1),red.withAlphaComponent(0.65),1.5,true)
for (i,low) in lows.enumerated() {
 let color = i == 5 ? gold : muted
 box(x(i)-16,y(low+1),32,40,color.withAlphaComponent(i == 5 ? 0.40:0.26))
 let outline=NSBezierPath(rect:NSRect(x:x(i)-16,y:h-y(low),width:32,height:40))
 color.withAlphaComponent(0.8).setStroke();outline.lineWidth=1.5;outline.stroke()
 text(String(i),x(i)-10,824,23,muted,false,55)
}
line(x(1),y(11),x(2),y(0),muted,3,true)
line(x(1),y(11),x(7),y(1),red,4,true)
line(x(3),y(10),x(7),y(1),green,5)
dot(x(1),y(11),red,8);dot(x(2),y(0),red,8)
dot(x(3),y(10),green,8);dot(x(7),y(1),green,8)
text("A：旧起点，顶高 11",x(1)-125,280,27,red,true,340)
text("B：较弱起点，顶高 10",x(3)-90,330,27,green,true,380)
text("X：底低 0",x(2)-125,700,26,red,true,230)
line(x(2)-15,742,x(2),y(0)-10,red,1.5)
text("C：底低 1",x(7)+32,721,26,green,true,250)
text("1",x(7)+34,y(1)-12,21,red,false,55)
text("第5根：两分型之外的独立K线",x(5)-130,471,22,gold,true,500)
line(x(5),516,x(5),y(6)-10,gold,1.5)
text("合并K线位置（从0计数）",65,862,20,muted)
func card(_ xx:CGFloat,_ title:String,_ detail:String,_ color:NSColor) {
 box(xx,908,495,150,color.withAlphaComponent(0.065))
 box(xx,908,5,150,color)
 text(title,xx+20,925,26,color,true,460)
 text(detail,xx+20,970,23,ink,false,460,74)
}
card(65,"① A→X：还不能形成首笔","中心距 2−1＝1，小于4。\n所以初始化仍在寻找端点。",muted)
card(600,"② A→C：旧起点失败","区间包含更低的 X：0＜1。\nC 不是这一区间的最低点。",red)
card(1135,"③ B→C：较弱起点成功","中心距 7−3＝4；区间最高10、最低1。\n第5根不属于任一端点分型。",green)
text("笔内按端点中心计算：X 在 B 左侧，不属于 B→C 的笔内范围。",68,1080,23,ink)
text("教学构造：9根连续合并K线，high＝low＋1，相邻无包含；未构造开收盘价。",68,1120,21,muted)
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:OUTPUT_PATH))
'''
output = HERE / "weaker-start-2b.png"
swift_path = HERE / "weaker-start-2b.swift"
swift_path.write_text(SWIFT.replace("OUTPUT_PATH", json.dumps(str(output))))
subprocess.run(["swift", "-module-cache-path", "/private/tmp/chan-bi-swift-cache", str(swift_path)], check=True)
manifest = {
    "source": "Synthetic teaching counterexample from current chat; no market OHLC invented.",
    "bars_low_high": BARS,
    "fractals_center_kind": FRACTALS,
    "labels": {"A": 1, "X": 2, "B": 3, "C": 7},
    "pair_checks": PAIRS,
    "B_window": [2, 3, 4],
    "C_window": [6, 7, 8],
    "independent_bar": 5,
    "note": "Pair interior includes endpoint centers, not the entire fractal windows.",
    "png_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
}
(HERE / "verification.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"png": str(output), "fractals": FRACTALS, "pair_validity": {key: value["valid"] for key, value in PAIRS.items()}}, ensure_ascii=False))

# The user clarified that2.b is ONLY the pending-start initialization decision.
# Render that stage separately; there is no qualified endpoint C or working Bi002.
initial_lows = [9, 10, 0, 9, 1, 12, 11]
initial_fractals = []
for i in range(1, len(initial_lows) - 1):
    if initial_lows[i] > max(initial_lows[i - 1], initial_lows[i + 1]):
        initial_fractals.append((i, "top"))
    elif initial_lows[i] < min(initial_lows[i - 1], initial_lows[i + 1]):
        initial_fractals.append((i, "bottom"))
assert initial_fractals == [(1, "top"), (2, "bottom"), (3, "top"), (4, "bottom"), (5, "top")]
assert 2 - 1 < 4 and 4 - 1 < 4
assert initial_lows[3] + 1 < initial_lows[1] + 1 < initial_lows[5] + 1
initial_prefix = SWIFT.split('text("2.b：', 1)[0]
initial_prefix = initial_prefix.replace("h:CGFloat=1160", "h:CGFloat=1080")
initial_prefix = initial_prefix.replace("200+165*CGFloat(i)", "220+200*CGFloat(i)")
initial_prefix = initial_prefix.replace("790-40*value", "740-32*value")
initial_prefix = initial_prefix.replace("[9,10,0,9,7,5,3,1,2]", "[9,10,0,9,1,12,11]")
initial_body = r'''
let blue=NSColor(calibratedRed:0.10,green:0.38,blue:0.72,alpha:1)
text("2.b：还在选起点，较弱同型点不替换当前起点",65,30,41,ink,true)
text("此时尚无合格首笔，Bi002 为空；这里只判断 Bi001S 是否更新。",69,102,28,muted)
box(75,179,24,24,muted.withAlphaComponent(0.35));text("连续合并K线的高低区间",114,168,23,muted)
text("没有 C，也没有已形成的笔。",1110,168,26,ink,true,510)
for value in stride(from:0,through:14,by:2) {
 let yy=y(CGFloat(value));line(145,yy,1560,yy,grid,1)
 text(String(value),95,yy-16,21,muted,false,50)
}
text("价格",78,232,22,muted,false,90)
for (i,low) in lows.enumerated() {
 box(x(i)-17,y(low+1),34,32,muted.withAlphaComponent(0.26))
 let outline=NSBezierPath(rect:NSRect(x:x(i)-17,y:h-y(low),width:34,height:32))
 muted.withAlphaComponent(0.75).setStroke();outline.lineWidth=1.5;outline.stroke()
 text(String(i),x(i)-10,793,23,muted,false,55)
}
line(x(1)-40,y(11),x(5)+40,y(11),blue.withAlphaComponent(0.5),2,true)
text("当前 A 的最高点＝11",65,380,22,blue,true,330)
dot(x(1),y(11),blue,8);dot(x(3),y(10),muted,8);dot(x(5),y(13),green,8)
text("A：顶高11",x(1)-70,313,29,blue,true,270)
text("较弱 B：顶高10",x(3)-85,440,28,muted,true,350)
text("更强 D：顶高13",x(5)-85,248,29,green,true,370)
text("10＜11：起点仍是 A",x(3)-100,487,24,muted,true,370)
text("13＞11：起点改为 D",x(5)-100,410,24,green,true,380)
dot(x(2),y(0),muted,6);dot(x(4),y(1),muted,6)
text("底 X：距 A 仅1，未成笔",x(2)-135,744,22,muted,false,370)
text("底 Y：距 A 仅3，未成笔",x(4)-135,712,22,muted,false,370)
text("合并K线位置（从0计数）",65,829,20,muted)
func initialCard(_ xx:CGFloat,_ title:String,_ detail:String,_ color:NSColor) {
 box(xx,873,495,123,color.withAlphaComponent(0.065));box(xx,873,5,123,color)
 text(title,xx+20,887,26,color,true,460)
 text(detail,xx+20,936,26,ink,true,460)
}
initialCard(65,"① 先读到 A，初始化起点","Bi001S＝A",blue)
initialCard(600,"② B 比当前起点弱：不替换","Bi001S 仍然＝A",muted)
initialCard(1135,"③ D 比当前起点强：更新","Bi001S＝D",green)
text("这张图仅说明初始化时的起点更新；还没有进入终点延伸或反向成笔阶段。",68,1015,23,ink)
text("教学构造：7根连续合并K线，high＝low＋1，相邻无包含；未构造开收盘价。",68,1050,20,muted)
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:OUTPUT_PATH))
'''
initial_output = HERE / "initialization-2b.png"
initial_swift = HERE / "initialization-2b.swift"
initial_swift.write_text(initial_prefix + initial_body.replace("OUTPUT_PATH", json.dumps(str(initial_output))))
subprocess.run(["swift", "-module-cache-path", "/private/tmp/chan-bi-swift-cache", str(initial_swift)], check=True)
(HERE / "initialization-verification.json").write_text(json.dumps({
    "source": "Synthetic illustration of the user's initialization2.b, before any qualified pair.",
    "bars_low_high": [(low, low + 1) for low in initial_lows],
    "fractals_center_kind": initial_fractals,
    "initial_start_center": 1,
    "weaker_top_center": 3,
    "stronger_top_center": 5,
    "failed_initial_pair_gaps": {"A_to_X": 1, "A_to_Y": 3},
    "start_sequence": [1, 1, 5],
    "png_sha256": hashlib.sha256(initial_output.read_bytes()).hexdigest(),
    "scope": "Local pending-start update only; no complete-algorithm or permanent-discard claim."
}, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"initialization_png": str(initial_output), "start_centers": [1, 1, 5]}, ensure_ascii=False))
