#!/usr/bin/env python3
"""
tratar_imagen.py — recorte a proporción y tratamiento de cohesión visual
para imágenes de contexto que se insertan en diapositivas.

Dos modos, y NO son intercambiables:

  --modo escena     Para categorías 2 y 3 (escena/contexto humano, decorativo).
                     Permite recorte + ajuste tonal sutil para que imágenes de
                     bancos distintos se sientan de la misma familia visual.

  --modo clinico     Para categoría 1 (hallazgo clínico real: exantema, fondo
                     de ojo, radiografía, lesión). SOLO recorta/redimensiona.
                     Nunca aplica ajuste de color — el color puede ser el dato
                     clínico (eritema, cianosis, ictericia, etc.) y alterarlo
                     falsearía la imagen.

Uso:
    python3 tratar_imagen.py entrada.jpg salida.png --modo escena \
        --ancho-in 4.6 --alto-in 4.6 --dpi 150 \
        --tono-hex "#0B3D91" --intensidad 0.08

    python3 tratar_imagen.py hallazgo.jpg salida.png --modo clinico \
        --ancho-in 4.6 --alto-in 4.6 --dpi 300

Requiere Pillow (ya disponible en el entorno).
"""

import argparse
from PIL import Image, ImageOps, ImageEnhance


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def crop_to_aspect(img: Image.Image, target_ratio: float) -> Image.Image:
    """Recorta al centro para alcanzar target_ratio (ancho/alto) sin deformar."""
    w, h = img.size
    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 1e-3:
        return img
    if current_ratio > target_ratio:
        # Imagen más ancha de lo necesario: recortar los lados.
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        # Imagen más alta de lo necesario: recortar arriba/abajo.
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def apply_cohesion_tone(img: Image.Image, tone_rgb: tuple, intensidad: float = 0.08) -> Image.Image:
    """Ajuste tonal MUY sutil (no un duotono fuerte) para dar sensación de
    familia visual entre imágenes de bancos distintos. Solo usar en modo
    'escena' — nunca en imágenes de categoría 1 (hallazgo clínico real).

    intensidad: 0.0 (sin efecto) a ~0.2 (perceptible). Por defecto conservador.
    """
    if intensidad <= 0:
        return img
    overlay = Image.new("RGB", img.size, tone_rgb)
    base = img.convert("RGB")
    blended = Image.blend(base, overlay, intensidad)
    # Recuperar un poco de contraste tras el blend, que suele aplanar la imagen.
    return ImageEnhance.Contrast(blended).enhance(1.05)


def add_rounded_corners(img: Image.Image, radius_px: int) -> Image.Image:
    """Añade máscara de esquinas redondeadas (estética de 'tarjeta') con canal alfa."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius_px, fill=255)
    img.putalpha(mask)
    return img


def resize_for_slide(img: Image.Image, ancho_in: float, alto_in: float, dpi: int) -> Image.Image:
    target_w = int(ancho_in * dpi)
    target_h = int(alto_in * dpi)
    img = crop_to_aspect(img, target_w / target_h)
    return img.resize((target_w, target_h), Image.LANCZOS)


def procesar(ruta_entrada, ruta_salida, modo, ancho_in, alto_in, dpi,
             tono_hex=None, intensidad=0.08, esquinas_redondeadas=0):
    img = Image.open(ruta_entrada)
    img = ImageOps.exif_transpose(img)  # corrige orientación de fotos de cámara/celular

    img = resize_for_slide(img, ancho_in, alto_in, dpi)

    if modo == "escena" and tono_hex:
        img = apply_cohesion_tone(img, _hex_to_rgb(tono_hex), intensidad)
    elif modo == "clinico" and tono_hex:
        raise ValueError(
            "Modo 'clinico': no se permite ajuste de color (--tono-hex). "
            "El color puede ser el dato clínico de la imagen. Omite --tono-hex "
            "y --intensidad para este modo."
        )

    if esquinas_redondeadas > 0:
        img = add_rounded_corners(img, esquinas_redondeadas)
        img.save(ruta_salida, "PNG", dpi=(dpi, dpi))
    else:
        img.convert("RGB").save(ruta_salida, "PNG", dpi=(dpi, dpi))

    print(f"OK: {ruta_salida} ({img.size[0]}x{img.size[1]}px, {dpi} dpi, modo={modo})")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--modo", choices=["escena", "clinico"], required=True)
    p.add_argument("--ancho-in", type=float, required=True)
    p.add_argument("--alto-in", type=float, required=True)
    p.add_argument("--dpi", type=int, default=150, help="150 para pantalla/diapositiva, 300 si además va a imprenta")
    p.add_argument("--tono-hex", type=str, default=None, help="Solo válido con --modo escena")
    p.add_argument("--intensidad", type=float, default=0.08)
    p.add_argument("--esquinas-redondeadas", type=int, default=0, help="Radio en px; 0 = sin redondear")
    args = p.parse_args()

    procesar(
        args.entrada, args.salida, args.modo, args.ancho_in, args.alto_in, args.dpi,
        tono_hex=args.tono_hex, intensidad=args.intensidad,
        esquinas_redondeadas=args.esquinas_redondeadas,
    )


if __name__ == "__main__":
    main()
