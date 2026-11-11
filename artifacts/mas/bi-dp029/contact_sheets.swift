import AppKit
import Foundation
let root = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "artifacts/mas/bi-dp029"
let pages = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: root + "/atlas-manifest.json"))) as! [[String:Any]]
try FileManager.default.createDirectory(atPath: root + "/visual-qa", withIntermediateDirectories: true)
func render(_ entries: [[String:Any]], width:Int, height:Int, columns:Int, cellW:Int, cellH:Int, to:String) throws {
 let bitmap = NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:width,pixelsHigh:height,bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0)!
 NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep:bitmap)
 NSColor.white.setFill();NSRect(x:0,y:0,width:width,height:height).fill()
 for (i,p) in entries.enumerated() {
  let x=(i%columns)*cellW;let top=(i/columns)*cellH
  let image=NSImage(contentsOfFile:root + "/" + (p["png"] as! String))!
  image.draw(in:NSRect(x:x,y:height-top-cellH,width:cellW,height:cellH-20),from:.zero,operation:.sourceOver,fraction:1)
  let bounds = p["raw"] as! [Int]
  let text="\(p["mode"]!) page\(p["page"]!) raw[\(bounds[0]):\(bounds[1]))" as NSString
  text.draw(at:NSPoint(x:x+6,y:height-top-16),withAttributes:[.font:NSFont.systemFont(ofSize:12),.foregroundColor:NSColor.black])
 }
 NSGraphicsContext.restoreGraphicsState()
 try bitmap.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:to))
}
for offset in stride(from:0,to:pages.count,by:2) {
 try autoreleasepool { try render(Array(pages[offset..<min(offset+2,pages.count)]),width:1600,height:1840,columns:1,cellW:1600,cellH:920,to:root + String(format:"/visual-qa/sheet-%03d.png",offset/2+1)) }
}
for mode in ["strong","weak"] { let subset=pages.filter{($0["mode"] as! String)==mode};try render(subset,width:1600,height:3430,columns:4,cellW:400,cellH:245,to:root+"/\(mode)/overview.png") }
