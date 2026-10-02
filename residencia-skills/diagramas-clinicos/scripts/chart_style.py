"""
chart_style.py — Helpers de matplotlib con estilo clínico/académico consistente.

Por qué existe este módulo: cuando hay que graficar datos numéricos (riesgos,
NNT, tendencias, cronogramas) es tentador escribir un script de matplotlib
desde cero cada vez, y eso produce gráficos inconsistentes entre sí (colores
distintos, sin fuente citada, sin unidades). Este módulo centraliza las
funciones más comunes para que cualquier gráfico que salga de la skill
"diagramas-clinicos" se vea como parte de la misma familia visual y siempre
incluya la fuente de los datos — algo obligatorio bajo el filtro de realidad
del usuario (nunca se grafica un número sin poder decir de dónde salió).

Uso típico:
    from chart_style import forest_plot, bar_comparison, timeline, line_chart, save

    fig, ax = forest_plot(
        labels=["Estudio A (2023)", "Estudio B (2024)"],
        point=[0.75, 0.60],
        lower=[0.60, 0.45],
        upper=[0.95, 0.80],
        xlabel="Riesgo relativo (IC 95%)",
        reference_line=1.0,
        source="Metaanálisis X et al., 2024, Lancet — [Evidencia]",
    )
    save(fig, "forest_plot.png")
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Paleta clínica: apta para daltonismo, consistente entre todos los gráficos.
COLOR_PRIMARY = "#1565C0"   # azul — dato principal / brazo de intervención
COLOR_SECONDARY = "#EF6C00"  # naranja — comparador / brazo control
COLOR_NEUTRAL = "#616161"   # gris — líneas de referencia, ejes
COLOR_POSITIVE = "#2E7D32"  # verde — resultado favorable / hito alcanzado
COLOR_NEGATIVE = "#C62828"  # rojo — resultado desfavorable / alarma
FONT_FAMILY = "DejaVu Sans"  # disponible por defecto, evita fallos de fuente

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "font.size": 11,
    "axes.edgecolor": COLOR_NEUTRAL,
    "axes.labelcolor": "#212121",
    "text.color": "#212121",
    "xtick.color": "#212121",
    "ytick.color": "#212121",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def _add_source_footer(fig, source: str | None):
    """Agrega la fuente citada al pie del gráfico. Si no hay fuente, agrega
    una nota visible de [No verificado] en vez de omitirla silenciosamente —
    un gráfico sin fuente clínica no debe verse igual a uno con evidencia."""
    if source:
        fig.text(0.01, 0.01, f"Fuente: {source}", fontsize=8,
                  color=COLOR_NEUTRAL, ha="left", va="bottom")
    else:
        fig.text(0.01, 0.01, "Fuente: [No verificado] — dato sin cita confirmada",
                  fontsize=8, color=COLOR_NEGATIVE, ha="left", va="bottom")


def forest_plot(labels, point, lower, upper, xlabel="Riesgo relativo (IC 95%)",
                 reference_line=1.0, source=None, title=None, figsize=None):
    """Forest plot para RR, OR, HR con intervalos de confianza.

    labels: nombres de los estudios/subgrupos (de arriba hacia abajo en el orden dado)
    point, lower, upper: listas del mismo largo con el estimador puntual y el IC
    reference_line: valor de "sin efecto" (1.0 para RR/OR/HR, 0 para diferencias de medias)
    """
    n = len(labels)
    figsize = figsize or (7, 1.2 + 0.5 * n)
    fig, ax = plt.subplots(figsize=figsize)
    y = list(range(n, 0, -1))  # primer estudio arriba
    err_low = [p - l for p, l in zip(point, lower)]
    err_high = [u - p for p, u in zip(point, upper)]
    ax.errorbar(point, y, xerr=[err_low, err_high], fmt="s", markersize=7,
                color=COLOR_PRIMARY, ecolor=COLOR_PRIMARY, capsize=4, linewidth=1.5)
    ax.axvline(reference_line, color=COLOR_NEUTRAL, linestyle="--", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylim(0.3, n + 0.7)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _add_source_footer(fig, source)
    return fig, ax


def bar_comparison(categories, values, group_labels=None, ylabel="", source=None,
                    title=None, colors=None, figsize=(7, 4.5)):
    """Barras comparativas (una o varias series). Útil para NNT/NNH, prevalencias,
    tasas de eventos entre brazos de tratamiento, etc.

    values: lista de listas — una lista por serie/grupo, cada una del largo de categories.
    Si solo hay una serie, pasar [[v1, v2, ...]].
    """
    import numpy as np
    fig, ax = plt.subplots(figsize=figsize)
    n_groups = len(values)
    n_cats = len(categories)
    width = 0.8 / n_groups
    default_colors = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_POSITIVE, COLOR_NEGATIVE]
    colors = colors or default_colors
    x = np.arange(n_cats)
    for i, series in enumerate(values):
        offset = (i - (n_groups - 1) / 2) * width
        label = group_labels[i] if group_labels else None
        ax.bar(x + offset, series, width=width, color=colors[i % len(colors)], label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold")
    if group_labels:
        ax.legend(frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _add_source_footer(fig, source)
    return fig, ax


def timeline(events, source=None, title=None, figsize=(9, 3.5)):
    """Línea de tiempo horizontal.

    events: lista de tuplas (fecha_o_hito: str, etiqueta: str), en orden cronológico.
    Ejemplo: [("2018", "Publicación guía KDIGO"), ("2024", "Actualización de umbrales")]
    """
    fig, ax = plt.subplots(figsize=figsize)
    n = len(events)
    xs = list(range(n))
    ax.hlines(0, -0.3, n - 0.7, color=COLOR_NEUTRAL, linewidth=2)
    ax.scatter(xs, [0] * n, s=90, color=COLOR_PRIMARY, zorder=3)
    for i, (fecha, etiqueta) in enumerate(events):
        va = "bottom" if i % 2 == 0 else "top"
        y_text = 0.15 if i % 2 == 0 else -0.15
        ax.annotate(f"{fecha}\n{etiqueta}", (xs[i], 0), xytext=(xs[i], y_text),
                    ha="center", va=va, fontsize=9.5)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=20)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _add_source_footer(fig, source)
    return fig, ax


def line_chart(x, series: dict, xlabel="", ylabel="", source=None, title=None,
                figsize=(7, 4.5)):
    """Curvas (ej. evolución de un parámetro, curvas de supervivencia simplificadas).

    series: dict {nombre_serie: [valores...]}, todas del mismo largo que x.
    """
    fig, ax = plt.subplots(figsize=figsize)
    palette = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_POSITIVE, COLOR_NEGATIVE]
    for i, (name, ys) in enumerate(series.items()):
        ax.plot(x, ys, marker="o", label=name, color=palette[i % len(palette)], linewidth=2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold")
    if len(series) > 1:
        ax.legend(frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _add_source_footer(fig, source)
    return fig, ax


def save(fig, path, dpi=300):
    """Guarda en alta resolución (300 dpi = calidad de impresión/Word/PDF).
    Para diapositivas basta con 150-200 dpi; usar dpi=150 si el archivo pesa mucho."""
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
