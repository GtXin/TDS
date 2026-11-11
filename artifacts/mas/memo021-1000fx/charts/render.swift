import AppKit
import Foundation

// Native static rendering of the exact Plotly figure arrays; no browser/network.
let charts = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "artifacts/mas/memo021-1000fx/charts", isDirectory: true)
let width = 1800
let height = 900
let plot = NSRect(x: 82, y: 145, width: 1670, height: 610)

func number(_ value: Any?) -> Double? {
    guard let n = value as? NSNumber else { return nil }
    return n.doubleValue
}
func array(_ value: Any?) -> [Any] { value as? [Any] ?? [] }
func dictionary(_ value: Any?) -> [String: Any] { value as? [String: Any] ?? [:] }
func color(_ text: String, fallback: NSColor = .black) -> NSColor {
    if text.hasPrefix("#"), text.count == 7, let value = UInt32(text.dropFirst(), radix: 16) {
        return NSColor(srgbRed: Double((value >> 16) & 255) / 255, green: Double((value >> 8) & 255) / 255, blue: Double(value & 255) / 255, alpha: 1)
    }
    if text.hasPrefix("rgb"), let left = text.firstIndex(of: "("), let right = text.firstIndex(of: ")") {
        let values = text[text.index(after: left)..<right].split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
        if values.count >= 3 { return NSColor(srgbRed: values[0] / 255, green: values[1] / 255, blue: values[2] / 255, alpha: values.count > 3 ? values[3] : 1) }
    }
    return fallback
}
func text(_ value: String, _ x: Double, _ y: Double, size: Double = 13, shade: NSColor = .darkGray, center: Bool = false, bold: Bool = false) {
    let font = bold ? NSFont.boldSystemFont(ofSize: size) : NSFont.systemFont(ofSize: size)
    let attrs: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: shade]
    let string = value as NSString
    let offset = center ? string.size(withAttributes: attrs).width / 2 : 0
    string.draw(at: NSPoint(x: x - offset, y: y), withAttributes: attrs)
}
func line(_ a: NSPoint, _ b: NSPoint, _ shade: NSColor, _ thickness: Double = 1) {
    let path = NSBezierPath(); path.move(to: a); path.line(to: b); path.lineWidth = thickness; shade.setStroke(); path.stroke()
}
func clean(_ value: String) -> String {
    value.replacingOccurrences(of: "<sup>", with: "").replacingOccurrences(of: "</sup>", with: "").replacingOccurrences(of: "&gt;", with: ">").replacingOccurrences(of: "&lt;", with: "<")
}
func bitmap(_ w: Int, _ h: Int) -> NSBitmapImageRep {
    return NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
}
func save(_ image: NSBitmapImageRep, _ url: URL) throws {
    guard let png = image.representation(using: .png, properties: [:]) else { throw NSError(domain: "png", code: 1) }
    try png.write(to: url)
}

let manifest = try JSONSerialization.jsonObject(with: Data(contentsOf: charts.appendingPathComponent("manifest.json"))) as! [[String: Any]]
var rendered: [[String: Any]] = []
let started = Date()
for (pageIndex, page) in manifest.enumerated() {
    let source = charts.appendingPathComponent(page["figure_json"] as! String)
    let figure = try JSONSerialization.jsonObject(with: Data(contentsOf: source)) as! [String: Any]
    let layout = dictionary(figure["layout"])
    let xRange = array(dictionary(layout["xaxis"])["range"]).compactMap { number($0) }
    let yRange = array(dictionary(layout["yaxis"])["range"]).compactMap { number($0) }
    guard xRange.count == 2 && yRange.count == 2 else { fatalError("Explicit source ranges required") }
    let xmin = xRange[0], xmax = xRange[1], ymin = yRange[0], ymax = yRange[1]
    func x(_ value: Double) -> Double { plot.minX + (value - xmin) / (xmax - xmin) * plot.width }
    func y(_ value: Double) -> Double { plot.minY + (value - ymin) / (ymax - ymin) * plot.height }
    func point(_ a: Double, _ b: Double) -> NSPoint { NSPoint(x: x(a), y: y(b)) }
    let image = bitmap(width, height)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: image)
    NSGraphicsContext.current?.shouldAntialias = true
    NSColor.white.setFill(); NSRect(x: 0, y: 0, width: width, height: height).fill()
    let title = clean(dictionary(layout["title"])["text"] as? String ?? "XD-P1 experiment").components(separatedBy: "<br>")
    text(title.first ?? "XD-P1 experiment", 82, 852, size: 22, shade: color("#0f172a"), bold: true)
    if title.count > 1 { text(title[1], 82, 824, size: 15) }
    text("Native static view of exact source arrays · offline HTML retains all hovers and indices", 82, 797, size: 12, shade: color("#64748b"))
    // Grid and axis labels outside clipping.
    for n in 0...6 {
        let value = ymin + Double(n) / 6 * (ymax - ymin)
        line(NSPoint(x: plot.minX, y: y(value)), NSPoint(x: plot.maxX, y: y(value)), color("#e2e8f0"), 0.7)
        text(String(format: "%.1f", value), 10, y(value) - 7, size: 11)
    }
    for n in 0...8 {
        let value = xmin + Double(n) / 8 * (xmax - xmin)
        line(NSPoint(x: x(value), y: plot.minY), NSPoint(x: x(value), y: plot.maxY), color("#f1f5f9"), 0.7)
        text(String(format: "%.0f", value), x(value), 119, size: 11, center: true)
    }
    line(NSPoint(x: plot.minX, y: plot.minY), NSPoint(x: plot.maxX, y: plot.minY), color("#64748b"))
    text("Observed raw-bar index · source positions retained; no calendar gaps", plot.midX, 91, size: 13, center: true)
    text("Price", 12, 772, size: 12)
    NSGraphicsContext.saveGraphicsState()
    NSBezierPath(rect: plot).addClip()
    for shapeValue in array(layout["shapes"]) {
        let shape = dictionary(shapeValue)
        guard shape["type"] as? String == "rect", let a = number(shape["x0"]), let b = number(shape["x1"]) else { continue }
        color(shape["fillcolor"] as? String ?? "rgba(245,158,11,0.08)").setFill()
        NSRect(x: x(a), y: plot.minY, width: x(b) - x(a), height: plot.height).fill()
    }
    var actualFX = Set<Int>()
    var actualBi = Set<Int>()
    var actualXD = Set<Int>()
    let traces = array(figure["data"]).map(dictionary)
    for trace in traces {
        let meta = dictionary(trace["meta"])
        let kind = meta["kind"] as? String ?? ""
        let xs = array(trace["x"])
        if kind == "raw" {
            let opens = array(trace["open"]), highs = array(trace["high"]), lows = array(trace["low"]), closes = array(trace["close"])
            for i in xs.indices {
                guard let px = number(xs[i]), let op = number(opens[i]), let hi = number(highs[i]), let lo = number(lows[i]), let cl = number(closes[i]) else { fatalError("Invalid candle") }
                let shade = color(cl >= op ? "#dc2626" : "#16a34a")
                line(point(px, lo), point(px, hi), shade, 0.65)
                shade.setFill()
                let bodyWidth = max(0.6, min(5, plot.width / (xmax - xmin) * 0.58))
                NSRect(x: x(px) - bodyWidth / 2, y: min(y(op), y(cl)), width: bodyWidth, height: max(0.8, abs(y(cl) - y(op)))).fill()
            }
            continue
        }
        let ys = array(trace["y"])
        let custom = array(trace["customdata"])
        if kind == "fx" {
            let marker = dictionary(trace["marker"])
            let shade = color(marker["color"] as? String ?? "#b91c1c")
            let top = meta["type"] as? String == "top"
            let labels = array(trace["text"])
            for i in xs.indices {
                guard let px = number(xs[i]), let py = number(ys[i]) else { continue }
                let center = point(px, py), radius = 3.8
                let triangle = NSBezierPath()
                if top {
                    triangle.move(to: NSPoint(x: center.x - radius, y: center.y + radius)); triangle.line(to: NSPoint(x: center.x + radius, y: center.y + radius)); triangle.line(to: NSPoint(x: center.x, y: center.y - radius))
                } else {
                    triangle.move(to: NSPoint(x: center.x - radius, y: center.y - radius)); triangle.line(to: NSPoint(x: center.x + radius, y: center.y - radius)); triangle.line(to: NSPoint(x: center.x, y: center.y + radius))
                }
                triangle.close(); shade.setFill(); triangle.fill()
                if i < custom.count, let id = number(array(custom[i]).first) { actualFX.insert(Int(id)) }
                if trace["mode"] as? String == "markers+text", i < labels.count, let label = labels[i] as? String, !label.isEmpty {
                    text(label, max(plot.minX + 23, min(plot.maxX - 23, center.x)), center.y + (top ? 10 : -20), size: 9, shade: shade, center: true)
                }
            }
            continue
        }
        let path = NSBezierPath()
        var previousPresent = false
        for i in xs.indices {
            guard let px = number(xs[i]), i < ys.count, let py = number(ys[i]) else { previousPresent = false; continue }
            if previousPresent { path.line(to: point(px, py)) } else { path.move(to: point(px, py)) }
            previousPresent = true
            if i < custom.count, let id = number(array(custom[i]).first) {
                if kind == "bi" { actualBi.insert(Int(id)) }
                if kind == "xd" { actualXD.insert(Int(id)) }
            }
        }
        let stroke = dictionary(trace["line"])
        if kind == "merged" {
            color(trace["fillcolor"] as? String ?? "rgba(100,116,139,0.10)").setFill(); path.fill()
        }
        color(stroke["color"] as? String ?? "#64748b").setStroke()
        path.lineWidth = number(stroke["width"]) ?? 1.0; path.stroke()
        if kind == "xd" {
            for i in xs.indices {
                guard let px = number(xs[i]), let py = number(ys[i]) else { continue }
                let center = point(px, py)
                let circle = NSBezierPath(ovalIn: NSRect(x: center.x - 3.5, y: center.y - 3.5, width: 7, height: 7))
                circle.lineWidth = 1.2; circle.stroke()
            }
        }
    }
    // Source-price annotations (XD endpoints); use their true source coordinates.
    for item in array(layout["annotations"]) {
        let annotation = dictionary(item)
        guard annotation["yref"] as? String != "paper", let px = number(annotation["x"]), let py = number(annotation["y"]), let label = annotation["text"] as? String else { continue }
        let halfLabel = (label as NSString).size(withAttributes: [.font: NSFont.boldSystemFont(ofSize: 10)]).width / 2 + 3
        text(label, max(plot.minX + halfLabel, min(plot.maxX - halfLabel, x(px))), y(py) + (number(annotation["yshift"]) ?? 0) - 5, size: 10, shade: color("#6d28d9"), center: true, bold: true)
    }
    NSGraphicsContext.restoreGraphicsState()
    for item in array(layout["annotations"]) {
        let annotation = dictionary(item)
        guard annotation["yref"] as? String == "paper", let px = number(annotation["x"]), let label = annotation["text"] as? String else { continue }
        text(label, max(plot.minX, min(plot.maxX - 195, x(px))), plot.maxY + 8, size: 12, shade: color("#a16207"))
    }
    var lx = 82.0
    let ly = 54.0
    for trace in traces {
        guard let name = trace["name"] as? String else { continue }
        let kind = dictionary(trace["meta"])["kind"] as? String ?? ""
        let shade: NSColor
        if kind == "fx" { shade = color(dictionary(trace["marker"])["color"] as? String ?? "#b91c1c") }
        else if kind == "raw" { shade = color("#dc2626") }
        else { shade = color(dictionary(trace["line"])["color"] as? String ?? "#64748b") }
        let label = name.replacingOccurrences(of: "completed ·", with: "completed /")
        line(NSPoint(x: lx, y: ly + 6), NSPoint(x: lx + 23, y: ly + 6), shade, kind == "xd" ? 3.5 : 1.5)
        text(label, lx + 29, ly, size: 12)
        lx += Double(label.count) * 6.3 + 55
    }
    text("XD-P1 experimental profile · solid: snapshot-completed; amber: open tail · not CC output or author-unique proof", 82, 22, size: 12, shade: color("#64748b"))
    NSGraphicsContext.restoreGraphicsState()
    let output = charts.appendingPathComponent(page["png"] as! String)
    try save(image, output)
    let expectedFX = Set(array(page["fx_positions"]).compactMap { number($0).map(Int.init) })
    let expectedBi = Set(array(page["bi_positions"]).compactMap { number($0).map(Int.init) })
    let expectedXD = Set(array(page["xd_positions"]).compactMap { number($0).map(Int.init) })
    precondition(actualFX == expectedFX && actualBi == expectedBi && actualXD == expectedXD, "Source ID coverage differs")
    rendered.append(["png": page["png"]!, "width": width, "height": height, "fractal_ids": actualFX.sorted(), "bi_ids": actualBi.sorted(), "xd_ids": actualXD.sorted(), "source_arrays_exact": true, "viewport": [xmin,xmax,ymin,ymax]])
    print("Rendered \(pageIndex + 1)/\(manifest.count) \(page["png"]!)")
}
// Readable 2-by-3 contact sheets covering every rendered page; inspect key PNGs separately.
for begin in stride(from: 0, to: manifest.count, by: 6) {
    let subset = Array(manifest[begin..<min(begin + 6, manifest.count)])
    let contact = bitmap(1800, 1350)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: contact)
    NSColor.white.setFill(); NSRect(x: 0,y: 0,width: 1800,height: 1350).fill()
    for (i, page) in subset.enumerated() {
        let filename = page["png"] as! String
        guard let image = NSImage(contentsOf: charts.appendingPathComponent(filename)) else { fatalError("Missing rendered page") }
        let column = i % 2, row = i / 2
        image.draw(in: NSRect(x: column * 900, y: 1350 - (row + 1) * 450, width: 900, height: 450))
    }
    NSGraphicsContext.restoreGraphicsState()
    try save(contact, charts.appendingPathComponent(String(format: "contact-%02d.png", begin / 6 + 1)))
}
let report: [String: Any] = ["renderer": "Swift/AppKit exact source arrays; native static style", "pages": rendered, "count": rendered.count, "seconds": Date().timeIntervalSince(started), "contact_sheets": (manifest.count + 5) / 6, "visual_qa": "pending parent inspection"]
try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted,.sortedKeys]).write(to: charts.appendingPathComponent("render.json"))
