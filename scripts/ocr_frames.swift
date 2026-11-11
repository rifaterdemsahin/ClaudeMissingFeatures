// macOS Vision OCR. Usage: ocr_frames in_dir out.json   -> {"0001.jpg":[{"t":text,"x":..,"y":..,"w":..,"h":..}]} in pixels, origin top-left
import Foundation
import Vision
import AppKit
let dir = CommandLine.arguments[1], out = CommandLine.arguments[2]
let files = try! FileManager.default.contentsOfDirectory(atPath: dir).filter { $0.hasSuffix(".jpg") }.sorted()
var result: [String: [[String: Any]]] = [:]
for f in files {
    guard let img = NSImage(contentsOfFile: dir + "/" + f), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNRecognizeTextRequest(); req.recognitionLevel = .accurate; req.usesLanguageCorrection = false
    try? VNImageRequestHandler(cgImage: cg).perform([req])
    result[f] = (req.results ?? []).compactMap { o in
        guard let c = o.topCandidates(1).first else { return nil }
        let b = o.boundingBox
        return ["t": c.string, "x": b.minX * W, "y": (1 - b.maxY) * H, "w": b.width * W, "h": b.height * H]
    }
}
try! JSONSerialization.data(withJSONObject: result).write(to: URL(fileURLWithPath: out))
print("ocr", files.count, "frames")
