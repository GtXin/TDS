import AppKit
import Foundation
let root=URL(fileURLWithPath:CommandLine.arguments[1])
let modes=["bi-strong_xd-strong","bi-strong_xd-weak","bi-weak_xd-strong","bi-weak_xd-weak"]
let titles=["Bi strong / XD strong — 41 segments","Bi strong / XD weak — 45 segments","Bi weak / XD strong — 59 segments","Bi weak / XD weak — 61 segments"]
let width=1800,height=1100
let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:width,pixelsHigh:height,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
NSColor.white.setFill();NSRect(x:0,y:0,width:width,height:height).fill()
for i in 0..<4 {
 let url=root.appendingPathComponent("charts/"+modes[i]+"/overview.png")
 let source=NSImage(contentsOf:url)!
 // Crop plotting area of existing exact-coordinate chart; all four share scales.
 source.draw(in:NSRect(x:82,y:Double(3-i)*260+62,width:1670,height:190),from:NSRect(x:82,y:145,width:1670,height:610),operation:.sourceOver,fraction:1)
 for (j,value) in [2492.4,2903.0,3313.6].enumerated() {
  (String(format:"%.0f",value) as NSString).draw(at:NSPoint(x:18,y:Double(3-i)*260+55+Double(j)*95),withAttributes:[.font:NSFont.systemFont(ofSize:14),.foregroundColor:NSColor.gray])
 }
 let attrs:[NSAttributedString.Key:Any]=[.font:NSFont.boldSystemFont(ofSize:21),.foregroundColor:NSColor.darkGray]
 (titles[i] as NSString).draw(at:NSPoint(x:60,y:Double(3-i)*260+273),withAttributes:attrs)
 
}
("Same full-data time/price scales | Purple: primary segments; orange: derived segments | Trial results; long derived segment unresolved" as NSString).draw(at:NSPoint(x:40,y:16),withAttributes:[.font:NSFont.systemFont(ofSize:19),.foregroundColor:NSColor.darkGray])
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:root.appendingPathComponent("comparison/four-panels-compact.png"))
