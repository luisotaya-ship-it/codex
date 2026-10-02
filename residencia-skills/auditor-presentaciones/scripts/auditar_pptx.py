#!/usr/bin/env python3
"""
Auditoría técnica de un archivo .pptx.

Extrae, diapositiva por diapositiva, las métricas que no se pueden juzgar "a ojo":
densidad de texto, tamaño de fuente mínimo, presencia de guion en notas, referencia
al pie, colisiones entre cajas, elementos fuera de la zona segura y tiempo estimado.

Uso:
    python auditar_pptx.py deck.pptx                 # informe en markdown por stdout
    python auditar_pptx.py deck.pptx --json out.json # además guarda los datos crudos
    python auditar_pptx.py deck.pptx --wpm 120       # ritmo de habla distinto

No modifica el archivo. Los umbrales son los de la skill `presentaciones-cientificas`
(título <= 10 palabras, <= 6 bullets, <= 10 palabras por bullet) y pueden ajustarse
con banderas si el deck sigue otra convención.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:
    sys.exit("Falta python-pptx. Instalar con: pip install python-pptx --break-system-packages")

ANIO = re.compile(r"\b(19|20)\d{2}\b")


def emu_a_cm(v):
    return round(Emu(v).cm, 2) if v is not None else None


def texto_de(shape):
    if not getattr(shape, "has_text_frame", False):
        return ""
    return shape.text_frame.text or ""


def tam_minimo(shape):
    """Menor tamaño de fuente declarado explícitamente en la forma (pt), o None si todo se hereda."""
    tams = []
    if not getattr(shape, "has_text_frame", False):
        return None
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size is not None:
                tams.append(r.font.size.pt)
    return min(tams) if tams else None


def es_pie_de_cita(shape, texto, alto):
    """Caja de referencia al pie: en el 12 % inferior, corta y con un año citado."""
    if shape.top is None or shape.top < alto * 0.88:
        return False
    return bool(ANIO.search(texto)) and len(texto.split()) <= 60


def bbox(shape):
    try:
        if None in (shape.left, shape.top, shape.width, shape.height):
            return None
        return (shape.left, shape.top, shape.left + shape.width, shape.top + shape.height)
    except Exception:
        return None


def solapan(a, b, tolerancia_emu=45720):  # 0.05 cm de tolerancia
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix = min(ax2, bx2) - max(ax1, bx1)
    iy = min(ay2, by2) - max(ay1, by1)
    if ix <= tolerancia_emu or iy <= tolerancia_emu:
        return 0.0
    area_i = ix * iy
    menor = min((ax2 - ax1) * (ay2 - ay1), (bx2 - bx1) * (by2 - by1))
    return round(area_i / menor, 3) if menor else 0.0


def auditar(ruta, wpm=130, margen_cm=0.6, max_bullets=6, max_pal_bullet=10, max_pal_titulo=10):
    prs = Presentation(ruta)
    ancho, alto = prs.slide_width, prs.slide_height
    margen = Emu(int(margen_cm * 360000))
    resultado = {
        "archivo": str(ruta),
        "diapositivas_total": len(prs.slides),
        "tamano_cm": [emu_a_cm(ancho), emu_a_cm(alto)],
        "wpm_usado": wpm,
        "diapositivas": [],
    }

    for i, slide in enumerate(prs.slides, start=1):
        cajas, palabras, bullets_largos, imagenes = [], 0, [], 0
        tams, tams_pie, fuera_zona, textos = [], [], [], []
        titulo = ""

        for sh in slide.shapes:
            if sh.shape_type is not None and "PICTURE" in str(sh.shape_type):
                imagenes += 1
            t = texto_de(sh).strip()
            if t and es_pie_de_cita(sh, t, alto):
                # La franja de cita (p. ej. 7.05-7.45 in en la plantilla UNINAVARRA) se diseña
                # pequeña y pegada al borde a propósito: no cuenta como texto proyectado ni
                # como violación de zona segura; solo se exige que siga siendo legible (>= 8 pt).
                tm = tam_minimo(sh)
                if tm:
                    tams_pie.append(tm)
                continue
            if t:
                textos.append(t)
                palabras += len(t.split())
                if not titulo:
                    # el primer texto de la mitad superior se toma como título
                    if sh.top is not None and sh.top < alto * 0.30:
                        titulo = t.split("\n")[0]
                for linea in t.split("\n"):
                    n = len(linea.split())
                    if n > max_pal_bullet:
                        bullets_largos.append({"palabras": n, "texto": linea[:90]})
                tm = tam_minimo(sh)
                if tm:
                    tams.append(tm)
            b = bbox(sh)
            if b:
                cajas.append((sh.shape_id, b))
                if b[0] < margen or b[1] < margen or b[2] > ancho - margen or b[3] > alto - margen:
                    fuera_zona.append({"forma": sh.shape_id, "texto": t[:60]})

        colisiones = []
        for j in range(len(cajas)):
            for k in range(j + 1, len(cajas)):
                r = solapan(cajas[j][1], cajas[k][1])
                if r > 0.15:
                    colisiones.append({"formas": [cajas[j][0], cajas[k][0]], "fraccion": r})

        notas = ""
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            notas = (slide.notes_slide.notes_text_frame.text or "").strip()
        pal_notas = len(notas.split())

        # referencia al pie: texto con un año en el tercio inferior
        pie_con_anio = False
        for sh in slide.shapes:
            t = texto_de(sh)
            if t and sh.top is not None and sh.top > alto * 0.78 and ANIO.search(t):
                pie_con_anio = True
                break

        n_parrafos = sum(len([p for p in s.text_frame.paragraphs if p.text.strip()])
                         for s in slide.shapes if getattr(s, "has_text_frame", False))

        resultado["diapositivas"].append({
            "n": i,
            "titulo": titulo,
            "palabras_titulo": len(titulo.split()) if titulo else 0,
            "palabras_diapositiva": palabras,
            "parrafos": n_parrafos,
            "imagenes": imagenes,
            "fuente_min_pt": min(tams) if tams else None,
            "fuente_min_pie_pt": min(tams_pie) if tams_pie else None,
            "tiene_notas": bool(notas),
            "palabras_notas": pal_notas,
            "minutos_estimados": round(pal_notas / wpm, 2) if pal_notas else 0.0,
            "referencia_al_pie": pie_con_anio,
            "bullets_largos": bullets_largos,
            "fuera_de_zona_segura": fuera_zona,
            "colisiones": colisiones,
            "banderas": banderas_de(palabras, n_parrafos, titulo, tams, tams_pie, notas, pie_con_anio,
                                    bullets_largos, fuera_zona, colisiones,
                                    max_bullets, max_pal_titulo),
        })

    total_min = round(sum(d["minutos_estimados"] for d in resultado["diapositivas"]), 1)
    resultado["minutos_totales_estimados"] = total_min
    return resultado


def banderas_de(palabras, parrafos, titulo, tams, tams_pie, notas, pie, bullets_largos, fuera, colis,
                max_bullets, max_pal_titulo):
    b = []
    if palabras > 60:
        b.append(f"DENSIDAD: {palabras} palabras proyectadas (umbral 60)")
    if parrafos > max_bullets + 2:
        b.append(f"BULLETS: {parrafos} párrafos de texto (umbral {max_bullets} + título + pie)")
    if titulo and len(titulo.split()) > max_pal_titulo:
        b.append(f"TITULO: {len(titulo.split())} palabras (umbral {max_pal_titulo})")
    if tams and min(tams) < 14:
        b.append(f"LEGIBILIDAD: fuente de {min(tams):.0f} pt (mínimo proyectable 14-16 pt)")
    if tams_pie and min(tams_pie) < 8:
        b.append(f"LEGIBILIDAD PIE: cita al pie de {min(tams_pie):.0f} pt (mínimo 8 pt)")
    if not notas:
        b.append("SIN GUION: la diapositiva no tiene notas del orador")
    if not pie:
        b.append("SIN REFERENCIA: no se detecta cita con año en la franja inferior")
    if bullets_largos:
        b.append(f"BULLETS LARGOS: {len(bullets_largos)} línea(s) por encima del límite de palabras")
    if fuera:
        b.append(f"ZONA SEGURA: {len(fuera)} elemento(s) tocan o exceden el margen")
    if colis:
        b.append(f"COLISION: {len(colis)} par(es) de formas superpuestas >15 %")
    return b


def informe_md(r):
    L = [f"# Auditoría técnica — {Path(r['archivo']).name}", ""]
    L.append(f"- Diapositivas: **{r['diapositivas_total']}**")
    L.append(f"- Tamaño: {r['tamano_cm'][0]} × {r['tamano_cm'][1]} cm")
    L.append(f"- Tiempo estimado según el guion en notas: **{r['minutos_totales_estimados']} min** "
             f"(a {r['wpm_usado']} palabras/min)")
    sin_notas = [d["n"] for d in r["diapositivas"] if not d["tiene_notas"]]
    sin_ref = [d["n"] for d in r["diapositivas"] if not d["referencia_al_pie"]]
    if sin_notas:
        L.append(f"- Sin guion en notas: {sin_notas}")
    if sin_ref:
        L.append(f"- Sin referencia detectada al pie: {sin_ref}")
    L += ["", "| # | Título | Palabras | Fuente mín. | Notas (min) | Ref. | Banderas |", "|---|---|---|---|---|---|---|"]
    for d in r["diapositivas"]:
        L.append("| {n} | {t} | {p} | {f} | {m} | {ref} | {b} |".format(
            n=d["n"],
            t=(d["titulo"][:38] or "—").replace("|", "/"),
            p=d["palabras_diapositiva"],
            f=f"{d['fuente_min_pt']:.0f}" if d["fuente_min_pt"] else "hered.",
            m=d["minutos_estimados"] or "—",
            ref="sí" if d["referencia_al_pie"] else "NO",
            b=len(d["banderas"]) or "—"))
    L += ["", "## Hallazgos por diapositiva", ""]
    for d in r["diapositivas"]:
        if d["banderas"]:
            L.append(f"**Diapositiva {d['n']}** — {d['titulo'][:60] or 'sin título'}")
            for x in d["banderas"]:
                L.append(f"- {x}")
            L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--wpm", type=int, default=130)
    ap.add_argument("--margen-cm", type=float, default=0.6)
    a = ap.parse_args()
    r = auditar(a.pptx, wpm=a.wpm, margen_cm=a.margen_cm)
    if a.json_out:
        Path(a.json_out).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(informe_md(r))
