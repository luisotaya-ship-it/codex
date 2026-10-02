---
name: imagenes-contextuales-diapositivas
description: "Busca o genera una fotografía/imagen de contexto (real, de banco libre, o creada por IA) para diapositivas que se ven planas o solo con texto/viñetas — p. ej. la foto de un paciente con EPOC en una diapositiva sobre exacerbaciones. Úsala SIEMPRE que pidan \"ponle imágenes/fotos a las diapositivas\", \"que no se vea tan plano\", \"imágenes reales o de IA según el tema\", compartan una diapositiva de ejemplo con fotos y pidan algo parecido, o se quejen de que el deck es solo texto. Verifica siempre la licencia de cualquier foto de internet antes de insertarla (bancos abiertos: CDC PHIL, NLM Open-i, Wikimedia Commons con licencia CC, Unsplash/Pexels/Pixabay) — nunca inserta una imagen con copyright sin verificar. NO es para diagramas ni gráficos de datos (usa `diagramas-clinicos`) ni para la portada/pieza única de una presentación (usa `imagenes-creativas-medicas`) — esta trabaja diapositiva por diapositiva dentro de un deck existente o en construcción."
---

# Imágenes de contexto en diapositivas

## Qué resuelve esta skill

Un deck puede tener buen contenido clínico y aun así verse "plano" porque cada
diapositiva es título + viñetas, sin nada que el ojo reconozca de inmediato.
Esta skill existe para esa fase específica: recorrer un deck (propio o en
construcción) y, diapositiva por diapositiva, decidir si necesita una
**fotografía o imagen de contexto** — real, de banco libre, o generada por
IA — que acompañe al texto, y conseguir/producir esa imagen en vez de
quedarse en "podrías ponerle una foto de un paciente con EPOC aquí".

No se solapa con las otras skills de imagen de este usuario:

| Skill | Qué produce | Cuándo usarla en vez de esta |
|---|---|---|
| `diagramas-clinicos` | Algoritmos, flujogramas, forest plots, líneas de tiempo — representación exacta de datos o lógica clínica | El contenido de la diapositiva es un dato, un algoritmo o una relación causal, no una escena o hallazgo visual |
| `imagenes-creativas-medicas` | Una pieza artística única (portada, póster, infografía) | Se necesita **una sola** imagen de impacto para la portada o el cierre, no una imagen por cada diapositiva de contenido |
| `plantilla-uninavarra` | El fondo institucional y la zona segura del deck | Define dónde puede ir la imagen que esta skill consigue, no la consigue ella misma |
| `diapositivas-dinamicas` | Movimiento y transiciones sobre un `.pptx` ya terminado | Se aplica **después** de que el contenido y las imágenes ya están puestos |
| **`imagenes-contextuales-diapositivas`** (esta) | Una fotografía/imagen de contexto por diapositiva de cuerpo, real o generada, con su fuente verificada | El pedido es "que no se vea tan plano/tan de texto", con imágenes que ilustren el tema de cada diapositiva |

## Paso 1 — Inventario: qué diapositivas necesitan imagen de contexto

Revisa el `.pptx` (o la lista de contenido si el deck todavía se está
redactando junto con `presentaciones-cientificas`) y clasifica cada
diapositiva de cuerpo:

- **Candidata clara**: diapositiva de solo texto/viñetas cuyo contenido tiene
  una contraparte visual reconocible — manifestaciones clínicas, impacto
  humano/psicosocial de la enfermedad, entorno de atención, un hallazgo
  físico específico, un fármaco/dispositivo, una escena de urgencias o
  consulta.
- **No forzar imagen**: diapositivas de datos puros, algoritmos, escalas o
  tablas de dosis — esas ya tienen su propio visual (`diagramas-clinicos`) y
  meterles además una foto decorativa compite por espacio y distrae.
- **Portada/cierre**: no son el objetivo de esta skill — para una pieza única
  de alto impacto ahí, usa `imagenes-creativas-medicas`.
- **Cuota razonable**: no todas las diapositivas necesitan foto. 1 imagen de
  contexto cada 3-5 diapositivas de contenido suele bastar para romper la
  monotonía sin saturar el deck ni parecer relleno. Si el usuario pidió
  explícitamente "en todas", respétalo, pero adviértelo si el resultado
  empieza a verse recargado.

Presenta brevemente esta clasificación antes de salir a buscar/generar nada
(qué diapositivas llevarán imagen y por qué) — no hace falta pedir
aprobación para continuar, solo dejar claro el criterio.

## Paso 2 — Clasificar qué tipo de imagen pide cada diapositiva candidata

No todas las imágenes de contexto son intercambiables. Antes de elegir la
fuente (Paso 3), decide a cuál de estas tres categorías pertenece cada
diapositiva candidata — la categoría determina si la imagen puede ser
generada por IA o tiene que ser real:

1. **Hallazgo clínico que debe ser diagnósticamente fiel** (un exantema, un
   fondo de ojo, una radiografía, una lesión dermatológica, un signo físico
   específico). **Tiene que ser una fotografía real** de fuente médica
   verificable — nunca generada por IA, porque un modelo de imagen puede
   producir un hallazgo clínicamente incoherente (proporciones, coloración,
   distribución) que un residente o un evaluador reconocería como incorrecto.
2. **Escena o contexto humano/asistencial** sin pretensión de ser un caso
   clínico verídico específico (un paciente genérico con oxígeno, una
   consulta, un ambiente de urgencias, una familia en sala de espera). Puede
   ser foto de banco libre **o** imagen generada por IA — lo que mejor se
   ajuste al tono y a lo que haya disponible con licencia clara.
3. **Elemento decorativo/conceptual** sin pretensión clínica (un ícono, una
   metáfora visual, un fondo abstracto). Generado por IA o vectorial es
   perfectamente válido aquí. Si el elemento decorativo pertenece a una
   campaña o identidad institucional (como el ícono de una campaña vigente en
   el fondo de `plantilla-uninavarra`), **no lo recrees por tu cuenta** — ese
   elemento pertenece al fondo oficial, no se inventa.

## Paso 3 — Buscar, verificar licencia y descargar (automatizado, no solo explicado)

Esta skill no se queda en "búscalo en tal banco": ejecuta
`scripts/buscar_y_descargar.py`, que busca, verifica la licencia y descarga
el archivo real. Los resultados de un buscador de imágenes genérico **no
están libres de derechos por el solo hecho de aparecer ahí** — por eso el
script solo trae de vuelta un archivo cuando pudo confirmar una licencia
abierta, y se niega a descargar cuando no puede verificarla.

**3.1 — Categoría 2 y 3 (escena/contexto, decorativo) → Wikimedia Commons**

```bash
python3 scripts/buscar_y_descargar.py commons-buscar "<términos en inglés>" --limite 8
python3 scripts/buscar_y_descargar.py commons-info "File:Título del candidato.jpg"
python3 scripts/buscar_y_descargar.py commons-descargar "File:Título del candidato.jpg" \
    --destino <carpeta-de-trabajo>/imagenes_descargadas/nombre.jpg
```

`commons-descargar` ya revalida la licencia antes de traer el archivo y
rechaza cualquier candidato sin licencia abierta reconocida (dominio
público, CC0, CC BY, CC BY-SA; CC BY-NC se acepta marcado como "solo uso
académico/no comercial", que es el caso de esta presentación). Buscar en
inglés da muchos más resultados que en español.

**3.2 — Categoría 1 (hallazgo clínico real con cita) → NLM Open-i**

```bash
python3 scripts/buscar_y_descargar.py openi-buscar "<hallazgo clínico en inglés>" --limite 8
# revisar el campo "caption" de cada candidato — debe describir el hallazgo real que necesitas
python3 scripts/buscar_y_descargar.py openi-descargar --pmcid <uid del candidato> \
    --url "<img_large del candidato>" \
    --destino <carpeta-de-trabajo>/imagenes_descargadas/hallazgo.png
```

`openi-descargar` verifica la licencia por su cuenta contra el servicio de
acceso abierto de NCBI (por PMCID) antes de traer el archivo — no hace falta
(ni conviene: la página de artículo de PMC suele bloquear el acceso
automatizado con un reCAPTCHA) intentar leer el artículo con la herramienta
de navegación web para esto. Si el artículo no está en el subconjunto de
acceso abierto de PMC, el script rehúsa descargar en vez de asumir que es
seguro usarlo — en ese caso, prueba otro candidato u otra query.

Si la licencia devuelta trae cláusula **ND** (No Derivatives — el propio
script lo marca con `"editable": false`), esa imagen se inserta tal cual,
**sin pasarla por `tratar_imagen.py`** ni recortarla.

**3.3 — Si ninguno de los dos bancos da un resultado adecuado**

Generar con IA (motor vectorial/Pillow de `imagenes-creativas-medicas`, o el
motor de generación de imágenes disponible en el entorno) — válido para
categorías 2 y 3, **nunca para la categoría 1** (un hallazgo clínico
generado por IA puede ser clínicamente incoherente).

**3.4 — Filtro que ningún script puede aplicar por ti: revisar el rostro**

Una licencia abierta autoriza el uso legal de la imagen, pero no dice nada
sobre si es apropiada para *esta* presentación. Antes de aceptar un
candidato de categoría 2 que muestre a una persona, **ábrelo con la
herramienta de lectura de imágenes** y revisa si es un rostro identificable
de un paciente real en un contexto clínico. Si lo es, **descártalo aunque la
licencia sea perfectamente abierta** — que el autor original haya liberado
la licencia no equivale a que esa persona haya consentido aparecer en el
material de estudio de un residente en otro país. Prefiere composiciones sin
rostro identificable (manos, equipo médico, espalda, plano general, o un
rostro no reconocible) para ilustrar "paciente genérico". Esto ya pasó en
las pruebas de esta skill: un candidato con licencia CC BY-SA 4.0
perfectamente válida mostraba a una paciente real reconocible — se descartó
igual.

**Otros bancos (CDC PHIL, OMS, StatPearls, Unsplash/Pexels/Pixabay).** No
tienen una API tan directa como Commons/Open-i; ver
`references/bancos-imagenes.md` para el procedimiento con `web_fetch`/`WebFetch` +
descarga por la terminal (`bash_tool`/`Bash`) en cada uno. Úsalos cuando Commons/Open-i no den un
resultado adecuado, antes de recurrir a generar con IA.

**Registro de fuente obligatorio.** Cada imagen que termina insertada en el
archivo lleva registrada su fuente y licencia (banco + enlace/PMCID, o
"generada con IA") en las notas del orador de esa diapositiva o en un pie
discreto — así el usuario puede verificarla antes de exponerla en un evento
público o una sustentación formal.

**Nunca pacientes reales identificables sin consentimiento.** Si el propio
usuario aporta una fotografía de un paciente real, aplica la misma regla ya
establecida en `presentaciones-cientificas`: señalarlo, recomendar rostro
difuminado si se proyectará ante público externo, y confirmar consentimiento
antes de usarla con rostro visible.

## Paso 4 — Tratamiento visual para que no se vea "collage"

Imágenes sacadas de fuentes distintas (bancos distintos + piezas de IA)
suelen no combinar bien entre sí — proporciones, temperatura de color y
recorte inconsistentes. `scripts/tratar_imagen.py` resuelve el recorte a la
proporción que necesita el layout y aplica un tratamiento de cohesión ligero
(cortes de esquina consistentes, ajuste tonal sutil) para que todas las
imágenes del deck se sientan de la misma familia visual.

**Excepción que no se negocia**: nunca apliques ajuste de color/tono a una
imagen de la categoría 1 (hallazgo clínico real) — el color es a menudo el
dato clínico (eritema, cianosis, ictericia, hallazgo dermatológico). Con esas
imágenes, `tratar_imagen.py` solo debe recortar/redimensionar, nunca
retocar color. El script separa ambos modos explícitamente (ver
docstring) — pásale siempre el modo correcto.

## Paso 5 — Insertar respetando la plantilla y la zona segura

- Si el deck usa la plantilla institucional (`plantilla-uninavarra`), coloca
  la imagen dentro de la zona de contenido principal de esa skill
  (1.45in–7.0in vertical) y nunca sobre la banda roja ni la franja de cita.
- Patrón de layout recomendado (el mismo que se ve en los mejores decks del
  usuario y en el ejemplo que suele traer): imagen ocupando 35-45% del ancho
  a un lado, texto/cifra clave al otro lado — no la imagen de fondo completo
  con texto encima, que casi siempre compromete la legibilidad y el contraste
  exigido por las reglas CRAP ya definidas en `presentaciones-cientificas`.
- Ver `references/insercion-pptx.md` para el snippet exacto de posicionamiento
  con `pptxgenjs`/`python-pptx`, incluida la variante opcional de "tarjeta de
  evidencia" (título + autores + PMID/DOI en una caja, como en el ejemplo del
  usuario) para diapositivas donde conviene mostrar el artículo de origen de
  forma visual además de la cita al pie.

## Paso 6 — Verificación visual obligatoria

Igual que en el resto del ecosistema de skills de este usuario: convertir el
`.pptx` resultante a imágenes (LibreOffice) y mirar cada diapositiva
modificada antes de entregar. Confirmar específicamente:

- Ninguna imagen tapa texto, la franja de cita, ni la banda institucional.
- Ninguna imagen se ve pixelada o estirada fuera de su proporción original.
- El tratamiento de color (si se aplicó) no distorsiona un hallazgo clínico
  real de categoría 1.
- El conjunto de imágenes del deck se siente cohesivo, no un collage de
  estilos sueltos.

## Paso 7 — Entrega

Entregar el `.pptx` actualizado junto con una lista corta "diapositiva N —
fuente de la imagen (banco/licencia o IA)" para que el usuario pueda
verificar antes de usar el material en público. Si el deck todavía no
existía como archivo (se estaba redactando el contenido), coordinar con
`presentaciones-cientificas` para que el `.pptx` final ya incluya las
imágenes en vez de entregarlas sueltas.

## Integración con otras skills

- Normalmente se activa **después** de que `presentaciones-cientificas`
  (o el usuario) ya tiene el contenido y el guion de cada diapositiva —
  esta skill no redacta ni decide qué dice cada diapositiva, solo la
  ilustra.
- Si el deck usa la plantilla institucional, respeta las coordenadas de
  `plantilla-uninavarra` en vez de inventar una zona segura propia.
- Si una diapositiva candidata resulta ser en realidad un dato o un
  algoritmo, redirige a `diagramas-clinicos` en lugar de forzar una foto
  ahí.
- Encadena antes de `diapositivas-dinamicas`: primero contenido + imágenes
  de contexto (esta skill), después el acabado de movimiento/transiciones.

## Ejemplo rápido

Pedido: "las diapositivas de mi gran sesión de EPOC se ven muy de texto,
ponle fotos o imágenes acordes al tema como en este ejemplo" (adjunta una
diapositiva con foto de un paciente con oxígeno junto a las tarjetas de los
artículos citados).

1. Inventario: de 30 diapositivas, 9 son candidatas claras (manifestaciones
   clínicas, impacto en la exacerbación, impacto psicosocial, mortalidad);
   el resto son portada, algoritmos, tablas de dosis o cifras — se dejan sin
   foto.
2. Clasificación por diapositiva: la de "impacto en la exacerbación" es
   categoría 2 (escena humana genérica de paciente con EPOC, no un caso
   clínico verídico) → banco libre o IA; la de "hallazgo en radiografía de
   tórax" (si existiera) sería categoría 1 → solo banco médico real, nunca IA.
3. Fuente: para la escena de paciente con oxígeno (categoría 2), ejecutar
   `commons-buscar "COPD oxygen therapy patient"` y revisar los candidatos
   con `commons-info` antes de descargar — descartando cualquiera que
   muestre un rostro identificable, aunque la licencia sea abierta; si no
   aparece un resultado adecuado, generar con IA una escena genérica y
   sobria. Para un hallazgo real (p. ej. una radiografía con hiperinflación,
   categoría 1), en cambio, se usa `openi-buscar`/`openi-descargar`.
4. Tratamiento: recorte a la proporción del layout (imagen a la izquierda,
   texto/tarjetas de evidencia a la derecha, como en el ejemplo), ajuste
   tonal sutil solo porque es categoría 2.
5. Inserción respetando la zona segura de `plantilla-uninavarra` si aplica.
6. Verificación visual, registro de fuente en notas del orador, entrega.

## Archivos de referencia

- `scripts/buscar_y_descargar.py` — busca, verifica licencia y descarga
  imágenes reales de Wikimedia Commons (categorías 2/3) y NLM Open-i
  (categoría 1, con verificación automática contra el servicio de acceso
  abierto de PMC por PMCID). Este es el paso que reemplaza "búscalo en tal
  banco" por un archivo real ya verificado.
- `references/bancos-imagenes.md` — lista completa de bancos (incluidos los
  que no tienen API directa: CDC PHIL, OMS, StatPearls, Unsplash/Pexels/
  Pixabay) con el procedimiento manual de verificación y descarga para cada
  uno, y las reglas de clasificación de licencia que usa el script.
- `references/insercion-pptx.md` — snippets de posicionamiento en
  `pptxgenjs`/`python-pptx` (layout imagen+texto, variante de tarjeta de
  evidencia) respetando la zona segura.
- `scripts/tratar_imagen.py` — recorte a proporción, tratamiento tonal de
  cohesión (solo para categorías 2 y 3, nunca categoría 1 ni licencias con
  cláusula ND), y exportación al tamaño/dpi correcto para insertar en la
  diapositiva.
