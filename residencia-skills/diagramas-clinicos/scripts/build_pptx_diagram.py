"""
build_pptx_diagram.py — Algoritmos y flujogramas clínicos como formas
NATIVAS y editables de PowerPoint (no una imagen aplanada).

Por qué existe este módulo, además de Graphviz (render_dot.sh): un PNG de
Graphviz es perfecto para un documento Word/PDF, pero dentro de un .pptx es
una imagen muerta — el residente no puede mover una caja, corregir un
umbral en el texto, o ajustar una flecha sin regenerar todo el diagrama
desde el .dot. Este módulo construye el mismo tipo de algoritmo (óvalos,
rombos de decisión, cajas de acción/alarma, flechas con etiqueta) como
formas reales de PowerPoint: cada caja, cada texto y cada conector queda
seleccionable y editable directamente en PowerPoint después de insertarlo.

Mantiene la misma convención visual que assets/plantilla_algoritmo.dot
(ver graphviz-guia.md) para que un algoritmo se vea igual sin importar qué
motor lo generó:
    - inicio/fin        -> óvalo verde   (#2E7D32)
    - decisión          -> rombo ámbar   (#FFB74D)
    - acción/estudio    -> caja azul     (#42A5F5)
    - alarma/hospital.  -> caja roja     (#E57373)

DISEÑO "VISUALMENTE ADAPTABLE": el layout NO es una plantilla de tamaño
fijo. Se calcula automáticamente a partir del contenido real:
    1. Cada nodo se ubica en un "nivel" (fila) según la distancia más larga
       desde el/los nodo(s) de inicio — igual que rankdir=TB de Graphviz.
    2. El tamaño de cada caja se estima a partir del largo de su texto
       (con ajuste de fuente hacia abajo si el texto es largo).
    3. Si una fila no cabe en el ancho de la diapositiva, se reduce la
       escala de fuente/caja de esa fila hasta que quepa, en vez de
       desbordarse o solaparse.
    4. Si aun al tamaño mínimo el diagrama no cabe en una diapositiva
       16:9 estándar, la función avisa (ver campo "warnings" del resultado)
       en vez de entregar algo ilegible — en ese caso, considera partir el
       algoritmo en sub-diagramas o usar Graphviz, que no tiene este límite.

Uso típico:
    from build_pptx_diagram import build_algorithm_pptx

    spec = {
        "nodes": [
            {"id": "inicio", "text": "Sospecha de HTA resistente", "type": "start_end"},
            {"id": "d1", "text": "¿PA >=130/80 con 3 farmacos a dosis maxima\nincluyendo diuretico?", "type": "decision"},
            {"id": "a1", "text": "Confirmar con MAPA/AMPA\ny descartar pseudorresistencia", "type": "action"},
            {"id": "alarma1", "text": "Descartar causas secundarias\n(SAHOS, hiperaldosteronismo)", "type": "alert"},
            {"id": "fin", "text": "HTA resistente confirmada:\nagregar espironolactona", "type": "start_end"},
        ],
        "edges": [
            {"from": "inicio", "to": "d1"},
            {"from": "d1", "to": "a1", "label": "Si"},
            {"from": "d1", "to": "fin", "label": "No"},
            {"from": "a1", "to": "alarma1"},
            {"from": "alarma1", "to": "fin"},
        ],
        "title": "Abordaje de hipertensión arterial resistente",
        "source": "ESH 2023 / ACC-AHA 2017 — [Evidencia]",
    }
    result = build_algorithm_pptx(spec, "algoritmo_hta.pptx")
    print(result["warnings"])  # revisar antes de entregar al usuario

Para verificar visualmente el resultado sin abrir PowerPoint, convertir a
PNG con LibreOffice (ya disponible en el sandbox) y mirarlo con la
herramienta Read antes de entregarlo:
    soffice --headless --convert-to png algoritmo_hta.pptx
"""

from __future__ import annotations

from collections import defaultdict, deque

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

# ---------------------------------------------------------------------------
# Convención visual (debe coincidir con assets/plantilla_algoritmo.dot)
# ---------------------------------------------------------------------------

NODE_STYLES = {
    "start_end": {"shape": MSO_SHAPE.OVAL, "fill": "2E7D32", "font": "FFFFFF"},
    "decision": {"shape": MSO_SHAPE.DIAMOND, "fill": "FFB74D", "font": "212121"},
    "action": {"shape": MSO_SHAPE.ROUNDED_RECTANGLE, "fill": "42A5F5", "font": "FFFFFF"},
    "alert": {"shape": MSO_SHAPE.ROUNDED_RECTANGLE, "fill": "E57373", "font": "FFFFFF"},
}
EDGE_COLOR = "616161"
SOURCE_COLOR = "616161"
SOURCE_MISSING_COLOR = "C62828"

# Slide estándar 16:9 (mismo ancho que presentaciones-cientificas/pptx usan
# por defecto), para que el diagrama se pueda copiar/pegar directo a un
# mazo existente sin reescalar horizontalmente. El ALTO, en cambio, se
# calcula dinámicamente a partir del contenido (ver build_algorithm_pptx):
# un algoritmo de 3 pasos no necesita el mismo lienzo que uno de 8 — forzar
# ambos a 7.5in fijos es lo que produce texto ilegible o cajas solapadas.
SLIDE_W_IN = 13.333
SLIDE_H_MIN_IN = 7.5    # nunca más bajo que una diapositiva estándar
SLIDE_H_MAX_IN = 19.0   # límite antes de recomendar dividir el algoritmo
MARGIN_IN = 0.5

# Límites de layout — el algoritmo de ajuste automático se mueve dentro de
# este rango antes de rendirse y avisar que no cabe.
FONT_SIZES_PT = [14, 13, 12, 11, 10, 9]
MIN_BOX_W_IN = {"start_end": 1.6, "decision": 2.0, "action": 1.8, "alert": 1.8}
MAX_BOX_W_IN = {"start_end": 3.0, "decision": 3.4, "action": 2.8, "alert": 2.8}
LINE_H_FACTOR = 1.28          # alto de línea relativo al tamaño de fuente
CHAR_W_FACTOR = 0.52          # ancho promedio de carácter relativo a la fuente (heurística)
PAD_X_IN = 0.14
PAD_Y_IN = 0.10
ROW_GAP_IN = 0.55             # espacio vertical entre niveles (para que quepan flechas/etiquetas)
COL_GAP_IN = 0.35             # espacio horizontal entre cajas de una misma fila
DECISION_AREA_PENALTY = 1.35  # un rombo "desperdicia" espacio en las esquinas: agrandar caja
OVAL_AREA_PENALTY = 1.22      # un óvalo con 3+ líneas también recorta las esquinas del texto


def _hex(color: str) -> RGBColor:
    return RGBColor.from_string(color)


def _estimate_box(text: str, node_type: str, font_pt: int) -> tuple[float, float, int]:
    """Estima (ancho_in, alto_in, n_lineas) para que `text` quepa en una
    caja de `node_type` a tamaño `font_pt`, envolviendo por palabra."""
    import textwrap

    char_w = font_pt * CHAR_W_FACTOR / 72
    line_h = font_pt * LINE_H_FACTOR / 72
    max_w = MAX_BOX_W_IN[node_type]
    min_w = MIN_BOX_W_IN[node_type]

    # Probar anchos crecientes (en caracteres por línea) hasta encontrar un
    # balance razonable de líneas vs. ancho, respetando saltos manuales \n.
    best = None
    for target_w_in in (min_w, (min_w + max_w) / 2, max_w):
        wrap_chars = max(6, int(target_w_in / char_w))
        lines: list[str] = []
        for para in text.split("\n"):
            wrapped = textwrap.wrap(para, wrap_chars) or [""]
            lines.extend(wrapped)
        width_in = max((len(l) for l in lines), default=1) * char_w + PAD_X_IN * 2
        width_in = min(max(width_in, min_w), max_w)
        height_in = len(lines) * line_h + PAD_Y_IN * 2
        if node_type == "decision":
            width_in *= DECISION_AREA_PENALTY
            height_in *= DECISION_AREA_PENALTY
        elif node_type == "start_end" and len(lines) >= 3:
            # con 3+ líneas, el texto se acerca a las esquinas del
            # rectángulo contenedor, que quedan FUERA de la curva del
            # óvalo — sin este margen extra, la última línea se ve cortada
            # por el borde inferior del óvalo (bug real visto en un
            # algoritmo de 4 líneas en el nodo de cierre).
            width_in *= OVAL_AREA_PENALTY
            height_in *= OVAL_AREA_PENALTY
        candidate = (width_in, height_in, len(lines))
        if best is None or candidate[1] < best[1]:
            best = candidate
        if candidate[1] <= 1.35:  # ya es compacto, no seguir ensanchando de más
            break
    return best


def _estimate_label(text: str, font_pt: float = 10.5, max_w_in: float = 1.8) -> dict:
    """Estima (líneas envueltas, ancho_in, alto_in) para una etiqueta de
    arista. Las etiquetas deben ser cortas ("Sí"/"No"/un umbral breve) pero
    si llega una más larga, se envuelve en vez de desbordarse sin control —
    y el alto resultante se usa para reservar espacio real entre filas
    (ver `_row_gaps` en build_algorithm_pptx), no solo para dibujarla."""
    import textwrap

    char_w = font_pt * CHAR_W_FACTOR / 72
    line_h = font_pt * LINE_H_FACTOR / 72
    wrap_chars = max(4, int(max_w_in / char_w))
    lines = textwrap.wrap(text, wrap_chars) or [text]
    width_in = min(max((len(l) for l in lines), default=1) * char_w + 0.14, max_w_in)
    height_in = len(lines) * line_h + 0.08
    return {"lines": lines, "w": width_in, "h": height_in}


def _check_overlaps(rects: list[tuple[str, float, float, float, float]], tolerance_in: float = 0.05) -> list[str]:
    """Verifica por fuerza bruta que ningún par de rectángulos (nodos y
    etiquetas, en pulgadas: nombre, x, y, w, h) se solape más allá de un
    margen de tolerancia. Esto es la red de seguridad final: en vez de
    confiar en que la aritmética del layout fue correcta, se mide
    directamente si algo quedó encima de otra cosa — que es exactamente el
    tipo de bug (etiqueta larga tapando la fila de abajo) que motivó esta
    función. No previene el problema, pero garantiza que quede reportado en
    `warnings` en vez de descubrirse solo al abrir el archivo."""
    problems = []
    n = len(rects)
    for i in range(n):
        name_a, xa, ya, wa, ha = rects[i]
        for j in range(i + 1, n):
            name_b, xb, yb, wb, hb = rects[j]
            overlap_x = min(xa + wa, xb + wb) - max(xa, xb)
            overlap_y = min(ya + ha, yb + hb) - max(ya, yb)
            if overlap_x > tolerance_in and overlap_y > tolerance_in:
                problems.append(
                    f"Posible solape detectado entre {name_a} y {name_b} "
                    f"(~{overlap_x:.2f}in x {overlap_y:.2f}in) — revisa "
                    f"visualmente antes de entregar."
                )
    return problems


def _fit_node(text: str, node_type: str, max_height_in: float) -> dict:
    """Elige el tamaño de fuente más grande de FONT_SIZES_PT que haga caber
    el texto dentro de max_height_in. Si ni el tamaño mínimo cabe, se queda
    con el tamaño mínimo (se marcará como advertencia más arriba)."""
    chosen = None
    for font_pt in FONT_SIZES_PT:
        w, h, n_lines = _estimate_box(text, node_type, font_pt)
        if h <= max_height_in or font_pt == FONT_SIZES_PT[-1]:
            chosen = {"font_pt": font_pt, "w": w, "h": h, "n_lines": n_lines}
            if h <= max_height_in:
                break
    return chosen


def _layer_nodes(nodes: list[dict], edges: list[dict]) -> dict[str, int]:
    """Asigna a cada nodo un nivel (fila) = distancia más larga desde un
    nodo raíz (sin entradas), igual que rankdir=TB en Graphviz.

    Implementado como una pasada topológica (Kahn) en vez de un BFS simple
    con "visitado una vez": un nodo solo se procesa (y solo entonces se usa
    su nivel para calcular el de sus hijos) una vez que TODOS sus
    predecesores ya fueron procesados. La versión anterior marcaba un nodo
    como visitado en cuanto lo alcanzaba la PRIMERA rama que llegaba a él, y
    si esa rama resultaba más corta que otra rama paralela que llegaba
    después, el nivel quedaba congelado en el valor corto — un nodo con
    varios caminos de entrada de distinta longitud terminaba en la misma
    fila que su propio origen en vez de una fila más abajo. Ese fue
    exactamente el bug real detectado probando el algoritmo de hipoglucemia:
    un nodo de "persiste/escalar" quedó al lado de la decisión que lo
    origina en vez de debajo, forzando una conexión lateral artificial cuya
    etiqueta terminaba encima de la caja vecina.
    """
    ids = [n["id"] for n in nodes]
    id_set = set(ids)
    outgoing = defaultdict(list)
    indeg = {i: 0 for i in ids}
    for e in edges:
        src, dst = e.get("from"), e.get("to")
        if src not in id_set or dst not in id_set:
            continue
        outgoing[src].append(dst)
        indeg[dst] += 1

    level = {i: 0 for i in ids}
    queue = deque(i for i in ids if indeg[i] == 0)
    processed = set()
    while queue:
        node = queue.popleft()
        if node in processed:
            continue
        processed.add(node)
        for nxt in outgoing[node]:
            candidate = level[node] + 1
            if candidate > level[nxt]:
                level[nxt] = candidate
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    # Nodos en un ciclo o inalcanzables desde una raíz nunca llegan a
    # indeg==0 y quedan en su nivel por defecto (0) en vez de colgar el
    # layout — no debería pasar en un algoritmo clínico bien formado (debe
    # ser un DAG), pero es preferible degradar sin romper a lanzar una
    # excepción.
    return level


def build_algorithm_pptx(
    spec: dict,
    output_path: str,
    *,
    content_top_in: float | None = None,
    content_bottom_in: float | None = None,
    slide_height_in: float | None = None,
    show_title: bool | None = None,
    show_footer: bool | None = None,
) -> dict:
    """Construye un .pptx de una sola diapositiva con el algoritmo descrito
    en `spec` como formas nativas editables de PowerPoint.

    spec = {
        "nodes": [{"id", "text", "type": start_end|decision|action|alert}, ...],
        "edges": [{"from", "to", "label"?}, ...],
        "title": str (opcional),
        "source": str (opcional pero recomendado — cita de la guía/artículo),
    }

    Por defecto el diagrama ocupa toda la diapositiva (título arriba, pie de
    fuente abajo) y el alto de la diapositiva se calcula solo según el
    contenido. Cuando el diagrama se va a pegar DENTRO de una diapositiva que
    ya tiene su propio encabezado/pie (ej. la plantilla institucional de
    `plantilla-uninavarra`, con banda roja 0–1.4in y franja de cita
    7.05–7.45in), pasa `content_top_in`/`content_bottom_in` para que el
    algoritmo respete esa zona segura en vez de dibujar su propio título o
    citar la fuente encima de lo que ya trae la plantilla — usa también
    `show_title=False, show_footer=False` en ese caso (ver
    `references/pptx-nativo-guia.md`, sección "Insertar sobre una plantilla
    con encabezado/pie propios").

    Devuelve {"path": output_path, "warnings": [...]}. Revisar "warnings"
    antes de entregar el archivo: si no está vacío, el diagrama quedó
    apretado o con texto reducido al mínimo y conviene simplificarlo o
    usar Graphviz en su lugar.
    """
    nodes = spec["nodes"]
    edges = spec.get("edges", [])
    title = spec.get("title")
    source = spec.get("source")
    warnings: list[str] = []

    if not nodes:
        raise ValueError("spec['nodes'] no puede estar vacío")

    show_title = bool(title) if show_title is None else show_title
    show_footer = True if show_footer is None else show_footer
    fixed_height = slide_height_in is not None

    levels = _layer_nodes(nodes, edges)
    rows: dict[int, list[dict]] = defaultdict(list)
    for n in nodes:
        rows[levels[n["id"]]].append(n)
    n_rows = max(rows.keys()) + 1 if rows else 1

    # Espacio entre cada fila y la siguiente: por defecto ROW_GAP_IN, pero si
    # una arista DIRECTA (nivel L -> L+1) trae una etiqueta que se envuelve
    # a varias líneas, ese gap se agranda para que la etiqueta quepa sin
    # invadir la fila de arriba o de abajo — el bug reportado era justo esto:
    # una etiqueta larga con un gap fijo terminaba solapando la fila vecina.
    gap_heights: dict[int, float] = {}
    for e in edges:
        src_lvl = levels.get(e.get("from"))
        dst_lvl = levels.get(e.get("to"))
        label = e.get("label")
        if not label or src_lvl is None or dst_lvl is None or dst_lvl - src_lvl != 1:
            continue
        needed = _estimate_label(label)["h"] + 0.15  # margen para no tocar las cajas
        gap_heights[src_lvl] = max(gap_heights.get(src_lvl, ROW_GAP_IN), needed)

    def _gap_after(level: int) -> float:
        return gap_heights.get(level, ROW_GAP_IN)

    usable_w = SLIDE_W_IN - 2 * MARGIN_IN
    top_offset = content_top_in if content_top_in is not None else MARGIN_IN + (0.45 if show_title else 0.0)
    bottom_reserved = 0.05
    if content_bottom_in is None and show_footer:
        bottom_reserved = 0.35 if source else 0.05

    # Paso 1: tamaño "natural" de cada nodo (sin forzar una altura de fila
    # fija todavía) — un tope generoso solo evita que un texto absurdamente
    # largo dispare una caja gigante.
    fitted: dict[str, dict] = {n["id"]: _fit_node(n["text"], n["type"], max_height_in=2.6) for n in nodes}

    # Paso 2: el alto de cada fila = el nodo más alto de esa fila. El alto
    # total de la diapositiva se calcula a partir de esto (no al revés) —
    # así el lienzo se adapta al algoritmo en vez de aplastar el algoritmo
    # para que quepa en un lienzo fijo. EXCEPCIÓN: si se pasó
    # content_bottom_in/slide_height_in (zona segura de una plantilla ya
    # existente), el espacio disponible es fijo y es el CONTENIDO el que
    # debe ceder (reducir fuente) — no se puede agrandar una diapositiva
    # que ya existe.
    row_heights = {lvl: max(fitted[n["id"]]["h"] for n in row_nodes) for lvl, row_nodes in rows.items()}
    content_h = sum(row_heights.values()) + sum(_gap_after(l) for l in range(n_rows - 1))

    # content_bottom_in fija un límite DURO al espacio disponible (ej. justo
    # antes de la franja de cita de una plantilla institucional) — en ese
    # caso el contenido debe encogerse para caber, nunca al revés.
    if content_bottom_in is not None:
        max_content_h = content_bottom_in - top_offset
    else:
        max_content_h = SLIDE_H_MAX_IN - top_offset - MARGIN_IN - bottom_reserved

    font_scale = 1.0
    if content_h > max_content_h:
        font_scale = max(0.55, max_content_h / content_h)
        if font_scale <= 0.57:
            zona_msg = "la zona de contenido asignada" if content_bottom_in is not None else "una sola diapositiva"
            warnings.append(
                f"El algoritmo tiene {n_rows} niveles y no cabe cómodamente en "
                f"{zona_msg} ni reduciendo la fuente al mínimo — considera "
                f"dividirlo en 2 diagramas (ej. 'evaluación inicial' y "
                f"'manejo') o usar Graphviz, que no tiene este límite de "
                f"tamaño de lienzo."
            )
        # Reajustar con fuente más chica y recalcular alturas naturales.
        fitted = {
            n["id"]: _fit_node(n["text"], n["type"], max_height_in=2.6 * font_scale)
            for n in nodes
        }
        row_heights = {lvl: max(fitted[n["id"]]["h"] for n in row_nodes) for lvl, row_nodes in rows.items()}
        content_h = sum(row_heights.values()) + sum(_gap_after(l) for l in range(n_rows - 1))

    if fixed_height:
        slide_h = slide_height_in
    elif content_bottom_in is not None:
        slide_h = content_bottom_in + MARGIN_IN + bottom_reserved
    else:
        natural_h = top_offset + MARGIN_IN + bottom_reserved + content_h
        slide_h = min(max(natural_h, SLIDE_H_MIN_IN), SLIDE_H_MAX_IN)
        if slide_h > SLIDE_H_MIN_IN + 0.05:
            warnings.append(
                f"El diagrama necesitó una diapositiva más alta que el estándar "
                f"({slide_h:.1f}in vs. {SLIDE_H_MIN_IN}in) para que el texto sea "
                f"legible sin solapes. Si lo pegas en un mazo de tamaño estándar, "
                f"selecciona todas las formas y usa 'Escalar' para que quepan en "
                f"una diapositiva 16:9."
            )

    # Paso 3: si una fila no cabe en el ancho, escalar esa fila hacia abajo
    # (independiente del ajuste de alto de arriba — algunas filas anchas con
    # pocas líneas de texto pueden necesitar esto aunque la altura ya esté bien).
    positions: dict[str, dict] = {}
    for level, row_nodes in rows.items():
        total_w = sum(fitted[n["id"]]["w"] for n in row_nodes) + COL_GAP_IN * (len(row_nodes) - 1)
        scale = 1.0
        if total_w > usable_w:
            scale = usable_w / total_w
            if scale < 0.55:
                warnings.append(
                    f"La fila con {len(row_nodes)} nodo(s) en el nivel {level} "
                    f"es demasiado ancha incluso reducida al mínimo — "
                    f"considera reorganizar el algoritmo (menos ramas por "
                    f"nivel) o usar Graphviz para este diagrama."
                )
                scale = 0.55
            total_w *= scale

        x = MARGIN_IN + (usable_w - total_w) / 2
        y = top_offset + sum(row_heights[lvl] for lvl in range(level)) + sum(_gap_after(l) for l in range(level))
        row_h = row_heights[level]
        for n in row_nodes:
            f = fitted[n["id"]]
            w = f["w"] * scale
            h = f["h"] * scale
            positions[n["id"]] = {
                # centrar verticalmente dentro del alto de fila si el nodo es
                # más bajo que el más alto de su fila (ej. óvalo junto a rombo)
                "x": x, "y": y + (row_h - h) / 2, "w": w, "h": h,
                "font_pt": max(8, round(f["font_pt"] * scale)) if scale < 1.0 else f["font_pt"],
                "type": n["type"], "text": n["text"],
            }
            x += w + COL_GAP_IN * scale

    # QA automático: registrar el rectángulo (en pulgadas) de cada elemento
    # visual a medida que se coloca, para poder verificar al final que nada
    # quedó solapado — en vez de confiar ciegamente en la aritmética del
    # layout (así se hubiera detectado solo el bug de la etiqueta larga que
    # reportó el usuario, sin depender de que alguien lo notara a simple
    # vista). Ver `_check_overlaps` más abajo.
    rects: list[tuple[str, float, float, float, float]] = [
        (f"nodo '{node_id}'", p["x"], p["y"], p["w"], p["h"]) for node_id, p in positions.items()
    ]

    # --- Construcción del .pptx ---
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W_IN)
    prs.slide_height = Inches(slide_h)
    # La plantilla base de python-pptx trae <p:sldSz type="screen4x3">; al
    # cambiar cx/cy a un tamaño no estándar (alto dinámico) ese atributo
    # queda inconsistente con las dimensiones reales. Quitarlo evita abrir
    # el archivo con un tamaño de diapositiva "reportado" que no coincide
    # con el real, causa conocida de que PowerPoint marque el archivo como
    # dañado y ofrezca "reparar" al abrirlo.
    sld_sz = prs.element.find(qn("p:sldSz"))
    if sld_sz is not None and "type" in sld_sz.attrib:
        del sld_sz.attrib["type"]
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # layout en blanco

    if title and show_title:
        tb = slide.shapes.add_textbox(Inches(MARGIN_IN), Inches(0.1), Inches(usable_w), Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = _hex("212121")

    shape_map = {}
    for node_id, pos in positions.items():
        style = NODE_STYLES[pos["type"]]
        shp = slide.shapes.add_shape(
            style["shape"], Inches(pos["x"]), Inches(pos["y"]), Inches(pos["w"]), Inches(pos["h"])
        )
        shp.fill.solid()
        shp.fill.fore_color.rgb = _hex(style["fill"])
        shp.line.color.rgb = _hex(style["fill"])
        shp.shadow.inherit = False
        tf = shp.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.05)
        tf.margin_right = Inches(0.05)
        tf.margin_top = Inches(0.03)
        tf.margin_bottom = Inches(0.03)
        lines = pos["text"].split("\n")
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line
            p.alignment = PP_ALIGN.CENTER
            p.font.size = Pt(pos["font_pt"])
            p.font.color.rgb = _hex(style["font"])
            p.font.name = "Calibri"
        shape_map[node_id] = shp

    # Conectores (flechas) — elbow para que se vean como flujograma, con la
    # etiqueta ("Si"/"No"/umbral) como un textbox pequeño cerca del punto
    # medio, igual que las etiquetas de arista de Graphviz.
    #
    # Caso especial — arista "salteada": cuando el destino está dos o más
    # niveles por debajo del origen (ej. una rama "No" que va directo al
    # cierre del algoritmo, saltándose los pasos intermedios), una línea
    # recta centro-a-centro pasaría visualmente ENCIMA de las cajas
    # intermedias — confuso y, en PowerPoint, dos formas superpuestas
    # difíciles de separar luego. En ese caso se enruta por un "carril"
    # lateral (derecha) que rodea las cajas intermedias, como haría un
    # diagramador a mano.
    right_edge_of_diagram = max((p["x"] + p["w"] for p in positions.values()), default=usable_w + MARGIN_IN)
    lane_base = min(right_edge_of_diagram + 0.35, SLIDE_W_IN - MARGIN_IN - 0.2)
    skip_lane_index = 0

    for e in edges:
        src, dst = shape_map.get(e["from"]), shape_map.get(e["to"])
        if src is None or dst is None:
            warnings.append(f"Arista ignorada: nodo no encontrado en {e}")
            continue

        src_level = levels[e["from"]]
        dst_level = levels[e["to"]]
        label = e.get("label")
        is_skip = dst_level - src_level >= 2

        if is_skip:
            # Ruta en 3 tramos: sale por la derecha de src, baja por un
            # carril lateral, entra por la derecha de dst.
            lane_x = Inches(lane_base + skip_lane_index * 0.32)
            skip_lane_index += 1
            x1 = src.left + src.width
            y1 = src.top + src.height // 2
            x2 = dst.left + dst.width
            y2 = dst.top + dst.height // 2
            fb = slide.shapes.build_freeform(x1, y1, scale=1.0)
            fb.add_line_segments([(lane_x, y1), (lane_x, y2), (x2, y2)], close=False)
            connector = fb.convert_to_shape()
            connector.fill.background()
            connector.shadow.inherit = False
            label_pos = (lane_x, Emu(int((y1 + y2) / 2)))
        else:
            x1 = src.left + src.width // 2
            y1 = src.top + src.height
            x2 = dst.left + dst.width // 2
            y2 = dst.top
            if y2 < y1:
                # el destino está en el mismo nivel o arriba (rama lateral
                # corta) — conectar desde el lado en vez de desde abajo. OJO:
                # x2 también debe pasar a ser el BORDE lateral de dst (no su
                # centro, que seguía puesto desde el cálculo top-a-top de
                # arriba) — si no, la flecha entra hasta el medio de la caja
                # destino y la etiqueta (que se centra en el punto medio de
                # x1/x2) termina cayendo encima de esa caja en vez de en el
                # espacio vacío entre ambas.
                y1 = src.top + src.height // 2
                y2 = dst.top + dst.height // 2
                if dst.left > src.left:
                    x1 = src.left + src.width
                    x2 = dst.left
                else:
                    x1 = src.left
                    x2 = dst.left + dst.width
            connector = slide.shapes.add_connector(MSO_CONNECTOR.ELBOW, x1, y1, x2, y2)
            label_pos = (Emu(int((x1 + x2) / 2)), Emu(int((y1 + y2) / 2)))

        connector.line.color.rgb = _hex(EDGE_COLOR)
        connector.line.width = Pt(1.25)
        line = connector.line._get_or_add_ln()
        arrow = line.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
        line.append(arrow)

        if label:
            # Las etiquetas de arista deben ser cortas ("Sí"/"No"/un umbral
            # breve) — igual que en la convención de Graphviz. El ancho/alto
            # se calculan a partir del texto real (ver _estimate_label) para
            # que una etiqueta más larga se envuelva en vez de desbordarse; y
            # el espacio entre filas ya se reservó para esa altura (ver
            # _row_gaps más arriba), así que no debería solapar la fila
            # siguiente aunque ocupe varias líneas.
            mx, my = label_pos
            lbl_font_pt = 10.5
            lbl_est = _estimate_label(label, lbl_font_pt)
            if len(lbl_est["lines"]) > 1:
                warnings.append(
                    f"La etiqueta de arista '{label[:40]}...' es larga y se "
                    f"envolvió en varias líneas — las etiquetas de arista "
                    f"deben ser cortas (ej. 'Sí'/'No'/un umbral breve); si es "
                    f"una aclaración extensa, considera ponerla dentro del "
                    f"texto del nodo en vez de en la arista."
                )
            lbl_w, lbl_h = Inches(lbl_est["w"]), Inches(lbl_est["h"])
            lbl = slide.shapes.add_textbox(Emu(int(mx - lbl_w / 2)), Emu(int(my - lbl_h / 2)), lbl_w, lbl_h)
            lbl.fill.solid()
            lbl.fill.fore_color.rgb = _hex("FFFFFF")
            lbl.line.fill.background()
            ltf = lbl.text_frame
            ltf.word_wrap = True
            ltf.margin_left = ltf.margin_right = Emu(0)
            ltf.margin_top = ltf.margin_bottom = Emu(0)
            for i, line_text in enumerate(lbl_est["lines"]):
                p = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
                p.text = line_text
                p.alignment = PP_ALIGN.CENTER
                p.font.size = Pt(lbl_font_pt)
                p.font.italic = True
                p.font.color.rgb = _hex(EDGE_COLOR)

            rects.append((
                f"etiqueta '{label[:25]}'",
                (mx - lbl_w / 2) / 914400, (my - lbl_h / 2) / 914400,
                lbl_w / 914400, lbl_h / 914400,
            ))

    # Pie con la fuente — igual convención que el .dot: nunca omitir en
    # silencio, marcar en rojo si falta (coherente con el filtro de realidad).
    # Si show_footer=False (ej. la plantilla destino ya trae su propia franja
    # de cita, como plantilla-uninavarra), esta skill NO dibuja un segundo
    # pie encima del que ya existe — pero sigue avisando si falta la fuente,
    # porque esa cita debe ir en algún lado (la franja de la plantilla).
    if not source:
        warnings.append(
            "No se indicó 'source'. " + (
                "El pie del diagrama quedó marcado como [No verificado]."
                if show_footer else
                "Como show_footer=False, asegúrate de citar la fuente en la "
                "franja de cita de la plantilla destino — esta skill no la "
                "generó aquí."
            )
        )
    if show_footer:
        src_text = f"Fuente: {source}" if source else "Fuente: [No verificado] — dato sin cita confirmada"
        src_color = SOURCE_COLOR if source else SOURCE_MISSING_COLOR
        fb = slide.shapes.add_textbox(Inches(MARGIN_IN), Inches(slide_h - MARGIN_IN - 0.05), Inches(usable_w), Inches(0.3))
        ftf = fb.text_frame
        p = ftf.paragraphs[0]
        p.text = src_text
        p.font.size = Pt(9)
        p.font.color.rgb = _hex(src_color)

    # QA final: verificar por geometría (no por confianza en el layout) que
    # ningún nodo ni etiqueta quedó encima de otro. La franja de fuente no
    # se incluye a propósito (su y ya está fuera del área de contenido por
    # diseño, y solaparía con la última fila en diagramas muy altos sin ser
    # un bug real de layout).
    warnings.extend(_check_overlaps(rects))

    prs.save(output_path)
    return {"path": output_path, "warnings": warnings}


if __name__ == "__main__":
    # Auto-demo si se ejecuta directamente, útil para probar el layout rápido.
    demo_spec = {
        "nodes": [
            {"id": "inicio", "text": "Sospecha de HTA resistente", "type": "start_end"},
            {"id": "d1", "text": "PA >=130/80 con 3 farmacos a dosis maxima\nincluyendo diuretico tipo tiazida?", "type": "decision"},
            {"id": "a1", "text": "Confirmar con MAPA/AMPA y descartar\npseudorresistencia (tecnica, adherencia)", "type": "action"},
            {"id": "alarma1", "text": "Descartar causas secundarias:\nSAHOS, hiperaldosteronismo primario,\nenfermedad renovascular", "type": "alert"},
            {"id": "fin", "text": "HTA resistente confirmada:\nagregar espironolactona (4o farmaco)", "type": "start_end"},
        ],
        "edges": [
            {"from": "inicio", "to": "d1"},
            {"from": "d1", "to": "a1", "label": "Si"},
            {"from": "d1", "to": "fin", "label": "No"},
            {"from": "a1", "to": "alarma1"},
            {"from": "alarma1", "to": "fin"},
        ],
        "title": "Abordaje de hipertensión arterial resistente",
        "source": "ESH 2023 / ACC-AHA 2017 — [Evidencia]",
    }
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "demo_algoritmo.pptx"
    result = build_algorithm_pptx(demo_spec, out)
    print(result)
