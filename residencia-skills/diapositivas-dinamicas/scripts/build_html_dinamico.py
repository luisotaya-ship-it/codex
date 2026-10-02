#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_html_dinamico.py — Genera el gemelo HTML animado/3D de una presentación
(reveal.js) a partir de un JSON estructurado con el mismo contenido que ya se
redactó para el .pptx en presentaciones-cientificas.

Este es el vehículo principal para "dinamismo real": aquí SÍ hay animación de
aparición automática y en cascada para cada bullet/tarjeta/paso de diagrama
(disparada por la clase ".present" que reveal.js pone/quita sola al navegar —
no depende de que el presentador avance fragmentos a mano, así que nunca se ve
una diapositiva "vacía"), gráficos que se dibujan al entrar a la diapositiva
(Chart.js), transiciones con profundidad 3D real (perspective + rotateY/rotateX
de CSS, o las transiciones 3D nativas de reveal.js), iconos 3D flotantes en CSS
puro para portada/cierre, y un brillo ambiental de baja intensidad detrás de
TODAS las diapositivas (no solo el preset "congreso") para que ninguna se sienta
plana incluso sin interacción del usuario. A diferencia del .pptx, cada línea de
JS/CSS generada aquí se puede leer y verificar antes de entregarla — por eso el
.pptx se queda con las transiciones seguras (ver pptx_dinamizar.py) y el HTML
carga con el resto del dinamismo.

Revelado progresivo (campo "revelado" por diapositiva, ver
references/esquema-json.md): además de la cascada automática, cualquier
diapositiva puede pedir que sus viñetas/imágenes aparezcan una a la vez con
fragmentos REALES de reveal.js ("progresivo" = se acumulan, "reemplazo" = la
nueva atenúa a la anterior) — esto es lo que permite sincronizar cada imagen
o punto con el momento exacto en que el presentador habla de él, y evitar que
una diapositiva con varias fotos o muchas viñetas se sienta "cargada" desde
el primer segundo. `advertencias_densidad()` revisa cada diapositiva al
construir el HTML y avisa por consola si algo va a verse sobrecargado incluso
con revelado progresivo — no es solo una regla de estilo en un .md, se
calcula sobre el contenido real.

Uso:
    python3 build_html_dinamico.py contenido.json salida.html --preset sobrio
    python3 build_html_dinamico.py contenido.json salida.html --preset congreso
    python3 build_html_dinamico.py contenido.json salida.html --preset marca \
        --color-primario "#0B3D91" --color-acento "#00A19A" --logo ruta/logo.png

Ver references/esquema-json.md para el formato exacto de contenido.json y
references/presets-estilo.md para el criterio de cada preset.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

CDNJS = "https://cdnjs.cloudflare.com/ajax/libs"
REVEAL_VERSION = "4.6.1"
CHARTJS_VERSION = "4.4.0"

# ---------------------------------------------------------------------------
# Presets — deben quedar visualmente coherentes con PRESETS de
# pptx_dinamizar.py (misma paleta, mismo "nivel de atrevimiento") para que el
# .pptx y el .html se sientan como la misma presentación, no como dos decks
# distintos.
# ---------------------------------------------------------------------------

PRESETS = {
    "sobrio": {
        "reveal_transition": "slide",
        "reveal_theme_bg": "#0f1b2d",
        "color_fondo": "#0f1b2d",
        "color_panel": "#16273f",
        "color_texto": "#eef3f8",
        "color_primario": "#3aa1ff",
        "color_acento": "#38d6b7",
        "color_alerta": "#ff8a5c",
        "fondo_parallax": False,
        # Antes en 0.0 ("solo si el usuario lo pide"): en la práctica eso
        # dejaba la portada/cierre sin ningún acento con movimiento y era la
        # diapositiva que más se veía "muerta" a primer vistazo. 0.55 mantiene
        # un icono discreto (no domina la diapositiva) pero SÍ hay movimiento
        # incluso en el preset más conservador — ver nota de diseño en
        # references/presets-estilo.md.
        "icono_3d_intensidad": 0.55,
        "fuente": "'Segoe UI', system-ui, sans-serif",
    },
    "congreso": {
        "reveal_transition": "concave",
        "reveal_theme_bg": "#0a0a12",
        "color_fondo": "#0a0a12",
        "color_panel": "#191934",
        "color_texto": "#f5f4ff",
        "color_primario": "#7c5cff",
        "color_acento": "#00e0c6",
        "color_alerta": "#ff5c8a",
        "fondo_parallax": True,
        "icono_3d_intensidad": 1.0,
        "fuente": "'Poppins', 'Segoe UI', system-ui, sans-serif",
    },
    "marca": {
        "reveal_transition": "fade",
        "reveal_theme_bg": "#ffffff",
        "color_fondo": "#ffffff",
        "color_panel": "#f4f6f9",
        "color_texto": "#16232f",
        "color_primario": "#0B3D91",
        "color_acento": "#00A19A",
        "color_alerta": "#C0392B",
        "fondo_parallax": False,
        "icono_3d_intensidad": 0.3,
        "fuente": "'Segoe UI', system-ui, sans-serif",
    },
    "ficha_clinica": {
        # Estilo "ficha de guía / infografía clínica de un solo vistazo": fondo
        # claro, tarjeta blanca con sombra suave, acentos de color reservados
        # para semáforo de riesgo (verde/ámbar/naranja/rojo) — inspirado en un
        # ejemplo real que el usuario mostró (ficha AHA/ACC de presión arterial).
        # Pensado para diapositivas tipo "resumen de guía", no para todo el deck.
        "reveal_transition": "fade",
        "reveal_theme_bg": "#eef1f5",
        "color_fondo": "#eef1f5",
        "color_panel": "#ffffff",
        "color_texto": "#1a2433",
        "color_primario": "#14213d",
        "color_acento": "#2563eb",
        "color_alerta": "#c0392b",
        "fondo_parallax": False,
        # Igual que "sobrio": la ficha en sí ya es la protagonista, pero si el
        # deck incluye portada/cierre con este preset no deben quedar inertes.
        "icono_3d_intensidad": 0.25,
        "fuente": "'Segoe UI', system-ui, sans-serif",
    },
}

ICONOS_3D = {
    "corazon": "❤",
    "rinon": "\U0001FAD8",
    "pulmon": "\U0001FAC1",
    "cerebro": "\U0001F9E0",
    "molecula": "⚛",
    "generico": "✦",
}

# ---------------------------------------------------------------------------
# Revelado progresivo — clases REALES de fragmento de reveal.js (documentadas
# en revealjs.com/fragments), no inventadas. Se usan cuando el usuario quiere
# que el contenido aparezca al ritmo de lo que va diciendo, en vez de todo de
# golpe al entrar a la diapositiva:
#   - "cascada" (default): comportamiento previo, todo entra solo y a la vez
#     (con pequeño escalonado CSS) apenas se activa la diapositiva. Bueno para
#     diapositivas con poco contenido donde no vale la pena pedir clics.
#   - "progresivo": cada viñeta/imagen es un fragmento real de reveal.js
#     (fade-up) — el presentador avanza con la flecha y cada elemento se suma
#     a los anteriores. Reduce lo que el público ve de golpe sin ocultar nada
#     para siempre.
#   - "reemplazo": cada viñeta/imagen nueva hace que la anterior se atenúe
#     (fade-in-then-semi-out) — para cuando mostrar 3-4 elementos a la vez se
#     sentiría saturado (p.ej. comparar 3 fotos clínicas una por una).
# ---------------------------------------------------------------------------
FRAGMENT_CLASS = {
    "progresivo": "fade-up",
    "reemplazo": "fade-in-then-semi-out",
}

# Las imágenes en modo "reemplazo" se apilan una encima de otra (mismo
# espacio, ver ".galeria-reemplazo" en el CSS) para que la nueva ocupe
# exactamente el lugar de la anterior. Con "fade-in-then-semi-out" (la que
# usan las viñetas) la foto anterior se queda al ~40% de opacidad DEBAJO de
# la nueva — con fotos reales eso se ve como un fantasma superpuesto, no como
# un reemplazo limpio (se confirmó el problema en QA visual con Playwright:
# las dos imágenes se leían encimadas). "fade-in-then-out" oculta del todo la
# anterior antes de que la nueva termine de aparecer, que es lo que de verdad
# se lee como "ahora esta, ya no la de antes" en una pila de imágenes.
IMG_FRAGMENT_CLASS = {
    "progresivo": "fade-up",
    "reemplazo": "fade-in-then-out",
}


def esc(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def render_bullets(bullets: list[str], revelado: str = "cascada") -> str:
    # Nota de diseño (por qué "cascada" nunca depende de fragmentos): si cada
    # <li> exigiera una tecla adicional por defecto, cualquiera que mire la
    # diapositiva sin avanzar fragmentos (una captura de pantalla, un vistazo
    # rápido, un video grabado saltando diapositivas) vería título y NADA de
    # contenido debajo — indistinguible de "esto está roto". Por eso "cascada"
    # sigue siendo el default: las viñetas entran solas apenas se activa la
    # diapositiva (".present .bullets li" en el CSS).
    #
    # "progresivo"/"reemplazo" SÍ usan fragmentos reales de reveal.js a
    # propósito — el usuario pidió que el material aparezca al ritmo de la
    # charla (una viñeta mientras se habla de ella, no todas antes de
    # empezar), y eso solo lo puede activar quien presenta, con las flechas.
    if revelado in FRAGMENT_CLASS:
        clase = FRAGMENT_CLASS[revelado]
        items = "\n".join(
            f'<li class="fragment {clase}" data-fragment-index="{i}">{esc(b)}</li>'
            for i, b in enumerate(bullets or [])
        )
    else:
        items = "\n".join(
            f'<li style="--i:{i}">{esc(b)}</li>' for i, b in enumerate(bullets or [])
        )
    return f'<ul class="bullets">{items}</ul>'


def render_imagenes(imagenes: list[dict], revelado: str = "progresivo") -> str:
    """Imágenes de apoyo que aparecen UNA A LA VEZ (fragmentos reales de
    reveal.js) en vez de todas juntas al entrar a la diapositiva — esto es lo
    que evita que una diapositiva con 3-4 fotos se sienta "cargada" incluso
    con poco texto: el público solo ve la imagen de la que se está hablando
    en ese momento, no una pared de imágenes desde el primer segundo.

    Cada imagen puede traer "bullet_index" para sincronizarse con la viñeta
    correspondiente (mismo data-fragment-index = aparecen juntas con el mismo
    clic) — si no se especifica, se numeran en el orden de la lista."""
    if not imagenes:
        return ""
    clase = IMG_FRAGMENT_CLASS.get(revelado, "fade-up")
    contenedor_clase = "galeria-reemplazo" if revelado == "reemplazo" else "galeria-progresiva"
    items = []
    for i, img in enumerate(imagenes):
        idx = img.get("bullet_index", i)
        pie = f'<figcaption>{esc(img.get("pie", ""))}</figcaption>' if img.get("pie") else ""
        items.append(
            f'<figure class="fragment {clase} imagen-apoyo" data-fragment-index="{idx}">'
            f'<img src="{esc(img.get("src", ""))}" alt="{esc(img.get("alt", ""))}" loading="lazy">'
            f"{pie}</figure>"
        )
    return f'<div class="{contenedor_clase}">{"".join(items)}</div>'


def advertencias_densidad(slide: dict) -> list[str]:
    """Chequeo real de carga visual por diapositiva — no es un límite que solo
    se documenta en un .md y se espera que se recuerde: se calcula sobre el
    contenido real de cada diapositiva y se imprime al construir el HTML, para
    que "no se vea tan cargada" sea verificable y no una promesa de buena fe."""
    avisos = []
    n_bullets = len(slide.get("bullets", []) or [])
    n_imgs = len(slide.get("imagenes", []) or [])
    revelado = slide.get("revelado", "cascada")
    titulo = slide.get("titulo") or "(sin título)"
    if n_bullets > 4 and revelado == "cascada":
        avisos.append(
            f'"{titulo}": {n_bullets} viñetas entran todas de golpe (revelado '
            f'"cascada"). Con más de 4, usa revelado:"progresivo" para que el '
            f"presentador las muestre una a una, o divide la diapositiva."
        )
    if n_imgs > 1 and revelado == "cascada":
        avisos.append(
            f'"{titulo}": {n_imgs} imágenes con revelado "cascada" — aparecen '
            f'todas juntas al entrar. Con más de 1 imagen usa revelado:'
            f'"progresivo" o "reemplazo" para que aparezcan una a la vez.'
        )
    if n_bullets + n_imgs * 2 > 8:
        avisos.append(
            f'"{titulo}": densidad total alta ({n_bullets} viñetas + {n_imgs} '
            f"imágenes) incluso con revelado progresivo — evalúa dividir el "
            f"contenido en 2 diapositivas en vez de una sola muy larga."
        )
    return avisos


def render_icono_3d(nombre: str, intensidad: float) -> str:
    if not nombre or intensidad <= 0:
        return ""
    glifo = ICONOS_3D.get(nombre, ICONOS_3D["generico"])
    return f'''
    <div class="icono3d-wrap" style="--i3d:{intensidad}">
      <div class="icono3d-cubo">
        <div class="cara cara-f">{glifo}</div>
        <div class="cara cara-b">{glifo}</div>
        <div class="cara cara-r">{glifo}</div>
        <div class="cara cara-l">{glifo}</div>
      </div>
    </div>'''


def render_diagrama(pasos: list[str], zoom_progresivo: bool = False) -> str:
    # Todas las cajas entran solas en cascada apenas se activa la diapositiva
    # (igual que render_bullets, mismo motivo: nunca depender de que alguien
    # sepa que debe avanzar un fragmento para ver el contenido).
    #
    # `zoom_progresivo` añade algo distinto encima, inspirado en el efecto
    # Zoom de sección de PowerPoint (ver references/tecnicas-nativas.md):
    # marca cada caja como fragmento de reveal.js SOLO para que, al avanzar
    # con las flechas del teclado, la caja "actual" se agrande y resalte
    # mientras las demás se atenúan — una sensación de "acercarse al paso
    # vigente" sin tocar el contenido en sí, que sigue visible desde el
    # principio (ver ".current-fragment" en el CSS: es la clase que reveal.js
    # aplica sola al fragmento que se está mostrando en ese momento, no algo
    # que haya que simular a mano). No es Zoom real de PowerPoint —eso vive en
    # un mecanismo OOXML propio que no se automatiza aquí—, es una
    # aproximación honesta hecha con herramientas que sí se pueden verificar.
    if not pasos:
        return ""
    cajas = []
    for i, paso in enumerate(pasos):
        clase_paso = "paso fragment" if zoom_progresivo else "paso"
        indice_attr = f' data-fragment-index="{i}"' if zoom_progresivo else ""
        cajas.append(f'<div class="{clase_paso}" style="--i:{i}"{indice_attr} data-paso="{i}">{esc(paso)}</div>')
        if i < len(pasos) - 1:
            cajas.append(f'<div class="flecha" style="--i:{i}" aria-hidden="true">&#10132;</div>')
    clase_contenedor = "diagrama-flujo diagrama-zoom" if zoom_progresivo else "diagrama-flujo"
    return f'<div class="{clase_contenedor}">{"".join(cajas)}</div>'


def render_escala(escala: dict) -> str:
    """Barra de gradiente con umbrales (ej. categorías de presión arterial)."""
    if not escala:
        return ""
    segmentos = escala.get("segmentos", [])
    minimo = escala.get("min", 0)
    maximo = escala.get("max", 100)
    rango = max(maximo - minimo, 1)
    partes = []
    anterior = minimo
    for seg in segmentos:
        hasta = seg.get("hasta", maximo)
        ancho = max(hasta - anterior, 0) / rango * 100
        partes.append(f'<div style="flex:{ancho};background:{esc(seg.get("color", "#999"))}"></div>')
        anterior = hasta
    marcas_html = "".join(f'<span>{esc(m)}</span>' for m in escala.get("marcas", []))
    return f'''
    <div class="escala-gradiente">
      <div class="escala-barra escala-barra-animada">{"".join(partes)}</div>
      <div class="escala-marcas">{marcas_html}</div>
    </div>'''


def render_tabla_clinica(tabla: dict) -> str:
    if not tabla:
        return ""
    columnas = tabla.get("columnas", [])
    filas = tabla.get("filas", [])
    head = "".join(f"<th>{esc(c)}</th>" for c in columnas)
    filas_html = []
    for fila in filas:
        color = fila.get("color", "#999")
        valores = fila.get("valores", [])
        primero, *resto = valores or [""]
        celdas_resto = "".join(f"<td>{esc(v)}</td>" for v in resto)
        filas_html.append(
            f'<tr><td><span class="punto-color" style="background:{esc(color)}"></span>{esc(primero)}</td>{celdas_resto}</tr>'
        )
    nota = f'<p class="tabla-nota">{esc(tabla.get("nota", ""))}</p>' if tabla.get("nota") else ""
    return f'''
    <table class="tabla-clinica">
      <thead><tr>{head}</tr></thead>
      <tbody>{"".join(filas_html)}</tbody>
    </table>
    {nota}'''


def render_tarjetas(tarjetas: list[dict]) -> str:
    if not tarjetas:
        return ""
    items = []
    for i, t in enumerate(tarjetas):
        color_key = t.get("color", "primario")
        color_var = {"primario": "var(--color-primario)", "alerta": "var(--color-alerta)", "acento": "var(--color-acento)"}.get(color_key, color_key)
        valor_html = f'<div class="tarjeta-valor">{esc(t.get("valor"))}</div>' if t.get("valor") else ""
        items.append(f'''
        <div class="tarjeta-ficha" style="border-left-color:{color_var};--i:{i}">
          <div class="tarjeta-titulo" style="color:{color_var}">{esc(t.get("titulo"))}</div>
          {valor_html}
          <p>{esc(t.get("descripcion"))}</p>
        </div>''')
    return f'<div class="tarjetas-laterales">{"".join(items)}</div>'


def render_pildoras(pildoras: dict) -> str:
    if not pildoras:
        return ""
    items = "".join(
        f'<span class="pildora" style="--i:{i}">{esc(item)}</span>'
        for i, item in enumerate(pildoras.get("items", []))
    )
    return f'''
    <div class="pildoras-banda">
      <div class="pildoras-titulo">{esc(pildoras.get("titulo"))}</div>
      <div class="pildoras-lista">{items}</div>
    </div>'''


def render_ficha(slide: dict) -> str:
    """Diapositiva tipo 'ficha de guía' / infografía clínica de un vistazo:
    eyebrow + badge, título, divisor, barra de escala, tabla con semáforo de
    color, tarjetas laterales de acento y franja de píldoras — ver
    references/presets-estilo.md § ficha_clinica para cuándo usar este tipo."""
    eyebrow = slide.get("eyebrow", "")
    badge = slide.get("badge", "")
    badge_nota = slide.get("badge_nota", "")
    titulo = slide.get("titulo", "")
    subtitulo = slide.get("subtitulo", "")
    nota_metodo = slide.get("nota_metodo", "")

    badge_html = ""
    if badge:
        badge_html = f'''
        <div class="ficha-badge-wrap">
          <span class="ficha-badge">{esc(badge)}</span>
          {f'<div class="ficha-badge-nota">{esc(badge_nota)}</div>' if badge_nota else ''}
        </div>'''

    return f'''
    <div class="ficha-card">
      <div class="ficha-encabezado">
        <div>
          <div class="ficha-eyebrow">{esc(eyebrow)}</div>
          <h1 class="ficha-titulo">{esc(titulo)}</h1>
          <p class="ficha-subtitulo">{esc(subtitulo)}</p>
        </div>
        {badge_html}
      </div>
      <div class="ficha-divisor"></div>
      {f'<p class="ficha-nota-metodo">{esc(nota_metodo)}</p>' if nota_metodo else ''}
      {render_escala(slide.get("escala", {}))}
      <div class="ficha-cuerpo">
        {render_tabla_clinica(slide.get("tabla", {}))}
        {render_tarjetas(slide.get("tarjetas", []))}
      </div>
      {render_pildoras(slide.get("pildoras", {}))}
    </div>'''


def render_indice(secciones: list[dict]) -> str:
    """Menú de navegación tipo acordeón — equivalente en HTML del menú de
    botones nativo de pptx_botones_helper.py (mismo propósito: índice
    clicable de un deck largo, cada sección se expande con su resumen).

    Implementado con <details>/<summary> nativos de HTML en vez de JS a
    medida: es accesible por teclado de fábrica, funciona sin una sola línea
    de JavaScript adicional, y no puede caer en el bug de "contenido
    invisible sin saberlo" — el título de cada sección (<summary>) siempre
    está visible; solo el detalle se pliega, que es exactamente el
    comportamiento esperado de un acordeón (a diferencia de una viñeta o un
    paso de diagrama, que sí deben verse siempre)."""
    if not secciones:
        return ""
    items = []
    for i, sec in enumerate(secciones):
        titulo_sec = esc(sec.get("titulo", ""))
        resumen = esc(sec.get("resumen", ""))
        bullets_html = render_bullets(sec.get("bullets", [])) if sec.get("bullets") else ""
        items.append(f'''
        <details class="acordeon-item" style="--i:{i}">
          <summary>{titulo_sec}</summary>
          <div class="acordeon-contenido">
            {f'<p>{resumen}</p>' if resumen else ''}
            {bullets_html}
          </div>
        </details>''')
    return f'<div class="acordeon">{"".join(items)}</div>'


def render_grafico(idx: int, grafico: dict) -> tuple[str, str]:
    """Devuelve (html_canvas, js_config) para una diapositiva de gráfico."""
    canvas_id = f"chart-{idx}"
    html_block = f'<div class="grafico-wrap"><canvas id="{canvas_id}"></canvas></div>'
    tipo = grafico.get("tipo", "bar")
    labels = grafico.get("labels", [])
    series = grafico.get("series", [])
    js_config = json.dumps(
        {
            "id": canvas_id,
            "type": tipo,
            "labels": labels,
            "series": series,
        },
        ensure_ascii=False,
    )
    return html_block, js_config


def render_slide(idx: int, slide: dict, preset: dict) -> tuple[str, str]:
    """Devuelve (html_section, js_chart_config_o_'')."""
    tipo = slide.get("tipo", "contenido")
    titulo = slide.get("titulo", "")
    subtitulo = slide.get("subtitulo", "")
    notas = slide.get("guion", "")
    take_home = slide.get("take_home", "")
    nota_pie = slide.get("nota_pie", "")
    js_chart = ""

    clases_section = [f"slide-{tipo}"]
    cuerpo = ""

    # Transición congruente con el tipo de contenido: en vez de aplicar la
    # misma transición del preset a las 30 diapositivas por igual, la
    # diapositiva de "impacto" (la cifra/frase de máximo efecto, 2-3 por
    # deck) recibe una transición propia más contundente — "zoom" es una
    # transición NATIVA de reveal.js (data-transition, ver revealjs.com/
    # transitions), no CSS inventado. El resto se queda con la transición del
    # preset a propósito: alternar transición diapositiva por diapositiva se
    # siente errático, no "congruente con la charla" — la consistencia
    # también transmite profesionalismo.
    transicion_attr = ' data-transition="zoom"' if tipo == "impacto" else ""

    if tipo == "portada":
        icono = render_icono_3d(slide.get("icono_3d", "generico"), preset["icono_3d_intensidad"])
        cuerpo = f'''
          <div class="portada-contenido">
            <h1 class="entra-arriba" style="--i:0">{esc(titulo)}</h1>
            <h3 class="entra-arriba" style="--i:1">{esc(subtitulo)}</h3>
          </div>
          {icono}'''
    elif tipo == "impacto":
        clases_section.append("fondo-oscuro-forzado")
        cuerpo = f'<div class="impacto-contenido"><p class="impacto-pop">{esc(titulo)}</p></div>'
    elif tipo == "grafico":
        canvas_html, js_chart = render_grafico(idx, slide.get("grafico", {}))
        cuerpo = f'''
          <h2>{esc(titulo)}</h2>
          <div class="layout-70-30">
            {canvas_html}
            <div class="panel-lateral">{render_bullets(slide.get("bullets", []))}</div>
          </div>'''
    elif tipo == "diagrama":
        diagrama_cfg = slide.get("diagrama", {})
        cuerpo = f'''
          <h2>{esc(titulo)}</h2>
          {render_diagrama(diagrama_cfg.get("pasos", []), zoom_progresivo=bool(diagrama_cfg.get("zoom_progresivo")))}'''
    elif tipo == "ficha":
        cuerpo = render_ficha(slide)
    elif tipo == "indice":
        cuerpo = f'''
          <h2>{esc(titulo)}</h2>
          {render_indice(slide.get("secciones", []))}'''
    elif tipo == "cierre":
        icono = render_icono_3d(slide.get("icono_3d", "generico"), preset["icono_3d_intensidad"])
        revelado_cierre = slide.get("revelado", "cascada")
        cuerpo = f'''
          <div class="portada-contenido">
            <h1 class="entra-arriba" style="--i:0">{esc(titulo)}</h1>
            {render_bullets(slide.get("bullets", []), revelado_cierre)}
          </div>
          {icono}'''
    else:  # contenido estándar
        revelado = slide.get("revelado", "cascada")
        imagenes = slide.get("imagenes", [])
        # revelado "cascada" no tiene sentido para imágenes (mostraría todas
        # de golpe, justo lo que el usuario pidió evitar) — si hay imágenes y
        # el JSON no especificó revelado, se fuerza "progresivo" para ellas
        # aunque las viñetas se queden en cascada; si el JSON sí puso
        # "progresivo"/"reemplazo" se respeta para ambos.
        revelado_imgs = revelado if revelado in FRAGMENT_CLASS else "progresivo"
        imagenes_html = render_imagenes(imagenes, revelado_imgs) if imagenes else ""
        bullets_html = render_bullets(slide.get("bullets", []), revelado)
        if imagenes:
            cuerpo = f'''
              <h2>{esc(titulo)}</h2>
              <div class="cuerpo-slide con-imagenes">
                {bullets_html}
                {imagenes_html}
              </div>'''
        else:
            cuerpo = f'''
              <h2>{esc(titulo)}</h2>
              {bullets_html}'''

    take_home_html = f'<div class="take-home">{esc(take_home)}</div>' if take_home else ""
    pie_html = f'<div class="nota-pie">{esc(nota_pie)}</div>' if nota_pie else ""
    notas_html = f'<aside class="notes">{esc(notas)}</aside>' if notas else ""

    section = f'''
    <section class="{" ".join(clases_section)}"{transicion_attr}>
      {cuerpo}
      {take_home_html}
      {pie_html}
      {notas_html}
    </section>'''
    return section, js_chart


CSS_BASE_TEMPLATE = """
:root {{
  --color-fondo: {color_fondo};
  --color-panel: {color_panel};
  --color-texto: {color_texto};
  --color-primario: {color_primario};
  --color-acento: {color_acento};
  --color-alerta: {color_alerta};
  --fuente: {fuente};
  /* Tokens de radio único — evita que cada componente nuevo invente su propio
     valor suelto (8px/10px/12px/18px mezclados) a medida que crece la skill. */
  --radio-sm: 8px;
  --radio-md: 12px;
  --radio-lg: 18px;
  /* line-height más generoso que el default del navegador (~1.2): esto se
     proyecta en un aula y se lee a distancia, no en una pantalla de cerca —
     texto apretado es más costoso de leer para el público del fondo. */
  --interlineado: 1.45;
}}
html, body {{ background: var(--color-fondo); }}
.reveal {{ font-family: var(--fuente); color: var(--color-texto); }}
.reveal p, .reveal li, .reveal td {{ line-height: var(--interlineado); }}
.reveal h1, .reveal h2, .reveal h3 {{ color: var(--color-texto); font-weight: 700; text-shadow: none; }}
.reveal section {{ text-align: left; }}
.reveal section.slide-portada, .reveal section.slide-cierre {{ text-align: center; }}
/* max-width más angosto (antes 82%) + h1 más chico que el tamaño gigante del
   tema base de reveal.js: títulos clínicos suelen ser largos ("Hipertensión
   arterial en el adulto mayor") y a tamaño completo cualquier posición del
   icono 3D termina debajo del texto. Con estos dos cambios el título deja un
   margen real a ambos lados en vez de extenderse borde a borde. */
.portada-contenido {{ max-width: 68%; margin: 0 auto; }}
.reveal section.slide-portada h1, .reveal section.slide-cierre h1 {{ font-size: 1.55em; }}

/* ---------------------------------------------------------------------
   Movimiento automático al entrar a la diapositiva.
   Todo lo de aquí abajo se dispara con la clase ".present" que reveal.js
   añade/quita solo al navegar — NO depende de fragmentos manuales, así que
   se ve exactamente igual si se presenta en vivo, si se avanza rápido, o si
   alguien toma una captura de pantalla justo al llegar a la diapositiva.
   Cada elemento de una lista recibe su índice en --i (puesto desde Python)
   para escalonar el retraso sin necesitar JavaScript adicional.
   --------------------------------------------------------------------- */
@keyframes entra-cascada {{
  from {{ opacity: 0; transform: translateY(22px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes entra-arriba-kf {{
  from {{ opacity: 0; transform: translateY(-26px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes pop-in-kf {{
  0%   {{ opacity: 0; transform: scale(0.82); }}
  70%  {{ opacity: 1; transform: scale(1.04); }}
  100% {{ opacity: 1; transform: scale(1); }}
}}
@keyframes crecer-ancho-kf {{
  from {{ transform: scaleX(0); }}
  to   {{ transform: scaleX(1); }}
}}
@keyframes flotar-kf {{
  0%, 100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-10px); }}
}}
@keyframes brillo-ambiente-kf {{
  0%   {{ transform: translate(-6%, -4%) scale(1); }}
  50%  {{ transform: translate(6%, 4%) scale(1.12); }}
  100% {{ transform: translate(-6%, -4%) scale(1); }}
}}
.reveal section.present .entra-arriba {{
  animation: entra-arriba-kf 0.65s cubic-bezier(.2,.8,.3,1) both;
  animation-delay: calc(var(--i, 0) * 0.14s + 0.05s);
}}
.reveal section.present h2 {{
  animation: entra-arriba-kf 0.55s ease both;
}}
.reveal section.present .impacto-pop {{
  animation: pop-in-kf 0.8s cubic-bezier(.2,.8,.3,1.3) both;
}}

.bullets {{ list-style: none; padding-left: 0; margin-top: 1.2em; }}
.bullets li {{
  background: var(--color-panel);
  border-left: 6px solid var(--color-primario);
  padding: 0.5em 0.9em;
  margin: 0.5em 0;
  border-radius: var(--radio-sm);
  font-size: 0.85em;
  box-shadow: 0 8px 18px rgba(0,0,0,0.25);
}}
/* Cascada (default): igual que antes, la viñeta entra sola al activarse la
   diapositiva. ":not(.fragment)" evita que esta regla choque con las
   viñetas en modo "progresivo"/"reemplazo" (esas son fragmentos reales de
   reveal.js más abajo, con su propio ciclo de opacidad que reveal.js ya
   controla — no hace falta ni conviene duplicarlo aquí). */
.bullets li:not(.fragment) {{ opacity: 0; transform: translateY(22px); }}
.reveal section.present .bullets li:not(.fragment) {{
  animation: entra-cascada 0.55s cubic-bezier(.2,.8,.3,1) both;
  animation-delay: calc(var(--i, 0) * 0.12s + 0.1s);
}}
/* Viñeta en modo fragmento (progresivo/reemplazo): reveal.js ya se encarga
   de opacity 0→1 vía sus clases .fragment/.visible — solo se añade la
   transición para que el cambio se sienta suave, no instantáneo. */
.bullets li.fragment {{ transition: opacity 0.4s ease, transform 0.4s ease; }}

/* --- Galería de imágenes con revelado progresivo/reemplazo (una imagen a la
   vez, sincronizada con el ritmo de la charla) — ver render_imagenes() en
   Python para el porqué: mostrar 3-4 fotos de golpe es exactamente lo que
   hace sentir "cargada" a una diapositiva incluso con poco texto. --- */
.cuerpo-slide.con-imagenes {{
  display: grid; grid-template-columns: 54% 43%; gap: 3%; align-items: start;
  margin-top: 1em;
}}
.galeria-progresiva {{ display: flex; flex-wrap: wrap; gap: 0.8em; align-content: flex-start; }}
.galeria-progresiva .imagen-apoyo {{ max-width: 100%; margin: 0; }}
.galeria-progresiva .imagen-apoyo img {{
  width: 100%; display: block; border-radius: var(--radio-md);
  box-shadow: 0 14px 32px rgba(0,0,0,0.4);
}}
.galeria-progresiva .imagen-apoyo figcaption {{
  font-size: 0.38em; opacity: 0.75; margin-top: 0.35em; text-align: center;
}}
/* "reemplazo": las fotos ocupan el mismo espacio, apiladas — al llegar el
   siguiente fragmento, reveal.js atenúa la anterior (fade-in-then-semi-out)
   mientras la nueva entra, así que en cualquier momento hay como máximo una
   completamente visible en vez de acumular todas en pantalla. */
.galeria-reemplazo {{ position: relative; min-height: 280px; }}
.galeria-reemplazo .imagen-apoyo {{
  position: absolute; inset: 0; margin: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}}
.galeria-reemplazo .imagen-apoyo img {{
  max-height: 280px; max-width: 100%; border-radius: var(--radio-md);
  box-shadow: 0 14px 32px rgba(0,0,0,0.4);
}}
.galeria-reemplazo .imagen-apoyo figcaption {{ font-size: 0.38em; opacity: 0.85; margin-top: 0.5em; }}
.layout-70-30 {{ display: grid; grid-template-columns: 68% 30%; gap: 2%; align-items: start; }}
.grafico-wrap {{
  background: var(--color-panel); border-radius: var(--radio-md); padding: 1em;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35); opacity: 0; transform: scale(0.94);
}}
.reveal section.present .grafico-wrap {{ animation: pop-in-kf 0.6s ease both; animation-delay: 0.05s; }}
.panel-lateral .bullets li {{ font-size: 0.75em; }}
.take-home {{
  /* Antes "position:absolute; bottom:6%" flotaba sobre el contenido — con
     3+ viñetas largas (o viñetas que ya no dependen de fragmentos manuales,
     así que siempre están completas en pantalla) terminaba tapando la
     última viñeta. Ahora fluye después de las viñetas: nunca puede solaparse
     con nada, sin importar cuánto contenido tenga la diapositiva. */
  display: inline-block; margin-top: 1em; clear: both;
  background: var(--color-acento); color: #06110f;
  padding: 0.5em 1em; border-radius: var(--radio-md); font-weight: 700; font-size: 0.6em;
  max-width: 60%; box-shadow: 0 10px 24px rgba(0,0,0,0.35);
  opacity: 0; transform: translateX(20px);
}}
.reveal section.present .take-home {{ animation: entra-cascada 0.5s ease both; animation-delay: 0.5s; }}
/* Igual razón que .take-home: "position:absolute; bottom:2%" chocaba con
   diagramas/listas que crecen en altura (p. ej. un algoritmo de 3 filas)
   porque el pie de página quedaba fijo en una coordenada sin importar cuánto
   contenido hubiera encima. Ahora es parte del flujo normal, siempre debajo
   de todo lo demás. */
.nota-pie {{ display: block; margin-top: 1.2em; font-size: 0.42em; opacity: 0.65; clear: both; }}
.fondo-oscuro-forzado {{ background: #000 !important; }}
.impacto-contenido p {{ font-size: 1.6em; text-align: center; font-weight: 700; }}
.diagrama-flujo {{ display: flex; align-items: center; flex-wrap: wrap; gap: 0.4em; margin-top: 1.5em; }}
.diagrama-flujo .paso {{
  background: var(--color-panel); border: 2px solid var(--color-primario);
  border-radius: var(--radio-md); padding: 0.6em 0.9em; font-size: 0.6em; min-width: 120px; text-align: center;
  box-shadow: 0 8px 20px rgba(0,0,0,0.3);
  opacity: 0; transform: scale(0.8);
}}
.reveal section.present .diagrama-flujo .paso {{
  animation: pop-in-kf 0.5s cubic-bezier(.2,.8,.3,1.3) both;
  animation-delay: calc(var(--i, 0) * 0.35s);
}}
.diagrama-flujo .flecha {{
  font-size: 1.1em; color: var(--color-acento); opacity: 0; transform: scaleX(0);
  transform-origin: left center; display: inline-block;
}}
.reveal section.present .diagrama-flujo .flecha {{
  animation: entra-cascada 0.35s ease both, crecer-ancho-kf 0.35s ease both;
  animation-delay: calc(var(--i, 0) * 0.35s + 0.25s);
}}

/* --- "Zoom progresivo" opcional en diagramas (diagrama.zoom_progresivo:true
   en el JSON) — aproximación honesta al Zoom de sección de PowerPoint hecha
   con el mecanismo de fragmentos de reveal.js: cada caja ya está visible
   desde que entra la diapositiva (ver regla de arriba), esto solo decide
   cómo se ve la caja "actual" cuando el presentador avanza con las flechas.
   ".current-fragment" la aplica reveal.js solo, no hay que calcularla. --- */
/* Especificidad calculada a propósito para ganarle a la regla base de
   reveal.js que oculta los fragmentos por defecto (3 clases + 1 elemento:
   .reveal .slides section .fragment) — con menos que eso, el fragmento se
   queda oculto sin importar lo que diga esta hoja de estilos. */
.reveal section .diagrama-zoom .paso.fragment {{
  /* !important justificado: es la única forma de garantizar, sin depender de
     calcular a mano la especificidad exacta del CSS interno de reveal.js
     (que puede cambiar entre versiones), que este contenido NUNCA quede
     oculto — el mismo tipo de bug de "diapositiva vacía" que ya se corrigió
     en render_bullets/render_diagrama para el resto de la skill. */
  opacity: 1 !important; visibility: visible !important; transform: scale(1);
  transition: transform 0.4s cubic-bezier(.2,.8,.3,1), opacity 0.4s ease, box-shadow 0.4s ease;
}}
.reveal section .diagrama-zoom .paso.fragment.current-fragment {{
  transform: scale(1.15);
  box-shadow: 0 0 0 3px var(--color-acento), 0 18px 36px rgba(0,0,0,0.45);
  z-index: 2;
  position: relative;
}}
.reveal section .diagrama-zoom .paso.fragment.visible:not(.current-fragment) {{
  opacity: 0.5; transform: scale(0.96);
}}

/* --- Icono 3D en CSS puro (sin WebGL/three.js): un cubo que gira mostrando
   un glifo clínico en cada cara, pensado para 1-2 diapositivas por deck
   (portada / cierre / impacto), nunca para todas. --- */
.icono3d-wrap {{
  /* Antes centrado verticalmente a la derecha (top:50%) — con títulos largos
     (frecuentes en medicina: nombres de enfermedades, guías) el icono
     terminaba superpuesto sobre el texto centrado de portada/cierre. Ahora
     vive en la esquina superior derecha, fuera de la franja donde cae el
     título, y es más pequeño (90px) para quedar como acento, no como
     elemento que compite con el texto. */
  position: absolute; right: 4%; top: 6%;
  perspective: 900px; width: 90px; height: 90px; opacity: var(--i3d, 1);
  animation: flotar-kf 5s ease-in-out infinite;
}}
.icono3d-cubo {{
  width: 100%; height: 100%; position: relative; transform-style: preserve-3d;
  animation: girar3d 14s linear infinite;
}}
.icono3d-cubo .cara {{
  position: absolute; width: 90px; height: 90px; display: flex; align-items: center;
  justify-content: center; font-size: 2.2em; border-radius: 16px;
  background: linear-gradient(135deg, var(--color-primario), var(--color-acento));
  box-shadow: 0 0 40px rgba(0,0,0,0.4) inset;
}}
.cara-f {{ transform: translateZ(45px); }}
.cara-b {{ transform: rotateY(180deg) translateZ(45px); }}
.cara-r {{ transform: rotateY(90deg) translateZ(45px); }}
.cara-l {{ transform: rotateY(-90deg) translateZ(45px); }}
@keyframes girar3d {{ from {{ transform: rotateY(0deg) rotateX(8deg); }} to {{ transform: rotateY(360deg) rotateX(8deg); }} }}

/* --- Ficha de guía / infografía clínica de un vistazo (tipo "ficha") ---
   Tarjeta clara con sombra, pensada para funcionar incluso sobre presets
   oscuros (flota igual que en el ejemplo de referencia), con semáforo de
   color reservado para riesgo/severidad, nunca para decorar. --- */
.reveal section.slide-ficha {{ text-align: left; }}
.ficha-card {{
  background: #ffffff; color: #1a2433; border-radius: var(--radio-lg); padding: 2.2em 2.6em;
  box-shadow: 0 24px 60px rgba(0,0,0,0.35); max-width: 100%; margin: 0 auto;
  opacity: 0; transform: scale(0.94) translateY(14px);
}}
.reveal section.present .ficha-card {{ animation: pop-in-kf 0.6s cubic-bezier(.2,.8,.3,1.2) both; }}
.ficha-encabezado {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1em; }}
.ficha-eyebrow {{ font-size: 0.42em; font-weight: 700; letter-spacing: 0.08em; color: #47505f; text-transform: uppercase; }}
/* Bug real encontrado en QA visual: la regla genérica ".reveal h1, .reveal h2,
   .reveal h3" (que fija color: var(--color-texto)) tiene MÁS especificidad
   CSS que ".ficha-titulo" sola (incluye el selector de elemento h1), así que en un
   preset oscuro (sobrio/congreso) el título de la ficha —que debe ser oscuro
   sobre su tarjeta blanca— se pintaba casi blanco sobre blanco: invisible en
   pantalla aunque el HTML fuera correcto. ".reveal .ficha-card h1" tiene
   especificidad mayor y gana siempre, sin importar el orden en la hoja de
   estilos ni el preset activo. */
.reveal .ficha-card h1.ficha-titulo {{ font-size: 1.15em; font-weight: 800; color: #10151f; margin: 0.15em 0; }}
.ficha-subtitulo {{ font-size: 0.55em; color: #2e3644; margin: 0; }}
.ficha-badge-wrap {{ text-align: right; flex-shrink: 0; }}
.ficha-badge {{
  display: inline-block; background: var(--color-primario); color: #fff; font-weight: 700;
  font-size: 0.4em; padding: 0.35em 0.8em; border-radius: 6px; letter-spacing: 0.03em;
}}
.ficha-badge-nota {{ font-size: 0.32em; color: #47505f; margin-top: 0.4em; }}
.ficha-divisor {{ height: 2px; background: #10151f; margin: 0.8em 0 1em; opacity: 0.85; }}
.ficha-nota-metodo {{ font-size: 0.42em; font-style: italic; color: #2e3644; margin-bottom: 1em; }}
.escala-gradiente {{ margin: 1em 0 1.4em; }}
.escala-barra {{ display: flex; height: 14px; border-radius: 7px; overflow: hidden; }}
.escala-barra-animada {{ transform: scaleX(0); transform-origin: left center; }}
.reveal section.present .escala-barra-animada {{ animation: crecer-ancho-kf 0.9s cubic-bezier(.2,.8,.3,1) both; animation-delay: 0.15s; }}
.escala-marcas {{ display: flex; justify-content: space-between; font-size: 0.4em; color: #47505f; margin-top: 0.4em; }}
.ficha-cuerpo {{ display: grid; grid-template-columns: 62% 35%; gap: 3%; align-items: start; }}
.tabla-clinica {{ width: 100%; border-collapse: collapse; font-size: 0.5em; }}
.tabla-clinica th {{ text-align: left; font-size: 0.85em; color: #47505f; text-transform: uppercase; letter-spacing: 0.04em; padding-bottom: 0.5em; }}
.tabla-clinica td {{ padding: 0.6em 0.4em; border-top: 1px solid #e3e7ee; color: #1a2433; font-weight: 600; }}
.punto-color {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.5em; }}
.tabla-nota {{ font-size: 0.36em; color: #47505f; margin-top: 0.6em; }}
.tarjetas-laterales {{ display: flex; flex-direction: column; gap: 0.7em; }}
.tarjeta-ficha {{
  border-left: 4px solid var(--color-primario); background: #f7f9fc; border-radius: 0 10px 10px 0;
  padding: 0.7em 1em; opacity: 0; transform: translateX(24px);
}}
.reveal section.present .tarjeta-ficha {{
  animation: entra-cascada 0.5s ease both;
  animation-delay: calc(var(--i, 0) * 0.15s + 0.3s);
}}
.tarjeta-titulo {{ font-size: 0.38em; font-weight: 800; letter-spacing: 0.03em; text-transform: uppercase; }}
.tarjeta-valor {{ font-size: 0.85em; font-weight: 800; color: #10151f; margin: 0.15em 0; }}
.tarjeta-ficha p {{ font-size: 0.42em; color: #2e3644; margin: 0.2em 0 0; }}
.pildoras-banda {{ background: #eef1f7; border-radius: var(--radio-md); padding: 0.8em 1.1em; margin-top: 1.2em; }}
.pildoras-titulo {{ font-size: 0.38em; font-weight: 800; letter-spacing: 0.03em; color: #10151f; margin-bottom: 0.4em; }}
.pildoras-lista {{ font-size: 0.46em; color: #1a2433; }}
.pildora {{ display: inline-block; margin: 0 0.4em 0.3em 0; opacity: 0; transform: translateY(10px); }}
.pildora:not(:last-child)::after {{ content: '·'; margin-left: 0.6em; color: #9aa4b2; }}
.reveal section.present .pildora {{
  animation: entra-cascada 0.4s ease both;
  animation-delay: calc(var(--i, 0) * 0.08s + 0.5s);
}}

/* --- Menú tipo acordeón (tipo "indice") — equivalente HTML del menú de
   botones nativo del .pptx. <details>/<summary> nativos: accesibles por
   teclado y por lector de pantalla sin JS adicional. --- */
.acordeon {{ margin-top: 1.2em; display: flex; flex-direction: column; gap: 0.6em; }}
.acordeon-item {{
  background: var(--color-panel); border: 1px solid rgba(255,255,255,0.12);
  border-radius: var(--radio-md); padding: 0.2em 0.9em; overflow: hidden;
  opacity: 0; transform: translateY(16px);
}}
.reveal section.present .acordeon-item {{
  animation: entra-cascada 0.45s ease both;
  animation-delay: calc(var(--i, 0) * 0.1s + 0.1s);
}}
.acordeon-item summary {{
  cursor: pointer; padding: 0.7em 0; font-weight: 700; font-size: 0.65em;
  list-style: none; display: flex; align-items: center; justify-content: space-between;
}}
.acordeon-item summary::-webkit-details-marker {{ display: none; }}
.acordeon-item summary::after {{
  content: '+'; font-size: 1.3em; color: var(--color-acento); margin-left: 0.6em;
  transition: transform 0.25s ease;
}}
.acordeon-item[open] summary::after {{ content: '−'; }}
.acordeon-contenido {{ padding: 0 0 0.9em; font-size: 0.55em; opacity: 0.92; }}
.acordeon-contenido .bullets {{ margin-top: 0.6em; }}
.acordeon-contenido .bullets li {{ font-size: 0.85em; }}

/* --- Fondo con profundidad (parallax suave con el mouse), solo si el preset
   lo activa --- */
.fondo-parallax {{
  position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none;
}}
.fondo-parallax .blob {{
  position: absolute; border-radius: 50%; filter: blur(60px); opacity: 0.35;
  background: radial-gradient(circle, var(--color-primario), transparent 70%);
  transition: transform 0.2s ease-out;
}}

/* --- Brillo ambiental de baja intensidad: a diferencia del parallax (que
   solo activa "congreso" y reacciona al mouse), esta capa vive en TODOS los
   presets a opacidad muy baja, para que ninguna diapositiva se sienta un
   fondo plano y estático incluso si el usuario no mueve el mouse ni avanza
   fragmentos. Es deliberadamente lento y sutil — profundidad ambiental, no
   un efecto que compita con el contenido clínico. --- */
.fondo-ambiente {{
  position: fixed; inset: -10%; z-index: -2; overflow: hidden; pointer-events: none;
}}
.fondo-ambiente .halo {{
  position: absolute; width: 60%; height: 60%; left: 20%; top: 15%; border-radius: 50%;
  filter: blur(90px); opacity: 0.16;
  background: radial-gradient(circle, var(--color-primario), transparent 65%);
  animation: brillo-ambiente-kf 22s ease-in-out infinite;
}}
.fondo-ambiente .halo:nth-child(2) {{
  left: -10%; top: 45%; width: 45%; height: 45%; opacity: 0.12;
  background: radial-gradient(circle, var(--color-acento), transparent 65%);
  animation-duration: 28s; animation-direction: reverse;
}}
"""


def build_html(contenido: dict, preset_name: str, overrides: dict) -> tuple[str, list[str]]:
    if preset_name not in PRESETS:
        raise SystemExit(f"Preset desconocido: {preset_name!r}. Usa: {', '.join(PRESETS)}")
    preset = {**PRESETS[preset_name], **{k: v for k, v in overrides.items() if v is not None}}

    titulo_deck = contenido.get("titulo", "Presentación")
    slides = contenido.get("slides", [])

    secciones = []
    chart_configs = []
    avisos = []
    for i, slide in enumerate(slides):
        section_html, js_chart = render_slide(i, slide, preset)
        secciones.append(section_html)
        if js_chart:
            chart_configs.append(js_chart)
        avisos.extend(advertencias_densidad(slide))

    css = CSS_BASE_TEMPLATE.format(**preset)

    # Brillo ambiental: siempre presente (todos los presets), independiente
    # del parallax reactivo al mouse de "congreso" — ver nota en
    # ".fondo-ambiente" del CSS_BASE_TEMPLATE.
    ambiente_html = '<div class="fondo-ambiente"><div class="halo"></div><div class="halo"></div></div>'

    parallax_html = ""
    if preset["fondo_parallax"]:
        parallax_html = (
            '<div class="fondo-parallax">'
            '<div class="blob" style="width:420px;height:420px;left:-10%;top:10%"></div>'
            '<div class="blob" style="width:320px;height:320px;right:-8%;bottom:5%;'
            'background:radial-gradient(circle,var(--color-acento),transparent 70%)"></div>'
            "</div>"
        )

    chart_configs_js = "[" + ",".join(chart_configs) + "]"

    html_doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{esc(titulo_deck)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="{CDNJS}/reveal.js/{REVEAL_VERSION}/reveal.min.css">
<link rel="stylesheet" href="{CDNJS}/reveal.js/{REVEAL_VERSION}/theme/black.min.css" id="reveal-theme">
<style>{css}</style>
</head>
<body>
{ambiente_html}
{parallax_html}
<div class="reveal">
  <div class="slides">
    {''.join(secciones)}
  </div>
</div>

<script src="{CDNJS}/reveal.js/{REVEAL_VERSION}/reveal.min.js"></script>
<script src="{CDNJS}/reveal.js/{REVEAL_VERSION}/plugin/notes/notes.min.js"></script>
<script src="{CDNJS}/Chart.js/{CHARTJS_VERSION}/chart.umd.min.js"></script>
<script>
  const CHART_CONFIGS = {chart_configs_js};
  const chartInstances = {{}};

  function paletaSerie(i) {{
    const colores = [
      getComputedStyle(document.documentElement).getPropertyValue('--color-primario').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-acento').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--color-alerta').trim(),
    ];
    return colores[i % colores.length];
  }}

  function construirGrafico(cfg) {{
    const canvas = document.getElementById(cfg.id);
    if (!canvas) return;
    if (chartInstances[cfg.id]) {{ chartInstances[cfg.id].destroy(); }}
    const datasets = (cfg.series || []).map((s, i) => ({{
      label: s.nombre || ('Serie ' + (i + 1)),
      data: s.datos || [],
      backgroundColor: paletaSerie(i),
      borderColor: paletaSerie(i),
      borderWidth: 2,
      tension: 0.35,
      fill: cfg.type === 'line' ? false : true,
    }}));
    chartInstances[cfg.id] = new Chart(canvas.getContext('2d'), {{
      type: cfg.type || 'bar',
      data: {{ labels: cfg.labels || [], datasets }},
      options: {{
        responsive: true,
        animation: {{ duration: 900, easing: 'easeOutQuart' }},
        plugins: {{ legend: {{ labels: {{ color: 'var(--color-texto)' }} }} }},
        scales: (cfg.type === 'doughnut' || cfg.type === 'pie') ? {{}} : {{
          x: {{ ticks: {{ color: 'var(--color-texto)' }}, grid: {{ color: 'rgba(255,255,255,0.08)' }} }},
          y: {{ ticks: {{ color: 'var(--color-texto)' }}, grid: {{ color: 'rgba(255,255,255,0.08)' }} }},
        }},
      }},
    }});
  }}

  // Los gráficos solo se construyen (y por tanto solo se animan) cuando su
  // diapositiva entra en pantalla — si se construyeran todos al cargar la
  // página, el usuario vería la animación de dibujo antes de que la
  // diapositiva sea visible, y perdería todo el efecto.
  function activarGraficoDeSlide(slideEl) {{
    if (!slideEl) return;
    const canvas = slideEl.querySelector('canvas');
    if (!canvas) return;
    const cfg = CHART_CONFIGS.find(c => c.id === canvas.id);
    if (cfg) construirGrafico(cfg);
  }}

  // Parallax suave del fondo con el mouse (si el preset lo activa).
  document.addEventListener('mousemove', (e) => {{
    const blobs = document.querySelectorAll('.fondo-parallax .blob');
    const dx = (e.clientX / window.innerWidth - 0.5) * 30;
    const dy = (e.clientY / window.innerHeight - 0.5) * 30;
    blobs.forEach((b, i) => {{
      const factor = i % 2 === 0 ? 1 : -1;
      b.style.transform = `translate(${{dx * factor}}px, ${{dy * factor}}px)`;
    }});
  }});

  Reveal.initialize({{
    hash: true,
    controls: true,
    progress: true,
    center: false,
    transition: '{preset["reveal_transition"]}',
    transitionSpeed: 'default',
    plugins: [ RevealNotes ],
  }}).then(() => {{
    activarGraficoDeSlide(Reveal.getCurrentSlide());
    Reveal.on('slidechanged', (event) => activarGraficoDeSlide(event.currentSlide));
  }});
</script>
</body>
</html>
"""
    return html_doc, avisos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contenido_json", type=Path)
    parser.add_argument("salida_html", type=Path)
    parser.add_argument("--preset", choices=list(PRESETS), default="sobrio")
    parser.add_argument("--color-primario", dest="color_primario", default=None)
    parser.add_argument("--color-acento", dest="color_acento", default=None)
    parser.add_argument("--logo", dest="logo", default=None, help="(reservado para uso futuro)")
    args = parser.parse_args()

    contenido = json.loads(args.contenido_json.read_text(encoding="utf-8"))
    overrides = {"color_primario": args.color_primario, "color_acento": args.color_acento}
    html_doc, avisos = build_html(contenido, args.preset, overrides)
    args.salida_html.write_text(html_doc, encoding="utf-8")
    print(f"HTML dinámico generado -> {args.salida_html}")
    if avisos:
        print("\nAvisos de densidad visual (revisar antes de entregar):")
        for a in avisos:
            print(f"  - {a}")
    else:
        print("Sin avisos de densidad visual.")


if __name__ == "__main__":
    main()
