#!/usr/bin/env python3
"""
Convierte un documento (PDF, DOCX, PPTX, XLSX, HTML, etc.) a Markdown con
markitdown UNA sola vez, lo guarda en disco, e imprime un pequeño reporte
de orientación (páginas/diapositivas, marcadores/bookmarks si existen,
tamaño aproximado en tokens) sin volcar el contenido completo a pantalla.

Uso:
    python3 convertir_indexar.py <archivo_entrada> [archivo_salida.md]

Si no se da archivo de salida, se guarda junto al original con extensión .md
"""
import sys
import os
from pathlib import Path

def estimar_tokens(texto: str) -> int:
    # Estimación gruesa (no exacta): ~4 caracteres por token en español/inglés mixto.
    return len(texto) // 4

def extraer_marcadores_pdf(ruta_pdf: str):
    """Intenta extraer el índice/bookmarks embebido del PDF (gratis si existe)."""
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz  # nombre antiguo del paquete
        except ImportError:
            return None, None
    try:
        doc = fitz.open(ruta_pdf)
        toc = doc.get_toc()  # [[nivel, titulo, pagina], ...]
        num_paginas = doc.page_count
        return toc, num_paginas
    except Exception:
        return None, None

def normalizar_espacios(texto: str) -> str:
    """pdfminer (usado por markitdown para PDF) a veces interpreta los
    espacios anchos de texto justificado como caracteres TAB en vez de
    espacios simples. Eso rompe búsquedas de frases con grep (ej. buscar
    "hipertensión resistente" no encuentra "hipertensión\\tresistente").
    Colapsamos tabs/espacios múltiples a un solo espacio, preservando
    saltos de línea y la indentación inicial de cada línea (listas)."""
    import re
    lineas = texto.split("\n")
    normalizadas = []
    for linea in lineas:
        sangria = len(linea) - len(linea.lstrip(" "))
        cuerpo = re.sub(r"[ \t]+", " ", linea.strip(" \t"))
        normalizadas.append((" " * sangria) + cuerpo if cuerpo else "")
    return "\n".join(normalizadas)

def insertar_marcas_de_pagina(texto: str) -> str:
    """markitdown/pdfminer separan páginas de PDF con un carácter form-feed
    (\\f, chr(12)). Lo convertimos en un marcador legible y grep-eable para
    poder ubicar en qué página física está cada coincidencia de búsqueda."""
    partes = texto.split("\f")
    if len(partes) <= 1:
        return texto
    salida = [partes[0]]
    for i, parte in enumerate(partes[1:], start=2):
        salida.append(f"\n\n<!-- página {i} -->\n\n{parte}")
    return "".join(salida)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    entrada = sys.argv[1]
    if not os.path.exists(entrada):
        print(f"❌ No existe el archivo: {entrada}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        salida = sys.argv[2]
    else:
        salida = str(Path(entrada).with_suffix(".md"))

    from markitdown import MarkItDown
    md = MarkItDown(enable_plugins=False)
    resultado = md.convert(entrada)
    texto = resultado.markdown

    es_pdf = entrada.lower().endswith(".pdf")
    bookmarks, num_paginas = (None, None)
    if es_pdf:
        texto = normalizar_espacios(texto)
        texto = insertar_marcas_de_pagina(texto)
        bookmarks, num_paginas = extraer_marcadores_pdf(entrada)

    with open(salida, "w", encoding="utf-8") as f:
        f.write(texto)

    # --- Reporte (esto es lo único que debería imprimirse/leerse en el chat) ---
    print(f"✅ Convertido → {salida}")
    print(f"   Tamaño: {len(texto):,} caracteres  |  ~{estimar_tokens(texto):,} tokens si se leyera COMPLETO")
    if num_paginas:
        print(f"   Páginas del PDF: {num_paginas}")
    if bookmarks:
        print(f"   📑 Índice embebido encontrado ({len(bookmarks)} entradas):")
        for nivel, titulo, pagina in bookmarks:
            print(f"      {'  ' * (nivel - 1)}- {titulo} (pág. {pagina})")
    elif es_pdf:
        print("   (Este PDF no trae índice/bookmarks embebido — usa grep sobre palabras clave)")

    encabezados = [l for l in texto.split("\n") if l.strip().startswith("#")]
    if encabezados:
        print(f"   🔖 Encabezados Markdown detectados ({len(encabezados)}):")
        for h in encabezados[:40]:
            print(f"      {h.strip()}")
        if len(encabezados) > 40:
            print(f"      ... y {len(encabezados) - 40} más (usa grep -n '^#' {salida})")
    elif es_pdf:
        print("   (markitdown NO reconstruye encabezados para PDF plano — busca por palabra clave con grep)")

    print()
    print(f"➡ Siguiente paso: grep -n -i 'palabra_clave' {salida}   (o -B2 -A15 para ver contexto)")
    print(f"   Luego lee SOLO el rango de líneas relevante, no el archivo completo.")

if __name__ == "__main__":
    main()
