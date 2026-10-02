---
name: imagenes-creativas-medicas
description: Genera la imagen real (PNG/PDF) de una pieza visual creativa — ilustración médica artística, portada de gran sesión/presentación, póster académico, infografía, o pieza para redes/cartelera — a partir del contexto clínico dado (tema, enfermedad, fármaco, guía o documento adjunto). Úsala siempre que pidan "una imagen creativa", "una ilustración", "un póster", "una portada bonita/vistosa", "arte médico", "algo visualmente atractivo para mi presentación/gran sesión", o se quejen de que el resultado se ve "plano"/"aburrido"/"muy de Word". NO es para diagramas técnicos, algoritmos ni gráficos de datos (RR, OR, forest plots) — eso es `diagramas-clinicos`. No reemplaza a `pptx`/`presentaciones-cientificas` ni a `docx`/`pdf` — produce la pieza visual que luego se inserta ahí.
---

# Imágenes creativas médicas

## Qué resuelve esta skill

Un residente pidiendo "algo visual" para una gran sesión, un póster de
pasillo o la portada de una presentación no quiere un párrafo describiendo
cómo se vería esa imagen — quiere el archivo. Esta skill existe para no
quedarse en la descripción: siempre termina en un PNG o PDF real, listo para
insertar en un documento, proyectar o imprimir.

Es la contraparte "artística" de `diagramas-clinicos`. Esa otra skill existe
para representar datos y algoritmos con exactitud (un forest plot, un
flujograma diagnóstico); esta skill existe para producir imágenes que
comunican por composición, color y concepto — una portada, una metáfora
visual, un póster con jerarquía tipográfica. Si en algún punto el pedido
resulta ser en realidad un gráfico de datos o un algoritmo de decisión,
redirige a `diagramas-clinicos` en lugar de forzarlo aquí.

## Paso 1 — Definir el brief creativo

Antes de generar nada, deja clara (mentalmente o preguntando si falta algo
esencial) esta información mínima:

- **Tema/contexto clínico**: la enfermedad, fármaco, guía o concepto sobre el
  que gira la imagen. Si el usuario adjuntó un documento o venías trabajando
  un tema en la conversación, úsalo — no preguntes lo que ya sabes.
- **Destino y formato**: ¿portada de una presentación o gran sesión (PPTX),
  ilustración dentro de una ficha de estudio (DOCX/PDF), póster para
  imprimir, o pieza suelta para compartir? Esto determina proporción,
  resolución y si el entregable es PNG, PDF, o ambos.
- **Tono**: casi siempre debe ser serio y profesional — sofisticado, nunca
  infantil, "clip-art" o de mal gusto. Un tema oncológico o de cuidados
  paliativos, por ejemplo, pide sobriedad; una portada de bienvenida a
  residentes puede ser más cálida. Si hay duda razonable sobre el tono
  apropiado, pregunta antes de generar.
- **Texto dentro de la imagen**: título/subtítulo si aplica. Mantenlo mínimo
  — estas piezas comunican visualmente, no con párrafos superpuestos.

No es necesario convertir esto en un cuestionario formal: para pedidos
simples ("hazme una portada bonita sobre diabetes para mi gran sesión"),
infiere lo razonable y genera directamente. Pregunta solo cuando falte algo
que cambiaría sustancialmente el resultado (p. ej. no sabes si es para
imprimir en A0 o para una diapositiva).

## Paso 2 — Elegir el motor

Hay dos motores disponibles y no son intercambiables — cada uno sirve a un
tipo de pedido distinto. Consulta `references/motor-decision.md` para la
tabla de decisión completa y ejemplos de `query` bien construidos; el
resumen es:

| Pedido | Motor |
|---|---|
| Póster académico, infografía, flyer, pieza para redes/cartelera con estructura reconocible | **Canva** (`mcp__*__generate-design`) |
| Ilustración artística libre, portada conceptual, metáfora visual sin plantilla — una pieza única | **Motor vectorial/programático** (código: PIL, matplotlib, reportlab) |
| Portada de presentación con estructura de diapositiva | **Canva** si se quiere plantilla profesional rápida; **motor vectorial** si se quiere una pieza más artística y original |

**Si la herramienta de Canva no está conectada en la sesión** (no aparece ningún `mcp__*__generate-design`, o el servidor figura como desconectado), dilo en una línea y usa el motor vectorial/programático para todo — no detengas la tarea esperando Canva.

Si tienes duda entre los dos, generar con Canva es más rápido y de menor
riesgo cuando el pedido tiene una forma reconocible (póster, infografía,
post). Resérvate el motor vectorial para cuando el pedido pide algo con
alma propia, sin plantilla, o cuando Canva no ofrezca un `design_type`
adecuado.

Ambos motores pueden combinarse: por ejemplo, generar una ilustración con el
motor vectorial y luego subirla como asset dentro de un póster de Canva
(`asset_ids` en `generate-design`), o al revés, exportar un diseño de Canva
como imagen base y refinarlo con código.

## Paso 3a — Generar con Canva

Usa la herramienta MCP de Canva (`mcp__*__generate-design`) con un `query`
detallado — no una sola frase. Incluye: tema clínico exacto, audiencia
(residentes/médicos de familia, pacientes, público general — cambia
completamente el registro), 2-4 elementos visuales o de contenido que deben
aparecer, y la paleta o mood si el usuario lo especificó. La herramienta no
tiene memoria de mensajes previos: repite el contexto relevante cada vez.

Elige `design_type` según el destino (`poster`, `infographic`, `flyer`,
`instagram_post`, `facebook_post`, `postcard`, `desktop_wallpaper`, etc. —
ver la lista completa en `references/motor-decision.md`). La herramienta
devuelve varios candidatos de diseño; muestra las opciones al usuario y usa
`create-design-from-candidate` con la que elija, luego `export-design` para
obtener el PNG/PDF final.

## Paso 3b — Generar con el motor vectorial/programático

Cuando el pedido es una ilustración artística libre sin plantilla de Canva
adecuada (por ejemplo, una portada conceptual o una pieza que funcione como
arte, no como documento estructurado), constrúyela con código:

1. **Define un concepto visual breve** antes de escribir código: qué idea
   central comunica la imagen, qué paleta de color, qué composición. Un
   párrafo basta — no hace falta el ejercicio completo de "filosofía de
   diseño" de la skill `canvas-design`, pero si el pedido es de una pieza
   puramente artística sin ningún contenido clínico específico que
   representar (p. ej. "una imagen abstracta e inspiradora para la portada
   de mi carpeta de estudio"), esa skill es una alternativa válida y más
   desarrollada para ese caso — puedes invocarla en su lugar.
2. **Construye la imagen con Python** (Pillow/PIL para composición e
   ilustración por capas, matplotlib para elementos con estructura
   geométrica o iconográfica, reportlab si el entregable final es PDF).
   Estas librerías ya están disponibles en el entorno. Si el flujo de
   trabajo se beneficia de dibujar en SVG y convertir a PNG, se puede
   instalar `cairosvg` con pip.
3. **Usa tipografía con criterio**: el directorio de fuentes de la skill
   `canvas-design` (`canvas-fonts/`) tiene variedad de familias con licencia
   OFL abierta — reutilízalo en vez de depender de la fuente por defecto del
   sistema si el texto es un elemento visual importante de la pieza.
4. **Mantén la seriedad clínica**: nada de ilustraciones "cartoon" o
   amateur salvo que el usuario lo pida explícitamente (p. ej. material para
   pacientes pediátricos). Por defecto, apunta a algo que se vería bien
   impreso en un póster de congreso o en la portada de una gran sesión.
5. Exporta a PNG a 300 dpi si va a imprenta/documento, 150 dpi si es solo
   para pantalla/diapositiva, y añade PDF si el destino es impresión.

## Regla sobre datos dentro de la imagen

Esta skill es para comunicación visual/conceptual, no para representar
datos clínicos con precisión — para eso existe `diagramas-clinicos`. Aun
así, si una pieza generada aquí incluye alguna cifra, umbral o dato
clínico visible (una prevalencia en una infografía, por ejemplo), esa cifra
debe venir de una fuente verificable y no inventarse — si no la tienes,
dilo explícitamente o pide la referencia en lugar de completar el vacío.
Los elementos puramente decorativos o metafóricos (color, forma, composición
sin pretensión de representar un dato) no necesitan esta verificación.

## Entrega e integración con otras skills

- Pieza suelta: entrega el PNG/PDF directamente como archivo independiente.
- Si va dentro de una ficha de estudio o informe: genera a 300 dpi y pásalo
  a la skill `docx` o `pdf` para insertarlo donde corresponda.
- Si va dentro de una presentación: genera a 150-200 dpi (o usa el flujo de
  Canva si el usuario ya trabaja ahí) y pásalo a `pptx` /
  `presentaciones-cientificas` para insertarlo en la diapositiva
  correspondiente. Si la presentación completa ya tiene un pase de
  "dinamización" visual (`diapositivas-dinamicas`), esta skill puede
  producir la pieza que esa otra fase termina de integrar.
- No reemplaces `diagramas-clinicos` cuando el pedido real es un algoritmo,
  flujograma o gráfico de datos — redirige ahí.

## Ejemplo rápido

Pedido: "hazme una portada creativa para mi gran sesión de hipertensión
arterial resistente, algo serio pero que no se vea aburrido"

1. Brief: tema = HTA resistente; destino = portada de PPTX; audiencia =
   residentes/docentes de Medicina Familiar; tono = serio, con impacto
   visual, sin texto largo.
2. Motor: sin plantilla estructurada de por medio → motor vectorial.
3. Concepto: paleta azul-carbón con un acento coral, composición con un
   trazo/ritmo que evoque una curva de presión arterial estilizada como
   elemento gráfico central, tipografía condensada para el título.
4. Construir con Pillow/matplotlib, exportar `portada_hta_resistente.png`
   a 150 dpi (destino: diapositiva) y `.pdf` si además se quiere en la
   ficha de estudio.
5. Entregar el archivo y ofrecer insertarlo con `pptx`/
   `presentaciones-cientificas` si el usuario ya tiene el mazo en curso.
