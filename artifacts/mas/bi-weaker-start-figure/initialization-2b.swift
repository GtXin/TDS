
import AppKit
let w:CGFloat=1700, h:CGFloat=1080
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
func x(_ i:Int)->CGFloat {220+200*CGFloat(i)}
func y(_ value:CGFloat)->CGFloat {740-32*value}
let lows:[CGFloat]=[9,10,0,9,1,12,11]
box(0,0,w,h,.white)

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
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:"/Users/coder/Public/EngineGit/TDS/artifacts/mas/bi-weaker-start-figure/initialization-2b.png"))
