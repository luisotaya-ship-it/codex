# Bancos de imágenes — cuál usar según la categoría

Ver `SKILL.md § Paso 2` para las tres categorías (1: hallazgo clínico real,
2: escena/contexto humano, 3: decorativo/conceptual). Esta tabla amplía el
Paso 3 con las fuentes concretas.

**Wikimedia Commons y NLM Open-i tienen API y ya están automatizados** en
`scripts/buscar_y_descargar.py` (búsqueda + verificación de licencia +
descarga en un solo comando — ver `SKILL.md § Paso 3.1-3.2`). Para el resto
de bancos de esta tabla no hay atajo: hay que abrir la página con
`web_fetch` y descargar con `bash_tool` como se describe más abajo.

## Bancos médicos de acceso abierto (categoría 1 y 2)

| Banco | URL | Qué tiene | Licencia |
|---|---|---|---|
| CDC Public Health Image Library (PHIL) | https://phil.cdc.gov | Fotografía clínica, microbiología, salud pública, brotes | Dominio público salvo que la ficha de la imagen indique lo contrario — revisar siempre la ficha individual |
| NLM Open-i | https://openi.nlm.nih.gov | Motor de búsqueda de imágenes biomédicas de artículos de PubMed Central — permite buscar por hallazgo clínico y trae la cita del artículo de origen | Varía por imagen (heredada del artículo); Open-i muestra la licencia de cada resultado — verificarla antes de usar |
| Wikimedia Commons | https://commons.wikimedia.org | Fotografía clínica, anatómica, de equipos, escenas — volumen enorme | Filtrar SIEMPRE por categoría de licencia (CC0, CC-BY, dominio público); ignorar cualquier imagen sin licencia clara en la página del archivo |
| NCI Visuals Online | https://visualsonline.cancer.gov | Fotografía e ilustración oncológica del National Cancer Institute | Dominio público (uso gubernamental de EE. UU.) |
| MedlinePlus / NLM Images | https://medlineplus.gov | Ilustraciones y fotografía educativa para pacientes | Uso educativo; verificar ficha antes de reutilizar en material que se distribuye fuera de la consulta |
| OMS / WHO Multimedia | https://www.who.int/multimedia | Fotografía de salud pública global, brotes, campañas | Verificar términos de uso de la OMS en cada pieza — algunas requieren atribución explícita |
| StatPearls / NCBI Bookshelf | https://www.ncbi.nlm.nih.gov/books/ | Ilustraciones y fotografía clínica dentro de capítulos de referencia | Muchos capítulos son CC-BY (NCBI Bookshelf lo indica); confirmar en cada capítulo |
| OpenStax (Anatomy & Physiology) | https://openstax.org | Ilustración anatómica de calidad editorial | CC-BY — atribuir según su guía |

Nota sobre Radiopaedia (https://radiopaedia.org): tiene un archivo enorme de
casos radiológicos reales, pero la mayoría de las imágenes son
**CC-BY-NC-SA** (no comercial, compartir igual) y muchas veces con
condiciones adicionales del caso — válido para una gran sesión académica sin
fines comerciales, pero **siempre** con atribución visible al caso y al
autor, y nunca en material que se vaya a vender o usar comercialmente.
Revisar la licencia de cada caso puntual antes de usar.

## Bancos de fotografía libre (categoría 2, escenas sin pretensión clínica)

| Banco | URL | Licencia |
|---|---|---|
| Unsplash | https://unsplash.com | Licencia Unsplash — uso libre, no requiere atribución (buena práctica citarla igual) |
| Pexels | https://www.pexels.com | Licencia Pexels — uso libre, no requiere atribución |
| Pixabay | https://pixabay.com | Licencia Pixabay — uso libre; revisar que la pieza puntual no tenga restricción marcada por el autor |

Estos bancos son buenos para "paciente genérico en sala de espera",
"consulta médica", "familia acompañando a adulto mayor" — nunca para un
hallazgo clínico específico que deba ser diagnósticamente fiel (eso es
categoría 1, arriba).

## Descarga manual para los bancos sin API (web_fetch/WebFetch + terminal)

Estos bancos no tienen un endpoint tan directo como Commons/Open-i, pero
igual se puede automatizar la descarga (no solo "mírala y cópiala a mano"):

**CDC PHIL** — cada imagen tiene una página de detalle
`https://phil.cdc.gov/Details.aspx?pid=<ID>`. Con `web_fetch` a esa página se
obtiene el enlace directo de descarga (termina en `.jpg`); descargarlo luego
con `bash_tool`:
```bash
curl -sL -A "Mozilla/5.0" -o <carpeta-de-trabajo>/imagenes_descargadas/nombre.jpg "<URL directa .jpg encontrada>"
```

**Unsplash / Pexels / Pixabay** — la página de la foto trae una etiqueta
`<meta property="og:image" content="...">` con la URL directa del archivo
(CDN de cada banco: `images.unsplash.com/...`, `images.pexels.com/...`,
`cdn.pixabay.com/...`). Procedimiento:
1. `web_fetch` a la página de la foto (la que se obtuvo por `image_search` o
   navegando el banco).
2. Localizar la URL del `og:image` en el HTML devuelto.
3. Descargar esa URL directa con `bash_tool`:
   ```bash
   curl -sL -A "Mozilla/5.0" -o <carpeta-de-trabajo>/imagenes_descargadas/nombre.jpg "<URL del og:image>"
   ```
4. Verificar que el archivo descargado es una imagen real antes de usarlo:
   ```bash
   python3 -c "from PIL import Image; im = Image.open('nombre.jpg'); print(im.size, im.mode)"
   ```

Estos tres bancos tienen licencia de uso libre por defecto (ver tabla
arriba), así que aquí el paso de verificación es sobre todo confirmar que la
página no marca una restricción puntual del autor, no clasificar el tipo de
licencia como sí hay que hacer con Commons/Open-i.

## Cómo verificar la licencia de una imagen puntual antes de insertarla

1. Nunca insertar directamente una imagen que viene de un resultado de
   búsqueda general (Google Imágenes y similares) sin visitar la página de
   origen.
2. Abrir la página de origen con la herramienta de lectura web y buscar
   explícitamente el término de licencia: "public domain", "CC0", "CC-BY",
   "royalty-free", "Creative Commons" son señales de vía libre (revisando si
   piden atribución). "All rights reserved", "Getty Images", "Shutterstock",
   "AP Images", "© [medio de prensa]", o un aviso de copyright de una
   revista/journal son señal de descartar la imagen.
3. Si la página no deja claro el estado de licencia, tratarla como protegida
   por defecto y no usarla — no asumir que "está en internet" equivale a
   libre de derechos.
4. Guardar el enlace de origen y el tipo de licencia para el registro de
   fuentes que se entrega junto con el `.pptx` (ver `SKILL.md § Paso 7`).

## Cuando ningún banco da un resultado adecuado

Generar con IA (categorías 2 y 3 únicamente — nunca categoría 1) usando el
motor vectorial/programático descrito en `imagenes-creativas-medicas`, o el
motor de generación de imágenes disponible en el entorno. Mantener el mismo
criterio de seriedad clínica que esa skill ya aplica: nada de estilo
"cartoon" o amateur salvo que el contenido sea explícitamente para pacientes
pediátricos, y nunca representar un rostro identificable como si fuera un
paciente real.
