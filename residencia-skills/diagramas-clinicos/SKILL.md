---
name: diagramas-clinicos
description: Genera la imagen real de un diagrama, algoritmo, esquema de mecanismo o gráfico de datos a partir de un documento, guía o artículo clínico — nunca se conforma con describir en texto cómo se vería. Para algoritmos/flujogramas destinados a una presentación, los construye como formas NATIVAS y editables de PowerPoint (cajas, rombos, flechas movibles) con layout que se adapta al número de pasos y al largo del texto, no como imagen plana. Úsala siempre que pidan "un diagrama", "un esquema", "un flujograma", "un algoritmo visual", "grafica esto", "un forest plot", "una línea de tiempo", que el esquema sea "editable"/"que pueda modificar en PowerPoint", o cuando el contenido de un documento incluya un algoritmo de decisión, una vía fisiopatológica, datos comparativos (RR, OR, HR, NNT) o una cronología. También úsala si se quejan de que "solo describiste el gráfico" o piden explícitamente que generes la imagen en vez de explicarla.
---

# Diagramas y gráficos clínicos

## El problema que resuelve esta skill

Es fácil quedarse en la descripción textual de un gráfico ("el algoritmo
empezaría con la sospecha diagnóstica, luego se evaluaría el criterio X...")
en vez de producir la imagen. Para un residente que va a usar el material en
una ficha de estudio, una presentación o una gran sesión, esa descripción no
sirve — necesita el archivo de imagen real, insertable y proyectable. La
regla de esta skill es simple: si el contenido se presta a un diagrama o
gráfico, **se genera el archivo de imagen**, no un párrafo que lo explica.

## Flujo de trabajo

1. **Extraer el contenido estructurado del documento/artículo.** Antes de
   graficar nada, identificar exactamente qué se va a representar: pasos y
   criterios de un algoritmo, relaciones causales de un mecanismo, o los
   valores numéricos exactos (con su fuente) de un gráfico de datos. No
   avanzar con supuestos — si un dato necesario no está en el documento,
   decirlo explícitamente en vez de completar el vacío (ver "Regla de datos"
   en `references/chart-types-guia.md`).

2. **Elegir el tipo de visualización y el motor.** Consultar
   `references/chart-types-guia.md` para la tabla de decisión completa.
   Resumen:
   - Algoritmo de decisión, flujograma, criterios de referencia/hospitalización, **destinado a insertarse en un PPTX y que el residente pueda seguir editándolo ahí** (mover una caja, corregir un umbral, reordenar una rama) → **python-pptx nativo** (`scripts/build_pptx_diagram.py`, ver más abajo). Este es el motor por defecto para algoritmos cuando el destino es una presentación.
   - El mismo tipo de algoritmo pero destinado a Word/PDF, a una imagen suelta, o cuando el usuario no necesita editarlo después → **Graphviz** (`assets/plantilla_algoritmo.dot` + `scripts/render_dot.sh`) — sigue siendo el motor correcto para eso, y el único con el que no hay límite de tamaño/complejidad del diagrama.
   - Fisiopatología / mecanismo de acción / relaciones causales con muchos nodos o clusters por sistema → **Graphviz** con clusters (ver `references/graphviz-guia.md`); python-pptx nativo no maneja bien clusters/agrupaciones complejas.
   - RR / OR / HR con IC 95% → **matplotlib**, `scripts/chart_style.py::forest_plot()`
   - Comparación de tasas, NNT/NNH, prevalencias entre grupos → **matplotlib**, `chart_style.py::bar_comparison()`
   - Línea de tiempo de guías, hitos o seguimiento → **matplotlib**, `chart_style.py::timeline()` (o Graphviz si tiene ramificaciones)
   - Tendencia de un parámetro en el tiempo (ej. TFGe en controles sucesivos) → **matplotlib**, `chart_style.py::line_chart()`

   Nota técnica: en este entorno, Mermaid CLI no funciona (requiere Chrome
   headless con librerías del sistema que no están disponibles sin permisos
   de root). Graphviz, matplotlib y python-pptx están preinstalados y son
   confiables — son los motores por defecto de esta skill, no una
   alternativa de respaldo.

3. **Construir y renderizar.**
   - **python-pptx nativo (algoritmos editables en PPTX):** importar
     `build_algorithm_pptx` de `scripts/build_pptx_diagram.py`, describir el
     algoritmo como una lista de nodos (`id`, `text`, `type`: `start_end` /
     `decision` / `action` / `alert`) y aristas (`from`, `to`, `label`
     opcional), y llamar `build_algorithm_pptx(spec, "salida.pptx")`. El
     layout (niveles, tamaño de caja, enrutamiento de flechas) se calcula
     automáticamente a partir del contenido — ver docstring del módulo y
     `references/pptx-nativo-guia.md` para el formato del spec y cómo leer
     la lista `warnings` que devuelve. **Siempre revisar `warnings` antes de
     entregar**: si no está vacía, el diagrama quedó apretado o con texto al
     límite y conviene acortar texto, dividir el algoritmo, o cambiar a
     Graphviz.
   - **Verificación visual obligatoria antes de entregar un .pptx nativo:**
     convertir a PNG con LibreOffice (`soffice --headless --convert-to png
     archivo.pptx`) y mirar el resultado con la herramienta de lectura de
     imágenes — igual que con cualquier otro gráfico de esta skill, no basta
     con que el script corra sin errores; hay que confirmar que no se vea
     apretado, cortado o desalineado.
   - Graphviz: copiar la plantilla relevante, editar nodos/aristas con el
     contenido real (citando el criterio o umbral exacto de la guía), y
     ejecutar `bash scripts/render_dot.sh archivo.dot salida.png` (o `.svg`).
   - matplotlib: importar las funciones de `scripts/chart_style.py`, pasar
     los datos con su fuente (`source=`), y guardar con `save(fig, ruta,
     dpi=...)`. Ver `chart-types-guia.md` para el dpi según destino.

4. **Etiquetar la evidencia.** Todo gráfico que representa una recomendación
   de guía o un dato de un estudio debe incluir su fuente visible en la
   imagen (pie de página del algoritmo, o el parámetro `source=` de las
   funciones de matplotlib) siguiendo las mismas etiquetas del filtro de
   realidad del usuario: `[Evidencia]`, `[Inferencia]`, `[Especulación]` o
   `[No verificado]` según corresponda.

5. **Entregar en el formato correcto según el destino:**
   - Si el gráfico va dentro de una ficha de estudio o informe → generar el
     PNG/SVG a 300 dpi y pasarlo a la skill `docx` (o `pdf`) para insertarlo
     donde corresponda en el documento. No dupliques la lógica de esas
     skills: genera la imagen aquí, insértala allá.
   - Si va dentro de una presentación y es un algoritmo/flujograma → usar el
     motor python-pptx nativo (arriba) y pasar el `.pptx` resultante a la
     skill `pptx` (dentro del flujo de `presentaciones-cientificas` si
     aplica) para copiar sus formas a la diapositiva correspondiente —
     quedan como objetos editables, no como imagen incrustada.
   - Si va dentro de una presentación y es un gráfico de datos (forest plot,
     barras, línea) → generar con matplotlib a 150–200 dpi y pasarlo a
     `pptx`/`presentaciones-cientificas` como imagen; estos gráficos no
     tienen aún una versión nativa editable en esta skill (ver limitación en
     `references/pptx-nativo-guia.md`).
   - Si el usuario solo quiere el gráfico suelto → entregar el archivo
     PNG/SVG (o `.pptx` si pidió que fuera editable) directamente como
     archivo independiente.

## Integración con otras skills

Esta skill no reemplaza a `estudio-cronicas`, `presentaciones-cientificas`,
`docx`, `pptx` ni `pdf` — las complementa. Cuando alguna de esas skills está
armando un documento y el contenido pide un algoritmo, un esquema o un
gráfico de datos, se invoca esta skill para producir la imagen real, y luego
se usa la skill de destino para insertarla en el documento o la diapositiva.
Si ya estás dentro del flujo de `presentaciones-cientificas` o
`estudio-cronicas` y llega el punto de incluir un diagrama, no te detengas
a redactar un párrafo describiéndolo: genera el archivo con esta skill y
continúa.

## Recursos de la skill

- `scripts/build_pptx_diagram.py` — genera algoritmos/flujogramas como
  formas nativas y editables de PowerPoint, con layout automático que se
  adapta al número de nodos y al largo del texto (ver docstring del módulo
  y `references/pptx-nativo-guia.md`).
- `scripts/chart_style.py` — funciones de matplotlib con estilo clínico
  consistente (`forest_plot`, `bar_comparison`, `timeline`, `line_chart`,
  `save`). Leer las docstrings antes de usarlas.
- `scripts/render_dot.sh` — wrapper para renderizar archivos `.dot` de
  Graphviz a PNG/SVG/PDF con resolución consistente.
- `assets/plantilla_algoritmo.dot` — plantilla base para algoritmos clínicos
  con la convención de colores/formas ya definida (Graphviz).
- `references/graphviz-guia.md` — sintaxis DOT, convención de colores/formas,
  patrón de clusters para fisiopatología, errores comunes.
- `references/pptx-nativo-guia.md` — formato del spec de
  `build_pptx_diagram.py`, cómo interpretar `warnings`, cómo verificar el
  resultado visualmente, y limitaciones conocidas del motor nativo.
- `references/chart-types-guia.md` — tabla de decisión motor/función según
  tipo de contenido, regla de datos (nunca inventar un número graficado),
  resolución de salida según destino.

## Ejemplo rápido

### Algoritmo editable para una presentación

```python
import sys
sys.path.insert(0, "scripts")
from build_pptx_diagram import build_algorithm_pptx

spec = {
    "nodes": [
        {"id": "inicio", "text": "TFGe <60 mL/min/1.73m2\nen control rutinario", "type": "start_end"},
        {"id": "d1", "text": "Persiste <60 en 2a medicion\na los 3 meses?", "type": "decision"},
        {"id": "erc", "text": "Enfermedad renal cronica:\nclasificar por KDIGO (G+A)", "type": "action"},
        {"id": "alarma", "text": "TFGe <30 o albuminuria >300:\nreferir a nefrologia", "type": "alert"},
        {"id": "fin", "text": "Seguimiento en atencion primaria", "type": "start_end"},
    ],
    "edges": [
        {"from": "inicio", "to": "d1"},
        {"from": "d1", "to": "erc", "label": "Si"},
        {"from": "d1", "to": "fin", "label": "No"},
        {"from": "erc", "to": "alarma"},
        {"from": "alarma", "to": "fin"},
    ],
    "title": "Diagnóstico de enfermedad renal crónica",
    "source": "KDIGO 2024 — [Evidencia]",
}
result = build_algorithm_pptx(spec, "/tmp/erc_algoritmo.pptx")
print(result["warnings"])  # revisar antes de entregar
```

```bash
# Verificación visual obligatoria antes de entregar:
soffice --headless --convert-to png /tmp/erc_algoritmo.pptx
# luego abrir /tmp/erc_algoritmo.png con la herramienta de lectura de imágenes
```

### El mismo tipo de algoritmo para Word/PDF (imagen fija, Graphviz)

```bash
cp assets/plantilla_algoritmo.dot /tmp/erc_algoritmo.dot
# editar /tmp/erc_algoritmo.dot con los nodos reales del algoritmo de KDIGO
bash scripts/render_dot.sh /tmp/erc_algoritmo.dot /tmp/erc_algoritmo.png 300
```

### Un dato numérico (forest plot, matplotlib)

```python
from chart_style import forest_plot, save
fig, ax = forest_plot(
    labels=["Estudio X (2023)", "Estudio Y (2024)"],
    point=[0.75, 0.60], lower=[0.60, 0.45], upper=[0.95, 0.80],
    xlabel="Riesgo relativo de progresión a ERC terminal (IC 95%)",
    source="Metaanálisis Z et al., 2024, Kidney Int — [Evidencia]",
)
save(fig, "/tmp/rr_progresion.png", dpi=300)
```

El `.pptx` del algoritmo se integra copiando sus formas a la diapositiva
destino (o insertando el archivo completo como referencia) con la skill
`pptx`; las imágenes PNG/SVG se insertan con `docx`, `pdf` o `pptx` según
corresponda.
