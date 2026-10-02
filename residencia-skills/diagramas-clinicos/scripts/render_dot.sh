#!/bin/bash
# render_dot.sh — renderiza un archivo .dot (Graphviz) a imagen.
#
# Por qué un script y no invocar `dot` directamente cada vez: para que el DPI
# y el formato sean consistentes en toda la skill sin que cada gráfico quede
# con una resolución distinta. Graphviz viene preinstalado en este entorno y
# no depende de un navegador headless (a diferencia de Mermaid CLI, que
# requiere Chrome y falla en sandboxes sin permisos de root) — por eso es el
# motor elegido para flujogramas y esquemas en esta skill.
#
# Uso:
#   ./render_dot.sh entrada.dot salida.png [dpi]
#   ./render_dot.sh entrada.dot salida.svg        (SVG no usa dpi, es vectorial)
#
# dpi por defecto: 200 (nítido en pantalla y en Word/PDF). Usar 300 si el
# destino es impresión o un póster.

set -euo pipefail

INPUT="$1"
OUTPUT="$2"
DPI="${3:-200}"

if [ ! -f "$INPUT" ]; then
  echo "Error: no existe el archivo $INPUT" >&2
  exit 1
fi

EXT="${OUTPUT##*.}"

case "$EXT" in
  svg)
    dot -Tsvg "$INPUT" -o "$OUTPUT"
    ;;
  png)
    dot -Tpng -Gdpi="$DPI" "$INPUT" -o "$OUTPUT"
    ;;
  pdf)
    dot -Tpdf "$INPUT" -o "$OUTPUT"
    ;;
  *)
    echo "Error: extensión '$EXT' no soportada (usa .png, .svg o .pdf)" >&2
    exit 1
    ;;
esac

echo "Generado: $OUTPUT"
