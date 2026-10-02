---
name: "presentaciones-cientificas"
description: "Convierte un tema médico o uno o varios documentos científicos (guías, artículos, handbooks, PDF) en una presentación académica completa de nivel residencia/congreso, con el guion oral de lo que debe decir el expositor en cada diapositiva y el archivo .pptx listo para proyectar. Úsala SIEMPRE que el usuario pida diapositivas, presentación, deck, clase, sesión académica, gran sesión, club de revista, seminario, exposición o \"cómo presentar\" un tema clínico, y también cuando adjunte guías o artículos con contexto de exponer (clase, gran sesión, club de revista, \"me toca presentar\") — en ese caso entrega la presentación directamente, sin pedir confirmación previa. Si adjunta un documento sin decir para qué y el hilo no lo aclara, pregunta en una frase si quiere exponerlo (esta skill), estudiarlo (medical-learning / estudio-cronicas) o practicar preguntas (preguntas-interactivas). NO es para revisar un .pptx ya hecho (auditor-presentaciones) ni para solo cambiarle el estilo (diapositivas-dinamicas)."
---

# Presentaciones científicas de nivel especialista

Transformar contenido científico en una conferencia lista para exponer: cada diapositiva con su
contenido exacto, su visual, su referencia al pie y **el guion oral de lo que hay que decir**.
El objetivo no es resumir el documento, es construir la clase.

Audiencia: residentes, especialistas, docentes de posgrado. No simplificar conceptos complejos.

## Flujo de trabajo

### Fase 0 — Análisis previo (antes de escribir ninguna diapositiva)

Nunca empezar por la diapositiva 1. Primero:

1. Leer los documentos adjuntos (en claude.ai suelen estar en `/mnt/user-data/uploads/`; en Claude
   Code/Cowork, en la carpeta de trabajo). Si son largos (guías, handbooks), usar primero
   `lectura-eficiente-pdf` para convertir una vez y leer solo las secciones necesarias.
2. Extraer los conceptos nucleares y las cifras con valor docente.
3. Eliminar redundancias y fusionar información repetida entre documentos.
4. Detectar contradicciones entre fuentes y **señalarlas explícitamente** (no promediarlas ni ocultarlas).
5. Verificar vigencia: ¿la guía adjunta sigue siendo la versión actual? Si hay herramienta de búsqueda
   web, comprobarlo y contrastar con la guía más reciente disponible.
6. Diseñar la narrativa: qué pregunta responde la charla y en qué orden.
7. **Si el usuario adjunta una plantilla `.pptx` institucional** (aunque venga "vacía"): analizarla
   antes de construir nada. Ver `references/produccion-pptx.md § Análisis de plantilla institucional`
   para el procedimiento (descomprimir, extraer color de marca, medir zona segura, revisar si de
   verdad está vacía). Nunca asumir el diseño a ojo desde las miniaturas.

Presentar este análisis al usuario en un bloque breve (10-15 líneas máximo) llamado
**Mapa de la presentación**: fuentes usadas, vigencia, contradicciones detectadas, esqueleto de
secciones y número de diapositivas. Después continuar directamente con las diapositivas —
no pedir permiso para seguir.

Si **no hay documentos adjuntos**, construir la presentación desde las guías vigentes prioritarias
(ver "Evidencia"), buscándolas en la web cuando la herramienta esté disponible, y advertir en el
Mapa qué se usó como fuente.

### Fase 1 — Diapositivas + guion

Escribir cada diapositiva con el formato exacto de `references/plantilla-diapositiva.md`.
Leer ese archivo antes de redactar la primera diapositiva.

### Fase 2 — Cierre

Auditoría científica + bibliografía dual (ver abajo).

### Fase 3 — Archivo .pptx

Generar siempre el `.pptx` además del texto en el chat, salvo que el usuario diga lo contrario.
Leer `references/produccion-pptx.md` y el SKILL.md de la skill `pptx` (cárgala con la herramienta
Skill; en claude.ai también está en `/mnt/skills/public/pptx/SKILL.md`) antes de generarlo.

Construir el archivo directamente con `pptxgenjs` (no editando slide por slide una plantilla
duplicada) — es el método que da control real sobre posición, zona segura y estilo. El
procedimiento completo de construcción, control de calidad y entrega está en
`references/produccion-pptx.md`; no se puede saltar el paso de revisión visual descrito allí
(convertir a imágenes y mirar cada diapositiva) — construir el .pptx a ciegas y entregarlo sin
mirarlo produce colisiones de texto que el usuario tiene que descubrir por su cuenta.

Si se identificaron pares candidatos a Morph (ver regla en "Reglas de construcción"), aplicar la
receta de `objectName` de `produccion-pptx.md § Construcción pensando en Morph` en esas
diapositivas concretas y dejarlos anotados en el Mapa de la presentación — es lo único que la
Fase 4 (`diapositivas-dinamicas`) necesita para activarlos, no requiere ningún paso adicional aquí.

**Índice/agenda navegable (decks largos).** Para una gran sesión o monografía de más de ~30
diapositivas, considerar incluir una diapositiva de índice temprana con las secciones principales
(las mismas que ya definiste en la narrativa de la Fase 0). No hace falta nada especial en el
`.pptx` de esta fase — basta con dejar clara la lista de secciones y a qué número de diapositiva
corresponde cada una en el Mapa de la presentación. Con esa lista, la Fase 4
(`diapositivas-dinamicas`) puede convertirla en navegación real: botones clicables en el `.pptx`
(`pptx_botones_helper.py`) y un menú de acordeón en el `.html` (tipo de diapositiva `indice`) — ver
`diapositivas-dinamicas/references/integracion.md § Caso 1c`.

## Skills que se encadenan dentro del flujo (sin que el usuario las pida)

| Momento | Skill | Para qué |
|---|---|---|
| Fase 0 | `lectura-eficiente-pdf` | Leer guías/artículos largos sin cargarlos completos |
| Fase 0 | `escalas-clinicas` | Si la patología tiene escala diagnóstica, de riesgo o pronóstica, incluirla con cortes verificados |
| Fase 1 | `visualizar-informacion` | Decidir qué forma visual toma cada bloque denso (o si va mejor como texto) |
| Fase 1 | `infografias-automaticas` | Clasificaciones, pasos, comparativas y líneas de tiempo como infografía |
| Fase 1 | `diagramas-clinicos` | Algoritmos (formas nativas editables), fisiopatología, forest plots |
| Fase 1 | `imagenes-contextuales-diapositivas` | Foto de contexto en 1 de cada 3-5 diapositivas de contenido |
| Fase 3 | `plantilla-uninavarra` | Si el usuario pide su plantilla institucional o el deck es para la universidad |
| Fase 4 | `diapositivas-dinamicas` | Acabado (transiciones, profundidad, gemelo HTML), salvo que pida versión simple |
| Cierre | `auditor-presentaciones` → `ensayo-y-defensa` | Si el deck va calificado o hay jurado |

## Extensión

Calcular ~1 diapositiva por minuto de exposición. Si el usuario indica duración, ajustarse a ella.
Sin indicación: 28-35 diapositivas para un tema completo, 15-20 para un club de revista,
40-50 para una gran sesión o monografía. Es preferible menos diapositivas bien construidas que
un recuento inflado con relleno.

## Reglas de construcción

**Una diapositiva = una pregunta.** ¿Qué es? ¿Por qué ocurre? ¿Cómo se diagnostica? ¿Cómo se trata?
Nunca dos ideas grandes juntas.

**Principio 70/30.** 70 % visual (esquema, tabla, algoritmo, gráfico, imagen), 30 % texto. Si una
diapositiva es solo bullets, casi siempre puede convertirse en tabla comparativa, diagrama de flujo
o línea de tiempo — hacerlo.

**Densidad.** Título ≤ 10 palabras. Máximo 6 bullets (4 visibles a la vez si se usa
`plantilla-uninavarra`; el resto con revelado progresivo). Máximo 8-10 palabras por bullet.
Nunca párrafos en la diapositiva: la prosa va en el guion del expositor, no proyectada.
**Máximo 1 imagen de apoyo por diapositiva** en el `.pptx` base — si el contenido
realmente necesita comparar 2-3 imágenes (varios patrones radiológicos, leve/
moderado/severo de un mismo hallazgo), no las amontones en una sola diapositiva:
anótalo en el Mapa de la presentación como "Diapositiva N: N imágenes, candidata
a revelado progresivo" para que la Fase 4 (`diapositivas-dinamicas`) las reparta
con revelado progresivo en el `.html` o con secuencia de Morph en el `.pptx`
(ver `diapositivas-dinamicas/references/integracion.md § Caso 1d`) — es preferible
eso a una diapositiva con 3 fotos y 3 bullets a la vez, que se siente cargada sin
importar cuánto se cuide el resto del formato.

**Patrón fijo e invariable** en las 3 zonas de toda diapositiva de contenido:
título arriba → visual + contenido en el cuerpo → franja inferior con las referencias.
La caja *Take Home* va en la esquina inferior derecha, máximo dos líneas.

**Principios CRAP**: contraste (jerarquía tipográfica clara), repetición (mismos estilos en todo el
deck), alineación (una rejilla, nada centrado al azar), proximidad (agrupar lo que se relaciona).

**Sin código de colores por tipo de diapositiva.** Preferencia explícita del usuario: no asignar
colores a definiciones/diagnóstico/tratamiento. Usar una paleta única y coherente en todo el deck;
el color se reserva para resaltar el dato clave o una alerta clínica, no para clasificar secciones.

**Diapositivas de alto impacto.** Para momentos dramáticos del guion (una pregunta retórica al
público, una votación, un cierre narrativo, una diapositiva en negro) romper deliberadamente el
patrón fijo: fondo oscuro sólido, sin encabezado ni logo institucional, tipografía grande y
centrada. El contraste con el resto del deck es lo que le da fuerza al momento — no se trata de un
descuido de formato, es una decisión de diseño que hay que tomar a propósito en 2-3 diapositivas
como máximo por presentación.

**Pares candidatos a Morph (para la Fase 4 de `diapositivas-dinamicas`).** Ciertos contenidos de
esta skill son, por naturaleza, una progresión entre dos estados — y eso es exactamente lo que la
transición nativa Morph de PowerPoint anima mejor (ver `references/produccion-pptx.md §
Construcción pensando en Morph`): un algoritmo donde se resalta el paso actual, una línea de tiempo
donde avanza el marcador, una escala clínica donde se resalta el umbral relevante del caso, un
"antes/después" de guía. Cuando el contenido se preste a esto, construir el par de diapositivas con
`objectName` idéntico en los elementos que deben transformarse (ver receta en `produccion-pptx.md`)
y anotarlo en el **Mapa de la presentación** como "Diapositivas N→N+1: candidatas a Morph" — así
`diapositivas-dinamicas` puede activar `--morph-en` sin tener que adivinar ni reconstruir nada. No
forzar esto en contenido que no sea realmente una progresión: dos diapositivas sin relación con
`objectName` igual solo confunden la Fase 4.

**Material gráfico con pacientes reales.** Si el usuario adjunta fotografías identificables de un
paciente real (rostro visible, contexto personal como bodas o fotos privadas de casa) para
incluirlas en la presentación: señalarlo explícitamente antes de insertarlas — recomendar rostro
difuminado o recorte si se proyectará ante público externo, y preguntar si ya existe consentimiento
para uso identificable. No usar fotos claramente privadas/íntimas (autorregistro personal en casa,
ropa de dormir, ángulos de espejo) en el material de proyección pública aunque el usuario las haya
compartido — son de un tono distinto a una foto social o clínica y merecen quedar fuera salvo que
el usuario confirme expresamente que quiere incluirlas.

**Visuales didácticos y prácticos.** Cada esquema debe servir por igual al expositor (le da el hilo
de lo que va a decir) y al público (se entiende sin explicación previa). Priorizar:
diagramas fisiopatológicos en cadena, algoritmos tipo guía con decisiones Sí/No, tablas comparativas,
líneas de tiempo, escalas clínicas maquetadas, árboles de decisión.

## Evidencia y honestidad científica

Toda la presentación se rige por el filtro de realidad del usuario:

- Etiquetar cuando corresponda: **[Evidencia]** (guía, RS, metaanálisis, ECA, texto de referencia),
  **[Inferencia]** (conclusión lógica no explícita en la fuente), **[Especulación]** (hipótesis
  plausible sin evidencia), **[No verificado]**.
- **Nunca inventar** referencias, cifras epidemiológicas, sensibilidad/especificidad, NNT, dosis ni
  recomendaciones. Si el dato no está en las fuentes disponibles, escribir en la diapositiva
  "dato no disponible en las fuentes consultadas" o retirar el dato — jamás rellenar con una cifra
  verosímil.
- Si falta información esencial para construir una sección, decirlo en el Mapa de la presentación y
  seguir con el resto.
- Si en una respuesta previa se afirmó algo sin evidencia suficiente, escribir exactamente:
  "Corrección: previamente presenté una afirmación no verificada. Debió identificarse como
  [Inferencia] o [No verificado]."

**Prioridad de fuentes** cuando varias sostienen la misma afirmación: guía clínica internacional más
reciente (2026 > 2025 > 2024; versiones previas solo si siguen vigentes) → revisión sistemática →
metaanálisis → ECA → estudio observacional → consenso de expertos → revisión narrativa → libro de
texto (solo para fisiopatología). Nunca citar un artículo suelto cuando existe una guía que lo cubre.

Organismos prioritarios: GRADE, ADA, AHA/ACC, ESC, KDIGO, GOLD, GINA, IDSA, ATS, ACP, NICE, USPSTF,
AAFP, CDC, OMS, Surviving Sepsis, NCCN, ASCO, EULAR, ACR, ACOG, ESPGHAN, NASPGHAN, AAP y el
Ministerio de Salud de Colombia cuando exista guía vigente aplicable (contexto: Colombia).

**Controversias**: cuando dos guías difieren, dedicar una diapositiva comparativa que muestre qué
recomienda cada una, con qué nivel de evidencia, y cuál tiene mayor respaldo metodológico.
No esconder la incertidumbre: nombrar calidad de evidencia, limitaciones y vacíos.

**Bioestadística**: cuando aparezcan resultados, traducirlos a riesgo absoluto, RR/HR/OR, NNT/NNH,
IC 95 % y significancia clínica frente a estadística.

## Referencias

Cada diapositiva lleva al pie **solo** las referencias que se usaron para construirla, en formato
`Autor o institución. Revista o guía. Año.` Ejemplos: `ADA Standards of Care 2026.` `ESC 2024.`
`Lancet. 2025.` No arrastrar referencias generales que no se usaron en esa diapositiva.

Dentro del contenido, cada cifra o recomendación importante lleva su cita abreviada al final del
elemento: `Mortalidad hospitalaria 18 % (NEJM, 2025)`, `Clase I, Nivel A (ESC, 2024)`,
`HbA1c objetivo < 7 % (ADA, 2026)`.

Toda figura, tabla, gráfico o algoritmo adaptado indica su origen: `Figura adaptada de ESC 2024`,
`Algoritmo basado en ADA 2026`, `Tabla del documento adjunto, capítulo 4`.

## Cierre obligatorio de la presentación

1. **Perlas clínicas** (1-2 diapositivas): error frecuente, lo que cambia la conducta, lo que más se
   pregunta en exámenes, lo que nunca debe olvidarse.
2. **Conclusiones**: 4-6 mensajes, uno por objetivo planteado al inicio.
3. **Bibliografía en Vancouver**, sin duplicados, numerada por orden de aparición.
4. **Índice diapositiva → referencia**: `Diapositiva 7 — KDIGO 2024`, `Diapositiva 8 — JAMA 2025`.
5. **Auditoría científica final**, marcando cada punto:
   - Ninguna diapositiva con exceso de texto ni con dos ideas principales.
   - Toda cifra y toda afirmación clínica relevante tienen referencia.
   - Toda imagen, tabla y algoritmo tienen fuente.
   - Los algoritmos son clínicamente correctos y los gráficos adecuados a los datos.
   - Cada diapositiva tiene guion, mensaje clave y referencias al pie.
   - No hay contradicciones internas; la narrativa es lógica.
   - La bibliografía final coincide con las referencias usadas.
   - La presentación puede exponerse sin volver a consultar el documento original.

Si algún punto de la auditoría falla, corregirlo antes de entregar y decir qué se corrigió.

## Comandos rápidos

El usuario puede pedir modos abreviados:

| Petición | Qué hacer |
|---|---|
| "solo el guion" | Entregar únicamente el guion del expositor por diapositiva |
| "amplía la diapositiva N" | Rehacer esa diapositiva con más profundidad, manteniendo el formato |
| "versión de X minutos" | Recalcular el número de diapositivas y recortar por prioridad clínica |
| "modo club de revista" | Estructura PICO: pregunta, diseño, población, intervención, comparador, desenlaces, resultados, sesgos, aplicabilidad, impacto para Medicina Familiar |
| "solo el pptx" | Saltar el detalle en el chat y entregar el archivo |

## Archivos de referencia

- `references/plantilla-diapositiva.md` — formato exacto de cada diapositiva y ejemplo resuelto.
  Leer **antes** de escribir la primera diapositiva.
- `references/produccion-pptx.md` — paleta, rejilla y receta de generación del archivo .pptx.
  Leer antes de la Fase 3.

