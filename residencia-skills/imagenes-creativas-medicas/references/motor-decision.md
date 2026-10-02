# Tabla de decisión: Canva vs. motor vectorial

## Cuándo usar Canva

Usa `generate-design` cuando el pedido tiene una **forma reconocible** —
alguien que lo describiera en una frase ya sabría qué plantilla buscar en
Canva. Es el camino rápido y de bajo riesgo: la plantilla ya resuelve
jerarquía, márgenes y composición.

`design_type` más relevantes para contexto médico/académico:

| design_type | Úsalo para |
|---|---|
| `poster` | Póster de congreso, cartelera de servicio, campaña de salud para imprimir |
| `infographic` | Datos/pasos resumidos visualmente con jerarquía clara (cifras de una guía, pasos de un protocolo) |
| `flyer` | Volante de una jornada, tamizaje, campaña de vacunación |
| `instagram_post` / `facebook_post` / `twitter_post` / `pinterest_pin` | Pieza de difusión en redes de un servicio o programa educativo |
| `postcard` | Invitación breve, agradecimiento, pieza pequeña |
| `desktop_wallpaper` / `phone_wallpaper` | Fondo de pantalla temático (menos común, pero válido si se pide) |
| `presentation` | **No uses `generate-design` para esto** — usa el flujo de outline review de Canva o mejor aún `pptx`/`presentaciones-cientificas`, que están diseñadas para mazos completos con guion oral |

Construcción del `query`: sé explícito y largo. Ejemplo bueno:

> "Póster académico para congreso de Medicina Familiar sobre manejo de
> hipertensión arterial resistente en adultos mayores. Audiencia: médicos
> residentes y especialistas. Debe transmitir seriedad clínica y rigor
> científico. Incluir espacio para: título, 3 puntos clave del abordaje
> escalonado según guía ESC/ESH 2024, y un apartado de conclusiones. Paleta
> azul/gris institucional, tipografía clara y profesional, sin ilustraciones
> infantiles."

Ejemplo malo (demasiado corto, la herramienta puede rechazarlo o generar
algo genérico): "Póster de hipertensión."

Flujo completo:
1. `generate-design` con `design_type` y `query` detallados → devuelve
   candidatos.
2. Muestra las opciones (o una descripción de ellas) al usuario para que
   elija, salvo que haya pedido explícitamente "el que tú prefieras".
3. `create-design-from-candidate` con el elegido → lo agrega a su cuenta de
   Canva.
4. `export-design` para bajar el archivo final en PNG o PDF.
5. Si el usuario tiene un brand kit configurado y quiere identidad visual
   consistente, pregúntale antes si quiere usarlo (`list-brand-kits` +
   parámetro `brand_kit_id`) — no lo asumas.

## Cuándo usar el motor vectorial/programático

Úsalo cuando el pedido **no tiene una plantilla natural** — quiere una
pieza única, conceptual, sin la estructura fija de un póster o infografía.
Ejemplos: la portada de una gran sesión con una metáfora visual propia, una
ilustración artística de un eje fisiológico (sin pretensión de exactitud
técnica, eso sería `diagramas-clinicos`), una imagen de apoyo para el cierre
de una presentación.

Herramientas disponibles en el entorno (ya instaladas):
- **Pillow (PIL)**: composición por capas, formas, gradientes, texto con
  fuentes TTF — la herramienta más flexible para ilustración.
- **matplotlib**: útil si la pieza tiene algún elemento con estructura
  geométrica/paramétrica (curvas, patrones repetidos, formas generadas
  matemáticamente) que se integra a la composición artística.
- **reportlab**: ensamblar el resultado final como PDF de una página si el
  destino es impresión.
- **cairosvg** (no instalado por defecto — `pip install cairosvg
  --break-system-packages` si se prefiere un flujo SVG → PNG).

Tipografía: reutiliza `../canvas-design/canvas-fonts/` (rutas TTF con
licencia OFL) en vez de depender de la fuente por defecto de PIL/matplotlib,
sobre todo si el texto (título de la portada, por ejemplo) es un elemento
visual protagonista.

Checklist de calidad antes de entregar:
- ¿Se ve como algo hecho con cuidado, o como un placeholder rápido? Si es lo
  segundo, dale una segunda pasada — ajusta espaciado, paleta, proporciones.
- ¿El texto (si lo hay) tiene suficiente contraste y espacio, sin
  desbordarse del lienzo?
- ¿El tono visual es coherente con el tema clínico (seriedad para temas
  graves, calidez para temas de bienvenida/educación al paciente, etc.)?
- ¿La resolución de salida es la correcta para el destino (300 dpi
  impresión/documento, 150-200 dpi pantalla/diapositiva)?

Para piezas puramente artísticas y abstractas sin ningún contenido clínico
específico que representar (portadas conceptuales genéricas, fondos, arte
decorativo), la skill `canvas-design` ya tiene un proceso más desarrollado
(filosofía de diseño + ejecución) — considera invocarla en lugar de
reconstruir ese proceso aquí.
