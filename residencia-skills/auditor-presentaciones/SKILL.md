---
name: auditor-presentaciones
description: 'Audita una presentación ya construida (.pptx propio, heredado de un compañero, descargado o recién generado en el chat) y devuelve un informe de hallazgos priorizados más el archivo corregido: densidad de texto, legibilidad a proyector, colisiones y márgenes, tiempo real de exposición, y sobre todo la verificación científica — cifras sin referencia, guías desactualizadas, dosis o umbrales mal transcritos, contradicciones entre diapositivas. Úsala SIEMPRE que el usuario adjunte un .pptx y diga "revisa", "corrige", "¿está bien?", "¿me alcanza el tiempo?", "¿quedó muy cargada?", "mira si tiene errores", "califica esta presentación", o quiera un control de calidad antes de exponer o de entregar a un docente; y como cierre de `presentaciones-cientificas` cuando el deck es largo o va con nota. NO construye contenido nuevo (eso es `presentaciones-cientificas`) ni cambia la estética (eso es `diapositivas-dinamicas`): juzga lo que ya existe y lo corrige.'
---

# Auditoría de presentaciones

Revisar un deck terminado con el criterio de un docente que va a calificarlo y de un
especialista que va a verificar cada cifra. El objetivo no es opinar "se ve bien": es
producir una lista de defectos concretos, con número de diapositiva, y arreglar los que
se puedan arreglar sin inventar contenido.

Dos cosas que esta skill nunca hace: rellenar un dato faltante con una cifra verosímil, y
"mejorar" una recomendación clínica que el usuario puso a propósito sin antes señalarla.
Si una corrección cambia el sentido clínico, se propone, no se aplica en silencio.

## Flujo de trabajo

### Fase 1 — Auditoría técnica (automática)

Ejecutar el script sobre el archivo. Da las métricas que no se pueden juzgar mirando:

```bash
python scripts/auditar_pptx.py <archivo.pptx> --json /tmp/auditoria.json
```

Devuelve por diapositiva: palabras proyectadas, número de párrafos, tamaño de fuente
mínimo, si tiene guion en notas, si hay una referencia con año en la franja inferior,
líneas demasiado largas, elementos fuera de la zona segura, colisiones entre formas y
minutos estimados de exposición. Si el deck sigue otra convención de densidad, ajustar
umbrales con `--margen-cm` o cambiar el ritmo con `--wpm` (130 es un ritmo académico
normal en español; 110-120 si el usuario habla despacio o el público es internacional).

El script no reemplaza mirar: es el filtro que dice **dónde** mirar.

### Fase 2 — Revisión visual

Convertir las diapositivas a imágenes y mirarlas, empezando por las que el script marcó.
El procedimiento de conversión está en `references/revision-visual.md`. Buscar lo que
ninguna métrica detecta: texto sobre una imagen oscura, tabla que se sale por la derecha,
gráfico ilegible al reducirse, viñetas desalineadas, dos diapositivas seguidas con el mismo
título, logo institucional tapado.

### Fase 3 — Auditoría científica (la parte que importa)

Leer el texto de todas las diapositivas y las notas. Verificar, en este orden:

1. **Cifras sin fuente.** Todo porcentaje, umbral, dosis, sensibilidad, NNT o RR debe tener
   cita abreviada. Listar los que no la tienen — no inventarles una.
2. **Vigencia de las guías citadas.** Si se cita ADA 2023, ESC 2021 o similar, comprobar con
   búsqueda web si hay versión más reciente y decir qué cambió en lo que la diapositiva
   afirma. Una guía superada no siempre invalida la diapositiva: decirlo con precisión.
3. **Transcripción.** Contrastar dosis, umbrales diagnósticos, puntos de corte de escalas y
   clases de recomendación contra la fuente citada. Los errores más frecuentes son de
   unidades (mg vs mg/kg), de coma decimal y de intervalos invertidos.
4. **Coherencia interna.** Una meta terapéutica que aparece distinta en dos diapositivas, un
   algoritmo que contradice la tabla anterior, una conclusión que no se sostiene con lo
   expuesto.
5. **Etiquetado de certeza.** Lo que sea inferencia o consenso débil presentado como hecho
   debe marcarse **[Inferencia]**, **[Especulación]** o **[No verificado]**.
6. **Bibliografía final.** Que exista, que esté en Vancouver, sin duplicados, y que coincida
   con lo citado en las diapositivas.

Todo lo que no pueda verificarse con las fuentes disponibles se reporta como
"no verificable con las fuentes consultadas", nunca como correcto por omisión.

### Fase 4 — Informe

Entregar el informe con esta estructura exacta:

```
## Veredicto
[2-3 líneas: ¿se puede exponer así? ¿qué es lo que más pesa?]

## Bloqueante (corregir antes de exponer)
[errores científicos, cifras sin fuente, guía desactualizada que cambia la conducta,
 diapositivas ilegibles a proyector]

## Recomendable (mejora clara)
[densidad, tiempo, colisiones, falta de guion, referencias al pie]

## Opcional (pulido)
[estética, orden, redundancias menores]

## Tiempo
[minutos estimados vs minutos disponibles, y qué diapositivas recortar si sobra]
```

Cada hallazgo lleva número de diapositiva y qué hacer, en una línea. Nada de párrafos
descriptivos: el usuario va a usar esto como lista de tareas.

### Fase 5 — Correcciones

Aplicar directamente lo mecánico (densidad, tamaños, colisiones, referencias que ya existen
en el documento pero no están al pie, guion faltante donde el contenido lo permite) y
entregar el `.pptx` corregido con sufijo `_auditado`. Ver
`references/revision-visual.md § Aplicar correcciones` para no romper la plantilla
institucional al editar.

Lo que toca contenido clínico se propone en el informe y se aplica solo si el usuario lo
aprueba. Al final decir en una línea qué se corrigió y qué quedó pendiente de su decisión.

## Criterios de evaluación

Estos son los umbrales por defecto, alineados con `presentaciones-cientificas`. Si el deck usa
`plantilla-uninavarra`, el tope de puntos de texto visibles a la vez es 4 (no 6): reportar 5-6 como
"Recomendable: repartir con revelado progresivo".

| Dimensión | Umbral | Bandera si |
|---|---|---|
| Palabras proyectadas por diapositiva | ≤ 60 | > 60 |
| Párrafos/bullets de contenido | ≤ 6 | > 6 |
| Palabras por bullet | ≤ 10 | > 10 |
| Palabras del título | ≤ 10 | > 10 |
| Fuente mínima del cuerpo | ≥ 16 pt | < 14 pt |
| Cita en la franja inferior (p. ej. 7.05–7.45 in en UNINAVARRA) | ≥ 8 pt; el script la reconoce sola y no la cuenta como texto proyectado ni como invasión de margen | < 8 pt |
| Guion del expositor en notas | en todas | falta en alguna |
| Referencia al pie | en toda diapositiva con dato clínico | falta |
| Ritmo | ~1 min por diapositiva de contenido | > 1,5 min o < 0,3 min |

Si el usuario indica una duración disponible, el ajuste de tiempo pasa a ser bloqueante:
una gran sesión que se pasa 10 minutos es un defecto tan real como una cifra sin fuente.

## Cuándo NO usar esta skill

- El usuario quiere **construir** la presentación → `presentaciones-cientificas`.
- Quiere que se vea más moderna, con animaciones o versión HTML → `diapositivas-dinamicas`.
- Quiere convertir un bloque denso en un visual → `visualizar-informacion`.
- Quiere ensayar la exposición, cronometrarse o prepararse para las preguntas →
  `ensayo-y-defensa`. La auditoría revisa el archivo; esa otra revisa al expositor.

## Archivos de referencia

- `scripts/auditar_pptx.py` — auditoría técnica automática. Ejecutar siempre primero.
- `references/revision-visual.md` — cómo convertir a imágenes, qué mirar en cada tipo de
  diapositiva y cómo aplicar correcciones sin romper la plantilla.
