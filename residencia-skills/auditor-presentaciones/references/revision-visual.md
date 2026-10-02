# Revisión visual y aplicación de correcciones

## Convertir el .pptx a imágenes

En el entorno con LibreOffice disponible:

```bash
soffice --headless --convert-to pdf --outdir /tmp/audit <archivo.pptx>
pdftoppm -jpeg -r 90 /tmp/audit/<archivo>.pdf /tmp/audit/slide
```

Quedan `slide-01.jpg`, `slide-02.jpg`… Mirarlas de verdad, no solo listarlas. Si LibreOffice
no está disponible, decirlo explícitamente en el informe y limitar la auditoría a lo textual
y lo métrico: no afirmar que una diapositiva "se ve bien" sin haberla visto.

Una prueba barata de legibilidad a proyector: reducir la imagen al 35 % y mirarla. Lo que no
se lee ahí, no se lee desde la última fila del auditorio.

## Qué mirar según el tipo de diapositiva

| Tipo | Fallos típicos |
|---|---|
| Portada | Título cortado, nombre/afiliación desactualizados, fecha vieja |
| Tabla | Se sale por la derecha, encabezado sin contraste, más de 6 filas × 5 columnas |
| Algoritmo | Flechas cruzadas, rombos sin las dos salidas rotuladas, texto dentro de la caja recortado |
| Gráfico | Ejes sin unidades, leyenda tapada, escala truncada que exagera el efecto, colores que no se distinguen en escala de grises |
| Imagen clínica | Texto encima sin fondo de contraste, paciente identificable, sin fuente ni licencia |
| Escala clínica | Puntajes mal sumados, puntos de corte que no coinciden con la fuente |
| Cierre | Bibliografía cortada entre diapositivas, referencia numerada que no existe en el cuerpo |

## Contraste

Comprobar el texto sobre fondos de color o imágenes. Regla práctica: relación de contraste
mínima 4.5:1 para texto normal y 3:1 para texto grande (≥ 24 pt). En la práctica de
proyección, texto claro sobre imagen fotográfica siempre necesita una capa oscura
semitransparente detrás — señalarlo cuando falte.

Nunca dejar el color como único portador de significado (por ejemplo, filas "rojas" para
contraindicaciones sin etiqueta textual): además de accesibilidad, muchos proyectores
distorsionan el color.

## Aplicar correcciones

Editar el archivo original con `python-pptx` sobre una **copia**, nunca sobre el archivo que
el usuario subió:

```bash
cp <archivo.pptx> <carpeta-de-trabajo>/<nombre>_auditado.pptx
```

Reglas para no romper el diseño institucional:

- No borrar ni mover las formas de fondo, logos, escudos ni la banda superior de la plantilla
  (en los decks UNINAVARRA suelen ser imágenes de fondo del layout).
- Reducir densidad moviendo texto al guion en notas, no borrando información clínica.
- Al bajar el tamaño de fuente para que quepa: si hay que ir por debajo de 16 pt, el problema
  es de exceso de contenido, no de tipografía — dividir la diapositiva en dos.
- Al corregir colisiones, mover la caja de menor jerarquía, nunca el título ni el pie.
- Conservar el `objectName` de los elementos si el deck tiene pares preparados para Morph
  (ver `presentaciones-cientificas` / `diapositivas-dinamicas`): renombrarlos rompe la
  transición.

Después de editar, volver a ejecutar `scripts/auditar_pptx.py` sobre la copia corregida y
mostrar el antes/después en una tabla corta (banderas totales por diapositiva). Es la
evidencia de que la corrección funcionó, y toma diez segundos.
