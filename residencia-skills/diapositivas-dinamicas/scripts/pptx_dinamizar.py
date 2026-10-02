#!/usr/bin/env python3
"""
pptx_dinamizar.py — Aplica transiciones nativas de PowerPoint + pulido de
profundidad visual a un .pptx ya construido (p. ej. por presentaciones-cientificas),
sin tocar el contenido de las diapositivas.

Por qué solo transiciones y no animaciones de aparición por elemento:
python-pptx no tiene API de animaciones y la única forma de añadirlas es escribir
a mano el árbol OOXML <p:timing>, que es intrincado y no se puede verificar aquí
sin PowerPoint real: un XML de timing con un error sutil produce el diálogo
"PowerPoint encontró un problema con el contenido... ¿reparar?" delante del
público, que es exactamente lo que este skill quiere evitar. Las transiciones de
diapositiva (<p:transition>) son un elemento único y bien documentado, así que sí
se aplican de forma segura mediante el módulo vendorizado `vendor/pptx_transitions.py`
(MIT, proyecto ppt-master de Hugo He — ver vendor/LICENSE_pptx_transitions.txt),
que además valida el resultado antes de darlo por bueno. El "dinamismo" que
requiere animación de aparición, gráficos que se dibujan o profundidad 3D real se
resuelve en el gemelo HTML (build_html_dinamico.py), donde sí se puede verificar
cada línea de JS/CSS antes de entregarla.

Uso:
    python3 pptx_dinamizar.py entrada.pptx salida.pptx --preset sobrio
    python3 pptx_dinamizar.py entrada.pptx salida.pptx --preset congreso --impacto 5,12,18
    python3 pptx_dinamizar.py entrada.pptx salida.pptx --preset sobrio --sin-pulido-visual

Presets disponibles: sobrio | congreso | marca
Ver references/presets-estilo.md para el criterio de cada uno.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))

from pptx_transitions import (  # noqa: E402
    AdvanceUpdate,
    EnterUpdate,
    apply_slide_motion_xml,
    set_directory_use_timings,
    validate_pptx_transition_package,
)

# ---------------------------------------------------------------------------
# Presets: cada uno es una lista de transiciones candidatas para diapositivas
# normales, y otra para diapositivas "de alto impacto" (fondo oscuro, cierre
# narrativo — ver SKILL.md de presentaciones-cientificas). El driver cicla la
# lista normal para que el deck no se sienta repetitivo, y reserva la lista de
# impacto para los números de diapositiva indicados en --impacto.
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict[str, object]] = {
    "sobrio": {
        "normales": ["fade", "push", "wipe"],
        "impacto": ["morph"],
        "duracion": 0.5,
    },
    "congreso": {
        "normales": ["morph", "reveal", "cube", "gallery", "doors"],
        "impacto": ["fracture", "prestige", "vortex"],
        "duracion": 0.6,
    },
    "marca": {
        # Igual de conservador que "sobrio": nunca competir visualmente con un
        # logo o plantilla institucional que el usuario ya definió.
        "normales": ["fade", "push"],
        "impacto": ["morph"],
        "duracion": 0.45,
    },
    "ficha_clinica": {
        # Mismo criterio que "marca": el diseño ya lleva suficiente peso visual
        # propio (tarjeta, semáforo de color, tabla) como para que además la
        # transición compita por atención.
        "normales": ["fade", "push"],
        "impacto": ["morph"],
        "duracion": 0.4,
    },
}


def _slide_parts(extract_dir: Path) -> list[Path]:
    slides_dir = extract_dir / "ppt" / "slides"
    parts = sorted(
        slides_dir.glob("slide*.xml"),
        key=lambda p: int("".join(filter(str.isdigit, p.stem)) or 0),
    )
    if not parts:
        raise SystemExit(f"No se encontraron diapositivas en {slides_dir}")
    return parts


def _rezip(extract_dir: Path, output_path: Path) -> None:
    if output_path.exists():
        output_path.unlink()
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(extract_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(extract_dir).as_posix())


def dinamizar(
    input_pptx: Path,
    output_pptx: Path,
    preset: str,
    impacto: list[int] | None = None,
    autoplay: bool = False,
    morph_en: list[int] | None = None,
) -> dict[str, str]:
    if preset not in PRESETS:
        raise SystemExit(f"Preset desconocido: {preset!r}. Usa: {', '.join(PRESETS)}")
    cfg = PRESETS[preset]
    impacto = set(impacto or [])
    # --morph-en fuerza la transición "morph" en diapositivas puntuales SIN
    # importar qué le tocaría por el ciclo normal del preset. Existe aparte de
    # --impacto porque Morph no es "la transición más dramática del preset" —
    # es una transición con un requisito estructural propio: solo produce el
    # efecto de transformación fluida si la diapositiva anterior y esta
    # comparten formas con EXACTAMENTE el mismo nombre (ver
    # references/tecnica-morph-real.md, técnica confirmada analizando el
    # tutorial de Morph de Jazz Guzman). Si el usuario/skill construyó ese par
    # de diapositivas a propósito (por ejemplo con
    # scripts/pptx_morph_helper.py), aquí se le pone la transición correcta en
    # la diapositiva de llegada del par.
    morph_en = set(morph_en or [])

    work_dir = output_pptx.parent / f".{output_pptx.stem}_extract"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    with zipfile.ZipFile(input_pptx, "r") as zf:
        zf.extractall(work_dir)

    applied: dict[str, str] = {}
    normales = cfg["normales"]
    for i, slide_path in enumerate(_slide_parts(work_dir), start=1):
        if i in morph_en:
            effect = "morph"
        else:
            effect = cfg["impacto"][i % len(cfg["impacto"])] if i in impacto else normales[i % len(normales)]
        slide_xml = slide_path.read_text(encoding="utf-8")
        updated_xml, _ = apply_slide_motion_xml(
            slide_xml,
            enter=EnterUpdate(effect=effect, duration=float(cfg["duracion"])),
            advance=AdvanceUpdate(mode="preserve"),
        )
        slide_path.write_text(updated_xml, encoding="utf-8")
        applied[slide_path.name] = effect

    if autoplay:
        set_directory_use_timings(work_dir, enabled=True)

    _rezip(work_dir, output_pptx)
    shutil.rmtree(work_dir)

    # QA obligatoria: si algo quedó mal formado, esto lanza ValueError y el
    # script debe fallar ruidosamente en vez de entregar un .pptx sospechoso.
    validate_pptx_transition_package(output_pptx)

    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument("--preset", choices=list(PRESETS), default="sobrio")
    parser.add_argument(
        "--impacto",
        default="",
        help="Números de diapositiva (1-indexado) separados por coma que deben "
        "recibir la transición de alto impacto del preset, ej: 5,12,18",
    )
    parser.add_argument(
        "--autoplay",
        action="store_true",
        help="Marca la presentación para reproducir con temporización activada "
        "(útil solo si además se añaden builds; con este script normalmente no hace falta)",
    )
    parser.add_argument(
        "--morph-en",
        default="",
        help="Números de diapositiva (1-indexado) que deben recibir la transición "
        "Morph a la fuerza, sin importar el preset — usar SOLO en la diapositiva "
        "de llegada de un par construido con pptx_morph_helper.py (formas con "
        "nombres idénticos en ambas diapositivas), ej: 6,7",
    )
    args = parser.parse_args()

    impacto = [int(x) for x in args.impacto.split(",") if x.strip()]
    morph_en = [int(x) for x in args.morph_en.split(",") if x.strip()]
    applied = dinamizar(args.entrada, args.salida, args.preset, impacto, args.autoplay, morph_en)

    print(f"Transiciones aplicadas ({args.preset}) -> {args.salida}")
    for name, effect in applied.items():
        print(f"  {name}: {effect}")
    print("Validación de paquete: OK")


if __name__ == "__main__":
    main()
