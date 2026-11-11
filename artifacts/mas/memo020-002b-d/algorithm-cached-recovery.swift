
import AppKit
let w:CGFloat=1900, h:CGFloat=1500
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

let bars:[(CGFloat,CGFloat)]=[(8,9),(9,10),(6,7),(4,5),(2,3),(0,1),(2,3),(4,5),(6,7),(7,8),(3,4),(-1,0),(1,2),(3,4),(5,6),(8,9),(5,6),(2,3),(0,1),(-2,-1),(-1,0)]
func x(_ i:Int)->CGFloat {180+75*CGFloat(i)}
func y(_ v:CGFloat,_ base:CGFloat)->CGFloat {base-(v+3)*25}
func chart(_ base:CGFloat) {
 box(x(0)-33,y(12,base),66,375,grid.withAlphaComponent(0.30));box(x(20)-33,y(12,base),66,375,grid.withAlphaComponent(0.30))
 for v in stride(from:-2,through:12,by:2) {let yy=y(CGFloat(v),base);line(120,yy,1765,yy,grid,1);text(String(v),65,yy-17,21,muted,false,60)}
 for (i,b) in bars.enumerated() {
  let c=muted.withAlphaComponent(0.26);box(x(i)-12,y(b.1,base),24,y(b.0,base)-y(b.1,base),c)
  let p=NSBezierPath(rect:NSRect(x:x(i)-12,y:h-y(b.0,base),width:24,height:y(b.0,base)-y(b.1,base)));muted.withAlphaComponent(0.65).setStroke();p.lineWidth=1.5;p.stroke()
  text(String(i),x(i)-11,base+16,20,muted,false,50)
 }
 text("合并位置",62,base+17,20,muted,false,120)
}
func stroke(_ a:Int,_ av:CGFloat,_ b:Int,_ bv:CGFloat,_ base:CGFloat,_ color:NSColor,_ dashed:Bool=false) {line(x(a),y(av,base),x(b),y(bv,base),color,4,dashed);dot(x(a),y(av,base),color);dot(x(b),y(bv,base),color)}
text("缓存恢复：从阻塞路线回到更早的选择点",70,35,43,ink,true)
text("21根连续、相邻无包含的合并K线；窄矩形只表示高低区间，不构造开收盘价。",73,104,25,muted)
line(75,172,128,172,blue,4);text("已暂存的笔",140,151,23,ink)
line(405,172,458,172,orange,4,true);text("当前工作笔（仍可延伸）",470,151,23,ink)
text("① 初始路线 1 → 5 → 9：尝试把顶9延伸到顶15时阻塞",76,220,28,ink,true)
chart(700)
stroke(1,10,5,0,700,blue);stroke(5,0,9,8,700,orange,true)
line(x(5),y(0,700),x(15),y(0,700),red,2,true);dot(x(11),y(-1,700),red,9);dot(x(15),y(9,700),orange,8)
text("顶1：10",x(1)-42,y(10,700)-47,24,blue,true)
text("底5：0",x(5)-44,y(0,700)+14,24,blue,true)
text("暂定顶9：8",x(9)-70,y(8,700)-49,24,orange,true)
text("底11：−1",x(11)-55,y(-1,700)+13,24,red,true)
text("新顶15：9",x(15)-55,y(9,700)-49,24,orange,true)
text("−1 < 0：底5已不是 5→15 范围内的最低点",970,270,24,red,true,810)
text("恢复的是“跳过首次底5”的选择：A=顶1，B未定，下一分型从顶9重新检查。",76,770,25,ink)
text("② 恢复后路线 1 → 11 → 15 → 19",76,827,28,ink,true)
chart(1300)
stroke(1,10,11,-1,1300,blue);stroke(11,-1,15,9,1300,blue);stroke(15,9,19,-2,1300,orange,true)
text("顶1：10",x(1)-42,y(10,1300)-47,24,blue,true)
text("底11：−1",x(11)-61,y(-1,1300)+14,24,blue,true)
text("顶15：9",x(15)-47,y(9,1300)-47,24,blue,true)
text("底19：−2",x(19)+17,y(-2,1300)-22,23,orange,true,220)
text("两幅图共用价格刻度与合并位置；灰色边缘0、20不属于所选端点之间的覆盖范围。",73,1390,24,muted)
text("第20根仍可作为底分型19的右邻证据；输入结束不等于最后工作笔确认。",73,1430,24,muted)

NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:"/Users/coder/Public/EngineGit/TDS/artifacts/mas/memo020-002b-d/algorithm-cached-recovery.png"))
