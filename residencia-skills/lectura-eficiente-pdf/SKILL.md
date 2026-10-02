---
name: lectura-eficiente-pdf
description: "Convierte PDF/DOCX/PPTX/XLSX a Markdown UNA sola vez con markitdown, lo guarda en disco, y usa grep por palabra clave (con marcadores de página y, si existen, bookmarks o encabezados) para leer SOLO la sección pedida — en vez de cargar el documento completo o rasterizar página por página. Úsala SIEMPRE que suban o mencionen un PDF, artículo, guía clínica, handbook, resolución, protocolo o presentación y pidan leerlo, resumirlo, extraer una parte (tratamiento, dosis, criterios diagnósticos, un algoritmo, una tabla) o usarlo como fuente para otra tarea — sobre todo si tiene muchas páginas o solo hace falta una parte. Es el primer paso antes de leer cualquier documento largo, aunque no se mencione 'tokens'. NO reemplaza la lectura visual de una página (rasterizarla e inspeccionarla como imagen) para figuras/tablas complejas/PDFs escaneados, ni a `pdf` para crear/combinar/dividir/rellenar/cifrar PDFs — esta decide CÓMO extraer y ubicar el texto barato antes de que esas otras entren a tallar."
---

# Lectura eficiente de documentos (PDF / DOCX / PPTX / XLSX)

## Por qué existe esta skill

Cargar un documento completo al contexto es caro y casi siempre innecesario:

- Texto plano de PDF: ~200–400 tokens/página . Una guía de 150 páginas (AHA/ACC, GOLD, Resolución 3280, un handbook propio) son 30.000–60.000 tokens solo por tenerla disponible, antes de razonar sobre ella.
- Rasterizar páginas como imagen: ~1.600 tokens/página. Nunca se debe hacer con el documento completo.
- La mayoría de los pedidos reales ("dame el tratamiento farmacológico", "los criterios diagnósticos", "el algoritmo de HTA resistente") solo necesitan 1–3 secciones, no el documento entero.

**El ahorro real no viene de una herramienta "mágica" más barata para extraer texto** — `pdftotext` y `markitdown` extraen texto a un costo por página similar; esto se verificó directamente y no hay que sobrevenderlo. El ahorro viene de un patrón de trabajo de dos pasos:

1. Convertir el documento a Markdown **una sola vez** y guardarlo en disco (esto no cuesta tokens de contexto, solo cómputo).
2. Buscar con `grep` dónde está lo que hace falta, y leer **solo esas líneas** — no el archivo completo.

Se usa `markitdown` como herramienta base porque da una interfaz única para PDF/DOCX/PPTX/XLSX/HTML (los cuatro formatos que maneja el usuario) y porque en DOCX/PPTX/XLSX sí reconstruye encabezados Markdown reales a partir de los estilos de Word/PowerPoint/Excel — un índice gratis. **Para PDF plano, markitdown NO reconstruye encabezados** (comprobado directamente convirtiendo un PDF de prueba): solo entrega el texto corrido, igual que `pdftotext`. En PDF, el ahorro depende 100% del patrón grep + lectura acotada, no de la herramienta de extracción.

## Cuándo usar esta skill vs. las otras de PDF

| Situación | Usa |
|---|---|
| Documento con texto (PDF/DOCX/PPTX/XLSX): extraer, resumir, usar una parte como fuente | **Esta skill**, primero y siempre |
| PDF escaneado (sin capa de texto), figuras, gráficas, tablas mal formadas, algoritmos que hay que VER | Rasterizar solo esa página (`pdftoppm -f N -l N -png -r 110 documento.pdf pag`) y mirarla con la herramienta de lectura de imágenes; en claude.ai, la skill `pdf-reading` si está instalada |
| Crear, combinar, dividir, rotar, marcar de agua, cifrar o rellenar formularios de PDF | `pdf` |

## Flujo de trabajo

### 1. Verificar/instalar dependencias (una vez por sesión)
```bash
pip show markitdown >/dev/null 2>&1 || pip install 'markitdown[pdf,docx,pptx,xlsx]' --break-system-packages
pip show pymupdf   >/dev/null 2>&1 || pip install pymupdf --break-system-packages
```
`pymupdf` es opcional: solo se usa para leer el índice/bookmarks embebido del PDF si existe. Si falla la instalación, el script sigue funcionando sin esa parte.

### 2. Convertir e indexar con el script incluido
```bash
python3 scripts/convertir_indexar.py /ruta/al/documento.pdf
```
Guarda `documento.md` junto al original e imprime un reporte corto: páginas, tamaño en tokens estimado si se leyera completo, índice/bookmarks del PDF si existen, y encabezados Markdown si existen (siempre para DOCX/PPTX/XLSX; a veces para PDF, si el PDF trae texto etiquetado).

**El reporte es lo único que debe llegar al chat en este paso — nunca imprimas ni leas con `view` el `.md` completo aquí.**

### 3. Ubicar la sección pedida según lo que reportó el script
- Si aparecieron **bookmarks** o **encabezados Markdown** → ya hay índice; ve directo a la sección con el número de página/línea que dio el reporte.
- Si no aparecieron (lo típico en PDF plano) → `grep -n -i "palabra_clave" documento.md` con los términos del pedido (ej. "tratamiento farmacológico", "criterios diagnósticos", "hipertensión resistente"). Usa `-B2 -A15` para ver contexto alrededor del match antes de decidir el rango exacto.
- El script inserta marcadores `<!-- página N -->` en los PDF, así se sabe en qué página física cae cada resultado — útil para citar la página o para decidir si conviene rasterizarla cuando el texto solo no basta (una tabla compleja, un algoritmo, una gráfica).

### 4. Leer SOLO el rango encontrado
```bash
sed -n '120,340p' documento.md
```
o la herramienta de lectura de archivos con rango de líneas (`view` con `view_range` en claude.ai; `Read` con `offset`/`limit` en Claude Code). No cargar el archivo completo, salvo que el usuario lo pida explícitamente o el documento sea corto (pocas páginas).

### 5. Iterar bajo demanda
Si después hace falta otra sección, repetir `grep`/`sed` sobre el mismo `.md` ya generado — no reconvertir el documento ni releer lo ya extraído.

## Limitaciones (decirlas, no ocultarlas)

- **Sin OCR automático**: si el PDF es escaneado (sin capa de texto), markitdown devuelve texto vacío o basura. Verificar con `pdffonts documento.pdf` (sin fuentes = escaneado) y usar el rasterizado por página (ver tabla de arriba) para esos casos.
- **Ciego a lo visual**: figuras, gráficas, ecuaciones, tablas complejas o algoritmos de flujo no se capturan bien como texto. Si el pedido depende de VER algo, rasterizar esa página puntual (ver tabla de arriba) — no el documento completo.
- **Espaciado irregular en PDF**: el texto justificado a veces hace que la extracción interprete espacios anchos como tabulaciones, lo que rompe búsquedas de frases completas. El script ya normaliza esto (`normalizar_espacios`); si se convierte un PDF por fuera del script, tenerlo en cuenta.
- El tamaño en tokens que imprime el script es una estimación aproximada (caracteres/4), no un conteo exacto.

## Notas

- El script funciona igual para `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html` — mismo comando, mismo flujo.
- Pensado para documentos de texto (guías, artículos, handbooks, resoluciones, protocolos). Para decks de diapositivas exportados a PDF donde el layout visual importa, sigue siendo mejor rasterizar las páginas relevantes.
