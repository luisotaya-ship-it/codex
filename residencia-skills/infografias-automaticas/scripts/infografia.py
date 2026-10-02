#!/usr/bin/env python3
"""
Motor de infografías clínicas. Recibe una especificación en JSON y devuelve
SVG + PNG listos para insertar en una diapositiva.

    python infografia.py spec.json --salida /ruta/nombre [--tema clinica|uninavarra]

Patrones disponibles (campo "patron" del JSON):

  categorias   — N bloques temáticos, cada uno con iconos + etiqueta.
                 Para clasificaciones: complicaciones, tipos, causas, criterios.
  pasos        — secuencia numerada horizontal. Para procesos y manejo escalonado.
  comparativa  — dos columnas enfrentadas. Para guía A vs guía B, fármaco A vs B.
  linea_tiempo — hitos sobre un eje. Para historia natural, cronología de una guía.

Ver `references/biblioteca-iconos.md` para el catálogo de iconos y cómo añadir uno.
Ningún dato numérico se inventa: lo que no venga en el JSON no aparece en la imagen.
"""
import argparse
import json
import sys

try:
    import cairosvg
except ImportError:
    sys.exit("Falta cairosvg. Instalar con: pip install cairosvg --break-system-packages")

TEMAS = {
    "clinica":   {"p": "#12365F", "a": "#1C6FB8", "b": "#C8322B", "c": "#E29B12",
                  "d": "#1E9A5B", "gris": "#F1F3F5", "txt": "#1B2733"},
    "uninavarra": {"p": "#7A1420", "a": "#A8232F", "b": "#12365F", "c": "#C8842A",
                   "d": "#4A6B57", "gris": "#F4F1F1", "txt": "#221A1C"},
}
SKIN = "#F5C9A6"

# --------------------------------------------------------------- iconos ---
# Cada icono se dibuja en un lienzo local de 100x100. Añadir uno nuevo es
# registrar una función más en este diccionario.

def _ico(nombre, T):
    N, R, A, G = T["p"], "#C8322B", T["a"], "#1E9A5B"
    I = {
"glucometro": f'''<rect x="26" y="14" width="40" height="72" rx="9" fill="#FFF" stroke="{N}" stroke-width="4"/>
 <rect x="33" y="24" width="26" height="20" rx="3" fill="#D6E8F7" stroke="{N}" stroke-width="3"/>
 <circle cx="38" cy="58" r="4.5" fill="{N}"/><circle cx="54" cy="58" r="4.5" fill="{N}"/>
 <circle cx="38" cy="72" r="4.5" fill="{N}"/><circle cx="54" cy="72" r="4.5" fill="{N}"/>
 <path d="M80,26 L80,66" stroke="{R}" stroke-width="8" stroke-linecap="round"/>
 <path d="M68,56 L80,72 L92,56" fill="none" stroke="{R}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>''',
"tubos": ''.join(f'''<rect x="{x}" y="16" width="18" height="66" rx="9" fill="#FFF" stroke="{N}" stroke-width="3.5"/>
 <path d="M{x+1.5},52 L{x+16.5},52 L{x+16.5},73 a9,9 0 0 1 -15,0 Z" fill="{c}"/>'''
 for x, c in [(24, "#E8B33A"), (44, "#D96A4B"), (64, "#E8B33A")]) +
 f'<path d="M50,6 c5,7 8,10 8,14 a8,8 0 0 1 -16,0 c0,-4 3,-7 8,-14 Z" fill="{R}"/>',
"matraz": f'''<path d="M32,16 L32,44 L18,80 a6,6 0 0 0 5,9 L69,89 a6,6 0 0 0 5,-9 L60,44 L60,16 Z"
 fill="#FFF" stroke="{N}" stroke-width="4" stroke-linejoin="round"/>
 <path d="M25,62 L67,62 L74,80 a6,6 0 0 1 -5,9 L23,89 a6,6 0 0 1 -5,-9 Z" fill="#F2C14E"/>
 <circle cx="34" cy="74" r="3.5" fill="#B07A10"/><circle cx="46" cy="79" r="3.5" fill="#B07A10"/>
 <circle cx="57" cy="72" r="3.5" fill="#B07A10"/>
 <path d="M28,12 L64,12" stroke="{N}" stroke-width="5" stroke-linecap="round"/>
 <path d="M86,74 L86,34" stroke="{R}" stroke-width="7" stroke-linecap="round"/>
 <path d="M76,45 L86,31 L96,45" fill="none" stroke="{R}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>''',
"corazon": f'''<path d="M50,88 C18,66 10,44 21,31 C31,19 46,23 50,35 C54,23 69,19 79,31 C90,44 82,66 50,88 Z"
 fill="#E0574F" stroke="#9E2B25" stroke-width="3.5" stroke-linejoin="round"/>
 <path d="M31,42 C39,48 44,56 47,66" fill="none" stroke="#F6C7C3" stroke-width="6" stroke-linecap="round"/>
 <circle cx="66" cy="52" r="10" fill="#FFF3C2" stroke="#9E2B25" stroke-width="3"/>
 <path d="M60,46 L72,58" stroke="#9E2B25" stroke-width="4" stroke-linecap="round"/>''',
"cerebro": f'''<path d="M50,14 C34,14 24,22 22,32 C13,36 11,48 18,55 C14,64 20,76 32,78
 C38,86 62,86 68,78 C80,76 86,64 82,55 C89,48 87,36 78,32 C76,22 66,14 50,14 Z"
 fill="#EFA9AE" stroke="#A9505A" stroke-width="3.5"/><path d="M50,18 L50,82" stroke="#A9505A" stroke-width="3"/>
 <path d="M36,26 C42,32 38,40 44,46 C38,52 44,60 38,68" fill="none" stroke="#A9505A" stroke-width="3" stroke-linecap="round"/>
 <path d="M64,26 C58,32 62,40 56,46 C62,52 56,60 62,68" fill="none" stroke="#A9505A" stroke-width="3" stroke-linecap="round"/>''',
"pierna": f'''<path d="M26,10 C40,8 48,16 48,30 C48,44 42,52 42,64 C42,74 46,82 40,90
 C34,96 22,92 24,82 C27,70 30,62 28,50 C26,38 18,28 20,20 Z" fill="{SKIN}" stroke="#C98F63" stroke-width="3.5" stroke-linejoin="round"/>
 <path d="M31,16 C33,30 36,40 35,52 C34,64 31,74 32,84" fill="none" stroke="{R}" stroke-width="4" stroke-linecap="round"/>
 <circle cx="70" cy="46" r="22" fill="#FFF" stroke="{N}" stroke-width="4"/>
 <path d="M52,46 a18,18 0 0 1 36,0" fill="#F6D9D6"/><circle cx="70" cy="46" r="9" fill="#C05046"/>''',
"ojo": f'''<path d="M8,50 C28,22 72,22 92,50 C72,78 28,78 8,50 Z" fill="#FFF" stroke="{N}" stroke-width="4"/>
 <circle cx="50" cy="50" r="19" fill="#7FB2D8" stroke="{N}" stroke-width="3"/><circle cx="50" cy="50" r="8" fill="{N}"/>
 <path d="M18,44 C28,50 30,56 26,62" fill="none" stroke="{R}" stroke-width="3" stroke-linecap="round"/>
 <path d="M82,44 C72,50 70,56 74,62" fill="none" stroke="{R}" stroke-width="3" stroke-linecap="round"/>
 <circle cx="63" cy="38" r="4" fill="#B33228"/>''',
"rinon": f'''<path d="M60,14 C79,16 88,34 88,52 C88,74 74,88 58,88 C44,88 34,79 33,66
 C32,54 41,50 41,42 C41,31 46,12 60,14 Z" fill="#B4574F" stroke="#7C3630" stroke-width="3.5"/>
 <path d="M46,38 C56,44 58,58 50,70" fill="none" stroke="#F0C3BE" stroke-width="5" stroke-linecap="round"/>
 <path d="M33,52 C24,52 18,58 14,66" fill="none" stroke="#E0A03A" stroke-width="6" stroke-linecap="round"/>
 <path d="M36,44 C28,42 22,38 18,32" fill="none" stroke="#C0403A" stroke-width="5" stroke-linecap="round"/>''',
"neurona": f'''<circle cx="30" cy="42" r="15" fill="#F2C744" stroke="#9A7A0E" stroke-width="3.5"/>
 <path d="M30,27 L26,12 M15,34 L4,26 M16,52 L5,58 M32,57 L30,70" stroke="#9A7A0E" stroke-width="4" stroke-linecap="round"/>
 <path d="M45,42 L92,42" stroke="#9A7A0E" stroke-width="5" stroke-linecap="round"/>
 <ellipse cx="56" cy="42" rx="9" ry="7" fill="#F2C744" stroke="#9A7A0E" stroke-width="3"/>
 <ellipse cx="76" cy="42" rx="9" ry="7" fill="#F2C744" stroke="#9A7A0E" stroke-width="3"/>
 <path d="M40,72 L52,66 M46,84 L60,79" stroke="{R}" stroke-width="4.5" stroke-linecap="round"/>''',
"pie": f'''<path d="M20,74 C14,60 17,44 26,35 C35,26 47,25 54,31 C61,37 62,47 66,55
 C70,63 79,64 86,68 C93,72 91,83 82,84 L32,86 C24,86 22,81 20,74 Z" fill="{SKIN}" stroke="#C98F63" stroke-width="3.5" stroke-linejoin="round"/>
 <path d="M33,20 C40,14 52,15 58,22" fill="none" stroke="#C98F63" stroke-width="4" stroke-linecap="round"/>
 <circle cx="36" cy="70" r="11" fill="#C4463C"/><circle cx="36" cy="70" r="5" fill="#7E2019"/>''',
"germenes": f'''<circle cx="36" cy="40" r="17" fill="#7CC08C" stroke="#2E7A48" stroke-width="3.5"/>
 <path d="M36,23 L36,14 M53,40 L62,40 M36,57 L36,66 M19,40 L10,40 M48,28 L54,22 M48,52 L54,58 M24,52 L18,58 M24,28 L18,22"
 stroke="#2E7A48" stroke-width="3.5" stroke-linecap="round"/><circle cx="30" cy="36" r="3.4" fill="#2E7A48"/>
 <ellipse cx="70" cy="68" rx="17" ry="13" fill="#C79AD8" stroke="#6C3E85" stroke-width="3.5"/>
 <path d="M70,55 L70,47 M87,68 L95,70 M70,81 L70,89 M53,68 L45,66" stroke="#6C3E85" stroke-width="3.5" stroke-linecap="round"/>''',
"piel": f'''<path d="M30,88 L30,50 C30,44 38,44 38,50 L38,30 C38,23 47,23 47,30 L47,26
 C47,19 56,19 56,26 L56,32 C56,25 65,25 65,32 L65,58 C65,76 58,88 48,90 Z"
 fill="{SKIN}" stroke="#C98F63" stroke-width="3.5" stroke-linejoin="round"/>
 <circle cx="44" cy="58" r="4" fill="#C4463C"/><circle cx="55" cy="50" r="3.4" fill="#C4463C"/>
 <circle cx="52" cy="66" r="3.4" fill="#C4463C"/><circle cx="42" cy="72" r="3" fill="#C4463C"/>''',
"masculino": f'''<circle cx="42" cy="62" r="24" fill="none" stroke="{A}" stroke-width="8"/>
 <path d="M60,44 L86,18" stroke="{A}" stroke-width="8" stroke-linecap="round"/>
 <path d="M66,16 L88,16 L88,38" fill="none" stroke="{A}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>''',
"pulmon": f'''<path d="M46,14 L54,14 L54,44 L46,44 Z" fill="#C08A8A"/>
 <path d="M44,34 C30,30 16,42 16,60 C16,76 24,86 34,86 C42,86 46,78 46,66 L46,40 Z" fill="#E7A9A9" stroke="#9E5B5B" stroke-width="3.5"/>
 <path d="M56,34 C70,30 84,42 84,60 C84,76 76,86 66,86 C58,86 54,78 54,66 L54,40 Z" fill="#E7A9A9" stroke="#9E5B5B" stroke-width="3.5"/>
 <path d="M50,14 L50,40" stroke="#9E5B5B" stroke-width="4" stroke-linecap="round"/>''',
"higado": f'''<path d="M14,40 C30,26 62,24 84,32 C92,36 92,52 84,62 C74,74 56,82 40,78
 C24,74 12,60 14,40 Z" fill="#9C5B4B" stroke="#6E3A2E" stroke-width="3.5"/>
 <path d="M50,30 C52,48 50,64 44,78" fill="none" stroke="#6E3A2E" stroke-width="3"/>''',
"pastilla": f'''<rect x="14" y="38" width="72" height="30" rx="15" fill="#FFF" stroke="{N}" stroke-width="4" transform="rotate(-25 50 53)"/>
 <path d="M50,53 m-36,0 a36,15 0 0 1 36,-15" fill="{A}" transform="rotate(-25 50 53)"/>
 <path d="M22,44 a15,15 0 0 0 0,18 L50,53 Z" fill="{A}" transform="rotate(-25 50 53)"/>''',
"jeringa": f'''<path d="M18,82 L34,66" stroke="{N}" stroke-width="5" stroke-linecap="round"/>
 <rect x="32" y="34" width="46" height="22" rx="4" fill="#FFF" stroke="{N}" stroke-width="4" transform="rotate(45 55 45)"/>
 <path d="M74,20 L86,8" stroke="{N}" stroke-width="6" stroke-linecap="round"/>
 <path d="M40,52 L58,34" stroke="{A}" stroke-width="10" stroke-linecap="round" opacity="0.7"/>''',
"balanza": f'''<path d="M50,14 L50,84 M28,84 L72,84" stroke="{N}" stroke-width="5" stroke-linecap="round"/>
 <path d="M18,30 L82,30" stroke="{N}" stroke-width="5" stroke-linecap="round"/>
 <path d="M6,30 L18,54 L30,30 Z" fill="{A}"/><path d="M70,30 L82,54 L94,30 Z" fill="{A}"/>
 <circle cx="50" cy="30" r="6" fill="{N}"/>''',
"reloj": f'''<circle cx="50" cy="52" r="34" fill="#FFF" stroke="{N}" stroke-width="5"/>
 <path d="M50,32 L50,52 L64,62" fill="none" stroke="{A}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
 <path d="M36,10 L64,10" stroke="{N}" stroke-width="6" stroke-linecap="round"/>''',
"alerta": f'''<path d="M50,10 L92,84 L8,84 Z" fill="#F2C14E" stroke="{R}" stroke-width="5" stroke-linejoin="round"/>
 <path d="M50,36 L50,60" stroke="{R}" stroke-width="8" stroke-linecap="round"/>
 <circle cx="50" cy="72" r="5" fill="{R}"/>''',
"chequeo": f'''<circle cx="50" cy="50" r="36" fill="none" stroke="{G}" stroke-width="6"/>
 <path d="M32,52 L45,64 L70,36" fill="none" stroke="{G}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>''',
"lupa": f'''<circle cx="44" cy="44" r="26" fill="#FFF" stroke="{N}" stroke-width="6"/>
 <path d="M63,63 L86,86" stroke="{N}" stroke-width="9" stroke-linecap="round"/>
 <path d="M32,44 a12,12 0 0 1 12,-12" fill="none" stroke="{A}" stroke-width="5" stroke-linecap="round"/>''',
"documento": f'''<path d="M24,10 L62,10 L78,28 L78,90 L24,90 Z" fill="#FFF" stroke="{N}" stroke-width="4" stroke-linejoin="round"/>
 <path d="M62,10 L62,28 L78,28" fill="none" stroke="{N}" stroke-width="4" stroke-linejoin="round"/>
 <path d="M34,44 L68,44 M34,56 L68,56 M34,68 L56,68" stroke="{A}" stroke-width="5" stroke-linecap="round"/>''',
"personas": f'''<circle cx="32" cy="34" r="13" fill="{A}"/><path d="M10,80 a22,22 0 0 1 44,0 Z" fill="{A}"/>
 <circle cx="68" cy="38" r="11" fill="{N}"/><path d="M50,80 a18,18 0 0 1 36,0 Z" fill="{N}"/>''',
    }
    if nombre not in I:
        raise KeyError(f"icono '{nombre}' no existe. Disponibles: {sorted(I)}")
    return I[nombre]


def icono(nombre, cx, cy, tam, T):
    e = tam / 100
    return f'<g transform="translate({cx-tam/2:.1f},{cy-tam/2:.1f}) scale({e:.4f})">{_ico(nombre, T)}</g>'


def txt(x, y, s, tam, color, peso="700", fam="Work Sans", anc="middle"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{fam}" font-size="{tam}" '
            f'font-weight="{peso}" fill="{color}" text-anchor="{anc}">{esc(s)}</text>')


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cinta(x, y, w, h, relleno, borde, lineas, tam, color_t, T):
    p = 34
    s = (f'<path d="M{x-p},{y-6} L{x+8},{y-6} L{x+8},{y+h+6} L{x-p},{y+h+6} L{x-p+18},{y+h/2} Z" fill="{T["d"]}" opacity="0.85"/>'
         f'<path d="M{x+w+p},{y-6} L{x+w-8},{y-6} L{x+w-8},{y+h+6} L{x+w+p},{y+h+6} L{x+w+p-18},{y+h/2} Z" fill="{T["d"]}" opacity="0.85"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{relleno}" stroke="{borde}" stroke-width="3.5"/>')
    n = len(lineas)
    for i, ln in enumerate(lineas):
        yy = y + h / 2 + (i - (n - 1) / 2) * (tam + 8) + tam * 0.35
        s += txt(x + w / 2, yy, ln, tam, color_t, fam="Outfit")
    return s


# -------------------------------------------------------------- patrones ---

def p_categorias(spec, T, W):
    bloques = spec["bloques"]
    cols = 2 if len(bloques) > 1 else 1
    filas = (len(bloques) + cols - 1) // cols
    pw = (W - 60 * (cols + 1)) / cols
    ph = 278
    y0 = 162
    colores = [T["a"], T["b"], T["c"], T["d"]]
    s = ""
    for k, b in enumerate(bloques):
        x = 60 + (k % cols) * (pw + 60)
        y = y0 + (k // cols) * (ph + 38)
        color = b.get("color") or colores[k % 4]
        s += f'<rect x="{x}" y="{y+26}" width="{pw}" height="{ph-26}" rx="16" fill="{T["gris"]}"/>'
        tw = 30 + len(b["titulo"]) * 17
        s += (f'<rect x="{x+(pw-tw)/2:.0f}" y="{y}" width="{tw}" height="52" rx="12" fill="{color}"/>'
              + txt(x + pw / 2, y + 35, b["titulo"], 26, "#FFFFFF", fam="Outfit"))
        items = b["items"]
        paso = pw / len(items)
        for i, it in enumerate(items):
            cx = x + paso * (i + 0.5)
            s += icono(it["icono"], cx, y + 132, 122 if len(items) <= 3 else 108, T)
            for j, ln in enumerate(envolver(it["texto"], 18)):
                s += txt(cx, y + 215 + j * 27, ln, 20 if len(items) <= 3 else 18, T["txt"])
    alto = y0 + filas * (ph + 38) + 46
    return s, alto


def p_pasos(spec, T, W):
    pasos = spec["bloques"]
    n = len(pasos)
    m, gap = 70, 26
    pw = (W - 2 * m - gap * (n - 1)) / n
    y = 190
    s = ""
    for i, b in enumerate(pasos):
        x = m + i * (pw + gap)
        s += f'<rect x="{x}" y="{y}" width="{pw}" height="300" rx="16" fill="{T["gris"]}"/>'
        s += f'<circle cx="{x+pw/2}" cy="{y}" r="26" fill="{T["a"]}"/>'
        s += txt(x + pw / 2, y + 9, str(i + 1), 27, "#FFFFFF", fam="Outfit")
        if b.get("icono"):
            s += icono(b["icono"], x + pw / 2, y + 100, 96, T)
        s += txt(x + pw / 2, y + 178, b["titulo"], 23, T["p"], fam="Outfit")
        for j, ln in enumerate(envolver(b.get("texto", ""), 24)[:4]):
            s += txt(x + pw / 2, y + 212 + j * 25, ln, 17, T["txt"], peso="400")
        if i < n - 1:
            xa = x + pw + gap / 2
            s += (f'<path d="M{xa-9},{y+140} L{xa+9},{y+150} L{xa-9},{y+160}" fill="{T["a"]}"/>')
    return s, y + 340


def p_comparativa(spec, T, W):
    a, b = spec["bloques"][0], spec["bloques"][1]
    filas = spec.get("filas", [])
    m = 70
    cw = (W - 2 * m - 30) / 2
    y = 172
    s = ""
    for k, (blo, col, x) in enumerate([(a, T["a"], m), (b, T["b"], m + cw + 30)]):
        s += f'<rect x="{x}" y="{y}" width="{cw}" height="64" rx="12" fill="{col}"/>'
        s += txt(x + cw / 2, y + 42, blo["titulo"], 28, "#FFFFFF", fam="Outfit")
    yy = y + 84
    for i, f in enumerate(filas):
        h = 88
        s += f'<rect x="{m}" y="{yy}" width="{W-2*m}" height="{h}" rx="12" fill="{T["gris"] if i%2==0 else "#FFFFFF"}"/>'
        s += txt(W / 2, yy + 26, f["criterio"], 19, T["p"], fam="Outfit")
        s += txt(m + cw / 2, yy + 62, f["a"], 19, T["txt"], peso="400")
        s += txt(m + cw + 30 + cw / 2, yy + 62, f["b"], 19, T["txt"], peso="400")
        s += f'<path d="M{W/2},{yy+40} L{W/2},{yy+h-10}" stroke="#D6DBE0" stroke-width="2"/>'
        yy += h + 8
    return s, yy + 40


def p_linea_tiempo(spec, T, W):
    hitos = spec["bloques"]
    n = len(hitos)
    m = 170
    y = 348
    s = f'<path d="M{m},{y} L{W-m},{y}" stroke="{T["a"]}" stroke-width="8" stroke-linecap="round"/>'
    paso = (W - 2 * m) / max(n - 1, 1)
    for i, b in enumerate(hitos):
        cx = m + i * paso
        arriba = i % 2 == 0
        s += f'<circle cx="{cx}" cy="{y}" r="14" fill="#FFFFFF" stroke="{T["a"]}" stroke-width="7"/>'
        cy = y - 150 if arriba else y + 150
        s += f'<path d="M{cx},{y} L{cx},{cy + (58 if arriba else -58)}" stroke="{T["a"]}" stroke-width="3" stroke-dasharray="6 6"/>'
        s += f'<rect x="{cx-135}" y="{cy-56}" width="270" height="112" rx="14" fill="{T["gris"]}"/>'
        if b.get("icono"):
            s += icono(b["icono"], cx - 92, cy, 62, T)
        s += txt(cx + 28, cy - 12, b["titulo"], 22, T["p"], fam="Outfit")
        for j, ln in enumerate(envolver(b.get("texto", ""), 22)[:2]):
            s += txt(cx + 28, cy + 16 + j * 24, ln, 17, T["txt"], peso="400")
    return s, y + 250


def envolver(t, ancho):
    palabras, lineas, cur = str(t).split(), [], ""
    for p in palabras:
        if len(cur) + len(p) + 1 <= ancho:
            cur = (cur + " " + p).strip()
        else:
            lineas.append(cur); cur = p
    if cur:
        lineas.append(cur)
    return lineas or [""]


PATRONES = {"categorias": p_categorias, "pasos": p_pasos,
            "comparativa": p_comparativa, "linea_tiempo": p_linea_tiempo}


def construir(spec, tema="clinica", W=1640):
    T = TEMAS[tema]
    cuerpo, alto = PATRONES[spec["patron"]](spec, T, W)
    cab = cinta(150, 34, W - 300, 74, "#FFFFFF" if tema == "uninavarra" else "#DCEBF8",
                T["a"], [spec["titulo"]], 46, T["p"], T)
    pie = ""
    H = alto + 110
    if spec.get("mensaje"):
        pie += cinta(300, alto + 8, W - 600, 66, T["a"], T["p"],
                     envolver(spec["mensaje"], 92), 23, "#FFFFFF", T)
        H = alto + 150
    fuente = spec.get("fuente")
    if fuente:
        pie += txt(W / 2, H - 26, fuente, 16, "#7B8794", peso="400")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>{cab}{cuerpo}{pie}</svg>'), W, H


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--salida", required=True, help="ruta base sin extensión")
    ap.add_argument("--tema", default="clinica", choices=list(TEMAS))
    ap.add_argument("--escala", type=float, default=2.0)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    svg, W, H = construir(spec, a.tema)
    open(a.salida + ".svg", "w", encoding="utf-8").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=a.salida + ".png",
                     output_width=int(W * a.escala), output_height=int(H * a.escala))
    print(f"{a.salida}.svg  {a.salida}.png  ({int(W*a.escala)}x{int(H*a.escala)})")
