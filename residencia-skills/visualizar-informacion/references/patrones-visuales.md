# Patrones visuales, geometría y esquema del script

Contenido:
1. Esquema JSON de `build_lamina_tarjetas.py`
2. Geometría interna de la lámina de tarjetas
3. Catálogo ampliado de patrones (cuándo y cómo)
4. Iconos: de dónde salen
5. Insertar la lámina en un deck existente

---

## 1. Esquema JSON de `build_lamina_tarjetas.py`

```json
{
  "titulo": "Título narrativo: una afirmación, no un rótulo",
  "fondo": "gran sesion/Plantilla_UNINAVARRA_fondo_2025.jpg",
  "cita": "Autor et al. Título. Revista. Año;vol(n):págs. doi:...",
  "notas": "Guion real del orador para esta lámina.",
  "tarjetas": [
    {
      "titulo": "Nombre de la categoría",
      "color": "#0F6E56",
      "icono": "iconos/plato.png",
      "vinetas": [
        {"texto": "Recomendación en ≤15 palabras", "grado": "5.36 · B"}
      ]
    }
  ],
  "cierre": {
    "mensaje": "Mensaje para llevar en una frase.",
    "puntos": ["Consecuencia 1", "Consecuencia 2", "Consecuencia 3"]
  }
}
```

- `fondo`, `icono`, `grado`, `cierre` y `notas` son opcionales. Si falta el fondo o un icono, el
  script avisa y sigue: mejor entregar la lámina que abortar.
- `color`: un hex por categoría. Elígelos con contraste entre sí y sentido semántico cuando exista
  (rojo para lo que se evita, verde para actividad, azul para sueño). El script deriva
  automáticamente el tinte claro del cuerpo de la tarjeta a partir de ese hex, para que el color
  sea un canal continuo y no solo una barra de encabezado.
- `grado`: cualquier código de la fuente (`5.36 · B`, `GRADE fuerte`, `Clase IIa, NE B-R`). Se
  imprime en 8.5pt negrita del color de la tarjeta, al final de la viñeta.

Avisos que emite el script (son las reglas del presupuesto de carga cognitiva, no errores):
más de 6 tarjetas, más de 35 palabras por tarjeta, más de 3 viñetas, viñetas de más de 15
palabras, tarjetas sin grado de evidencia, lámina sin cita.

---

## 2. Geometría interna (lienzo 13.333 × 7.5 in)

| Elemento | Posición |
|---|---|
| Banda roja institucional | 0 – 1.4 in (intocable) |
| Título | 1.55 in, alto 0.75 in, 28pt bold navy `0E2841` |
| Fila de tarjetas | desde 2.40 in; alto auto-ajustado al contenido y centrado en el aire sobrante |
| Encabezado de tarjeta | 0.52 in, 12pt bold blanco sobre el color |
| Icono | ≈32% del alto de la tarjeta, centrado |
| Banda de cierre | 0.62 in, termina 0.20 in antes de la cita |
| Cita | 7.05 in, 8pt, centrada entre 1.30 y 12.03 in (los extremos los ocupa el pie institucional) |

Ancho de cada tarjeta = (12.25 − 0.18 × (n−1)) / n. Con n = 6 son 1.89 in, que a 10.5pt admite
unos 22–24 caracteres por línea: esa es la razón física del límite de 15 palabras por viñeta.

El alto de la tarjeta se calcula a partir de las líneas estimadas de texto, no del espacio
disponible. Estirar la tarjeta hasta el fondo es exactamente lo que produce el 40% de espacio
muerto que hace ver plana una lámina.

---

## 3. Catálogo ampliado de patrones

**Franja de tarjetas paralelas** — 3 a 6 elementos comparables, sin orden entre ellos.
Una sola fila. Si son más de 6, divide en dos láminas por criterio (no partas 6 en 3+3
arbitrariamente: busca el eje que las agrupa).

**Cifra grande** — cuando el mensaje ES el dato. 48–60pt para la cifra, 12–14pt para la etiqueta,
nada más en la lámina. Funciona en epidemiología ("88% de la diabetes en el embarazo es
gestacional"). Pierde todo su efecto si pones dos o tres cifras grandes compitiendo.

**Ecuación visual** — definiciones de 2 a 4 componentes que se suman: `criterio A + criterio B →
diagnóstico`. Sustituye a la lista de viñetas cuando los elementos no son independientes sino
constitutivos.

**Embudo por fases** — sospecha → confirmación → localización. La regla de oro (umbral, punto de
corte) va resaltada FUERA del flujo, no enterrada en una caja. Delega en `diagramas-clinicos`.

**Cascada / eje** — fisiopatología. Vertical si son ≤5 pasos, horizontal si son ≤4 con texto corto.
Delega en `diagramas-clinicos`.

**Gauge o tabla de umbrales** — valores de corte (glucemias, TFG, puntajes). Nunca como lista de
números sueltos en prosa.

**Línea de tiempo** — historia natural, evolución de guías, plan de seguimiento. Delega en
`diagramas-clinicos`.

**Tabla comparativa honesta** — cuando dos o tres guías difieren. Una tabla bien hecha es un
formato visual legítimo: no la conviertas en tarjetas para "que se vea más gráfico", porque la
comparación fila a fila es precisamente lo que el lector necesita.

**Escala validada reproducida** — PHQ-9, GAD-7, FRAX, Wells, CURB-65: reproduce la tabla real con
su puntuación e interpretación, citada. Resumirla en prosa la vuelve inutilizable en consulta.

**Figura anatómica con callouts** — complicaciones por sistema. Costosa de producir; úsala cuando
la localización anatómica es parte del mensaje, no como adorno.

---

## 4. Iconos

La doble codificación exige iconos **concretos y figurativos**: un plato con comida, unos tenis,
una luna, un cigarrillo tachado. Un engranaje o un bombillo no codifican nada porque sirven para
cualquier cosa.

Opciones, en orden de preferencia:
1. Iconos de bancos libres verificados (Tabler, Lucide, Bootstrap Icons, Material Symbols —
   licencias MIT/Apache), descargados como SVG/PNG. Verifica la licencia como exige
   `imagenes-contextuales-diapositivas`.
2. Generados a medida cuando el concepto es clínico y específico.
3. Sin icono, si no hay uno honesto: mejor una tarjeta limpia que un icono decorativo que
   distrae.

---

## 5. Insertar la lámina en un deck existente

El script genera un `.pptx` de una sola diapositiva. Para incorporarla a un deck ya construido:

- Si el deck aún no existe, genera primero las láminas sueltas y arma el deck con
  `presentaciones-cientificas` / `plantilla-uninavarra` reutilizando el mismo fondo.
- Si el deck ya existe, convierte la lámina a PNG a 300 dpi (`soffice --headless --convert-to png`)
  e insértala a sangre completa en la diapositiva correspondiente, o replica el bloque de tarjetas
  con las mismas coordenadas dentro del deck para conservar el texto editable. La segunda opción
  es preferible cuando el usuario va a seguir editando.
- Verifica siempre el resultado renderizado antes de entregar: el QA visual de `pptx` detecta
  invasiones de la banda roja y de la franja de cita que el código no ve.
