---
name: "visualizar-informacion"
description: "Convierte informacion densa en texto (guias, recomendaciones, notas, tablas, secciones de un articulo, contenido ya escrito de una diapositiva) en una pieza visual que baja la carga cognitiva: decide primero SI vale la pena visualizarla y con que patron, aplicando doble codificacion, segmentacion y jerarquia tipografica, sin perder trazabilidad de la evidencia (grados de recomendacion, umbrales, criterios). Usala cuando el usuario diga 'hazlo mas visual', 'que no sea solo letras', 'se ve muy plano', 'organizame esto', 'ponlo en una lamina', o cuando entregue un bloque denso que terminaria como muro de texto o vinetas. Por defecto usa la plantilla institucional UNINAVARRA, salvo que pida no usarla. NO es para elegir la foto de contexto de una diapositiva (imagenes-contextuales-diapositivas), ni para dibujar un algoritmo ya definido (diagramas-clinicos), ni para armar una presentacion completa (presentaciones-cientificas): decide que forma visual toma la informacion antes de que esas skills la dibujen."
---

# Visualizar información — bajar la carga cognitiva, no decorar

## Por qué existe esta skill

El origen es una comparación real entre dos versiones de la misma lámina (medidas no
farmacológicas en DM2, ADA *Standards of Care* 2026): una con seis tarjetas de texto corrido
sobre la plantilla institucional, y otra con seis columnas con icono, viñetas cortas y una banda
de cierre. **El contenido era casi idéntico; lo que cambió fue el número de canales usados para
codificarlo.** La primera usaba uno (leer). La segunda usaba cinco (posición, color, icono,
tipografía y síntesis final).

De ahí sale el principio que gobierna toda esta skill:

> La diferencia entre una lámina que se entiende y una que no rara vez es estética. Es cuántos
> canales cargan la información y cuánta memoria de trabajo exige leerla.

Y el contrapeso, igual de importante: al condensar se perdieron cosas que no debían perderse
(los grados de recomendación A/B/C/E, el matiz "sin más de 2 días consecutivos sin actividad",
y apareció una banda de "beneficios comprobados" sin fuente rastreable). **Visualizar sin
degradar la evidencia es la mitad del trabajo de esta skill, no un detalle.**

## Paso 0 — Decidir si esto merece ser visual

"Cuando sea necesario" es parte del encargo: no todo bloque de texto mejora al volverse gráfico.
Antes de construir nada, clasifica el contenido:

**Sí conviene visualizar cuando el contenido tiene forma:**

- Elementos paralelos y comparables (pilares, criterios, categorías, fármacos, guías enfrentadas).
- Secuencia o decisión (algoritmo, ruta, fases, pasos de manejo).
- Relación causal o de flujo (fisiopatología, eje hormonal, cascada).
- Magnitudes o umbrales (cifras de corte, dosis, riesgos, prevalencias).
- Cronología (historia natural, evolución de guías, seguimiento).
- Contención o pertenencia (qué está dentro de qué, niveles de atención).

**No conviene, y es mejor prosa limpia o una tabla honesta cuando:**

- El contenido es un argumento con matices encadenados (una controversia entre guías se explica
  mejor escrita que en cajitas).
- Cada elemento necesita más de ~35 palabras para no perder sentido clínico.
- Los elementos no son comparables entre sí (forzarlos a una rejilla inventa una simetría falsa).
- Es una definición corta o un dato aislado: un gráfico ahí es decoración.
- El usuario pidió explícitamente texto, o el entregable es un documento de estudio en prosa.

Si decides no visualizar, **dilo en una frase** ("esto rinde más como párrafo porque X") en vez
de entregar un diagrama forzado en silencio. Un diagrama que no aporta cuesta más atención de la
que ahorra.

## Paso 1 — Elegir el patrón según la forma de la información

No elijas el patrón por el tema, sino por la **estructura lógica** del contenido:

| Forma de la información | Patrón visual | Quién lo dibuja |
|---|---|---|
| N elementos paralelos, comparables (3–6) | Franja de tarjetas en una fila: encabezado de color + icono + ≤3 viñetas | `scripts/build_lamina_tarjetas.py` de esta skill |
| Decisión con ramas / criterios de corte | Flujograma o embudo por fases, con la regla de oro resaltada aparte | `diagramas-clinicos` (formas nativas editables) |
| Cadena causa→efecto, eje, retroalimentación | Cascada o eje vertical/horizontal | `diagramas-clinicos` |
| Cifras que compiten (RR, OR, HR, NNT, prevalencias) | Gráfico de datos (barras, forest plot, gauge) | `diagramas-clinicos` |
| Cronología / evolución | Línea de tiempo | `diagramas-clinicos` |
| Una sola cifra que es el mensaje | Cifra gigante 48–60pt + etiqueta pequeña, casi sin texto | Directo en el .pptx |
| 2–4 conceptos que se suman para dar una definición | Ecuación visual con `+` y `→` | Directo en el .pptx |
| Escala validada (PHQ-9, FRAX, Wells, CURB-65) | Reproducir la tabla real con su puntuación e interpretación | Directo, citada |
| Contenido correcto pero la lámina se siente vacía o fría | Foto de contexto real o generada | `imagenes-contextuales-diapositivas` |

Regla de variedad: si vas a producir varias láminas seguidas, **no repitas el mismo patrón dos
veces consecutivas**. La monotonía de patrón reintroduce la sensación de "muro" que estás
intentando eliminar.

## Paso 2 — Reglas de composición (las que hacen la diferencia medible)

Estas son las que separaron la versión buena de la plana. Aplícalas como presupuesto, no como
sugerencia:

1. **Doble codificación**: cada elemento paralelo lleva un icono figurativo y concreto (un plato,
   unos tenis, una luna), no un símbolo abstracto. El icono ocupa ~30–35% de la altura de la
   tarjeta.
2. **Presupuesto de texto**: ≤35 palabras por tarjeta, en ≤3 viñetas de ≤15 palabras. Si no cabe,
   el problema es de recorte, no de tipografía: recorta adjetivos, nunca criterios.
3. **Señalización por línea**: micro-icono por viñeta **solo** cuando cada viñeta es una dimensión
   distinta (tiempo / fuerza / sedentarismo). Si las viñetas son homogéneas, el micro-icono es ruido.
4. **Color como canal continuo**: el color de la categoría recorre encabezado → fondo de la
   tarjeta → acento del icono. Un color que muere en la barra del encabezado no está codificando
   nada.
5. **Cero espacio muerto**: si sobra más del ~15% del área de una tarjeta, falta contenido o
   sobra tarjeta. Prefiere una fila única de N columnas a una rejilla 2×3 con tarjetas medio vacías.
6. **Orientación con significado**: fila única = elementos simultáneos y comparables; rejilla o
   columna = jerarquía o secuencia. No uses rejilla para contenido que no tiene orden.
7. **Tres niveles tipográficos**: título (28–36pt) > encabezado de tarjeta (12–14pt) > cuerpo
   (10–11pt). Si el título compite con los encabezados, no hay jerarquía.
8. **Título narrativo**: una afirmación, no un rótulo. "Medidas no farmacológicas: el pilar que
   sostiene todo lo demás" enseña; "Tratamiento no farmacológico" solo etiqueta.
9. **Banda de cierre**: mensaje para llevar + 3–4 beneficios/consecuencias + fuente. Convierte la
   lámina en una pieza que se entiende sola cuando el residente la revisa una semana después.

## Paso 3 — Trazabilidad de la evidencia al condensar (irrenunciable)

Condensar es donde se rompe la medicina basada en evidencia sin que nadie lo note. Antes de dar
por buena una pieza, corre este chequeo comparando el texto original contra el visual:

- **Grados y códigos**: si la fuente trae nivel de evidencia o número de recomendación
  (5.36 · B, GRADE fuerte, clase IIa), va en la lámina como chip pequeño al final de la viñeta.
  No se sacrifica por estética.
- **Criterios que definen la conducta**: frecuencias, intervalos, valores de corte, quién puede
  prescribir, condiciones de exclusión. Si al recortar desapareció "sin más de 2 días consecutivos
  sin actividad", recortaste el criterio y no el adjetivo. Reviértelo.
- **Deriva semántica**: verbo por verbo. "Solo puede *facturarla* un nutricionista-dietista" ≠
  "solo puede *brindarla*". "Disrupciones del sueño relacionadas con la diabetes" ≠ "condiciones
  relacionadas con la diabetes".
- **Contenido nuevo**: cualquier cosa que aparezca en el visual y no esté en la fuente (típicamente
  la banda de beneficios) necesita su propia referencia, o se reetiqueta como objetivo/expectativa,
  o se marca `[No verificado]`. Nunca se presenta como resultado comprobado.
- **Cita al pie**: una línea con la fuente real. Si no la tienes, dilo; no rellenes con una fuente
  genérica.

Cuando detectes una pérdida, **repórtala al usuario junto con la entrega** en dos o tres líneas
("al condensar la tarjeta de actividad física se cayó X; lo devolví como chip"). Esa observación
es parte del valor de la skill, no una molestia.

## Paso 4 — Plantilla UNINAVARRA por defecto

Salvo indicación contraria, toda pieza visual entregable sale sobre la plantilla institucional.
Lee `plantilla-uninavarra` para el fondo real, la zona segura y la tipografía; lo esencial:

- Lienzo `LAYOUT_WIDE` 13.333 × 7.5 in. Fondo = el JPG institucional real, nunca un rectángulo
  rojo "parecido".
- Banda roja 0–1.4 in: intocable. Contenido 1.45–7.0 in. Franja de cita 7.05–7.45 in.
  (Si el deck en curso ya usa la convención antigua con la cita en 6.45 in, mantén la del deck
  para no romper la consistencia; no mezcles las dos.)
- Rojo institucional `#DB0C20`; títulos en navy `0E2841`, Arial.

**Desactivación:** si el usuario dice "sin plantilla", "esta vez no", "no la uses", "es para otra
cosa / otra universidad / redes / un documento", o pide explícitamente un PNG/SVG suelto, entrega
la pieza sin el fondo institucional y con márgenes libres. La instrucción vale para esa tarea; no
la extiendas a las siguientes ni la olvides dentro de la misma tarea.

## Paso 5 — Producir

Para el patrón más frecuente (N elementos paralelos), usa el script incluido en vez de recomponer
la geometría cada vez:

```bash
python3 scripts/build_lamina_tarjetas.py spec.json salida.pptx
```

El script recibe un JSON con título, tarjetas (encabezado, color, icono, viñetas con su chip de
grado), banda de cierre, cita y notas de orador; calcula anchos, tintes y posiciones dentro de la
zona segura, y **avisa por consola cuando una tarjeta rompe el presupuesto de palabras o cuando
hay más de 6 tarjetas en una fila**. El esquema completo y ejemplos están en
`references/patrones-visuales.md`; ejecútalo con `--esquema` para ver la plantilla del JSON.

Para todo lo demás (algoritmos, gráficos, líneas de tiempo, fotos de contexto), esta skill decide
el patrón y delega el dibujo a la skill correspondiente de la tabla del Paso 1.

## Integración con las otras skills

Esta es una **capa de decisión**, no un competidor. Encaja así:

- `presentaciones-cientificas` define qué dice cada diapositiva → esta skill define **qué forma
  visual toma** cada bloque → `diagramas-clinicos` / `imagenes-contextuales-diapositivas` dibujan
  → `plantilla-uninavarra` da el marco institucional → `diapositivas-dinamicas` hace el acabado.
- Si el usuario está en medio del flujo de `presentaciones-cientificas` y dice "esto quedó muy de
  texto", actívala sobre las diapositivas ya escritas sin rehacer el contenido.
- Si el entregable es un documento (`estudio-cronicas`, `docx`), aplica igual: la pieza visual se
  genera como imagen y se inserta; el presupuesto de palabras y la trazabilidad no cambian.
- El filtro de realidad del usuario (`[Evidencia]` / `[Inferencia]` / `[Especulación]` /
  `[No verificado]`) sigue vigente en todo lo que produzcas aquí, incluido el texto de las tarjetas.

## QA antes de entregar

1. ¿La pieza se entiende en 5 segundos sin leer todo? Si no, sobra texto o falta jerarquía.
2. ¿Alguna tarjeta pasa de 35 palabras o de 3 viñetas?
3. ¿Todos los grados/códigos de la fuente sobrevivieron?
4. ¿Hay contenido en el visual que no esté en la fuente y sin cita?
5. ¿El texto invade la banda roja o la franja de cita?
6. ¿El color codifica algo o solo decora?
7. ¿Queda más del 15% de espacio muerto en alguna tarjeta?
8. Convierte a imagen y míralo (QA de la skill `pptx`) — no lo des por bueno sin verlo renderizado.

## Qué NO hacer

- No infografiar por defecto: el Paso 0 existe para poder decir "esto va mejor como texto".
- No sacrificar grados de recomendación, umbrales ni criterios para ganar espacio.
- No inventar beneficios, cifras ni fuentes para completar la banda de cierre.
- No usar iconos abstractos intercambiables (engranajes, bombillos, checks genéricos) donde el
  concepto tiene una imagen concreta disponible.
- No meter seis ideas en una rejilla 2×3 con la mitad del área vacía solo porque "cabe".
- No aplicar la plantilla institucional cuando el usuario pidió no usarla, ni omitirla cuando no
  lo pidió.
