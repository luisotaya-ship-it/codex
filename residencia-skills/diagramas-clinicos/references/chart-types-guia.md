# Qué gráfico usar según el tipo de contenido clínico

Esta tabla es el punto de partida para decidir motor y función. El criterio
no es "qué se ve más bonito" sino qué visualización comunica correctamente
el tipo de dato — un algoritmo de decisión como gráfico de barras sería
tan confuso como un forest plot dibujado como flujograma.

| Contenido a graficar | Motor | Función / plantilla |
|---|---|---|
| Algoritmo diagnóstico o terapéutico, árbol de decisión, criterios de referencia/hospitalización — **destino PPTX, debe quedar editable** | python-pptx nativo | `scripts/build_pptx_diagram.py::build_algorithm_pptx()` (ver `pptx-nativo-guia.md`) |
| El mismo tipo de algoritmo — destino Word/PDF/imagen suelta, o diagrama grande/complejo | Graphviz | `assets/plantilla_algoritmo.dot` (ver `graphviz-guia.md`) |
| Fisiopatología, mecanismo de acción, cascada de señalización, relaciones causales entre sistemas | Graphviz | patrón de clusters en `graphviz-guia.md` |
| Riesgo relativo, odds ratio, hazard ratio con IC 95% de uno o varios estudios | matplotlib | `chart_style.forest_plot()` |
| Comparación de tasas/eventos entre grupos o brazos de tratamiento, NNT/NNH visual | matplotlib | `chart_style.bar_comparison()` |
| Evolución temporal de guías, hitos de una enfermedad, cronograma de seguimiento | matplotlib (simple) o Graphviz `rankdir=LR` (con ramificaciones) | `chart_style.timeline()` |
| Tendencia de un parámetro numérico en el tiempo (ej. TFGe, HbA1c a lo largo de controles) | matplotlib | `chart_style.line_chart()` |
| Anatomía o imagen médica real (radiografía, corte histológico) | Ninguno de estos — no se debe recrear una imagen médica real con código. Si el documento ya trae la imagen, extraerla del PDF/artículo en vez de redibujarla. | — |

## Regla de datos: nunca graficar un número inventado

Todo valor numérico que entra a `forest_plot`, `bar_comparison` o
`line_chart` (RR, OR, HR, IC 95%, tasas, NNT) debe venir explícitamente del
documento o artículo proporcionado, con su fuente. Si el usuario pide
graficar algo y el documento no trae el dato exacto (por ejemplo, pide
"grafica el NNT" pero el artículo solo da el riesgo relativo sin poder
calcular NNT sin la tasa basal), decirlo explícitamente en vez de estimar o
inventar un valor plausible — coherente con el filtro de realidad: usar
`[Inferencia]` solo si el cálculo se deriva matemáticamente de datos que sí
están en el documento (ej. NNT = 1 / diferencia de riesgo absoluto, cuando
esa diferencia sí está dada), y `[No verificado]` si falta un dato necesario.

## Resolución de salida según destino

- Word/PDF (ficha de estudio, informe): PNG o SVG a 300 dpi — usar
  `chart_style.save(fig, path, dpi=300)`.
- PowerPoint (.pptx): 150–200 dpi es suficiente y mantiene el archivo liviano
  — usar `dpi=150`.
- Imagen independiente para compartir o proyectar en pantalla grande: SVG
  cuando sea posible (vectorial, no pierde nitidez al hacer zoom); Graphviz
  produce SVG nativamente con `render_dot.sh archivo.dot salida.svg`.
- PowerPoint (.pptx) cuando el algoritmo debe quedar editable: no aplica
  "resolución" en el sentido de dpi — el motor nativo (`build_pptx_diagram.py`)
  genera formas vectoriales que escalan sin perder nitidez a cualquier
  tamaño. El único parámetro relevante es el tamaño de la diapositiva, que
  el propio script calcula según el contenido (ver `pptx-nativo-guia.md`).
