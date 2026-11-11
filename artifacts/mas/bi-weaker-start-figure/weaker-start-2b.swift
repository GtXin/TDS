
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
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:"/Users/coder/Public/EngineGit/TDS/artifacts/mas/bi-weaker-start-figure/weaker-start-2b.png"))
