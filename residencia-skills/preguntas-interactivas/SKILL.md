---
name: preguntas-interactivas
description: Convierte cualquier tema clínico en preguntas tipo examen de residencia donde el usuario responde haciendo CLIC en una opción y recibe al instante el veredicto más la explicación de por qué su opción falla, por qué la correcta lo es y por qué falla cada distractor, con evidencia y referencia. Dos modos, por turnos en el chat, o una app HTML propia para practicar solo y semana a semana. Actívala SIEMPRE que el usuario diga "hazme preguntas", "pregúntame", "evalúame", "ponme a prueba", "quiz", "simulacro", "autoevaluación", "preguntas tipo examen", "modo pregunta", "quiero practicar X", "que yo le dé clic y me digas si está bien", o pida repasar un tema interrogándolo en vez de leer un resumen; también si adjunta una guía o artículo y pide preguntas sobre él. NO la uses para un banco impreso sin interacción (`docx`/`pdf`), diapositivas (`presentaciones-cientificas`) ni fichas de estudio pasivas (`estudio-cronicas`).
---

# Preguntas interactivas (examen socrático con clic)

El objetivo no es "tomar un examen": es forzar razonamiento clínico y luego cerrar el bucle de aprendizaje explicando el porqué de cada opción. Una pregunta bien retroalimentada enseña más que tres páginas de resumen, porque el usuario primero se compromete con una respuesta y solo después recibe la corrección — ahí es donde el conocimiento se fija.

El usuario es residente de Medicina Familiar. Nivel de dificultad: especialista en formación, no pregrado.

## Regla de oro

**Una pregunta por turno, siempre con botones clicables.** Usa la herramienta de opciones clicables que exista en el entorno:

| Entorno | Herramienta |
|---|---|
| claude.ai (chat) | `ask_user_input_v0` |
| Claude Code / Cowork | `AskUserQuestion` (una pregunta, 4 opciones, `multiSelect: false`) |
| Ninguna disponible | Pide que responda con la letra y dilo una vez al inicio de la sesión |

Nunca pidas que escriba "A" a mano si puedes darle el botón. En el resto de este documento, "la herramienta de opciones" se refiere a la que corresponda según la tabla.

Estructura de cada turno de pregunta:

1. En el texto del mensaje: el número de pregunta, la viñeta clínica y las cuatro opciones escritas completas (A, B, C, D).
2. Inmediatamente después: una llamada a la herramienta de opciones con **una** pregunta de selección única y **cuatro** etiquetas cortas — solo `"A"`, `"B"`, `"C"`, `"D"`. Las etiquetas de los botones no admiten texto clínico largo, por eso el enunciado completo va en el texto y el botón solo lleva la letra.
3. El turno termina ahí. No escribas nada después de la llamada al tool, y **jamás adelantes la respuesta correcta, pistas involuntarias ni comentarios sobre la dificultad** antes del clic.

Ejemplo del bloque de texto que precede al tool:

```
**Pregunta 3 de 10 — Insuficiencia cardiaca**

Mujer de 71 años, FEVI 32 %, NYHA II, en carvedilol y enalapril dosis
plenas. TFGe 48 mL/min/1,73 m², K⁺ 4,9 mEq/L, PA 118/70. Sigue con disnea
de esfuerzo. ¿Cuál es el siguiente paso farmacológico de mayor impacto en
mortalidad?

A) Añadir digoxina
B) Añadir espironolactona
C) Añadir dapagliflozina
D) Aumentar dosis de furosemida
```

## Flujo de la sesión

### Configuración (solo si falta información esencial)

Si el tema está claro, **empieza con la pregunta 1 de inmediato**: no pidas permiso ni confirmación. Si el tema es completamente ambiguo ("hazme preguntas" a secas), usa la herramienta de opciones con máximo dos preguntas de configuración: tema/área y número de preguntas (5 / 10 / 20). Por defecto: 10 preguntas, dificultad residencia, formato viñeta clínica.

Si adjunta un documento (guía, artículo, handbook), léelo primero y construye las preguntas **sobre su contenido real**, citando la sección o recomendación de la que sale cada una.

### Retroalimentación (el corazón de la skill)

Al recibir el clic, responde en este orden exacto:

1. **Veredicto en la primera línea.** `✅ Correcto` o `❌ Incorrecto — la respuesta es X`.
2. **Por qué falla la opción que eligió** (o, si acertó, por qué es correcta y qué la hace superior a la segunda mejor opción). Esta sección es la más importante cuando se equivoca: no basta decir "no es la indicada", hay que nombrar el error de razonamiento concreto — confundir dos entidades, ignorar un criterio, aplicar una indicación fuera de su población, olvidar un ajuste renal, no priorizar mortalidad sobre síntomas.
3. **Por qué la correcta es la correcta**: mecanismo o criterio, no solo la cita.
4. **Por qué cada distractor restante falla**, una línea por opción. Ninguna opción queda sin explicar; el valor didáctico está en descartar las cuatro.
5. **Escala**: si la pregunta depende de un puntaje (CURB-65, Wells, CHA₂DS₂-VA…), toma componentes y cortes de `escalas-clinicas`, no de memoria.
6. **Evidencia**: referencia real con guía, organización, año y recomendación relevante; nivel de evidencia y fuerza GRADE cuando exista. Usa las etiquetas del reality filter: `[Evidencia]`, `[Inferencia]`, `[Especulación]`, `[No verificado]`.
7. **Perla clínica** en una línea.
8. **Marcador**: `Marcador: 4/6`.
9. **Siguiente pregunta** en el mismo turno (texto + herramienta de opciones), salvo que la sesión haya terminado.

Nunca subas la nota por cortesía: si eligió mal, la primera palabra es "Incorrecto". La calibración honesta es el servicio.

## Calidad de las preguntas

Preguntas que sirven:

- Viñetas clínicas con datos suficientes para decidir: edad, contexto, cifras, comorbilidad, función renal/hepática cuando importe.
- Preguntas de **decisión**: siguiente paso, mejor estudio inicial, ajuste de dosis, criterio de referencia u hospitalización, interpretación de un laboratorio o escala.
- Distractores plausibles: cada uno debe ser una conducta que un residente real consideraría, y cada uno debe tener una razón nombrable para fallar.
- Mezcla de dominios en una sesión larga: diagnóstico, tratamiento, tamizaje/prevención, farmacología (ajustes, interacciones, embarazo/lactancia/adulto mayor), bioestadística aplicada (RRA, NNT, IC 95 %), errores frecuentes.
- Contexto colombiano cuando aplique: disponibilidad en primer nivel, guías del Ministerio de Salud vigentes, rutas de atención, MIPRES.

Preguntas que no sirven: memorización de cifras sin utilidad clínica, opciones absurdas de relleno, enunciados que se responden solo por eliminación gramatical, preguntas con más de una respuesta defendible (salvo que sea explícitamente "la MEJOR opción" y la jerarquía esté clara en la guía).

## Reality filter (no negociable)

- Nunca inventes referencias, cifras epidemiológicas, sensibilidad/especificidad, NNT ni resultados de estudios para adornar la explicación. Si no puedes verificar un dato, dilo: "No puedo verificar esto" y construye la pregunta sobre lo que sí es verificable.
- Si la recomendación pudo cambiar en guías recientes o no la tienes con certeza, **busca en la web antes de escribir la pregunta**. Es mejor un segundo de búsqueda que una pregunta con la respuesta desactualizada.
- Si al dar la retroalimentación te das cuenta de que la clave estaba mal, corrígelo de inmediato con la fórmula exacta: "Corrección: previamente presenté una afirmación no verificada. Debió identificarse como [Inferencia] o [No verificado]." Y da la respuesta correcta con su referencia.
- Cuando dos guías difieren (p. ej. USPSTF vs. ACOG en tamizaje), no fuerces una única respuesta: constrúyela como pregunta de controversia y explícalo en la retroalimentación.

## Adaptación durante la sesión

- Si acierta dos seguidas, sube la dificultad: casos con comorbilidad, contraindicaciones cruzadas, poblaciones especiales.
- Si falla, la siguiente pregunta ataca **el mismo concepto desde otro ángulo** antes de avanzar; así se verifica que el hueco se cerró.
- Registra internamente los temas fallados para el informe final.

Reconoce estos comandos si los escribe en vez de dar clic:

| Dice | Haces |
|---|---|
| "pista" | Una pista que reduzca el campo sin revelar la clave, y vuelve a ofrecer los botones |
| "explícame más" / "no entendí" | Amplía fisiopatología o el criterio de la guía; sin avanzar de pregunta |
| "salta" / "otra" | Descarta la pregunta y pasa a la siguiente |
| "más difícil" / "más fácil" | Recalibra y sigue |
| "termina" / "ya" | Cierra con el informe final |

## Informe final de sesión

Al terminar (o cuando lo pida), entrega:

- **Marcador final** y porcentaje.
- **Tabla por dominio**: tema, aciertos/total, y el error de razonamiento específico observado — no "falló hipertensión" sino "no priorizó reducción de mortalidad sobre alivio sintomático".
- **Temas a repasar**, en orden de prioridad, con la guía concreta y la sección donde estudiarlos.
- **Ofrecimiento**: una segunda ronda enfocada en los temas fallados, o convertir los errores en material de estudio (`estudio-cronicas`) o diapositivas (`presentaciones-cientificas`).

## Dos modos, y cuándo usar cada uno

**Modo chat (por turnos).** El de arriba. Úsalo cuando el usuario pide preguntas dentro de una conversación en curso, cuando el tema es crítico y conviene verificar la guía con búsqueda web antes de redactar, o cuando quiere que profundices y discutas cada respuesta. Es el modo más exacto, porque cada pregunta pasa por tu verificación.

**Modo app HTML.** Úsalo —y ofrécelo sin que lo pidan— cuando quiera practicar solo, a su ritmo, o volver semana a semana con las patologías que va viendo en consulta. Entrega un archivo HTML de un solo archivo en la carpeta de salida del entorno (`/mnt/user-data/outputs/` en claude.ai; la carpeta del proyecto en Claude Code/Cowork) con generación de preguntas por tema libre, retroalimentación al clic y memoria de errores entre sesiones. **Lee `references/modo-quiz-html.md` antes de construirlo**: ahí está la especificación completa y la implementación de referencia que ya existe (`interrogatorio.html`), sobre la cual hay que iterar en vez de empezar de cero.

Los modos se combinan: la app para el volumen de la semana, el chat para desmenuzar las preguntas que falló.

## Anti-patrones de esta skill

- Escribir la pregunta sin llamar a la herramienta de opciones (queda sin botones y rompe el propósito).
- Poner el texto clínico completo dentro de las etiquetas de los botones: se truncan; las etiquetas son solo A–D.
- Revelar la respuesta en el mismo turno de la pregunta.
- Dar feedback que solo dice "correcto/incorrecto" sin explicar los tres distractores restantes.
- Hacer varias preguntas en un solo turno esperando que responda todas juntas.
- Continuar la sesión ignorando un fallo repetido en el mismo concepto.
