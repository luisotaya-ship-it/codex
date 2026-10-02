#!/usr/bin/env python3
"""
pptx_morph_helper.py — Construye pares de diapositivas listos para la
transición Morph nativa de PowerPoint, e implementa el único requisito
estructural del que depende ese efecto: que las formas que deben "fluir" de
una diapositiva a la siguiente tengan EXACTAMENTE el mismo nombre interno
(shape.name) en ambas.

De dónde sale esto: analizando el tutorial de Morph de Jazz Guzman
("La mejor TRANSICIÓN de POWERPOINT — Morph", YouTube, @JazzGuzman) se
confirma que Morph no anima "lo que cambió entre dos diapositivas" de forma
mágica — solo interpola las formas cuyo nombre coincide exactamente entre la
diapositiva N y la N+1 (identificable en PowerPoint desde el Panel de
selección, Alt+F10). Si el nombre no coincide, Morph simplemente hace un
fundido normal entre esa forma y nada. Esto es lo que permite:
  - Mover/redimensionar una forma → Morph la desliza/escala suavemente.
  - Cambiar el texto de un cuadro de texto con el mismo nombre → Morph anima
    la transformación letra a letra (efecto "texto cinético" barato).
  - Mover una forma fuera del lienzo en la diapositiva de llegada (o de
    partida) → Morph la anima entrando/saliendo de la diapositiva.

Por qué esto SÍ es seguro de automatizar (a diferencia de las animaciones de
aparición por elemento, ver pptx_dinamizar.py): Morph es una transición
(<p:transition>), no un árbol <p:timing> hecho a mano — el mismo mecanismo ya
vendorizado y autovalidado en scripts/vendor/pptx_transitions.py. Lo único que
esta skill no podía hacer antes era la mitad "de contenido": duplicar una
diapositiva conservando los nombres de forma y saber si un par de diapositivas
realmente van a producir Morph o un fundido plano. Este módulo cierra ese
hueco con python-pptx puro (sin tocar OOXML de animación).

Uso típico (dentro de un script Python, no una CLI de un solo comando, porque
la modificación entre "antes" y "después" es siempre específica del contenido):

    from pptx import Presentation
    from pptx_morph_helper import duplicar_diapositiva, verificar_par_morph

    prs = Presentation("entrada.pptx")
    nueva = duplicar_diapositiva(prs, indice=5)  # duplica la diapositiva 6 (0-idx 5)
    # ... aquí mueves/redimensionas/cambias texto de formas en `nueva` ...
    prs.save("con_par_morph.pptx")

    ok, detalle = verificar_par_morph(prs, indice_a=5, indice_b=6)
    print(detalle)  # dice qué formas SÍ van a hacer Morph y cuáles no

Luego aplicar la transición con:
    python3 pptx_dinamizar.py con_par_morph.pptx salida.pptx --preset sobrio --morph-en 7

(la diapositiva de LLEGADA del par es la que lleva la transición Morph — así
funciona en PowerPoint real: la transición vive en la diapositiva a la que se
entra, no en la de salida).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

try:
    from pptx import Presentation
    from pptx.oxml.ns import qn
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Este módulo requiere python-pptx (pip install python-pptx --break-system-packages)"
    ) from exc


# Atributos que contienen un rId de relación (r:embed en imágenes/blips,
# r:id en hipervínculos y otras referencias) — se necesitan migrar a mano
# porque al duplicar una diapositiva por XML, el rId que trae copiado sigue
# apuntando al esquema de relaciones de la diapositiva ORIGEN, no al de la
# nueva (cada diapositiva tiene su propio archivo .rels independiente).
_ATRIBUTOS_RELACION = (qn("r:embed"), qn("r:id"), qn("r:link"))


def _migrar_relaciones(elemento_copiado, part_origen, part_destino, mapa_rids: dict[str, str]) -> None:
    """Recorre un elemento XML ya copiado y, por cada rId de relación que
    encuentre (imagen, hipervínculo...), crea la relación equivalente en la
    diapositiva destino (reutilizando el MISMO part de imagen — no duplica
    los bytes de la foto) y reescribe el atributo con el nuevo rId.

    Sin este paso, una imagen duplicada queda con un r:embed "huérfano" que
    el lector de OOXML (PowerPoint o LibreOffice) puede resolver contra
    CUALQUIER relación que coincida por número en la diapositiva nueva —
    esto se detectó en QA visual: una foto duplicada se veía con el
    contenido de otra foto agregada después, por colisión de rId."""
    for el in elemento_copiado.iter():
        for attr in _ATRIBUTOS_RELACION:
            rid_antiguo = el.get(attr)
            if not rid_antiguo:
                continue
            if rid_antiguo not in mapa_rids:
                rel = part_origen.rels[rid_antiguo]
                if rel.is_external:
                    nuevo_rid = part_destino.relate_to(
                        rel.target_ref, rel.reltype, is_external=True
                    )
                else:
                    nuevo_rid = part_destino.relate_to(rel.target_part, rel.reltype)
                mapa_rids[rid_antiguo] = nuevo_rid
            el.set(attr, mapa_rids[rid_antiguo])


def duplicar_diapositiva(prs: "Presentation", indice: int):
    """Duplica la diapositiva en `indice` (0-indexado) e la inserta justo
    después, conservando el nombre (shape.name) de cada forma — condición
    indispensable para que Morph las reconozca como "la misma forma" en la
    diapositiva siguiente — y migrando correctamente cualquier relación
    (imágenes, hipervínculos) que las formas copiadas necesiten.

    python-pptx no tiene un método nativo de "duplicar diapositiva": esto usa
    una técnica conocida y estable (copiar el XML de la diapositiva vía
    copy.deepcopy y reinsertarlo en el árbol de diapositivas), sin generar
    animaciones ni timing — solo formas, texto, estilos e imágenes, que es
    exactamente lo que Morph necesita comparar.
    """
    origen = prs.slides[indice]
    layout = origen.slide_layout
    nueva_slide = prs.slides.add_slide(layout)

    # add_slide() crea placeholders vacíos según el layout; los descartamos y
    # copiamos el árbol <p:spTree> completo de la diapositiva original para
    # partir de una copia exacta (mismas formas, mismos nombres, mismo texto).
    for shape in list(nueva_slide.shapes):
        shape._element.getparent().remove(shape._element)

    spTree_origen = origen.shapes._spTree
    spTree_nueva = nueva_slide.shapes._spTree
    mapa_rids: dict[str, str] = {}
    for child in list(spTree_origen):
        tag = child.tag
        if tag in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            continue  # ya existen en la diapositiva nueva, no se duplican
        copia = copy.deepcopy(child)
        _migrar_relaciones(copia, origen.part, nueva_slide.part, mapa_rids)
        spTree_nueva.append(copia)

    # Mover la diapositiva recién creada (que add_slide() puso al final del
    # deck) a la posición justo después del original, para que quede como
    # "par consecutivo" — condición necesaria para que la transición Morph de
    # la segunda tenga efecto sobre la primera al presentar en orden.
    xml_slides = prs.slides._sldIdLst
    slides = list(xml_slides)
    nueva_id_elem = slides[-1]
    xml_slides.remove(nueva_id_elem)
    xml_slides.insert(indice + 1, nueva_id_elem)

    return prs.slides[indice + 1]


@dataclass
class ResultadoVerificacionMorph:
    formas_coincidentes: list[str]
    formas_solo_en_a: list[str]
    formas_solo_en_b: list[str]

    @property
    def morph_tendra_efecto(self) -> bool:
        return len(self.formas_coincidentes) > 0

    def resumen(self) -> str:
        lineas = [
            f"Formas que SÍ harán Morph (nombre idéntico en ambas diapositivas): "
            f"{len(self.formas_coincidentes)}",
        ]
        for nombre in self.formas_coincidentes:
            lineas.append(f"  ✓ {nombre}")
        if self.formas_solo_en_a:
            lineas.append(
                f"Formas SOLO en la diapositiva de origen (Morph las desvanecerá, "
                f"no las transformará): {len(self.formas_solo_en_a)}"
            )
            for nombre in self.formas_solo_en_a:
                lineas.append(f"  ✗ {nombre}")
        if self.formas_solo_en_b:
            lineas.append(
                f"Formas SOLO en la diapositiva de llegada (Morph las hará aparecer "
                f"con fundido, no con transformación): {len(self.formas_solo_en_b)}"
            )
            for nombre in self.formas_solo_en_b:
                lineas.append(f"  ✗ {nombre}")
        if not self.morph_tendra_efecto:
            lineas.append(
                "⚠ NINGUNA forma coincide por nombre — con este par, la transición "
                "'morph' se comportará como un fundido plano, no como Morph real. "
                "Revisa el Panel de selección (Alt+F10 en PowerPoint) y renombra las "
                "formas que deban fluir de una diapositiva a la otra con el MISMO nombre."
            )
        return "\n".join(lineas)


def verificar_par_morph(prs: "Presentation", indice_a: int, indice_b: int) -> ResultadoVerificacionMorph:
    """Compara los nombres de forma entre dos diapositivas y reporta cuáles
    producirán una transformación Morph real y cuáles solo un fundido — para
    detectar el error más común del tutorial (formas sin renombrar) ANTES de
    entregar el .pptx, en vez de que el usuario lo descubra presentando."""
    nombres_a = {s.name for s in prs.slides[indice_a].shapes}
    nombres_b = {s.name for s in prs.slides[indice_b].shapes}
    return ResultadoVerificacionMorph(
        formas_coincidentes=sorted(nombres_a & nombres_b),
        formas_solo_en_a=sorted(nombres_a - nombres_b),
        formas_solo_en_b=sorted(nombres_b - nombres_a),
    )


def renombrar_forma(slide, nombre_actual: str, nombre_nuevo: str) -> bool:
    """Renombra una forma por su nombre actual (equivalente a doble clic en el
    nombre dentro del Panel de selección de PowerPoint). Devuelve False si no
    encontró ninguna forma con ese nombre."""
    for shape in slide.shapes:
        if shape.name == nombre_actual:
            shape.name = nombre_nuevo
            return True
    return False


# ---------------------------------------------------------------------------
# Secuencia de revelado progresivo en .pptx real (sin <p:timing>)
# ---------------------------------------------------------------------------
# Motivación: en el gemelo HTML (build_html_dinamico.py) el revelado
# progresivo de imágenes se resuelve con fragmentos reales de reveal.js
# (el presentador avanza y cada imagen aparece). En el .pptx no existe un
# mecanismo igual de seguro — la única forma de "aparición por elemento
# dentro de una misma diapositiva" es <p:timing>, y esta skill decidió desde
# el principio no automatizar eso por el riesgo de corrupción no verificable.
#
# Esto NO significa que el .pptx (el que se proyecta en el hospital sin
# internet) tenga que quedarse con la diapositiva sobrecargada. Morph SÍ es
# seguro (ver el resto de este archivo) y permite el mismo resultado
# percibido por otro camino: en vez de una diapositiva con 3 fotos a la vez,
# se construyen 3 diapositivas casi idénticas — cada una con una foto más que
# la anterior — unidas con Morph. Al pasar de una a la siguiente, la foto
# nueva entra con una transformación suave (Morph la anima igual que
# cualquier forma nueva) y las anteriores simplemente se quedan quietas
# (mismo nombre, misma posición → Morph no les aplica ningún cambio visible).
# El público nunca ve más de lo que ya se reveló, igual que en el HTML.
@dataclass
class CapaRevelado:
    """Una capa de contenido que se agrega en su propio paso de la secuencia.

    `elementos`: lista de dicts, cada uno con las claves de `agregar_imagen`
    (`ruta`, `left`, `top`, y opcionalmente `width`, `height`, `nombre`).
    Puede tener más de un elemento si dos cosas deben aparecer juntas en el
    mismo paso (p. ej. una imagen y su etiqueta de texto)."""

    elementos: list[dict]


def agregar_imagen(slide, ruta: str, left, top, width=None, height=None, nombre: str | None = None):
    """Inserta una imagen y le asigna un nombre explícito. Necesario porque
    Morph identifica formas por `shape.name`, y el nombre automático que
    python-pptx asigna (`Picture 3`, `Picture 7`...) depende del orden de
    inserción — no es estable si se insertan imágenes en diapositivas
    duplicadas por separado. Aquí sí importa poco porque cada imagen nueva
    nace en una sola diapositiva de la secuencia y de ahí en adelante viaja
    intacta (misma copia de XML) en cada duplicación siguiente."""
    pic = slide.shapes.add_picture(ruta, left, top, width=width, height=height)
    if nombre:
        pic.name = nombre
    return pic


def construir_secuencia_revelado(prs: "Presentation", indice_base: int, capas: list[CapaRevelado]) -> list[int]:
    """A partir de una diapositiva base ya construida (título, fondo, texto
    fijo — lo que se ve DESDE el primer paso), genera una diapositiva física
    nueva por cada capa de `capas`, donde cada una agrega esos elementos a
    todo lo que ya traía la diapositiva anterior de la secuencia.

    Ejemplo: una diapositiva "Hallazgos radiológicos" con 3 fotos que se
    sentía cargada se reparte en 3 diapositivas — la primera con la foto 1,
    la segunda con las fotos 1+2, la tercera con las 3 — encadenadas con
    Morph. El presentador avanza diapositiva por diapositiva (no fragmentos,
    esto es .pptx real) y en cada paso el público ve exactamente una foto más
    que en el paso anterior, con una transición suave en vez de aparición
    instantánea.

    Devuelve la lista de índices (0-indexados) de las diapositivas nuevas, en
    el orden en que quedaron insertadas. Con esa lista:
      1. Verifica la cadena con `verificar_secuencia_revelado` antes de
         entregar — si algún eslabón no va a producir Morph real, hay que
         corregirlo, no prometerlo igual.
      2. Aplica la transición con
         `pptx_dinamizar.py ... --morph-en i1+1,i2+1,i3+1` (recordar que
         `--morph-en` es 1-indexado y va en la diapositiva de LLEGADA de cada
         par, que es cada una de estas diapositivas nuevas).
    """
    indices_nuevos: list[int] = []
    indice_actual = indice_base
    for capa in capas:
        nueva_slide = duplicar_diapositiva(prs, indice_actual)
        indice_actual += 1  # duplicar_diapositiva siempre inserta justo después
        for elem in capa.elementos:
            agregar_imagen(
                nueva_slide,
                elem["ruta"],
                elem["left"],
                elem["top"],
                elem.get("width"),
                elem.get("height"),
                elem.get("nombre"),
            )
        indices_nuevos.append(indice_actual)
    return indices_nuevos


def verificar_secuencia_revelado(
    prs: "Presentation", indice_base: int, indices_capas: list[int]
) -> list[ResultadoVerificacionMorph]:
    """Corre `verificar_par_morph` sobre cada eslabón consecutivo de la
    secuencia (base→capa1, capa1→capa2, ...) — por construcción todos deben
    dar `morph_tendra_efecto=True` porque cada capa nace de duplicar la
    anterior, pero se verifica igual en vez de asumirlo: si alguien insertó
    manualmente una diapositiva en medio de la secuencia después de
    construirla, esto lo detecta antes de que el usuario lo descubra
    presentando."""
    cadena = [indice_base] + list(indices_capas)
    resultados = []
    for a, b in zip(cadena, cadena[1:]):
        resultados.append(verificar_par_morph(prs, a, b))
    return resultados
