from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from showchango.core.curva import calcular_curva
from showchango.core.esquema import Proyecto


def renderizar_curva(proyecto: Proyecto, formato: str = "png") -> bytes:
    """Genera una imagen PNG o SVG de la curva de energía/baile del set."""
    if formato not in {"png", "svg"}:
        raise ValueError("formato debe ser 'png' o 'svg'")

    curva = calcular_curva(proyecto)
    puntos = curva["puntos"]
    tiempos = [p["tiempo_min"] for p in puntos]
    energias = [p["energia"] for p in puntos]
    bailabilidades = [p["bailabilidad"] for p in puntos]
    titulos = [p["titulo"] for p in puntos]

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#0f0f11")
    ax.set_facecolor("#0f0f11")

    ax.step(tiempos, energias, where="post", label="Energía", color="#ff6b35", linewidth=2)
    if any(b > 0 for b in bailabilidades):
        ax.step(
            tiempos,
            bailabilidades,
            where="post",
            label="Bailabilidad",
            color="#5B8CFF",
            linewidth=2,
        )

    ax.set_xlabel("Tiempo (min)", color="#e6e6e6")
    ax.set_ylabel("Intensidad (0–1)", color="#e6e6e6")
    ax.set_title(
        f"{proyecto.show.nombre or 'Set'} — {proyecto.show.artista or 'Sin artista'}",
        color="#e6e6e6",
        loc="left",
    )
    ax.tick_params(colors="#999")
    ax.set_ylim(0, 1.05)
    ax.legend(facecolor="#1a1a1f", edgecolor="#2a2a30", labelcolor="#e6e6e6")
    ax.spines["bottom"].set_color("#2a2a30")
    ax.spines["left"].set_color("#2a2a30")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(color="#2a2a30", linestyle="--", linewidth=0.5)

    if titulos:
        ax.set_xticks(tiempos)
        ax.set_xticklabels(titulos, rotation=45, ha="right", fontsize=8)

    buffer = io.BytesIO()
    kwargs = {"facecolor": "#0f0f11", "edgecolor": "none", "bbox_inches": "tight"}
    if formato == "svg":
        plt.savefig(buffer, format="svg", **kwargs)
    else:
        plt.savefig(buffer, format="png", **kwargs)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()
