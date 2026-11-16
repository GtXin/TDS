import AppKit
import Foundation
let root=URL(fileURLWithPath:CommandLine.arguments[1])
let modes=["bi-strong_xd-strong","bi-strong_xd-weak","bi-weak_xd-strong","bi-weak_xd-weak"]
let titles=["Bi strong / XD strong","Bi strong / XD weak","Bi weak / XD strong","Bi weak / XD weak"]
let stems=["overview"]+(1...7).map{String(format:"detail-%03d",$0)}
func label(_ text:String,_ x:Double,_ y:Double,_ size:Double=14){(text as NSString).draw(at:NSPoint(x:x,y:y),withAttributes:[.font:NSFont.systemFont(ofSize:size),.foregroundColor:NSColor.darkGray])}
for (page,stem) in stems.enumerated(){
 let figure=try JSONSerialization.jsonObject(with:Data(contentsOf:root.appendingPathComponent("compact-sources/"+modes[0]+"/"+stem+".figure.json"))) as! [String:Any]
 let layout=figure["layout"] as! [String:Any]
 let yr=(layout["yaxis"] as! [String:Any])["range"] as! [Double]
 let xr=(layout["xaxis"] as! [String:Any])["range"] as! [Double]
 let subtitle=page==0 ? "All 3027 fractals" : "FX\((page-1)*500)–\(min(page*500-1,3026))"
 let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:1800,pixelsHigh:1100,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
 NSGraphicsContext.saveGraphicsState();NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
 NSColor.white.setFill();NSRect(x:0,y:0,width:1800,height:1100).fill()
 for i in 0..<4{
  let base=Double(3-i)*260
  let source=NSImage(contentsOf:root.appendingPathComponent("compact-sources/"+modes[i]+"/"+stem+".png"))!
  source.draw(in:NSRect(x:82,y:base+62,width:1670,height:190),from:NSRect(x:82,y:145,width:1670,height:610),operation:.sourceOver,fraction:1)
  label(titles[i]+"   |   "+subtitle,60,base+273,21)
  for j in 0...2{let value=yr[0]+(yr[1]-yr[0])*Double(j)/2;label(String(format:"%.0f",value),15,base+55+Double(j)*95)}
  for j in 0...4{let value=xr[0]+(xr[1]-xr[0])*Double(j)/4;label(String(format:"%.0f",max(value,0)),82+Double(j)*417.5-10,base+43,12)}
 }
 label("Aligned raw-bar axis / common price scale per page | Purple: confirmed; gray dashed: unconfirmed tail | C trial results; no per-window restart",40,15,18)
 NSGraphicsContext.restoreGraphicsState()
 try bitmap.representation(using:.png,properties:[:])!.write(to:root.appendingPathComponent("comparison/compact-"+stem+".png"))
 print("Saved compact-\(stem).png")
}
