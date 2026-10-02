---
name: enrutador-de-skills
description: "Decide qué skill(s), plugin(s) o combinación de herramientas de este Cowork conviene usar interpretando el contexto completo de la solicitud (no solo palabras sueltas): el objetivo real, lo que se adjunta, el formato de entrega esperado y lo que ya se habló antes en la conversación. Cubre explicar/entender un tema, estudiar, repasar, ficha, preguntas tipo examen, escalas, leer una guía en PDF, diapositivas, presentación, clase, gran sesión, plantilla institucional, infografías, fotos para diapositivas, caso clínico, documento Word/PDF/Excel, póster, artículo, guía, ensayo clínico, fármaco, diseño, roadmap, crear o mejorar una skill o plugin, revisión de código o planes con Codex (codex-review, codex-dispatch), programar una tarea recurrente, etc. Úsala SIEMPRE al empezar una tarea nueva o cuando no esté claro qué skill(s) aplican, antes de invocar cualquier otra skill. No hace falta releerla si ya se está siguiendo el flujo de una skill específica que ya se activó correctamente para esa misma tarea."
---


# Enrutador de skills — qué usar según el contexto de la solicitud

## Por qué existe esto

Este Cowork tiene muchas skills instaladas: varias hechas a medida para tu residencia
(aprender: `medical-learning`, `estudio-cronicas`, `preguntas-interactivas`, `escalas-clinicas`,
`lectura-eficiente-pdf`; presentar: `presentaciones-cientificas`, `plantilla-uninavarra`,
`visualizar-informacion`, `infografias-automaticas`, `diagramas-clinicos`,
`imagenes-contextuales-diapositivas`, `imagenes-creativas-medicas`, `diapositivas-dinamicas`,
`auditor-presentaciones`, `ensayo-y-defensa`), varias de oficina
(`docx`, `pdf`, `pptx`, `xlsx`, `canvas-design`), varios plugins de investigación biomédica
(PubMed, Consensus, ClinicalTrials.gov, ChEMBL, bioRxiv, Open Targets) y otras de dominios que casi
nunca vas a necesitar (diseño de producto, gestión de producto, desarrollo de software). Este mapa
existe para acertar a la primera y, sobre todo, para saber **cuándo combinar varias herramientas**
en cadena en vez de usar solo una.

## Principio central: el contexto manda, no la palabra suelta

No busques una palabra clave exacta y te detengas ahí. Interpreta la situación completa antes de
elegir:

- **El objetivo real**, no solo el verbo usado. "Necesito algo para el lunes sobre hipotiroidismo"
  no dice "diapositivas" ni "estudiar", pero si antes mencionaste que el lunes tienes clase, el
  objetivo real es una presentación, no una ficha de estudio.
- **Lo que se adjunta.** Un PDF de una guía + "revisa esto" probablemente pide analizarlo y
  convertirlo en algo (ficha, deck, resumen) — infiere cuál según el resto de la conversación, y si
  no es obvio, pregunta en una sola frase en vez de adivinar.
- **Lo que ya se habló antes en el hilo.** Si ya estás dentro del flujo de `presentaciones-cientificas`
  y el usuario dice "se ve muy plano" o "hazlo más dinámico", eso no es una tarea nueva que requiera
  releer este mapa — es la señal exacta para encadenar `diapositivas-dinamicas` sin que el usuario
  tenga que nombrarla.
- **El nivel y la audiencia implícitos.** Todo lo clínico en este Cowork es para nivel residencia de
  Medicina Familiar (ver las preferencias del usuario) — eso ya condiciona profundidad y evidencia
  exigida sin que haga falta que el usuario lo repita cada vez.
- **Cuando falte contexto para decidir entre dos caminos razonables, pregunta.** Adivinar mal cuesta
  más tiempo que una pregunta corta.

Las tablas de abajo son puntos de partida y ejemplos de frases típicas, **no una lista cerrada de
palabras a buscar**. Si la solicitud no calza literal pero el contexto apunta claramente a una fila,
usa esa fila igual.

## Cómo usar este mapa

1. Lee la solicitud completa en su contexto (mensaje actual + hilo + adjuntos) e identifica el
   objetivo real y el dominio.
2. Busca en las tablas la fila que mejor representa ese objetivo — por significado, no por coincidencia
   textual.
3. Invoca la(s) skill(s) indicada(s) con la herramienta Skill.
4. Si la fila dice "+ plugin", usa también esa herramienta MCP (PubMed, Consensus, etc.) para reunir
   información antes o durante la tarea — no reemplaza a la skill principal, la completa.
5. Si la skill elegida ya tiene su propio flujo completo (`estudio-cronicas`,
   `presentaciones-cientificas`), no dupliques su lógica ni uses `docx`/`pptx` "a mano" por tu
   cuenta — actívala y sigue sus instrucciones tal cual.
6. Después de entregar, anticipa la siguiente skill de la cadena si el contexto la sugiere (ver
   "Cadenas típicas" abajo) — no esperes a que el usuario la pida con el nombre exacto.
7. Si ninguna fila coincide ni por contexto, dilo explícitamente, usa `find-skills` para ver si hay
   algo instalable que ayude, o pregunta al usuario qué formato de entrega quiere.
8. Sin importar qué skill termine generando el entregable, el filtro de realidad del usuario
   (etiquetas `[Evidencia]` / `[Inferencia]` / `[Especulación]` / `[No verificado]`, nunca inventar
   cifras, dosis, referencias ni resultados de estudios) sigue aplicando siempre.

## Tabla 1 — Núcleo clínico/académico (lo que más vas a pedir)

### Aprender y estudiar

| Situación / objetivo real | Skill(s) | Notas |
|---|---|---|
| Quiere **entender** un tema en la conversación: "explícame", "¿por qué…?", "no entendí", "repásame", "explícame rápido", mecanismo de un síntoma, fármaco o laboratorio | `medical-learning` | Enseña por cadenas causales, por bloques con preguntas intercaladas. No produce Word salvo que lo pida. |
| Quiere un **documento** (Word/PDF) para estudiar una enfermedad crónica: "hazme la ficha de ERC", "material para el examen de EPOC" | `estudio-cronicas` | Genera el docx/pdf con diagramas, casos y preguntas; guía internacional + colombiana. |
| Quiere **practicar con preguntas**: "pregúntame", "hazme un quiz", "simulacro", "evalúame", "que yo le dé clic" | `preguntas-interactivas` | Modo chat con botones o app HTML. Dentro de `medical-learning`, "pregúntame" sobre el tema en curso se queda ahí. |
| Pregunta por una **escala o puntaje**: componentes, cortes, cómo calcularla en un caso | `escalas-clinicas` | También se encadena sola en fichas, decks y quizzes. |
| Adjunta un **PDF/DOCX largo** (guía, handbook, resolución) y pide algo de él | `lectura-eficiente-pdf` primero, luego la skill del objetivo | Convierte una vez y lee solo la sección necesaria. |
| Repasar un **fármaco** específico | `medical-learning` (plantilla de medicamento) | En Word: `estudio-cronicas` § "Formato de tratamiento farmacológico". |
| Adjunta un documento sin decir para qué y el hilo no lo aclara | Pregunta en una frase: ¿exponerlo, estudiarlo o practicar preguntas? | No adivinar. |

### Exponer y presentar

| Situación / objetivo real | Skill(s) | Notas |
|---|---|---|
| Va a exponer, dar clase, gran sesión o club de revista ("el lunes tengo que exponer X") | `presentaciones-cientificas` | Guion + .pptx. Encadena por dentro `escalas-clinicas`, `visualizar-informacion`, `infografias-automaticas`, `diagramas-clinicos`, `imagenes-contextuales-diapositivas`. Actívala directo. |
| Pide su plantilla institucional, "como mis gran sesión anteriores", fondo UNINAVARRA | `plantilla-uninavarra` (+ `presentaciones-cientificas` si aún no hay contenido) | Capa visual institucional; no investiga contenido. |
| "Hazlo más visual", "que no sea solo texto", "organízame esto en una lámina" sobre un bloque concreto | `visualizar-informacion` | Decide SI conviene y QUÉ patrón; delega el dibujo. |
| Pide un algoritmo, flujograma, esquema de mecanismo, forest plot, línea de tiempo | `diagramas-clinicos` | Algoritmos para pptx salen como formas nativas editables. |
| Pide infografías de clasificaciones, pasos o comparativas | `infografias-automaticas` | Se activa sola al construir un deck. |
| "Ponle fotos", "se ve muy de texto" (fotos de contexto por diapositiva) | `imagenes-contextuales-diapositivas` | Verifica licencia; nunca IA para hallazgos clínicos reales. |
| Portada, póster, ilustración artística | `imagenes-creativas-medicas` | Pieza única; no diagramas. |
| Ya tiene un .pptx y lo quiere menos plano / con animaciones | `diapositivas-dinamicas` | Solo estética. Enlázala al terminar `presentaciones-cientificas`, salvo versión simple. |
| Ya tiene un .pptx y quiere saber si está bien ("revísalo", "¿me alcanza el tiempo?") | `auditor-presentaciones` | Informe priorizado + .pptx corregido. |
| Le preocupa exponerlo: "qué me van a preguntar", "ensáyame", jurado | `ensayo-y-defensa` | Cronometraje, apertura/cierre, banco de preguntas. |

### Evidencia adicional

| Situación | Herramienta | Notas |
|---|---|---|
| Falta evidencia en los adjuntos, o hay que verificar vigencia de una guía | Búsqueda web; y si están conectados, los MCP de PubMed, Consensus, ClinicalTrials.gov, ChEMBL, bioRxiv | Complementan la skill principal. Si un MCP aparece desconectado, dilo y usa búsqueda web. Actívalos proactivamente si la evidencia es insuficiente. |

## Cadenas típicas (contexto que dispara la siguiente skill sin que la nombren)

- **Estudiar un tema a fondo** = `medical-learning` (comprensión en chat) → `preguntas-interactivas`
  (comprobar) → `estudio-cronicas` solo si quiere el documento descargable.
- **Presentación clínica completa** = `presentaciones-cientificas` → (evidencia insuficiente en
  adjuntos) `pubmed`/`consensus` → (por defecto, al terminar) `diapositivas-dinamicas` para el
  acabado visual, salvo que pidan versión simple.
- **Deck que va a calificarse** (gran sesión, monografía, sustentación con jurado) = cadena
  anterior → `auditor-presentaciones` como control de calidad final → `ensayo-y-defensa` para
  preparar al expositor. Las dos últimas se ofrecen sin esperar a que las pidan por nombre en
  cuanto el usuario mencione nota, rúbrica, jurado o docente evaluador.
- **Deck que llega ya hecho** (propio de antes, de un compañero, descargado) = `auditor-presentaciones`
  primero — nunca `presentaciones-cientificas`, que reconstruiría desde cero contenido que ya existe.
- **Ficha con controversia entre guías** = `estudio-cronicas` + `consensus`/`pubmed` cuando la guía
  sola no resuelve el punto en disputa.
- **Club de revista / lectura crítica** = `presentaciones-cientificas` en modo PICO si el resultado
  son diapositivas; `estudio-cronicas` si el resultado es texto/ficha con el artículo como fuente.
- **Mejorar una skill propia** = `skill-creator` → si se tocaron scripts, `codex-review:code` (o
  `code-review`) antes de empaquetar → empaquetar `.skill` y entregarla para instalar.
- **Cambio grande de código o de una app de estudio** = `superpowers:brainstorming` →
  `superpowers:writing-plans` → `codex-review:plan` → implementar (o `codex-dispatch:codex-dispatch`
  para que lo ejecute Codex) → `codex-review:code` → `superpowers:verification-before-completion`.
- **"No me gusta cómo quedó" sobre algo ya entregado** = no es tarea nueva ni requiere releer este
  mapa completo — identifica qué skill lo generó y usa su modo de corrección/iteración, o
  `diapositivas-dinamicas` si el reclamo es puramente estético sobre un .pptx.

## Tabla 2 — Documentos, oficina y archivos

| Necesita | Skill | Notas |
|---|---|---|
| Documento para leer, compartir o comentar (informe, carta, protocolo, guía práctica, hoja de ruta) sin formato pedido | `docs` | Default para "un documento"; exporta a Word/PDF si hace falta. |
| Pide explícitamente Word (.docx), editar un .docx o control de cambios | `docx` | |
| Crear, combinar, dividir o extraer de un PDF | `pdf` | Para LEER uno largo, primero `lectura-eficiente-pdf`. |
| Ver, anotar, firmar o rellenar un PDF existente | `pdf-viewer:open` / `pdf-viewer:annotate` / `pdf-viewer:sign` / `pdf-viewer:fill-form` | `pdf-viewer:view-pdf` para revisión visual colaborativa. |
| Hoja de cálculo (.xlsx): base de pacientes, notas, cronograma, tabla de datos | `xlsx` | |
| Diapositivas genéricas no clínicas | `pptx` | Si el tema es clínico/académico → `presentaciones-cientificas`. |
| Convertir cualquier archivo a Markdown | `markitdown` | `lectura-eficiente-pdf` ya lo usa por dentro. |
| Crear o editar un archivo en Google Docs/Sheets/Slides | `google-workspace` | Requiere el conector de Google Drive. |
| Gráfico de datos fuera de lo clínico (dashboard, métricas) | `dataviz` | Si es forest plot o dato clínico → `diagramas-clinicos`. |
| Póster o pieza visual artística no clínica | `canvas-design` | Clínica → `imagenes-creativas-medicas`. |
| Página web / app interactiva compartible (artifact) | `artifact-design` (+ `artifact-capabilities` si guarda datos; `artifact-diagramming` si lleva diagramas) | Apps React complejas: `web-artifacts-builder`. |
| Pulir un texto propio para que suene natural (sin ocultar autoría donde se exija declararla) | `humanizer` o `watermarks-remover:clean-user-facing-text` | Nunca para evadir políticas de integridad académica de la universidad. |
| Programar algo recurrente ("cada mañana", "todos los lunes", "recuérdame en una hora") | `loop` en sesión; rutinas o `send_later` en Claude Code en la nube; `schedule` en Cowork | Si no existe ninguna en el entorno, dilo. |
| Ver o configurar su brief matutino | `morning` | Solo si lo pide explícitamente. |
| Aprender un concepto NO médico (programación, herramientas, idiomas) | `learn` | Lo médico va a `medical-learning`. |
| Importar memoria exportada de otro asistente | `import-memory` | |

## Tabla 3 — Programación, skills y revisión de código (incluido Codex)

Aplica cuando la tarea es explícitamente de software: los scripts de tus skills (p. ej.
`auditar_pptx.py`, `infografia.py`), una app HTML de estudio, o un repositorio.

| Necesita | Skill | Notas |
|---|---|---|
| Crear, mejorar o evaluar una skill propia | `skill-creator` | Empaqueta en `.skill` para instalar. Para plugins de Cowork: `cowork-plugin-management:*`. |
| Buscar si existe una skill instalable | `find-skills` | |
| Diseñar antes de construir algo nuevo | `superpowers:brainstorming` → `superpowers:writing-plans` | |
| **Segunda opinión de Codex sobre un plan** antes de implementarlo | `codex-review:plan` | Claude y Codex iteran el plan hasta que Codex lo aprueba. Úsalo en planes con varios archivos o decisiones de arquitectura. |
| **Revisión de Codex sobre cambios ya hechos** (diff de la sesión): bugs, seguridad, rendimiento | `codex-review:code` | Después de modificar scripts o código y antes de hacer commit/PR. |
| **Delegar a Codex** una revisión de diff/regresiones o la ejecución de un plan escrito por Claude dentro de un repo | `codex-dispatch:codex-dispatch` | Frases: "que Codex lo revise", "que Codex implemente", "mándaselo a Codex". |
| Revisión de código propia de Claude | `code-review` (bugs), `simplify` (limpieza), `security-review` (seguridad), `superpowers:requesting-code-review` | Complementan, no reemplazan, a Codex. |
| Depurar un error o test fallido | `superpowers:systematic-debugging` | |
| Implementar con pruebas | `superpowers:test-driven-development`, `superpowers:executing-plans` / `superpowers:subagent-driven-development` | |
| Verificar antes de decir "terminado" | `superpowers:verification-before-completion` | |
| Cerrar la rama (merge/PR) | `superpowers:finishing-a-development-branch` | |
| Ejecutar o ver la app funcionando | `run` | |
| Documentar el repo (CLAUDE.md) / hook de inicio en la nube | `init` / `session-start-hook` | |
| Configurar Claude Code (permisos, hooks, atajos) | `update-config`, `keybindings-help`, `fewer-permission-prompts` | |
| Construir con la API de Claude | `claude-api` | |

**Cuándo elegir cada herramienta de Codex:** `codex-review:plan` = todavía no hay código, solo un
plan; `codex-review:code` = ya hay cambios en la sesión y quieres que Codex los critique;
`codex-dispatch:codex-dispatch` = quieres que Codex **trabaje** (revise un diff concreto o ejecute
un plan) dentro de un repositorio. Las tres requieren que la CLI o el servidor MCP de Codex estén
instalados y conectados; si no lo están, dilo en una línea y usa `code-review` /
`superpowers:requesting-code-review` como alternativa.

## Tabla 4 — Investigación biomédica avanzada (fuera de lo clínico habitual)

| Necesita | Skill |
|---|---|
| Orientarse sobre las herramientas de investigación biomédica | `bio-research:start` |
| Elegir o evaluar un problema de investigación (p. ej. tema de trabajo de grado) | `bio-research:scientific-problem-selection` |
| RNA-seq/WGS/ATAC-seq, pipelines nf-core | `bio-research:nextflow-development` |
| QC de single-cell (.h5ad/.h5) | `bio-research:single-cell-rna-qc` |
| Integración/batch correction, CITE-seq, multiome | `bio-research:scvi-tools` |
| Datos de instrumentos de laboratorio a Allotrope/CSV | `bio-research:instrument-data-to-allotrope` |

## Tabla 5 — Otros dominios (uso ocasional)

| Dominio | Cuándo | Skill(s) |
|---|---|---|
| Diseño/UX | Crítica de diseño, accesibilidad, copy, investigación de usuarios, handoff | `design:*` |
| Gestión de producto | Roadmap, sprint, spec/PRD, métricas, brief competitivo, lluvia de ideas | `product-management:*` |
| Cursos narrados y roleplay (AmpUp) | Crear/editar un curso o un roleplay de práctica | `ampup-mcp-plugin:*` (requiere el conector AmpUp) |
| Marca Anthropic | Solo si se pide ese estilo | `brand-guidelines` |
| Diagnóstico de una sesión de superpowers que salió mal | "¿por qué tardó tanto?", reporte de bug | `superpowers:diagnosing-superpowers` |

## Qué NO hacer

- No te quedes esperando la palabra exacta de una tabla — el contexto (adjuntos, hilo previo,
  objetivo real) pesa más que la coincidencia literal.
- No uses `pptx` ni `docx` "sueltos" cuando `presentaciones-cientificas` o `estudio-cronicas`
  aplican: ya orquestan esos skills por dentro y traen reglas de evidencia que un uso suelto no tiene.
- No confundas las tres skills de presentaciones: `presentaciones-cientificas` **construye**
  contenido, `auditor-presentaciones` **juzga y corrige** lo que ya existe, `diapositivas-dinamicas`
  **cambia la estética** sin tocar el contenido, y `ensayo-y-defensa` trabaja sobre el **expositor**,
  no sobre el archivo. Ante un .pptx adjunto, lo que decide es el verbo real: hacer / revisar /
  embellecer / exponer.
- No saltes el filtro de realidad sin importar cuál skill termine generando el entregable.
- No uses las skills de Codex ni `superpowers:*` para contenido clínico: son de software. Un
  "revisa mi presentación" es `auditor-presentaciones`, no `codex-review:code`.
- Si una skill depende de un conector o CLI que no está disponible en la sesión (Canva, Codex,
  PubMed, AmpUp, Google Drive), dilo en una línea y sigue con la alternativa — no inventes la salida.
- Si el contexto admite dos caminos razonables y no hay forma de inferir cuál quiere el usuario,
  pregunta antes de elegir en vez de adivinar.

