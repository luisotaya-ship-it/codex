---
name: diapositivas-dinamicas
description: "Dinamiza y moderniza la estética de una presentación para que deje de verse plana — transiciones nativas de PowerPoint congruentes con cada diapositiva, profundidad/sombra en tarjetas, revelado progresivo de viñetas/imágenes al ritmo de la charla (para que no se vea cargada con mucho texto o muchas fotos a la vez), y un gemelo en HTML (reveal.js) con gráficos animados, diagramas paso a paso e iconos 3D. Úsala SIEMPRE justo después de construir el .pptx en presentaciones-cientificas, salvo que el usuario pida una versión simple, sin animaciones. Úsala también cuando diga hazlo más dinámico, se ve muy plano, quiero animaciones, que las imágenes aparezcan, que no se vea tan cargada, versión más moderna/3D, o adjunte un .pptx pidiendo mejorarlo visualmente. No decide el contenido ni inventa datos, solo dinamiza lo ya escrito."
---

# Diapositivas dinámicas — acabado estético y movimiento

Convertir una presentación ya redactada (normalmente por `presentaciones-cientificas`,
pero funciona con cualquier `.pptx`) en algo que se sienta vivo sin dejar de ser
serio: transiciones reales entre diapositivas, profundidad visual en tarjetas y
diagramas, y un gemelo HTML con gráficos animados, diagramas que se revelan paso
a paso y acentos 3D en CSS puro. El principio guía es honestidad técnica: cada
efecto que esta skill promete, lo puede verificar antes de entregarlo; lo que no
puede verificar (animaciones de aparición nativas dentro del `.pptx`), lo dice
explícitamente en vez de arriesgarse a entregar un archivo que PowerPoint tenga
que "reparar" delante del público.

## Por qué el trabajo se reparte entre .pptx y .html

`python-pptx` no tiene API de animaciones; la única forma de añadir animaciones
de aparición por elemento es escribir a mano el árbol OOXML `<p:timing>`, que es
intrincado y no se puede validar por completo sin PowerPoint real — un error
sutil ahí produce el diálogo de "reparar archivo" delante de los especialistas
que están evaluando al residente, justo lo contrario de lo que se busca. Por eso:

- El **`.pptx`** recibe solo lo que se puede verificar con certeza: transiciones
  de diapositiva nativas (`<p:transition>`, un elemento simple y bien
  documentado) y sombras de profundidad en formas (`<a:outerShdw>`, igual de
  estándar y seguro). Ambos se aplican con módulos que se autovalidan.
- El **`.html`** (reveal.js) es donde vive el dinamismo que de verdad requiere
  animación de aparición, gráficos que se dibujan y profundidad 3D: aquí cada
  línea de JS/CSS se escribe y se puede leer antes de entregarla, así que no
  hay excusa para no hacerlo bien.

Entregar ambos no es redundante: el `.pptx` es la garantía que funciona en
cualquier proyector de hospital sin internet; el `.html` es la versión que
realmente "se mueve" cuando hay un portátil con navegador disponible.

## Flujo de trabajo

### 1. Elegir el preset

Lee `references/presets-estilo.md`. Hay cuatro: `sobrio` (institucional, por
defecto), `congreso` (moderno/llamativo para charla internacional), `marca`
(respeta colores/plantilla institucional del usuario — extráelos del archivo
adjunto si existe, nunca los adivines) y `ficha_clinica` (infografía de guía
de un solo vistazo — semáforo de color, tabla, tarjetas de acento; usar en
1-3 diapositivas "resumen" de un deck, no en todo el deck).

### 2. Dinamizar el `.pptx`

```bash
python3 scripts/pptx_dinamizar.py entrada.pptx salida.pptx --preset sobrio --impacto 5,12,18
python3 scripts/pptx_profundidad.py salida.pptx salida.pptx --intensidad media
```

`--impacto` recibe los números de diapositiva (1-indexado) que ya se diseñaron
como "de alto impacto" (fondo oscuro, cierre narrativo) — reciben la transición
más dramática del preset; el resto recibe la transición base. Si no sabes
cuáles son de alto impacto (por ejemplo, el usuario adjuntó un `.pptx` ajeno),
omite `--impacto` y todas las diapositivas reciben la transición base — más
seguro que adivinar cuáles merecen un efecto especial.

Después de correr ambos scripts, el propio `pptx_dinamizar.py` valida el
paquete (`validate_pptx_transition_package`) y falla ruidosamente si algo
quedó mal formado — si eso pasa, no hay que intentar "arreglarlo a mano" en el
XML: entregar el `.pptx` sin dinamizar (con nota al usuario) es preferible a
forzar un archivo sospechoso.

### 2b. Diapositiva sobrecargada en el .pptx (varias imágenes o mucho texto)

Si una diapositiva del `.pptx` trae 2+ imágenes o mucho texto y se sentiría
"cargada" al proyectarse de golpe, no la dejes así solo porque el `.pptx` no
soporta fragmentos: usa `scripts/pptx_morph_helper.construir_secuencia_revelado()`
para repartirla en 2-4 diapositivas casi idénticas (una por elemento nuevo),
encadenadas con Morph — ver `references/tecnica-morph-real.md § Revelado
progresivo en el .pptx real`. Verifica siempre con
`verificar_secuencia_revelado()` antes de aplicar la transición, y aplica
`pptx_dinamizar.py --morph-en` sobre los índices que devuelve. Esto multiplica
el número de diapositivas del deck — avisa al usuario en una frase ("la
diapositiva de hallazgos radiológicos ahora son 3 diapositivas seguidas para
que cada foto entre por separado") en vez de dejar que lo descubra solo.

### 2c. Menú de navegación clicable (opcional)

Si el usuario pidió "un menú interactivo", "que se pueda saltar entre
secciones" o el deck tiene una diapositiva de índice/agenda clara, usa
`scripts/pptx_botones_helper.py` → `construir_menu_interactivo()` sobre el
mismo `.pptx` (antes o después de `pptx_dinamizar.py`, el orden no importa
porque son mecanismos distintos: transiciones vs. hipervínculos). No inventes
las secciones — reutiliza el índice que ya redactó `presentaciones-cientificas`
o el que te dé el usuario.

### 3. Construir el gemelo HTML

Arma `contenido.json` con el mismo texto/guion ya redactado (ver
`references/esquema-json.md` para el formato exacto — no te saltes los campos
`tipo` de cada diapositiva, son los que deciden qué plantilla visual usar).

**Si una diapositiva tiene varias imágenes o más de 4 viñetas**, usa el campo
`revelado` ("progresivo" para acumular, "reemplazo" para comparar una a la
vez — ver `references/esquema-json.md § Revelado progresivo`) en vez de
dejar que todo entre junto: esto es lo que sincroniza cada imagen/punto con
el momento en que el presentador habla de él y evita que la diapositiva se
sienta cargada. `build_html_dinamico.py` imprime avisos de densidad al
construir el HTML — revísalos y ajusta antes de entregar, no los ignores.

```bash
python3 scripts/build_html_dinamico.py contenido.json salida.html --preset sobrio
# Preset "marca" con colores extraídos de la plantilla institucional:
python3 scripts/build_html_dinamico.py contenido.json salida.html --preset marca \
    --color-primario "#0B3D91" --color-acento "#00A19A"
```

El HTML resultante es un archivo único y autocontenido (usa CDN de reveal.js y
Chart.js, así que necesita internet la primera vez que se abre) — se abre con
doble clic en cualquier navegador, se presenta con las flechas del teclado, y
`S` abre la vista de notas del orador si `contenido.json` incluía `guion`.

### 4. Verificar antes de entregar (no es opcional)

- Confirmar que `pptx_dinamizar.py` terminó con "Validación de paquete: OK".
- Abrir el `.pptx` resultante con LibreOffice/soffice y convertir 2-3
  diapositivas a imagen para confirmar que no hay colisiones nuevas causadas
  por las sombras de profundidad (una sombra puede hacer que una tarjeta se
  vea recortada si estaba pegada al borde de la diapositiva).
- Revisar el HTML generado: abrirlo (o al menos revisar que no haya errores de
  sintaxis JS con `node --check` sobre el bloque de script si se editó a mano)
  y confirmar que cada diapositiva `grafico` tiene datos reales, no inventados.
- Leer los "Avisos de densidad visual" que imprime `build_html_dinamico.py` al
  generar el HTML — si aparecen, decidir si se ajusta el `revelado` o se
  divide la diapositiva antes de entregar, no ignorarlos.
- Si el usuario pidió preset `marca`, confirmar que los colores usados
  coinciden con los que se extrajeron del archivo institucional, no con una
  paleta genérica.

### 5. Entregar

Copiar ambos archivos (`.pptx` dinamizado y `.html`) a la carpeta de salida y
explicar en una frase cuándo usar cada uno (proyector sin internet → `.pptx`;
portátil con navegador o quiere ver los gráficos animarse → `.html`).

## Integración con otras skills

Lee `references/integracion.md` antes de la primera vez que uses esta skill en
una sesión: ahí está el detalle de cómo encadenarla justo después de
`presentaciones-cientificas` (caso normal), cómo aplicarla sobre un `.pptx` que
el usuario ya tiene, y qué cosas esta skill deliberadamente no hace.

## Límites que hay que comunicar al usuario, no ocultar

- Las transiciones y sombras del `.pptx` se probaron abriendo el archivo con
  LibreOffice y validando la estructura OOXML; no hay forma de confirmar en
  este entorno que PowerPoint de escritorio las reproduce pixel-perfecto en
  todas las versiones (Morph, por ejemplo, necesita PowerPoint 2019+ y cae de
  forma segura a un fundido si la versión es más antigua).
- El `.html` necesita conexión a internet la primera vez que se abre (carga
  reveal.js y Chart.js desde CDN) — si el lugar de exposición no tiene
  internet, avisar con antelación y probarlo offline antes del día del evento,
  o generar la versión sin conexión bajando los archivos de CDN localmente si
  el usuario lo pide.
- Nunca prometer "animaciones dentro del PowerPoint" si lo que se hizo fueron
  transiciones de diapositiva — son cosas distintas y hay que nombrarlas bien.

## Archivos de referencia

- `references/presets-estilo.md` — los 4 presets de estilo, cuándo usar cada uno.
- `references/esquema-json.md` — formato exacto de `contenido.json` para el HTML, incluye los tipos `indice` (menú acordeón), el campo `diagrama.zoom_progresivo`, y `revelado`/`imagenes` para revelado progresivo de viñetas y fotos.
- `references/tecnica-morph-real.md` — qué se confirmó por video (Morph) y qué se implementó con conocimiento general verificado (botones, acordeón, zoom progresivo, secuencia de revelado progresivo en .pptx) — honestidad sobre las fuentes de cada técnica.
- `references/integracion.md` — cómo encadenar esta skill con `presentaciones-cientificas`
  y qué hacer cuando el usuario ya tiene un `.pptx` propio.
- `scripts/pptx_dinamizar.py` — transiciones nativas del `.pptx` (con autovalidación), incluye `--morph-en` para forzar Morph en pares de diapositivas específicos.
- `scripts/pptx_morph_helper.py` — duplica una diapositiva conservando nombres de forma (y migrando correctamente las relaciones de imagen), verifica si un par va a producir Morph real, y construye secuencias completas de revelado progresivo (`construir_secuencia_revelado`) para diapositivas con varias imágenes.
- `scripts/pptx_botones_helper.py` — menús de navegación e "índice clicable" con `click_action` nativo (API estable de python-pptx desde Office 2007): botones que saltan a una diapositiva y botón "⌂ volver al menú" en cada sección.
- `scripts/pptx_profundidad.py` — sombras de profundidad en tarjetas/cuadros del `.pptx`.
- `scripts/build_html_dinamico.py` — genera el gemelo HTML animado/3D (reveal.js + Chart.js).
- `scripts/vendor/pptx_transitions.py` — motor OOXML de transiciones (MIT, proyecto
  [ppt-master](https://github.com/hugohe3/ppt-master) de Hugo He; licencia completa en
  `scripts/vendor/LICENSE_pptx_transitions.txt`). No modificar este archivo directamente:
  si hace falta un comportamiento nuevo, envolverlo desde `pptx_dinamizar.py`.
