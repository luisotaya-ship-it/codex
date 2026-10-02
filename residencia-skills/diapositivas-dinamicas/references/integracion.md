# Cómo se integra con `presentaciones-cientificas`

Esta skill es un módulo de acabado estético, no un generador de contenido
propio. Nunca decide qué dice una diapositiva ni inventa cifras — solo controla
cómo se mueve y se ve lo que otra skill (o el usuario) ya redactó.

## Caso 1 — Flujo normal: se acaba de generar una presentación nueva

Cuando termines la Fase 3 (archivo `.pptx`) de `presentaciones-cientificas`,
continúa automáticamente con esta skill como **Fase 4**, salvo que el usuario
haya pedido explícitamente "sin animaciones" / "version plana" / "solo el pptx
simple":

1. Determina el preset (ver `references/presets-estilo.md`) según lo que haya
   dicho el usuario o el contexto (plantilla institucional adjunta → `marca`;
   "para congreso" / "algo más moderno" → `congreso`; cualquier otro caso →
   `sobrio`).
2. Identifica los números de diapositiva "de alto impacto" que ya definiste al
   construir el deck (fondo oscuro, cierre narrativo) y pásalos con `--impacto`.
3. Corre `scripts/pptx_dinamizar.py` sobre el `.pptx` recién construido.
4. Corre opcionalmente `scripts/pptx_profundidad.py` sobre el resultado si el
   deck tiene tarjetas/cajas/cuadrantes (formas `roundRect` rellenas) — mira el
   patrón de construcción en `produccion-pptx.md` de `presentaciones-cientificas`
   para saber si aplica.
5. Construye `contenido.json` (ver `references/esquema-json.md`) reutilizando
   el mismo texto y el mismo guion que ya escribiste — nunca resumas ni
   reinventes el contenido para la versión HTML.
6. Corre `scripts/build_html_dinamico.py` con el mismo preset.
7. Entrega ambos archivos: el `.pptx` dinamizado (para el proyector del
   hospital, sin depender de internet) y el `.html` (para exponer desde un
   portátil con navegador, o para practicar la exposición viendo cómo se
   comportan los gráficos y transiciones). Explica en una línea cuál usar en
   qué contexto — no asumas que el usuario ya sabe la diferencia.

### Caso 1b — El Mapa de la presentación trae pares candidatos a Morph

Si `presentaciones-cientificas` anotó en su Mapa algo como "Diapositivas 6→7:
candidatas a Morph" (ver su `produccion-pptx.md § Construcción pensando en
Morph`), esas diapositivas ya vienen con `objectName`/`shape.name` idéntico en
los elementos que deben transformarse — no hay que reconstruir nada:

1. Corre `scripts/pptx_morph_helper.py` → `verificar_par_morph(prs, idx_a, idx_b)`
   para confirmar que el nombre sí llegó intacto desde pptxgenjs a la
   diapositiva final (a veces una herramienta de conversión intermedia lo
   pierde) antes de prometerle Morph al usuario.
2. Si confirma coincidencia, pasa el número de la diapositiva de **llegada**
   en `--morph-en` al correr `pptx_dinamizar.py` (paso 3 del Caso 1 normal).
3. Si no coincide ninguna forma, avisa que ese par no va a producir Morph real
   (quedará como fundido normal) en vez de aplicar la bandera igual — ver
   `references/tecnica-morph-real.md`.

### Caso 1c — El Mapa de la presentación trae un índice/agenda de secciones

Si `presentaciones-cientificas` dejó anotada la lista de secciones y su
diapositiva correspondiente (ver su `SKILL.md § Índice/agenda navegable`),
construye navegación real en los dos formatos:

1. **`.pptx`**: `scripts/pptx_botones_helper.py` → `construir_menu_interactivo(prs, indice_menu, items, agregar_boton_regreso=True)`
   con `items` = la misma lista de secciones del Mapa. Esto añade los botones
   clicables en la diapositiva de índice y un botón "⌂ volver" en cada
   sección — no inventes secciones que no estén en el Mapa.
2. **`.html`**: usa el tipo de diapositiva `indice` en `contenido.json` (ver
   `references/esquema-json.md`) con la misma lista, como acordeón
   desplegable — reutiliza el resumen de cada sección que ya redactaste, no
   lo resumas de nuevo ni inventes uno.

### Caso 1d — Una diapositiva del Mapa quedó con varias imágenes o texto denso

Si `presentaciones-cientificas` señaló una diapositiva con 2+ imágenes de
apoyo o más de 4 puntos (algo que su propia regla 70/30 y límite de bullets
debería minimizar, pero puede pasar con contenido legítimamente denso, p. ej.
comparar varios patrones radiológicos), no la dejes entrar toda de golpe:

1. **`.html`**: usa `revelado: "progresivo"` o `"reemplazo"` en esa
   diapositiva (ver `references/esquema-json.md`) — cada imagen/punto aparece
   con su propio clic, sincronizado con `bullet_index` si corresponde.
2. **`.pptx`**: usa `scripts/pptx_morph_helper.construir_secuencia_revelado()`
   para repartir la diapositiva en varias diapositivas encadenadas con Morph
   (ver `references/tecnica-morph-real.md § Revelado progresivo en el .pptx
   real`) — el número final de diapositivas del `.pptx` crece, avísalo al
   usuario en una frase.

No inventes cómo agrupar las imágenes si el Mapa no lo especificó — pregunta
o usa el orden en que aparecen en el contenido ya redactado.

### Nota de orden: combinar Morph con botones de navegación

Si un par de diapositivas Morph (`pptx_morph_helper.py`) también necesita un
botón "⌂ volver al menú" (`pptx_botones_helper.py`), añade el botón **antes**
de duplicar la diapositiva para crear el par, no después: `duplicar_diapositiva()`
copia todas las formas que existan en ese momento, así que si el botón ya está
puesto, la diapositiva duplicada lo hereda automáticamente con el mismo
nombre — y al no moverse de sitio, Morph simplemente lo deja donde está, sin
efecto visible extraño. Si el botón se añade después (por ejemplo llamando a
`construir_menu_interactivo` con la diapositiva de origen del par en la lista
de `items`, ya duplicada), la diapositiva de llegada del Morph se queda sin
botón y el usuario pierde la forma de volver al menú desde ahí — se descubrió
este orden probando ambos módulos juntos, no es una suposición.

## Caso 2 — El usuario ya tiene un `.pptx` y solo quiere "hazlo más dinámico"

No reconstruyas la presentación. Trabaja directamente sobre el archivo que
adjuntó:

1. Corre `pptx_dinamizar.py` y opcionalmente `pptx_profundidad.py` sobre ese
   archivo tal cual.
2. Si además quiere la versión HTML, tendrás que extraer el texto de cada
   diapositiva (con el skill de `pptx` — lectura de `.pptx`) para reconstruir
   `contenido.json`; dile qué partes no pudiste inferir con seguridad (p. ej.
   qué diapositivas eran "de alto impacto") en vez de adivinarlas.

## Caso 3 — Presentación fuera de medicina / sin pasar por `presentaciones-cientificas`

La skill funciona igual de bien para cualquier `.pptx` ajeno al contexto
clínico: los scripts no asumen contenido médico, solo estructura de
diapositivas. Aplica el mismo flujo, ajustando el preset al tono del evento.

## Qué NO hace esta skill

- No añade animaciones de aparición/build nativas dentro del `.pptx` (ver el
  docstring de `pptx_dinamizar.py` para el porqué: riesgo de corrupción no
  verificable sin PowerPoint real). Si el usuario insiste en tener eso en el
  `.pptx` mismo, la alternativa honesta es indicarle el camino manual: seleccionar
  la forma → pestaña Animaciones → Entrada → Aparecer/Flotar hacia adentro —
  2 clics por elemento, controlado por el propio usuario en PowerPoint.
- No inventa cifras, referencias ni datos para "llenar" un gráfico — si
  `contenido.json` no trae `grafico`, la diapositiva no lleva gráfico.
- No sustituye el criterio de contenido de `presentaciones-cientificas`
  (densidad de texto, regla 70/30, límite de bullets, etc.) — ese criterio se
  aplica antes, al redactar; esta skill solo dinamiza lo que ya se decidió.
