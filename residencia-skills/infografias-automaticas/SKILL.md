---
name: infografias-automaticas
description: 'Genera automáticamente las infografías de una presentación — cuadrícula de categorías, secuencia de pasos, comparativa de dos columnas y línea de tiempo — como PNG y SVG vectorial listos para insertar en la diapositiva, con biblioteca propia de iconos médicos dibujados por código. Se activa SOLA, sin preguntar, cada vez que se construye o se rehace un deck: detecta qué diapositivas quedarían como muro de viñetas (una clasificación, un proceso escalonado, una comparación entre guías o fármacos, una cronología) y produce la pieza visual para cada una. Úsala también cuando el usuario diga "hazlo automático", "ponle infografías", "que no sea solo texto", "como la de complicaciones de la diabetes", "que decida tú qué merece imagen", o pida una infografía suelta sobre un tema. NO es para algoritmos de decisión con rombos ni gráficos de datos (`diagramas-clinicos`), ni para fotos clínicas reales (`imagenes-contextuales-diapositivas`), ni para portadas artísticas (`imagenes-creativas-medicas`).'
---

# Infografías automáticas

El usuario no quiere que le pregunten qué diapositiva merece una imagen. Quiere abrir el
`.pptx` y encontrarlas ya hechas. Esta skill existe para eso: decidir sola y producir el
archivo, no describirlo.

## Regla de activación

Al construir un deck (o al rehacer uno), recorrer las diapositivas ya redactadas y marcar
las que cumplan alguno de estos criterios. **No preguntar**: generar y entregar.

| La diapositiva contiene | Patrón que le corresponde |
|---|---|
| Una clasificación con 2-4 grupos y 2-4 elementos por grupo (complicaciones, tipos, causas, criterios, contraindicaciones) | `categorias` |
| Un proceso ordenado de 3-6 etapas (abordaje escalonado, ruta de atención, secuencia diagnóstica) | `pasos` |
| Dos opciones enfrentadas sobre los mismos criterios (guía A vs guía B, fármaco A vs B, tipo 1 vs tipo 2) | `comparativa` |
| Hitos sobre un eje temporal (historia natural, evolución de las guías, cronograma de seguimiento) | `linea_tiempo` |

Tope sensato: **una infografía cada 4-6 diapositivas de contenido**. Un deck donde todo es
infografía cansa igual que uno donde todo es viñeta. Si dos diapositivas seguidas califican,
elegir la de mayor densidad y dejar la otra en texto.

Cuando la diapositiva califica, la infografía **reemplaza** las viñetas, no se suma a ellas:
el detalle que se cae del cuerpo se mueve al guion del orador en las notas.

## Cómo se genera

Escribir un JSON de especificación y ejecutar el motor:

```bash
python scripts/infografia.py spec.json --salida /ruta/nombre --tema clinica --escala 2
```

Salen dos archivos: `.png` (para insertar en la diapositiva) y `.svg` (vectorial, editable en
Illustrator/Inkscape, escala sin pixelarse). Temas disponibles: `clinica` (azul institucional
neutro) y `uninavarra` (rojo/vino de la plantilla del usuario). Si el deck usa la plantilla
UNINAVARRA, el tema es `uninavarra` sin preguntar.

Estructura del JSON, catálogo completo de iconos y ejemplos de los cuatro patrones:
`references/especificacion.md`. Leerlo antes de escribir el primer spec.

## Reglas de contenido

1. **Nada de datos inventados.** Lo que no venga verificado no entra en la imagen. Si la
   infografía va a llevar cifras (prevalencias, umbrales, NNT), tienen que salir de la fuente
   que ya se está usando en el deck y llevar la referencia en el campo `fuente`. Sin fuente
   disponible: se hace la infografía sin cifras y se dice por qué.
2. **El campo `fuente` casi nunca va vacío.** Es el pie de la imagen: guía, organización y
   año. Cuando la pieza es una clasificación conceptual sin datos, decirlo explícitamente ahí
   (por ejemplo: "clasificación conceptual, sin cifras epidemiológicas").
3. **Texto corto.** Etiquetas de 1-4 palabras en `categorias`, una frase de ≤ 24 caracteres
   por línea en `pasos` y `linea_tiempo`. El motor envuelve el texto, pero una etiqueta larga
   se sale del bloque igual.
4. **Icono que signifique algo.** Si ningún icono del catálogo representa el concepto, es mejor
   un icono neutro (`documento`, `chequeo`, `lupa`) que uno anatómicamente equivocado. Añadir
   iconos nuevos al diccionario del script cuando haga falta — está pensado para crecer.

## Verificación obligatoria

Después de generar, **mirar la imagen** (abrirla, no solo confirmar que el comando terminó).
Lo que se busca: texto que se sale del bloque, etiquetas de tres líneas que invaden el borde
inferior, iconos que no se distinguen a tamaño de diapositiva. Reducir la vista previa al 35 %
y comprobar que las etiquetas siguen legibles: así se verá desde la última fila.

Si algo se desborda, se corrige el texto del spec (acortar la etiqueta) antes que forzar el
tamaño de fuente.

## Integración

- Dentro de `presentaciones-cientificas`: se ejecuta en la Fase 1, después de redactar las
  diapositivas y antes de construir el `.pptx`, y los PNG se insertan en la Fase 3. Anotar en
  el Mapa de la presentación qué diapositivas llevan infografía.
- Con `plantilla-uninavarra`: usar `--tema uninavarra`.
- Con `diapositivas-dinamicas`: los PNG generados aquí se animan sin ningún paso extra.
- Cuando lo que pide la diapositiva es un algoritmo de decisión con rombos y ramas,
  redirigir a `diagramas-clinicos` (que además los construye como formas nativas editables).
  Cuando pide una fotografía real de un paciente o una lesión, es
  `imagenes-contextuales-diapositivas`.

## Archivos de referencia

- `scripts/infografia.py` — motor. Cuatro patrones, dos temas, catálogo de iconos.
- `references/especificacion.md` — formato del JSON, catálogo de iconos y un ejemplo completo
  de cada patrón, listo para copiar.
