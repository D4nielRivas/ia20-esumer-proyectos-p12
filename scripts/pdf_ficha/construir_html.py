"""README.md de P12 -> HTML con portada, listo para imprimir con Chrome sin interfaz.

Uso: python3 -I construir_html.py <README.md> <salida.html>
Requiere Python-Markdown 3.7 (pip install markdown==3.7).
"""
import html
import re
import sys

import markdown

src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().split("\n")

title = lines[0].lstrip("# ").strip()            # Proyecto 12 · Del chat a la comanda
num, name = [t.strip() for t in title.split("·", 1)]
kicker = lines[2].strip("* ")
subtitle = lines[4].strip("* ")
# tabla de chips: encabezado en la línea 8, valores en la 10
heads = [c.strip() for c in lines[8].strip("|").split("|")]
vals = [c.strip() for c in lines[10].strip("|").split("|")]
chips = "".join(
    f'<span class="chip">{html.escape(h)}{" " if h == "Dificultad" else ": "}{html.escape(v)}</span>'
    for h, v in zip(heads, vals))

body_start = next(i for i, l in enumerate(lines) if l.startswith("## Ficha técnica"))
body = "\n".join(lines[body_start + 1:])
body_html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists"])
# la primera tabla es la ficha técnica: encabezado morado con el título de la sección
body_html = body_html.replace(
    "<table>\n<thead>\n<tr>\n<th>Campo</th>\n<th>Detalle</th>",
    '<table class="ficha">\n<thead>\n<tr>\n<th>Ficha técnica</th>\n<th></th>', 1)

css = """
@page { size: Letter; margin: 0.75in 0.75in 0.9in 0.75in; }
body { font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.55; color: #24292f; }
.cover { background: #f0effb; border-left: 6px solid #5b4fd1; padding: 22px 26px 18px; margin-bottom: 12px; }
.kicker { letter-spacing: .18em; font-size: 9pt; color: #57606a; text-transform: uppercase; }
.num { color: #5b4fd1; font-weight: 700; font-size: 15pt; margin-top: 14px; }
.name { font-size: 27pt; font-weight: 800; margin: 0 0 8px; line-height: 1.15; }
.sub { color: #444; font-size: 12pt; margin-bottom: 12px; }
.chip { display: inline-block; border: 1px solid #5b4fd1; color: #4a3fc0; border-radius: 14px;
        padding: 2px 11px; margin: 0 6px 6px 0; font-size: 9.5pt; }
h2 { font-size: 16pt; border-bottom: 1px solid #d0d7de; padding-bottom: 4px; margin-top: 26px; page-break-after: avoid; }
h3 { font-size: 13pt; margin-top: 20px; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 9pt; }
th, td { border: 1px solid #d0d7de; padding: 6px 8px; text-align: left; vertical-align: top; }
thead { display: table-header-group; }
th { background: #f6f8fa; font-weight: 600; }
tr { page-break-inside: avoid; }
table.ficha th { background: #5b4fd1; color: white; }
table.ficha td:first-child { font-weight: 600; width: 22%; }
code { font-family: Menlo, monospace; font-size: 8.8pt; background: #eff1f3; padding: 1px 4px; border-radius: 4px; }
pre { background: #f6f8fa; padding: 10px 12px; border-radius: 6px; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { background: #f5f5fb; border-left: 4px solid #b8b2ec; margin: 12px 0; padding: 8px 16px; }
a { color: #4a3fc0; text-decoration: none; }
a code { color: #4a3fc0; }
li::marker { color: #5b4fd1; }
hr { border: none; border-top: 1px solid #d0d7de; }
"""
doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>{css}</style></head><body>
<div class="cover"><div class="kicker">{html.escape(kicker)}</div>
<div class="num">{html.escape(num)}</div><div class="name">{html.escape(name)}</div>
<div class="sub">{html.escape(subtitle)}</div><div>{chips}</div></div>
{body_html}
</body></html>"""
open(out, "w", encoding="utf-8").write(doc)
print("ok", len(doc))
