# Modo app HTML (predeterminado para práctica semanal)

Cuando el usuario quiera practicar por su cuenta, semana a semana, sobre las patologías que va viendo en consulta, no sirve el ping-pong de chat: entrega una **app HTML de un solo archivo** en la carpeta de salida del entorno (`/mnt/user-data/outputs/` en claude.ai, carpeta del proyecto en Claude Code/Cowork) y preséntala con la herramienta de envío de archivos disponible (`present_files` o `SendUserFile`).

## Qué debe tener, sin excepción

1. **Campo de tema libre.** El usuario escribe la patología, el fármaco o la guía de esa semana y arranca. Las preguntas se generan una a una llamando a la API de Anthropic desde la propia app (`claude-sonnet-4-6`, `max_tokens: 1000`, sin API key — la maneja el entorno). Una pregunta por llamada: caben cómodamente la viñeta, las cuatro opciones con su explicación, la evidencia y la perla.

2. **Prompt de sistema con el reality filter dentro de la app.** Es lo que impide que la app degenere en preguntas inventadas: prohibición explícita de fabricar referencias, cifras, sensibilidad/especificidad o NNT; etiquetas `[Evidencia]`, `[Inferencia]`, `[Especulación]`, `[No verificado]`; guía + organización + año reales; contexto de primer nivel en Colombia; nivel residencia, no pregrado.

3. **Salida en JSON estricto** para poder renderizarla: `dominio`, `vineta`, `pregunta`, `opciones[4]` (cada una con `letra`, `texto`, `correcta`, `porque`), `correcta`, `evidencia`, `perla`. Parsear con `try/catch` tras limpiar backticks, y validar que haya cuatro opciones y exactamente una correcta antes de mostrarla.

4. **Retroalimentación al clic, no al final.** Al pulsar una opción: la correcta se marca en verde, la elegida errónea en rojo, y **cada una de las cuatro** despliega su razón debajo. Luego el bloque "por qué falla la que elegiste" (solo si falló), "por qué la correcta es la correcta", evidencia y perla.

5. **Banco verificado de respaldo.** Al menos un tema con preguntas escritas y revisadas a mano, que funcione aunque la generación falle. Sirve de demo de calidad y de referencia de tono.

6. **Memoria entre sesiones** con `window.storage` (nunca `localStorage`, que no funciona en artifacts): histórico de aciertos, estadística por tema, lista de preguntas falladas y modo "repasar mis errores". Todo con `try/catch`; la primera lectura falla porque la clave no existe todavía.

7. **Adaptación.** Enviar en cada llamada los conceptos ya preguntados para que no se repitan; si acaba de fallar, pedir el mismo concepto desde otro ángulo; si lleva dos aciertos, subir dificultad.

8. **Informe**: marcador de sesión, tabla por tema ordenada de peor a mejor, y los temas bajo 70 % como plan de repaso.

## Aviso obligatorio en la interfaz

Las preguntas generadas al vuelo no pasan por verificación con búsqueda web. La app debe decirlo en texto visible: verificar dosis, umbrales y referencias contra la guía original antes de darlas por buenas. Cuando el usuario quiera certeza sobre un tema crítico, el modo por turnos en el chat es superior, porque ahí sí se puede buscar y contrastar la guía antes de redactar.

## Implementación de referencia

Ya existe una construida para este usuario: `interrogatorio.html` — tira de estado tipo monitor, banco verificado de hipertensión (AHA/ACC 2025 y ESC 2024), generación por tema libre, memoria de errores e informe. Si pide "otra app así" o "agrégale X", parte de esa, no de cero. **Si el archivo no está accesible en la sesión** (no aparece en la carpeta de trabajo ni en los adjuntos), pídele al usuario que lo adjunte; si no lo tiene, construye una nueva siguiendo esta especificación y dilo en una línea — no finjas que la estás editando.
