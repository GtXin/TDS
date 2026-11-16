import AppKit
import Foundation
let root=URL(fileURLWithPath:CommandLine.arguments[1])
let modes=["bi-strong_xd-strong","bi-strong_xd-weak","bi-weak_xd-strong","bi-weak_xd-weak"]
let titles=["Bi strong / XD strong — 41 segments","Bi strong / XD weak — 45 segments","Bi weak / XD strong — 59 segments","Bi weak / XD weak — 61 segments"]
let width=1800,height=3300
let bitmap=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:width,pixelsHigh:height,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:bitmap)
NSColor.white.setFill();NSRect(x:0,y:0,width:width,height:height).fill()
for i in 0..<4 {
 let url=root.appendingPathComponent("charts/"+modes[i]+"/overview.png")
 let source=NSImage(contentsOf:url)!
 // Crop plotting area of existing exact-coordinate chart; all four share scales.
 source.draw(in:NSRect(x:0,y:Double(3-i)*800+80,width:1800,height:675),from:NSRect(x:0,y:100,width:1800,height:675),operation:.sourceOver,fraction:1)
 let attrs:[NSAttributedString.Key:Any]=[.font:NSFont.boldSystemFont(ofSize:21),.foregroundColor:NSColor.darkGray]
 (titles[i] as NSString).draw(at:NSPoint(x:60,y:Double(3-i)*800+770),withAttributes:attrs)
 
}
("Same full-data time/price scales | Purple: primary segments; orange: derived segments | Trial results; long derived segment unresolved" as NSString).draw(at:NSPoint(x:40,y:16),withAttributes:[.font:NSFont.systemFont(ofSize:19),.foregroundColor:NSColor.darkGray])
NSGraphicsContext.restoreGraphicsState()
try bitmap.representation(using:.png,properties:[:])!.write(to:root.appendingPathComponent("comparison/four-panels-vertical.png"))
