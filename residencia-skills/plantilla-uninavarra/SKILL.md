---
name: "plantilla-uninavarra"
description: "Genera diapositivas .pptx con la plantilla institucional oficial de Fundación Universitaria Navarra (UNINAVARRA) — fondo blanco con banda roja superior (logo + escudo + banner de campaña vigente), escudo de león en marca de agua tenue al centro y pie institucional — reproduciendo el calibre visual y de contenido de las mejores \"gran sesión\" de residencia del usuario: títulos narrativos, infografía o diagrama custom por diapositiva (no viñetas planas), cita de evidencia en el pie y guion de orador en notas. ACTÍVALA si el usuario pide la plantilla UNINAVARRA, el fondo institucional de su universidad, que las diapositivas se vean \"como mis gran sesión anteriores\", menciona archivos como \"diabetes gestacional.pptx\" u \"osteoporosis.pptx\" como referencia de estilo, o nombra esta skill. NO se activa solo por pedir \"diapositivas\" genéricas — para eso usa presentaciones-cientificas; esta es la capa visual/institucional que se suma encima."
---

## Qué es esto y de dónde sale

Analizando cuatro presentaciones reales del usuario (síndrome de Cushing, diabetes
gestacional, osteoporosis, EPOC y salud mental) se confirmó que las cuatro comparten,
byte a byte, el mismo fondo institucional: un JPG aplicado como fondo del patrón de
diapositivas (`slideMaster`), con banda roja institucional arriba (logo + escudo
Fundación Universitaria Navarra + banner de campaña vigente), escudo de león en marca de
agua muy tenue al centro, y franja de datos de contacto + hashtag institucional abajo.
Ese fondo es lo que le da a cualquier deck, incluso uno con contenido sencillo, la
apariencia de "gran sesión" oficial de la universidad — y es el elemento que esta skill
reproduce.

Lo segundo que distingue a las mejores diapositivas del usuario (diabetes gestacional y
Cushing por encima de osteoporosis, que es notablemente más plana y bulleteada) no es la
plantilla sino la densidad de **infografía propia**: cada diapositiva de peso resuelve su
contenido con un diagrama, embudo, línea de tiempo, gauge, tabla de puntajes o figura
anatómica hecha a la medida — casi nunca con una caja de viñetas suelta. Reproducir solo
el fondo sin esto da un deck con cara de "residencia" pero contenido de "clase plana"; las
dos partes de esta skill (plantilla + arquitectura de contenido) van juntas.

## 1. Conseguir el fondo institucional

Se verificó una copia OFICIAL del fondo directamente de un archivo entregado por la
universidad (`PLANTILLA UNINAVARRA 2025 VACIO.pptx`). **Importante — ese archivo NO
estaba realmente vacío**: traía 31 diapositivas de una gran sesión previa sobre
estreñimiento crónico y 2 imágenes sueltas sin relación (mapa mundial de esperanza de
vida, foto de dolor abdominal). El usuario confirmó extraer solo el diseño y descartar
ese contenido — nunca reutilices un `.pptx` que el usuario llame "plantilla vacía" sin
abrirlo primero y revisar si de verdad está vacío.

De ese archivo se extrajo el fondo real, en 5000×3750px (banner de campaña "Vagón EDI"):

```
gran sesion/Plantilla_UNINAVARRA_fondo_2025.jpg
```

Pídele al usuario que guarde esa imagen en su carpeta de trabajo `gran sesion/` si no
está ahí. (Una versión anterior de esta skill apuntaba a
`gran sesion/Plantilla_UNINAVARRA_fondo.jpg`, extraída de decks de residentes en
4000×3000px — mismo diseño, menor resolución. Usa la versión `_2025` de aquí en
adelante por ser la fuente más reciente y de mayor calidad.)

Si necesitas volver a extraerlo de cualquier `.pptx` de gran sesión del usuario (todos
comparten el mismo fondo):

```bash
python3 -c "import zipfile; zipfile.ZipFile('cualquier_gran_sesion.pptx').extract('ppt/media/image1.jpg', 'fondo_extraido')"
```

Si el usuario menciona que la universidad cambió de plantilla o de campaña institucional
(el banner rojo superior derecho cambia de semestre a semestre), pide que suba un
`.pptx` reciente y repite la extracción en vez de asumir que el archivo guardado sigue
vigente.

## 2. Aplicar el fondo (pptxgenjs)

Fija el layout ancho **antes** de crear diapositivas y asigna el fondo a cada una — no
hay forma de ponerlo una sola vez a nivel de presentación en pptxgenjs:

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333in x 7.5in — confirmado en el archivo oficial 2025

const FONDO = "gran sesion/Plantilla_UNINAVARRA_fondo_2025.jpg";

function nuevaDiapositiva() {
  const slide = pres.addSlide();
  slide.background = { path: FONDO };
  return slide;
}
```

Un deck de referencia (síndrome de Cushing) tenía el lienzo en 17.78×10in en vez de
13.333×7.5in — es una inconsistencia de ese archivo, no el estándar; no la repitas.

## 3. Zona segura de contenido

El fondo no es decorativo del todo: tiene texto real (contacto, hashtag, banner de
campaña) que no debe taparse. Estas coordenadas se re-verificaron directamente contra el
archivo oficial 2025 (escaneo de píxeles con PIL, más la posición real de la caja de
cita de evidencia en diapositivas reales del archivo: `top=7.06in` y `top=7.08in`) —
coinciden con lo medido en los 4 decks de residentes analizados previamente, así que
quedan confirmadas con dos fuentes independientes:

| Zona | Rango vertical | Notas |
|---|---|---|
| Banda roja (logo + campaña) | 0 – 1.4in | Color exacto verificado: `#DB0C20` (RGB 219,12,32). No pongas contenido aquí, ya trae el logo |
| **Contenido principal** | **1.45in – 7.0in** | Título, cuerpo, imágenes |
| Franja de cita de evidencia | 7.05in – 7.45in | Confirmado con cajas de texto reales del archivo oficial (7.06–7.08in) |
| Pie institucional (contacto/hashtag) | ya incluido en el fondo | No lo reproduzcas, ya está en la imagen |

Horizontal: márgenes de 0.5–0.6in a cada lado para texto; las imágenes de contenido
pueden llegar hasta el borde (varios decks analizados usan `left: 0`) siempre que no
invadan la franja de cita. La franja de cita, en cambio, sí debe dejar libres los extremos
(≈1.3in–11.8in) porque el hashtag institucional vive en la esquina inferior izquierda y
los datos de contacto en la inferior derecha, dentro del propio fondo.

Tamaño de lienzo confirmado en el archivo oficial 2025: `12192000×6858000 EMU` = exactamente
`13.333×7.5in` (16:9, `LAYOUT_WIDE` de pptxgenjs) — coincide con el estándar ya documentado.

## 4. Tipografía observada

| Elemento | Fuente | Tamaño | Estilo |
|---|---|---|---|
| Título de diapositiva | Arial | 36–40pt | Negrita, color oscuro (no negro puro: `0E2841` o similar navy funcionó bien) |
| Cuerpo / etiquetas | Arial | 14–20pt según densidad | — |
| Cita de evidencia (pie) | Trebuchet MS (o Arial si priorizas que el QA de LibreOffice sea confiable) | 8pt | Regular, autor(es) en texto normal, revista en cursiva |

La cita al pie sigue el mismo patrón en las cuatro presentaciones: `Autor(es) et al.
Título del artículo. Revista, año; volumen(número): páginas. DOI o URL.` — una línea por
diapositiva, sin numerar, en la franja de 7.05–7.45in. Esto es lo que sostiene la promesa
de "medicina basada en evidencia" del usuario a nivel visual: cada afirmación clínica
fuerte que aparece en una diapositiva debe poder rastrearse a esa línea.

No inventes la referencia para llenar la línea — si no tienes la cita real (guía, revisión
sistemática, ensayo, texto de referencia), dilo explícitamente en vez de poner una fuente
genérica o inventada; esto aplica el mismo filtro de realidad que ya sigues para todo
contenido clínico de este usuario.

## 5. Arquitectura de contenido por diapositiva

Esto es lo que separa un deck "de calibre" de uno plano. En vez de título + viñetas,
cada diapositiva de contenido clínico se resuelve con **uno** de estos patrones, tomados
directamente de los cuatro decks analizados. Varía el patrón entre diapositivas
consecutivas — no repitas el mismo dos veces seguidas. **Regla de densidad**: cada patrón
lleva como máximo 1 imagen/diagrama de apoyo y hasta 4 puntos de texto visibles a la vez
— si un contenido realmente necesita 2-3 imágenes (comparar patrones, leve/moderado/severo)
o más puntos, no los amontones en la misma diapositiva: anótalo para que la fase de
`diapositivas-dinamicas` los reparta con revelado progresivo (`.html`, fragmentos reales
de reveal.js) o con secuencia de Morph (`.pptx`, varias diapositivas encadenadas que
acumulan un elemento por paso) — ver `diapositivas-dinamicas/references/integracion.md §
Caso 1d`. Una diapositiva con 3 fotos y varios bullets a la vez se siente "cargada" sin
importar cuánto se cuide el resto del formato institucional.

- **Portada**: título narrativo (no solo el nombre de la enfermedad — p. ej. "Respirar en
  el vacío: la experiencia emocional en pacientes con EPOC" en vez de "EPOC y salud
  mental"), nombre(s) del residente, "Residente de I año Medicina Familiar", año.
- **Epidemiología con cifra grande**: 1-2 estadísticos en tipografía de 48-60pt con
  etiqueta pequeña debajo, casi sin texto de relleno (ej. "88% de la diabetes en el
  embarazo corresponde a Diabetes Gestacional").
- **Definición como ecuación visual**: conceptos conectados con flechas/signos (+, →) en
  vez de una lista, cuando la definición tiene 2-4 componentes que se combinan.
- **Fisiopatología como eje o cascada**: diagrama de flujo vertical u horizontal
  (hormona → receptor → efecto → retroalimentación), nunca un párrafo corrido.
  Genera este tipo de diagrama con la skill `diagramas-clinicos` en vez de describirlo en
  texto — es exactamente el uso que esa skill espera.
- **Factores de riesgo en tarjetas por categoría**: tarjetas de color por categoría
  (maternos / metabólicos-genéticos / obstétricos, o genéticos / historia reproductiva /
  estilo de vida), cada una con su ícono.
- **Algoritmo diagnóstico tipo embudo o flowchart**: "Fase 1: sospecha → Fase 2:
  confirmación → Fase 3: localización", con la regla de oro (umbral, valor de corte)
  resaltada aparte del flujo, no enterrada en el texto.
- **Umbrales o dosis en gauges/tablas**: valores de corte de laboratorio como
  medidores tipo velocímetro (ayuno, 1h, 2h postcarga) o tabla de dosis por semana
  gestacional/peso — nunca una lista de números sueltos.
- **Ruta de atención / síntesis final como timeline circular**: pasos numerados
  conectados en línea de tiempo (evaluación → diagnóstico → intervención →
  seguimiento → alta), casi siempre la última diapositiva de contenido antes de
  "Gracias".
- **Complicaciones por sistema sobre figura anatómica**: silueta corporal con
  callouts de color agrupados por sistema (cardiovascular, metabólico, renal-infeccioso,
  obstétrico).
- **Instrumento de tamizaje reproducido fielmente**: si el tema incluye una escala
  validada (PHQ-9, GAD-7, Zung, DSM-5, FRAX, etc.), reproduce la tabla real de la escala
  con su sistema de puntuación e interpretación — no la resumas en prosa. Cítala.
- **Slide humanístico/narrativo (solo si el tema lo amerita)**: en el deck de EPOC y
  salud mental, las diapositivas emocionales usan foto a sangre completa + cita textual
  de paciente en cuadro tipo bocadillo, para conectar antes de volver a lo clínico. Úsalo
  con moderación y solo en temas donde el impacto psicosocial es parte del contenido
  (salud mental, cuidados paliativos, enfermedad crónica con alta carga emocional) — no lo
  fuerces en un tema puramente técnico como dosis de insulina.

Para cualquiera de estos patrones que requiera un diagrama, ícono compuesto, gauge o
figura (la mayoría), usa la skill `diagramas-clinicos` para generar la imagen real en vez
de intentar construirla con formas nativas de pptxgenjs o, peor, solo describirla en
texto. Los cuatro decks analizados casi no tienen diagramas hechos con autoformas: son
imágenes PNG insertadas (16 a 61 por deck) — ese es precisamente el motivo por el que se
ven pulidos.

## 6. Notas del orador

Cada diapositiva de los decks analizados trae notas de orador extensas — el guion real
que dice el residente, no un resumen. Escribe las notas con `slide.addNotes(...)`
(texto plano) cubriendo qué decir, no solo qué está escrito en pantalla. Si el usuario ya
generó este guion con `presentaciones-cientificas`, reutilízalo aquí en vez de
reescribirlo.

## 7. Flujo de trabajo sugerido

1. Si el contenido clínico (definición, epidemiología, fisiopatología, diagnóstico,
   tratamiento, evidencia) todavía no existe, consíguelo primero — con
   `presentaciones-cientificas` si el usuario solo dio el tema, o con lo que el usuario ya
   traiga escrito. Esta skill no reemplaza la investigación de evidencia ni las reglas de
   etiquetado [Evidencia]/[Inferencia]/[Especulación]/[No verificado] que ya sigues para
   este usuario — solo decide cómo se ve.
2. Mapea cada bloque de contenido a uno de los patrones de la sección 5. Si un tema no
   encaja en ninguno, no fuerces el patrón: una diapositiva de texto limpio con buena
   jerarquía tipográfica es preferible a un diagrama forzado que no aporta.
3. Construye el `.pptx` con pptxgenjs aplicando fondo + zona segura + tipografía de las
   secciones 2-4, generando las imágenes de apoyo con `diagramas-clinicos` según se
   necesiten.
4. Añade la cita de evidencia real en el pie de cada diapositiva con contenido clínico
   sustantivo, y el guion de orador en las notas.
5. Corre el QA de la skill `pptx` (`scripts/office/validate.py`, conversión a imágenes,
   inspección visual) — presta especial atención a que ningún texto invada la franja de
   cita (7.05–7.45in) ni la banda roja superior, y a que el texto tenga contraste
   suficiente sobre las zonas donde el fondo es blanco vs. donde se acerca a la marca de
   agua del león.
6. Si el usuario pide que además se vea "dinámico" (transiciones, profundidad, revelado
   progresivo de imágenes, versión HTML), encadena `diapositivas-dinamicas` al final —
   esta skill no toca animaciones ni transiciones.

## Qué NO hacer

- No regeneres el fondo institucional con un rectángulo rojo genérico "parecido" — usa el
  archivo real. El logo, el escudo y el pie tienen texto legal (NIT, vigilancia
  Mineducación) que no puedes recrear de memoria sin arriesgarte a errores.
- No llenes la franja de cita con una referencia inventada o genérica solo por
  completar el formato — repórtalo como fuente pendiente si no la tienes.
- No uses el patrón de "título + viñetas" como default; resérvalo para los pocos casos
  donde de verdad no hay nada que diagramar.
- No repitas el mismo patrón de diapositiva dos veces seguidas — los decks analizados
  alternan constantemente y eso es parte de lo que se percibe como "buen calibre".
- No amontones 2+ imágenes o más de 4 puntos de texto en una sola diapositiva "porque
  ya vienen los datos" — repártelos con revelado progresivo (ver sección 5) en vez de
  entregar una diapositiva cargada solo por evitar un paso extra.
- No reutilices un archivo que el usuario llame "plantilla vacía" como base de una
  presentación nueva sin abrirlo primero y revisar si de verdad está vacío — el archivo
  `PLANTILLA UNINAVARRA 2025 VACIO.pptx` analizado para esta skill traía 31 diapositivas
  completas de un tema no relacionado y 2 imágenes sueltas de otra presentación distinta
  todavía. Extrae solo el fondo y descarta el resto, o avisa al usuario si encuentras
  contenido inesperado antes de seguir.

