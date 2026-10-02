# Producción del archivo .pptx

Construir con `pptxgenjs` en Node, directamente — no partir de una plantilla y editar diapositiva
por diapositiva con `python-pptx`. Controlar cada elemento por posición absoluta da resultados más
limpios que intentar reutilizar layouts ajenos.

## Paleta y rejilla

- **Sin código de colores por tipo de diapositiva** (salvo que el usuario pida lo contrario): una
  paleta única — un color oscuro para texto/títulos, un acento positivo, un acento de alerta
  (distinto del color de marca institucional si existe, para no competir con él), gris para notas.
- `LAYOUT_WIDE` (13.33 × 7.5 in) salvo que el usuario indique otro formato.
- Título ≤10 palabras, máximo 6 bullets de 8-10 palabras.
- Franja de referencia al pie en fuente pequeña (10-12pt), discreta.

## Análisis de plantilla institucional (si el usuario adjunta una)

Nunca juzgar una plantilla solo por las miniaturas — analizarla:

1. **Descomprimir el .pptx** (`python3 -c "import zipfile; zipfile.ZipFile(...).extractall(...)"`)
   y revisar `ppt/slideLayouts/`, `ppt/slideMasters/`, `ppt/theme/theme1.xml` y `ppt/media/`.
2. **Extraer la paleta real**: grep de `<a:srgbClr val="...">` en el theme, y si el diseño usa una
   imagen de fondo de página completa (común en plantillas institucionales), muestrear píxeles con
   PIL para sacar el color exacto de marca (ej. rojo del encabezado) en vez de adivinarlo.
3. **Medir la zona segura real**, no asumirla: con PIL, escanear filas de píxeles desde arriba para
   encontrar dónde termina el color de encabezado, y desde abajo para encontrar dónde empieza el
   pie institucional. Convertir esa fracción a pulgadas sobre el tamaño real de diapositiva
   (`slide_height_in × fracción`). Dejar un margen de seguridad de ~0.15in extra.
4. **Revisar si "vacía" significa vacía de verdad**: mirar el texto de cada `slide{N}.xml` — es
   común encontrar contenido sobrante de una presentación anterior (cita, texto de ejemplo) en una
   plantilla que el usuario cree vacía. Si aparece, avisarle explícitamente antes de reutilizarla.
5. Si hay más de un layout (por ejemplo uno "en blanco" sin encabezado), guardarlo para las
   diapositivas de alto impacto (ver SKILL.md § Reglas de construcción).
6. Aplicar el fondo institucional en pptxgenjs como imagen de fondo de diapositiva completa
   (`slide.background = { path: "fondo.jpg" }`), nunca reconstruyendo el diseño con formas propias.

## Construcción con pptxgenjs

- Definir constantes `SAFE_TOP` / `SAFE_BOTTOM` (en pulgadas) una sola vez, calculadas del análisis
  anterior, y usarlas en *todas* las diapositivas — nunca coordenadas sueltas por diapositiva.
- **Regla de oro contra colisiones**: cualquier elemento a la derecha o al lado del título
  (gráfico, tarjeta, imagen) debe empezar **debajo** de la banda vertical del título
  (`SAFE_TOP + altura_del_título`), nunca a la misma altura que el título aunque parezca haber
  espacio horizontal libre — el texto del título puede ser más largo de lo previsto y solapar.
- Preferir **gráficos nativos** (`addChart`, tipo barra/columna) para series comparativas de
  porcentajes o cifras, en vez de imágenes estáticas — permiten etiquetas de dato automáticas y se
  ven mejor.
- Para mecanismos o procesos encadenados: cajas (`roundRect`) conectadas con líneas cortas
  (`addShape("line", ...)`) hacia un elemento central o de desenlace — construir esto con formas,
  no como imagen.
- Para frameworks de cuadrantes (ej. dimensiones de un modelo, comparaciones 2×2): grid de
  `roundRect` con texto dentro; si una categoría está deliberadamente incompleta o sin datos,
  dejar el cuadrante correspondiente vacío y con borde distinto en vez de rellenarlo con relleno
  — el vacío visual puede ser parte del mensaje.
- Diapositivas de alto impacto (ver SKILL.md): `slide.background = { color: "000000" }` (o un
  oscuro casi negro), sin imagen de fondo institucional, texto blanco centrado.

## Construcción pensando en Morph

Aprendido analizando tutoriales nativos de PowerPoint (ver
`diapositivas-dinamicas/references/tecnica-morph-real.md`): la transición Morph
de PowerPoint no es un efecto que se "activa" y ya — interpola las formas de
una diapositiva con las de la siguiente **comparando su nombre interno**
(atributo `name` en el XML, `<p:cNvPr name="...">`). Si dos formas en
diapositivas consecutivas tienen el mismo nombre, PowerPoint anima
posición/tamaño/color/rotación entre una y otra; si no, no hay Morph aunque la
transición esté puesta.

`pptxgenjs` permite fijar ese nombre con la opción `objectName` en `addShape`,
`addText` e `addImage`. Para dejar un par de diapositivas listo para Morph:

```js
// Diapositiva N — estado "antes"
slide1.addShape(pres.ShapeType.roundRect, {
  x: 0.8, y: 1.6, w: 2, h: 1.2,
  fill: { color: colorPrimario },
  objectName: "marcadorAlgoritmo",   // <- mismo nombre en las dos diapositivas
});

// Diapositiva N+1 — estado "después" (posición/tamaño/color distintos)
slide2.addShape(pres.ShapeType.roundRect, {
  x: 8.5, y: 4.5, w: 4, h: 2.2,
  fill: { color: colorAcento },
  objectName: "marcadorAlgoritmo",   // <- idéntico: esto es lo que activa Morph
});
```

Reglas prácticas:

- Usar `objectName` **solo** en los elementos que de verdad deben transformarse
  entre esas dos diapositivas (el marcador de paso actual en un algoritmo, el
  punto en una línea de tiempo, la franja resaltada de una escala clínica).
  El resto de elementos de la diapositiva (título, pie de referencia, logo) no
  necesitan nombre especial y no deben compartir `objectName` con nada — un
  nombre repetido sin intención produce un Morph que "salta" cosas que no
  deberían moverse.
- Elegir nombres descriptivos y únicos por concepto (`marcadorAlgoritmo`,
  `puntoLineaTiempo`, `franjaEscalaHTA`) — nunca genéricos como `shape1`, que
  podrían coincidir por accidente con otra forma sin relación en otra parte
  del deck.
- Dejarlo anotado en el Mapa de la presentación (ver SKILL.md) para que la
  Fase 4 sepa exactamente en qué diapositiva de llegada activar
  `pptx_dinamizar.py --morph-en`.
- Esto es aparte del control de calidad normal: un par con `objectName`
  correcto pero con colisión de texto sigue siendo un error que hay que
  corregir en la revisión visual de abajo.

## Control de calidad obligatorio (no es opcional)

Después de generar el `.pptx`:

1. **Validar la estructura**: `python <ruta-skill-pptx>/scripts/office/validate.py archivo.pptx`
2. **Convertir a imágenes para revisión visual**:
   ```
   python <ruta-skill-pptx>/scripts/office/soffice.py --headless --convert-to pdf archivo.pptx
   pdftoppm -jpeg -r 100 archivo.pdf slide
   ```
3. **Mirar cada diapositiva** (o al menos todas las que tengan gráficos, imágenes o texto denso
   cerca del título) con la herramienta de visualización de imágenes. Buscar específicamente:
   texto de título solapado con contenido lateral, imágenes que invaden el pie institucional,
   pies de cita que chocan con badges/logos de la plantilla.
4. **Corregir cualquier colisión encontrada** y repetir el ciclo build → validar → convertir →
   mirar hasta que quede limpio. No se entrega un .pptx que no se ha visto renderizado.
5. **Grep de contenido** buscando placeholders olvidados antes de entregar:
   ```
   markitdown archivo.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|TODO|\[insert"
   ```

## Entrega

Copiar a la carpeta de salida del entorno (`/mnt/user-data/outputs/` en claude.ai; carpeta del proyecto en Claude Code/Cowork) y entregar con la herramienta de envío de archivos disponible (`present_files` o `SendUserFile`). `<ruta-skill-pptx>` es el directorio base que muestra la skill `pptx` al cargarse (en claude.ai: `/mnt/skills/public/pptx`). Si el usuario pidió también el
guion en texto, ese va aparte en el chat o en un `.md`, no dentro del `.pptx`.
