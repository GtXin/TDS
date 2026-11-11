
import AppKit
let w:CGFloat=1700, h:CGFloat=1050
let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:Int(w),pixelsHigh:Int(h),bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
let ink=NSColor(calibratedRed:0.12,green:0.17,blue:0.23,alpha:1)
let muted=NSColor(calibratedRed:0.42,green:0.47,blue:0.53,alpha:1)
let blue=NSColor(calibratedRed:0.07,green:0.39,blue:0.72,alpha:1)
let orange=NSColor(calibratedRed:0.84,green:0.38,blue:0.10,alpha:1)
let red=NSColor(calibratedRed:0.77,green:0.18,blue:0.20,alpha:1)
let grid=NSColor(calibratedRed:0.88,green:0.90,blue:0.93,alpha:1)
func box(_ x:CGFloat,_ y:CGFloat,_ ww:CGFloat,_ hh:CGFloat,_ color:NSColor) {color.setFill();NSBezierPath(rect:NSRect(x:x,y:h-y-hh,width:ww,height:hh)).fill()}
func text(_ s:String,_ x:CGFloat,_ y:CGFloat,_ size:CGFloat=25,_ color:NSColor=ink,_ bold:Bool=false,_ ww:CGFloat=1700) {
 let font=NSFont(name:bold ? "PingFangSC-Semibold":"PingFangSC-Regular",size:size) ?? NSFont.systemFont(ofSize:size)
 (s as NSString).draw(in:NSRect(x:x,y:h-y-70,width:ww,height:70),withAttributes:[.font:font,.foregroundColor:color])
}
func line(_ x1:CGFloat,_ y1:CGFloat,_ x2:CGFloat,_ y2:CGFloat,_ color:NSColor,_ width:CGFloat=2,_ dashed:Bool=false) {
 let p=NSBezierPath();p.move(to:NSPoint(x:x1,y:h-y1));p.line(to:NSPoint(x:x2,y:h-y2));p.lineWidth=width
 if dashed {p.setLineDash([9,7],count:2,phase:0)};color.setStroke();p.stroke()
}
func dot(_ x:CGFloat,_ y:CGFloat,_ color:NSColor,_ r:CGFloat=7) {color.setFill();NSBezierPath(ovalIn:NSRect(x:x-r,y:h-y-r,width:2*r,height:2*r)).fill()}
box(0,0,w,h,.white)

let bars:[(CGFloat,CGFloat)]=[(1,3),(0,2),(3,5),(6,8),(9,11),(12,14),(10,12),(8,10),(12,14),(16,18),(13,15),(10,12),(7,9),(4,6),(5,7)]
func x(_ i:Int)->CGFloat {130+100*CGFloat(i)}
func y(_ v:CGFloat)->CGFloat {850-(v+2)*26}
text("B合格以后仍可更新：先等反向C，再推进工作笔",65,35,41,ink,true)
text("15根连续合并K线；底7距离不足，顶9更高且可与底1成笔，故B从5更新到9。",68,106,25,muted)
for v in stride(from:0,through:20,by:2) {let yy=y(CGFloat(v));line(90,yy,1590,yy,grid,1);text(String(v),45,yy-17,21,muted,false,50)}
for (i,b) in bars.enumerated() {box(x(i)-13,y(b.1),26,y(b.0)-y(b.1),muted.withAlphaComponent(0.30));text(String(i),x(i)-11,875,21,muted,false,70)}
line(x(1),y(0),x(5),y(14),muted,3,true);dot(x(5),y(14),muted)
line(x(1),y(0),x(9),y(18),blue,4);dot(x(1),y(0),blue);dot(x(9),y(18),blue)
line(x(9),y(18),x(13),y(4),orange,4,true);dot(x(13),y(4),orange)
dot(x(7),y(8),muted)
text("底1：0",x(1)-38,y(0)+16,26,blue,true)
text("旧暂定顶5：14",x(5)-115,y(14)-53,25,muted,true)
text("底7：8，间隔仅2",x(7)-105,y(8)+26,24,muted,true)
text("更新后的顶9：18",x(9)-95,y(18)-56,27,blue,true)
text("反向底13：4",x(13)-70,y(4)+20,26,orange,true)
text("合并位置",35,875,19,muted)
text("首次局部收下的是 1→9；9→13成为新的暂定工作笔，继续等待其反向端点。",68,948,26,ink,true)
text("图中只有合并K线高低区间；折线表示该候选路线，未设置市场确认时间。",68,996,23,muted)

NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:"/Users/coder/Public/EngineGit/TDS/artifacts/mas/memo020-002b-d/algorithm-endpoint-extension.png"))
