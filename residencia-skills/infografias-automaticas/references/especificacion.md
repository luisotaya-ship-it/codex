# Especificación del JSON

Campos comunes a todos los patrones:

| Campo | Obligatorio | Qué es |
|---|---|---|
| `patron` | sí | `categorias`, `pasos`, `comparativa` o `linea_tiempo` |
| `titulo` | sí | Va en la cinta superior. En mayúsculas, ≤ 55 caracteres |
| `bloques` | sí | Contenido; su forma depende del patrón (abajo) |
| `mensaje` | no | Cinta inferior de cierre. Solo en `categorias` tiene sentido visual |
| `fuente` | casi siempre | Pie de la imagen: guía, organización y año, o la advertencia de que no lleva cifras |

Ejecución:

```bash
python scripts/infografia.py spec.json --salida /ruta/nombre --tema clinica|uninavarra --escala 2
```

`--escala 2` da ~3280 px de ancho: sirve proyectado y también impreso en póster.

## Catálogo de iconos

Anatómicos: `corazon`, `cerebro`, `rinon`, `ojo`, `pulmon`, `higado`, `neurona`, `pie`,
`pierna`, `piel`, `masculino`.

Clínicos y de proceso: `glucometro`, `tubos`, `matraz`, `pastilla`, `jeringa`, `germenes`,
`balanza`, `reloj`, `alerta`, `chequeo`, `lupa`, `documento`, `personas`.

Para añadir uno nuevo: agregar una entrada al diccionario `I` dentro de `_ico()` en
`scripts/infografia.py`, dibujada en un lienzo local de 100×100. Usar `{N}` (color primario),
`{R}` (rojo de alarma), `{A}` (acento) y `{G}` (verde) para que respete el tema.

## Patrón `categorias`

Bloques temáticos con iconos. 2-4 bloques, 3-4 items por bloque.

```json
{"patron":"categorias","titulo":"COMPLICACIONES DE LA DIABETES MELLITUS",
 "mensaje":"PREVENCIÓN: control glucémico individualizado, tamizaje periódico...",
 "fuente":"Clasificación conceptual. Verificar cifras contra el ADA Standards of Care vigente.",
 "bloques":[
  {"titulo":"COMPLICACIONES AGUDAS","items":[
    {"icono":"glucometro","texto":"Hipoglucemia"},
    {"icono":"tubos","texto":"Cetoacidosis diabética"}]},
  {"titulo":"MICROVASCULARES","items":[
    {"icono":"ojo","texto":"Retinopatía diabética"},
    {"icono":"rinon","texto":"Nefropatía diabética"}]}]}
```

Se puede fijar el color de un bloque con `"color":"#C8322B"`; si se omite, el motor rota la
paleta del tema.

## Patrón `pasos`

Secuencia numerada horizontal. 3-6 etapas; con más de 6 las tarjetas quedan ilegibles.

```json
{"patron":"pasos","titulo":"ABORDAJE ESCALONADO EN CONSULTA",
 "fuente":"Esquema de proceso.",
 "bloques":[
  {"icono":"personas","titulo":"Captación","texto":"Identificar al paciente de riesgo"},
  {"icono":"lupa","titulo":"Evaluación","texto":"Anamnesis dirigida y estratificación"},
  {"icono":"reloj","titulo":"Seguimiento","texto":"Control programado y criterios de remisión"}]}
```

`texto` se corta a 4 líneas: si no cabe, va al guion del orador, no a la imagen.

## Patrón `comparativa`

Dos columnas enfrentadas sobre los mismos criterios. 3-6 filas.

```json
{"patron":"comparativa","titulo":"COMPARACIÓN DE DOS ESQUEMAS",
 "fuente":"[fuente de cada columna]",
 "bloques":[{"titulo":"OPCIÓN A"},{"titulo":"OPCIÓN B"}],
 "filas":[
  {"criterio":"Vía de administración","a":"Oral","b":"Subcutánea"},
  {"criterio":"Monitorización","a":"Función renal","b":"Función renal y peso"}]}
```

Cada celda, ≤ 30 caracteres. Si las dos columnas vienen de guías distintas, decir cuál es
cuál en `fuente` — es el error más frecuente de este patrón.

## Patrón `linea_tiempo`

Hitos alternados sobre un eje. 3-6 hitos.

```json
{"patron":"linea_tiempo","titulo":"HISTORIA NATURAL",
 "fuente":"Esquema conceptual sin plazos numéricos.",
 "bloques":[
  {"icono":"chequeo","titulo":"Susceptibilidad","texto":"Factores de riesgo presentes"},
  {"icono":"alerta","titulo":"Clínica","texto":"Aparición de manifestaciones"}]}
```

`titulo` de cada hito ≤ 16 caracteres y `texto` de máximo 2 líneas: la tarjeta es angosta.
Si el eje lleva plazos reales (meses, años), tienen que venir de la fuente citada.
