# Guía del motor nativo de PowerPoint (`build_pptx_diagram.py`)

Este motor construye algoritmos/flujogramas clínicos como formas reales de
PowerPoint (óvalos, rombos, cajas, conectores) en vez de una imagen
aplanada. La diferencia importa cuando el destino es una presentación: el
residente puede después abrir el `.pptx`, hacer clic en una caja, corregir
un umbral o mover una flecha — algo imposible con un PNG de Graphviz
incrustado.

## Cuándo usarlo (y cuándo no)

Úsalo cuando el algoritmo va a vivir dentro de un `.pptx` y tiene un tamaño
razonable (hasta ~10-12 nodos, pocas ramas simultáneas por nivel). Para todo
lo demás, sigue siendo mejor Graphviz:

- Destino Word/PDF/imagen suelta → Graphviz (`render_dot.sh`), no este motor.
- Fisiopatología con clusters por sistema, muchos nodos, relaciones no
  estrictamente jerárquicas → Graphviz. Este motor solo entiende una
  jerarquía de niveles (como `rankdir=TB`), no agrupaciones.
- Algoritmo enorme (>12-15 nodos) o con muchísimas ramas paralelas → si el
  layout automático avisa en `warnings` que no cabe ni reduciendo la
  fuente, no insistas escalando más — divide el algoritmo en 2 diagramas
  (ej. "evaluación inicial" + "manejo") o usa Graphviz, que no tiene este
  límite de lienzo.

## Formato del spec

```python
spec = {
    "nodes": [
        {"id": "identificador_unico", "text": "Texto del paso\ncon saltos opcionales", "type": "start_end"},
        # type: "start_end" (óvalo verde) | "decision" (rombo ámbar) |
        #       "action" (caja azul) | "alert" (caja roja, alarma/hospitalización)
    ],
    "edges": [
        {"from": "id_origen", "to": "id_destino", "label": "Sí"},  # label opcional
    ],
    "title": "Título del algoritmo (opcional)",
    "source": "Guía/artículo, organización, año — [Evidencia]",  # muy recomendado
}
```

Reglas de contenido (coherentes con el resto de la skill):

- Las etiquetas de decisión deben llevar el umbral o criterio exacto de la
  guía, no una paráfrasis vaga — igual que en la convención de Graphviz.
- `source` no es decorativo: si se omite, el pie del diagrama queda
  marcado en rojo como `[No verificado]`, igual que el nodo de fuente
  obligatorio en la plantilla `.dot`.
- El texto de cada nodo puede tener `\n` para forzar saltos de línea
  manuales (útil para separar "condición" de "umbral"), pero no hace falta
  envolver manualmente el texto — el layout lo hace automáticamente según
  el ancho disponible.

## Cómo funciona el layout automático ("visualmente adaptable")

1. **Niveles**: cada nodo se ubica en una fila según la distancia más larga
   desde el/los nodo(s) de inicio (igual que `rankdir=TB` de Graphviz).
2. **Tamaño de caja**: se estima a partir del largo real del texto, con
   ajuste de tamaño de fuente hacia abajo si hace falta.
3. **Alto de la diapositiva**: se calcula a partir del contenido, no al
   revés — un algoritmo de 3 pasos genera una diapositiva estándar
   (7.5in), uno de 8 pasos genera una más alta. Si el resultado es más alto
   que el estándar, `warnings` lo informa y sugiere escalar las formas al
   pegarlas en un mazo de tamaño fijo.
4. **Ancho de fila**: si una fila con varias ramas no cabe en el ancho de
   la diapositiva, esa fila se reduce de escala hasta que quepa.
5. **Aristas "salteadas"**: cuando una rama va directo a un nodo dos o más
   niveles más abajo (ej. una rama "No" que salta directo al cierre del
   algoritmo), la flecha se enruta por un carril lateral en vez de dibujar
   una línea recta que atravesaría las cajas intermedias.

## QA automático de solapes (no solo confiar en el layout)

Además de las advertencias de tamaño/fuente, `build_algorithm_pptx()` mide
por geometría, al final de la construcción, si algún nodo o etiqueta quedó
encima de otro (`_check_overlaps`) y lo agrega a `warnings` con el nombre
de los dos elementos involucrados. Esto existe porque un bug real ya llegó
al usuario así: una etiqueta de arista larga con un espacio de fila fijo
terminó tapando la caja de abajo, y nadie lo detectó hasta abrir el
archivo. La aritmética del layout ahora reserva espacio dinámicamente para
evitar esto (ver más arriba), pero esta verificación es la red de
seguridad que lo confirma en cada generación — no un reemplazo de mirar el
PNG, sino un chequeo adicional barato que atrapa la mayoría de los casos
antes de eso.

## Bug corregido: asignación de niveles con caminos de distinta longitud

Probando el motor con un algoritmo real (manejo de hipoglucemia, con una
rama que hace "Regla 15-15 → reevaluar" y otra que hace "grave → glucagón/IV
→ reevaluar", de distinto largo, convergiendo en el mismo nodo de decisión)
apareció un bug real en `_layer_nodes`: el nodo alcanzado primero por el
camino MÁS CORTO quedaba "congelado" en esa fila aunque un camino paralelo
más largo llegara después y debiera empujarlo más abajo. El síntoma visible
fue un nodo de escalamiento ("persiste, repetir tratamiento") dibujado al
lado de la decisión que lo origina en vez de debajo, con la etiqueta de la
arista lateral cayendo encima de la caja vecina.

Se corrigió reimplementando `_layer_nodes` como una pasada topológica
(Kahn): un nodo solo se procesa una vez que TODOS sus predecesores ya
fueron procesados, así que su nivel final siempre es el máximo real sobre
todos los caminos de entrada, sin importar el orden en que se recorran. Esto
es relevante para cualquier algoritmo con ramas que convergen después de
caminos de distinto número de pasos (común en escalamiento terapéutico:
"si falla lo simple, se agregan pasos, y todo converge en la reevaluación").

De paso también se corrigió el conector lateral (mismo nivel): antes
entraba hasta el CENTRO de la caja destino en vez de su borde, lo que
también podía hacer que la etiqueta quedara encima de la caja destino
incluso cuando el nivel sí era correcto.

## Bug corregido: texto de 3+ líneas en óvalos de inicio/fin

Un óvalo con 3 o más líneas de texto cercano al ancho máximo de su caja
mostraba la última línea cortada por la curva del óvalo — el cálculo de
tamaño reservaba espacio como si fuera un rectángulo, pero un óvalo
"recorta" las esquinas del rectángulo que lo contiene, así que el texto
cerca de los bordes queda visualmente fuera de la forma. Se corrigió
agrandando la caja (`OVAL_AREA_PENALTY`) para óvalos con 3+ líneas, igual
en espíritu al ajuste que ya existía para rombos de decisión.

## Siempre revisar `warnings` y verificar visualmente

`build_algorithm_pptx()` devuelve `{"path": ..., "warnings": [...]}`.
`warnings` no vacío no significa que el archivo esté roto, pero sí que el
layout tuvo que ceder en algo (fuente más pequeña, fila más angosta,
diapositiva más alta) — léelo y decide si conviene simplificar el spec
antes de entregar.

Independientemente de `warnings`, verifica el resultado visualmente antes
de entregarlo — igual que exige esta skill para Graphviz y matplotlib:

```bash
soffice --headless --convert-to png archivo.pptx
```

y luego abre el PNG resultante con la herramienta de lectura de imágenes.
No entregues el `.pptx` solo porque el script terminó sin errores.

## Insertar sobre una plantilla con encabezado/pie propios (ej. UNINAVARRA)

Si el diagrama se va a pegar dentro de una diapositiva que ya tiene su
propio encabezado (banda de logo) y su propia franja de cita al pie —como
la plantilla institucional de la skill `plantilla-uninavarra`, que reserva
0–1.4in para la banda roja y 7.05–7.45in para la cita—, **no uses los
parámetros por defecto**: el diagrama dibujaría su propio título y su
propio pie de fuente, que quedarían encima de lo que ya trae la plantilla
(esto fue justo el bug reportado: dos citas superpuestas e ilegibles).

En su lugar, pasa la zona segura explícitamente y desactiva el título/pie
propios del diagrama:

```python
result = build_algorithm_pptx(
    spec, "algoritmo.pptx",
    content_top_in=1.55,     # justo debajo de la banda roja (0-1.4in)
    content_bottom_in=6.95,  # justo antes de la franja de cita (7.05-7.45in)
    slide_height_in=7.5,     # la diapositiva real de UNINAVARRA no crece
    show_title=False,        # el título ya lo pone la plantilla/el guion de la diapositiva
    show_footer=False,       # la cita ya va en la franja institucional, no la dupliques aquí
)
```

Con `slide_height_in` fijo, el algoritmo NO puede agrandar el lienzo si no
cabe — en su lugar reduce la fuente hasta el mínimo y, si aun así no
alcanza, lo dice en `warnings` en vez de solaparse. Si eso pasa, la salida
correcta es dividir el algoritmo en dos diagramas más simples, no forzarlo.

La cita de la fuente (`spec["source"]`) sigue siendo obligatoria aunque
`show_footer=False` — solo cambia dónde vive visualmente (en la franja de
cita de la plantilla, no en un pie propio del diagrama). Si se omite, el
diagrama avisa en `warnings` que falta citarla en algún lado.

## Limitaciones conocidas

- Solo soporta la jerarquía de niveles tipo flujograma — no clusters ni
  relaciones de red complejas (para eso, Graphviz).
- Los gráficos de datos (`forest_plot`, `bar_comparison`, `line_chart`,
  `timeline` de `chart_style.py`) **no** tienen todavía una versión nativa
  editable en PowerPoint — se siguen entregando como imagen matplotlib. Un
  forest plot con barras de error no tiene un equivalente directo en los
  tipos de gráfico nativos de PowerPoint sin trabajo adicional considerable;
  si el usuario pide explícitamente que un gráfico de datos también sea
  editable en PowerPoint, dilo explícitamente como limitación actual en vez
  de simular que se hizo.
- El enrutamiento de flechas "salteadas" usa un solo carril lateral por
  arista; con muchísimas ramas salteadas simultáneas el resultado puede
  verse recargado — en ese caso, considera Graphviz.
