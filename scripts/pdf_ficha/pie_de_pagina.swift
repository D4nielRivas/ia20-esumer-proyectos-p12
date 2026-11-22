// Uso: swift pie_de_pagina.swift <entrada.pdf> <salida.pdf> "<título>"
// Agrega el pie «IA20 · Esumer · <título> · Página N de M» y los metadatos Title y Creator.
import PDFKit
import AppKit
let a = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: a[1]))!
let out = NSMutableData()
var box = doc.page(at: 0)!.bounds(for: .mediaBox)
let ctx = CGContext(consumer: CGDataConsumer(data: out as CFMutableData)!, mediaBox: &box,
  [kCGPDFContextTitle: a[3], kCGPDFContextCreator: "IA20 · Esumer"] as CFDictionary)!
let n = doc.pageCount
let font = NSFont.systemFont(ofSize: 8)
let attrs: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: NSColor(white: 0.3, alpha: 1)]
for i in 0..<n {
  let p = doc.page(at: i)!
  var mb = p.bounds(for: .mediaBox)
  ctx.beginPage(mediaBox: &mb)
  p.draw(with: .mediaBox, to: ctx)
  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = NSGraphicsContext(cgContext: ctx, flipped: false)
  let left = NSAttributedString(string: "IA20 · Esumer · " + a[3], attributes: attrs)
  left.draw(at: NSPoint(x: 54, y: 34))
  let right = NSAttributedString(string: "Página \(i+1) de \(n)", attributes: attrs)
  right.draw(at: NSPoint(x: mb.width - 54 - right.size().width, y: 34))
  NSGraphicsContext.restoreGraphicsState()
  ctx.endPage()
}
ctx.closePDF()
out.write(toFile: a[2], atomically: true)
print("páginas", n)
