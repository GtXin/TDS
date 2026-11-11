import AppKit
import Foundation
let d = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath:"/tmp/cc200-chart.json"))) as! [String:Any]
let bars=d["bars"] as! [[Double]], fx=d["fx"] as! [[Double]], route=d["route"] as! [Int]
let w=1800,h=850
let image=NSImage(size:NSSize(width:w,height:h)); image.lockFocus()
NSColor.white.setFill();NSRect(x:0,y:0,width:w,height:h).fill()
func label(_ s:String,_ x:Double,_ y:Double,_ size:Double=15){s.draw(at:NSPoint(x:x,y:y),withAttributes:[.font:NSFont.systemFont(ofSize:size),.foregroundColor:NSColor.darkGray])}
let lo=bars.map{$0[1]}.min()!-10, hi=bars.map{$0[2]}.max()!+10
func point(_ x:Double,_ y:Double)->NSPoint{NSPoint(x:85+x/bars.last![0]*1660,y:110+(y-lo)/(hi-lo)*620)}
label("Memo029 DP — first 200 CC-derived fractals",85,795,26)
label("Strong distance | FX0 → FX198 | 34 strokes | provisional route",85,760,19)
for j in 0...5 {let v=lo+(hi-lo)*Double(j)/5;let y=point(0,v).y;NSColor(white:0.90,alpha:1).setStroke();let p=NSBezierPath();p.move(to:NSPoint(x:85,y:y));p.line(to:NSPoint(x:1745,y:y));p.stroke();label(String(format:"%.0f",v),15,y-7)}
NSColor(white:0.65,alpha:0.65).setStroke()
for b in bars {let p=NSBezierPath();p.move(to:point(b[0],b[1]));p.line(to:point(b[0],b[2]));p.lineWidth=1;p.stroke()}
for f in fx {let p=NSBezierPath();let c=point(f[0],f[1]);let s=4.0;let sign=f[2]==1 ? 1.0 : -1.0;p.move(to:NSPoint(x:c.x,y:c.y));p.line(to:NSPoint(x:c.x-s,y:c.y+sign*8));p.line(to:NSPoint(x:c.x+s,y:c.y+sign*8));p.close();(f[2]==1 ? NSColor.systemRed : NSColor.systemGreen).setFill();p.fill()}
NSColor.systemBlue.setStroke();let line=NSBezierPath();for (i,r) in route.enumerated(){let p=point(fx[r][0],fx[r][1]);if i==0{line.move(to:p)}else{line.line(to:p)}};line.lineWidth=2.5;line.stroke()
for r in route {let p=point(fx[r][0],fx[r][1]);NSColor.systemBlue.setFill();NSBezierPath(ovalIn:NSRect(x:p.x-3,y:p.y-3,width:6,height:6)).fill();label("\(r)",p.x-8,p.y+(fx[r][2]==1 ? 12 : -24),11)}
for j in 0...10 {let x=bars.last![0]*Double(j)/10;label(String(format:"%.0f",x),point(x,lo).x-10,80)}
label("Merged K-line position • endpoint labels are zero-based FX positions",480,40,16)
image.unlockFocus()
let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:CommandLine.arguments[1]))
