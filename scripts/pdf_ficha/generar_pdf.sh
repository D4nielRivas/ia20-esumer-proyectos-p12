#!/bin/sh
# Regenera docs/proyecto-12-del-chat-a-la-comanda.pdf desde README.md.
# Uso, desde la raíz del repositorio: sh scripts/pdf_ficha/generar_pdf.sh
# Requiere macOS con Google Chrome, Swift (Xcode Command Line Tools) y Python 3.
set -eu
RAIZ=$(pwd)
TMP=$(mktemp -d)
python3 -m venv "$TMP/venv"
"$TMP/venv/bin/pip" -q install markdown==3.7
"$TMP/venv/bin/python" -I scripts/pdf_ficha/construir_html.py README.md "$TMP/ficha.html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$TMP/sin_pie.pdf" "file://$TMP/ficha.html"
swift scripts/pdf_ficha/pie_de_pagina.swift "$TMP/sin_pie.pdf" \
  "$RAIZ/docs/proyecto-12-del-chat-a-la-comanda.pdf" "Proyecto 12 · Del chat a la comanda"
rm -rf "$TMP"
echo "Listo: docs/proyecto-12-del-chat-a-la-comanda.pdf"
