# Morph real: lo aprendido de tutoriales nativos de PowerPoint

Esta nota documenta una técnica CONFIRMADA (no inferida) analizando el
tutorial ["La mejor TRANSICIÓN de POWERPOINT ✅ Morph ✅"](https://www.youtube.com/watch?v=2rU_g5WAYGc)
del canal de Jazz Guzman (playlist "Los MEJORES EFECTOS para presentaciones
Impactantes en PowerPoint"), que hasta ahora esta skill no explotaba: **Morph
es 100% automatizable de forma segura con python-pptx**, sin tocar el árbol
`<p:timing>` de animaciones que el resto de esta skill evita a propósito.

## El mecanismo real (no es magia de IA de PowerPoint)

Morph no "detecta cambios" entre dos diapositivas de forma inteligente. El
motor de PowerPoint compara las formas de la diapositiva N con las de la
diapositiva N+1 **por su nombre interno** (`shape.name`, visible en el Panel
de selección de PowerPoint, `Alt+F10`):

- Si dos formas tienen el **mismo nombre** en ambas diapositivas → Morph
  interpola posición, tamaño, rotación, color y (para cuadros de texto)
  el contenido — de ahí salen los efectos de "objeto que se mueve/crece",
  "texto que se transforma letra a letra" y "objeto que entra/sale del
  lienzo" (basta con ponerlo fuera de los límites de la diapositiva en un
  extremo del par).
- Si el nombre **no coincide**, Morph no falla ni avisa — simplemente hace un
  fundido cruzado normal en esa forma, como si la transición fuera "fade".
  Este es el error más común y silencioso: el usuario cree que configuró
  Morph pero varias formas no se están transformando porque no las renombró.

## Por qué esto cambiaba el análisis de riesgo de esta skill

Antes de esta nota, `SKILL.md` explicaba que **ninguna** animación nativa se
automatizaba porque la única vía (escribir `<p:timing>` a mano) no se puede
validar sin PowerPoint real. Eso sigue siendo cierto para animaciones de
**aparición por elemento** (entrance animations del Panel de Animación). Pero
Morph no vive en `<p:timing>` — vive en `<p:transition>`, el mismo elemento
simple y auto-validable que ya usa `pptx_dinamizar.py` para fade/push/wipe/etc.
Lo único que faltaba era la mitad de "contenido": duplicar una diapositiva
conservando nombres de forma, y una forma de verificar que el par realmente
va a producir Morph antes de entregarlo. Eso es lo que añade
`scripts/pptx_morph_helper.py`.

## Cómo usarlo en esta skill

1. Construye (o identifica) la diapositiva "de partida" del efecto Morph.
2. Duplícala con `duplicar_diapositiva(prs, indice)` — conserva todos los
   nombres de forma automáticamente, porque copia el XML tal cual.
3. Modifica SOLO lo que debe animarse en la diapositiva nueva (mover una
   forma, cambiar su tamaño, reescribir el texto de un cuadro con el mismo
   nombre) usando la API normal de python-pptx (`shape.left`, `shape.width`,
   `shape.text_frame.text`, etc.).
4. Antes de entregar, corre `verificar_par_morph(prs, indice_a, indice_b)` y
   lee el resumen — si dice "NINGUNA forma coincide", algo en el paso 2 rompió
   un nombre (por ejemplo, si en vez de duplicar creaste una forma nueva desde
   cero) y hay que corregirlo antes de continuar.
5. Aplica la transición con `pptx_dinamizar.py ... --morph-en <n>`, donde
   `<n>` es el número (1-indexado) de la diapositiva de **llegada** del par
   (Morph se configura en la diapositiva a la que se entra, no en la de
   salida — así es como lo aplica PowerPoint real).

## Límite de esta técnica

Sigue sin cubrir animaciones de aparición dentro de una misma diapositiva
(una viñeta que aparece al hacer clic, por ejemplo) — eso sigue siendo
`<p:timing>` y sigue fuera del alcance seguro de esta skill. Morph resuelve un
subconjunto específico pero muy vistoso: transformar/mover/redimensionar
formas y texto **entre** dos diapositivas consecutivas.

## Otras técnicas de la playlist: qué se pudo verificar y qué no

Se intentó dos veces extraer subtítulos del resto de la playlist (Zoom de
sección, Zoom infinito, menús interactivos, acordeón, Parallax, Efectos 3D).
La primera vez YouTube dejó de servir subtítulos tras varios vídeos seguidos;
la segunda vez (con Chrome ya reconectado) el bloqueo fue más profundo: los
propios vídeos se quedaron en `readyState 0` (sin cargar datos de video en
absoluto, no solo subtítulos) en varios videos distintos de forma consistente
— es decir, YouTube empezó a frenar la reproducción misma para esta sesión de
navegador, probablemente por el patrón de saltos rápidos de tiempo (`seek`)
usado para barrer subtítulos sin ver el video completo. No es algo que se
pueda resolver reintentando con más código.

Con eso como límite real (no un "no lo intenté"), esto es lo que sí se hizo
con las dos técnicas restantes que valía la pena resolver ahora:

- **Botones/menús de navegación** (`pptx_botones_helper.py`): no se pudo
  confirmar por video el detalle exacto de la técnica de Jazz Guzman, pero el
  mecanismo (`click_action`/hipervínculo interno) es API pública y estable de
  python-pptx desde Office 2007 — se implementó, se probó de verdad (enlaces
  internos verificados releyendo el `.pptx`, render en LibreOffice sin
  errores) y se documenta como **[Evidencia]** de la documentación oficial de
  python-pptx, no como algo visto en el tutorial.
- **Menú de acordeón** (`indice` en el `.html`): tampoco se pudo confirmar el
  detalle visual exacto del tutorial de acordeón de Jazz Guzman. Se construyó
  con `<details>/<summary>` nativos de HTML — un patrón de acordeón estándar y
  accesible, no una reconstrucción de lo que se ve en ese video específico.
- **Zoom de sección (nativo de PowerPoint)**: sigue sin automatizarse — es un
  mecanismo OOXML propio (miniaturas embebidas + enlaces de sección) fuera del
  alcance seguro de esta skill. En su lugar se construyó `zoom_progresivo`
  para diagramas en el `.html`: una aproximación honesta con fragmentos de
  reveal.js (resalta/agranda el paso actual), etiquetada explícitamente como
  aproximación y no como el efecto Zoom real de PowerPoint.
- **Disparadores (Triggers) del Panel de Animación**: el mecanismo general es
  conocimiento estable y bien documentado de Microsoft (clic derecho sobre una
  animación → Cronología → Desencadenar → Al hacer clic en → elegir el
  objeto), pero vive dentro de `<p:timing>` con un `<p:cond>` de disparador —
  sigue fuera del alcance seguro de automatización de esta skill. Queda como
  instrucción manual para el usuario.
- **Parallax / Efectos 3D**: sin cambios esta ronda — ya existían en el
  gemelo HTML (`fondo_parallax`, `icono_3d`) de rondas anteriores de esta
  skill, no se pudo contrastarlos contra la técnica específica del tutorial.

Si en el futuro el bloqueo de YouTube se libera, sigue pendiente confirmar el
detalle visual exacto de Zoom, acordeón y Parallax tal como los construye Jazz
Guzman, por si hay un matiz que valga la pena incorporar además de lo ya
implementado aquí con conocimiento general verificado.

## Revelado progresivo en el .pptx real (secuencia de Morph)

El HTML resuelve "que las imágenes/viñetas aparezcan una a la vez, al ritmo
de la charla" con fragmentos reales de reveal.js (ver `esquema-json.md §
Revelado progresivo`). El `.pptx` no tiene un mecanismo equivalente seguro
dentro de UNA sola diapositiva — la única vía es `<p:timing>`, fuera del
alcance de esta skill. Pero el problema que motivó pedirlo ("no se vea tan
cargada con muchas imágenes o texto") sí se resuelve en `.pptx` real con la
misma Morph que ya se documentó arriba, aplicada distinto:

En vez de una diapositiva con 3 fotos a la vez, `pptx_morph_helper.
construir_secuencia_revelado()` construye 3 diapositivas casi idénticas —
cada una con una foto más que la anterior, todas encadenadas con Morph. El
título y las formas ya reveladas comparten nombre entre diapositivas
consecutivas (Morph las deja quietas, sin efecto visible) y cada foto nueva
NO existe en la diapositiva anterior, así que Morph la hace entrar con un
fundido/transformación suave en vez de aparecer de golpe. El presentador
avanza diapositiva por diapositiva (flecha derecha normal, no fragmentos) y
en cada paso el público ve exactamente una imagen más que en el paso
anterior — mismo resultado percibido que el revelado progresivo del HTML,
logrado con un mecanismo enteramente distinto porque el `.pptx` no tiene
fragmentos.

**Bug real encontrado y corregido en QA (no una advertencia teórica):** la
primera versión de `duplicar_diapositiva()` copiaba el XML de las formas
(incluida la referencia `r:embed` de las imágenes) pero NO migraba la
relación `.rels` correspondiente. Resultado: en la diapositiva duplicada, la
imagen "vieja" quedaba con un `r:embed` huérfano que LibreOffice resolvía
contra la relación que coincidiera por número con la imagen agregada
DESPUÉS — en la prueba, dos fotos de colores distintos (roja y verde)
terminaron renderizando ambas en verde. Se corrigió migrando explícitamente
cada relación (`part.relate_to()`) al part de la diapositiva nueva,
reutilizando el mismo part de imagen (no duplica los bytes de la foto) y
reescribiendo el rId en el XML copiado. Se verificó con Playwright/LibreOffice
render a PNG de una secuencia real de 4 diapositivas (base + 3 capas): cada
paso mostró exactamente las fotos correctas en el color/posición correctos,
y `pptx_dinamizar.py --morph-en` validó el paquete sin errores.

Uso:
```python
from pptx_morph_helper import construir_secuencia_revelado, verificar_secuencia_revelado, CapaRevelado

capas = [
    CapaRevelado([{"ruta": "rx1.jpg", "left": Inches(0.7), "top": Inches(1.6), "width": Inches(3.5), "nombre": "FotoA"}]),
    CapaRevelado([{"ruta": "rx2.jpg", "left": Inches(4.4), "top": Inches(1.6), "width": Inches(3.5), "nombre": "FotoB"}]),
]
indices_nuevos = construir_secuencia_revelado(prs, indice_base=0, capas=capas)
for r in verificar_secuencia_revelado(prs, 0, indices_nuevos):
    assert r.morph_tendra_efecto  # por construcción siempre True; se verifica igual
# indices_nuevos = [1, 2] (0-indexado) -> pasar 2,3 (1-indexado) a --morph-en
```

Esta técnica solo tiene sentido cuando el usuario necesita el `.pptx` para
proyectar sin depender de un navegador (el caso típico: auditorio de
hospital). Si el usuario va a presentar desde su portátil con el HTML, el
revelado progresivo con fragmentos de reveal.js es más simple y no multiplica
el número de diapositivas — usar la secuencia de Morph solo cuando el
`.pptx` es el entregable que de verdad se va a proyectar en vivo.
