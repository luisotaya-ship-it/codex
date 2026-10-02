# Inserción en la diapositiva — layout imagen + texto

Estos snippets asumen `pptxgenjs` (el motor que ya usa
`presentaciones-cientificas`/`produccion-pptx.md`), lienzo `LAYOUT_WIDE`
(13.333 × 7.5 in). Si el deck usa `plantilla-uninavarra`, la zona de
contenido principal es 1.45in–7.0in vertical — ajustar los números de abajo
a ese rango en vez de asumir el lienzo completo.

## Patrón base: imagen a un lado, texto/cifra clave al otro

```javascript
function diapositivaConImagenContexto(pres, {
  titulo, imagenPath, textoLado, imagenIzquierda = true,
}) {
  const slide = pres.addSlide();
  // ... fondo/plantilla institucional si aplica, título arriba, franja de cita abajo

  const anchoImagen = 4.6; // in, ~35% del ancho útil
  const xImagen = imagenIzquierda ? 0.5 : 13.333 - 0.5 - anchoImagen;
  const xTexto = imagenIzquierda ? xImagen + anchoImagen + 0.4 : 0.5;
  const anchoTexto = 13.333 - anchoImagen - 1.3;

  slide.addImage({
    path: imagenPath,
    x: xImagen, y: 1.6, w: anchoImagen, h: 4.6,
    sizing: { type: "cover", w: anchoImagen, h: 4.6 }, // recorte a proporción, no deformar
  });

  slide.addText(textoLado, {
    x: xTexto, y: 1.6, w: anchoTexto, h: 4.6,
    fontSize: 18, valign: "middle",
  });

  return slide;
}
```

`sizing: { type: "cover" }` evita el error más común: estirar la imagen para
que "quepa" en el rectángulo, lo que deforma rostros y proporciones. Si la
imagen ya viene recortada a la proporción correcta por
`scripts/tratar_imagen.py`, `cover` no debería recortar nada adicional
relevante.

## Variante: "tarjeta de evidencia" (título + autores + PMID/DOI)

Útil cuando conviene mostrar visualmente de qué artículo sale una cifra,
además de la cita abreviada al pie que ya exige
`presentaciones-cientificas`. No es un sustituto de esa cita al pie, es un
refuerzo visual para 1-2 diapositivas donde el artículo mismo es parte del
mensaje (p. ej. "esta es la evidencia detrás de esta cifra").

```javascript
function tarjetaEvidencia(slide, { x, y, w, titulo, autores, pmid, doi }) {
  slide.addShape("roundRect", {
    x, y, w, h: 1.3,
    fill: { color: "FFFFFF" },
    line: { color: "D9D9D9", width: 0.75 },
    rectRadius: 0.08,
    shadow: { type: "outer", color: "000000", opacity: 0.15, blur: 6, offset: 2 },
  });
  slide.addText(titulo, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: 0.55, fontSize: 11, bold: true });
  slide.addText(autores, { x: x + 0.15, y: y + 0.62, w: w - 0.3, h: 0.3, fontSize: 9, color: "555555" });
  slide.addText(
    `PMID: ${pmid}${doi ? `   DOI: ${doi}` : ""}`,
    { x: x + 0.15, y: y + 0.92, w: w - 0.3, h: 0.3, fontSize: 8, color: "0563C1" },
  );
}
```

No inventar `pmid`/`doi`/autores — si el artículo real no trae esos datos
disponibles, omitir la tarjeta o dejar el campo en blanco con una nota, igual
que el resto de las reglas de evidencia de este usuario.

## Reglas de posicionamiento

- La imagen nunca invade la franja de cita (7.05in–7.45in en
  `plantilla-uninavarra`) ni la banda superior con el logo.
- Si dos diapositivas consecutivas llevan imagen, alterna el lado
  (izquierda/derecha) para que el deck no se sienta repetitivo — mismo
  principio de variar patrones que ya sigue `plantilla-uninavarra`.
- Para el patrón "humanístico/narrativo" (foto a sangre completa + cita
  textual de paciente en bocadillo, descrito en `plantilla-uninavarra`), la
  imagen puede ocupar el 100% del ancho — es la excepción deliberada al
  patrón imagen+texto lado a lado, y se usa con moderación (ver esa skill).
