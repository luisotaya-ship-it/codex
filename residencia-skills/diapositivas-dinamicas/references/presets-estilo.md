# Los 4 presets de estilo

El usuario que encargó esta skill quiere poder elegir "qué tan atrevido" es el
diseño sin dejar de verse profesional/clínico. Por eso hay 3 presets, coherentes
entre el `.pptx` (`pptx_dinamizar.py`) y el `.html` (`build_html_dinamico.py`) —
mismo espíritu de color y de intensidad de movimiento en ambos formatos.

## `sobrio` — institucional (preset por defecto)

Para: gran sesión, sustentación ante especialistas, examen de residencia.

- Paleta: azul/verde clínico oscuro, alto contraste, sin degradados llamativos.
- Transiciones .pptx: `fade`, `push`, `wipe` (categoría "subtle" de PowerPoint);
  `morph` reservado para 1-2 diapositivas de alto impacto.
- Transición reveal.js: `slide` (la más neutra).
- Sin parallax de fondo. Icono 3D solo si el usuario lo pide explícitamente
  (`icono_3d_intensidad` bajo).
- Regla de oro: si dudas entre dos niveles de intensidad, usa este.

## `congreso` — moderno, tipo charla internacional

Para: congreso médico, charla TED-like, club de revista con público amplio.

- Paleta más saturada (violeta/turquesa), tipografía más grande.
- Transiciones .pptx: `morph`, `reveal`, `cube`, `gallery`, `doors` (normales);
  `fracture`, `prestige`, `vortex` reservadas a diapositivas de alto impacto
  (máximo 2-3 por deck, igual que la regla de "diapositivas de alto impacto"
  de `presentaciones-cientificas` — no conviertas cada diapositiva en un efecto
  especial, pierde fuerza).
- Transición reveal.js: `concave` (da sensación de profundidad/3D al pasar de
  diapositiva).
- Parallax de fondo activado (sutil, con blur alto — nunca debe distraer del
  contenido ni marear).
- Icono 3D activo por defecto en portada/cierre.

## `marca` — plantilla institucional del usuario

Para: cuando el usuario adjunta o pide que se respete el logo/colores de su
universidad, hospital o programa de residencia.

- Antes de generar nada: pedir o extraer los colores reales de marca (si hay un
  `.pptx` institucional adjunto, sigue el procedimiento de
  `presentaciones-cientificas/references/produccion-pptx.md § Análisis de
  plantilla institucional` para sacar el color exacto en vez de adivinarlo).
- Pasar esos colores con `--color-primario` / `--color-acento` en
  `build_html_dinamico.py`; en `pptx_dinamizar.py` no hay parámetro de color
  porque el color de marca ya vive en la plantilla misma — este preset solo
  controla qué tan llamativas son las transiciones (las más conservadoras,
  igual que `sobrio`, para no competir con el diseño institucional).
- Sin parallax por defecto (podría chocar con un fondo institucional con imagen).
- Icono 3D con intensidad baja (0.3) — un acento discreto, no un elemento
  dominante.

## `ficha_clinica` — infografía de guía, de un solo vistazo

Para: resumir una guía clínica (umbrales, categorías, dosis) en una sola
diapositiva que se entiende sin narración — el formato que un residente
fotografiaría con el celular para repasar después. Inspirado directamente en
un ejemplo real que el usuario mostró (ficha AHA/ACC de presión arterial
hecha en "Diseño de Claude", `claude.ai/design`).

- Fondo claro (`#eef1f5`) con una tarjeta blanca flotante (`ficha-card`) —
  funciona incluso si el resto del deck usa un preset oscuro, porque la
  tarjeta lleva su propio fondo y sombra.
- Estructura fija: eyebrow en mayúsculas + badge de guía/año arriba, título y
  subtítulo, línea divisoria, nota de método, barra de escala con umbrales de
  color (semáforo verde→ámbar→naranja→rojo), tabla con indicador de color por
  fila, tarjetas laterales de acento (una de ellas puede ser roja para una
  alerta tipo "crisis hipertensiva"), franja inferior de píldoras para listas
  cortas (estilo de vida, contraindicaciones, etc.).
- El color en este preset **sí** codifica severidad/riesgo (verde = normal,
  rojo = alerta) — es la única excepción a la regla de "paleta única, sin
  código de colores por tipo" de `presentaciones-cientificas`, porque aquí el
  color es el dato clínico mismo (un semáforo de PA, no una categoría de
  diapositiva).
- Úsalo para 1-3 diapositivas "resumen" del deck (una por guía o algoritmo
  clave), no para reemplazar el flujo narrativo completo de diapositivas de
  contenido — sigue necesitando el resto de tipos (`contenido`, `grafico`,
  `diagrama`) para explicar el porqué.
- Requiere los campos `escala`, `tabla`, `tarjetas` y opcionalmente `pildoras`
  del tipo de diapositiva `ficha` — ver `references/esquema-json.md`.

## Elegir el preset

Si el usuario no especifica, usar `sobrio`. Si pide "algo más llamativo/moderno/
para congreso", usar `congreso`. Si menciona su universidad/hospital, adjunta un
logo o una plantilla `.pptx` con membrete, usar `marca` y extraer sus colores
reales — nunca preguntar el código hex si ya se puede leer del archivo adjunto.
Si pide "una ficha", "resumen de guía en una sola diapositiva", "algo tipo
infografía" o menciona umbrales/categorías de riesgo que se prestan a un
semáforo de color, añadir una o más diapositivas `tipo: "ficha"` (con el
preset `ficha_clinica` si esa es la diapositiva dominante del deck, o
mezclada dentro de otro preset si es solo un resumen puntual).
