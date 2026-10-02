# App de estudio interactiva — especificación

Se genera al cerrar el bloque D de una ficha NIVEL 2 o 3. Es **un solo archivo HTML
autocontenido** (CSS y JS inline; sin dependencias externas obligatorias) que el residente abre
con doble clic, también sin internet.

## Contenido (pestañas)

| Pestaña | Qué lleva | Regla |
|---|---|---|
| Ruta | Los 4 bloques (A–D) con revelado progresivo: cada bloque se despliega con un botón y actualiza una barra de progreso | Texto ya escrito en la ficha; no contenido nuevo |
| Quiz | 8–12 preguntas tipo viñeta clínica, 4 opciones, una mejor respuesta. Al clic: veredicto + por qué la correcta lo es + **por qué falla cada distractor** + referencia | Nunca revelar la clave antes del clic |
| Flashcards | 10–20 tarjetas que se voltean con clic. Frente: pregunta de razonamiento ("¿Por qué…?"). Reverso: la cadena causal corta | Nunca frentes de definición |
| Diagramas | Las cadenas causales de la ficha como SVG inline (máx. 7 nodos por diagrama, código de color de la sesión) | Mismo contenido y fuente que en el chat |
| Guion | Guion hablado de 5 / 10 / 20 minutos, en pestañas internas | Texto para decir en voz alta, sin viñetas |
| Repaso | Lista de preguntas falladas y tarjetas marcadas "no lo sé", con la fecha sugerida de repaso (hoy + 3 días) | Guardar en `localStorage` dentro de `try/catch`; la app funciona igual si falla |

## Requisitos técnicos

- Un único `.html`; nombre: `estudio-<tema>-<AAAA-MM-DD>.html`.
- Funciona en móvil (ancho de 360 px sin scroll horizontal) y en escritorio.
- Accesible: botones reales (`<button>`), contraste suficiente, tamaño de fuente ≥ 16 px.
- Los datos (preguntas, tarjetas, bloques) en un único objeto JSON al inicio del `<script>`
  para que sea fácil corregir una pregunta sin tocar la lógica.
- Cada pregunta y cada diagrama lleva su campo `fuente` y su etiqueta de evidencia
  (`[Evidencia]`, `[Inferencia]`, `[Especulación]`, `[No verificado]`).
- Pie de la app: "Fecha de verificación de guías: AAAA-MM-DD. Verificar vigencia antes de aplicar."

## Verificación antes de entregar

1. Extrae el bloque `<script>` y valida la sintaxis (`node --check` si hay Node disponible).
2. Abre la app con el navegador headless disponible (Playwright/Chromium) o, si no hay, revisa
   el HTML a mano: que cada pregunta tenga exactamente una opción correcta y una explicación
   por distractor.
3. Confirma que ninguna cifra de la app falta en la ficha (no se agregan datos nuevos aquí).

## Entrega

Guarda el archivo en la carpeta de salida del entorno (la del proyecto o la de outputs) y
preséntalo con la herramienta de envío de archivos disponible (`present_files`, `SendUserFile`
o equivalente). Cierra con la frase de repaso espaciado del SKILL.md.

Para un banco de preguntas que se reutiliza semana a semana entre temas, no amplíes esta app:
deriva a `preguntas-interactivas` (modo app HTML).
