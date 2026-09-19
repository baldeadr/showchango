from __future__ import annotations

from showchango.core.curva import calcular_curva
from showchango.core.esquema import Proyecto


def _mmss(segundos: float | None) -> str:
    if segundos is None or segundos == 0:
        return "—"
    total = int(round(segundos))
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def exportar_markdown(proyecto: Proyecto) -> str:
    """Devuelve un Markdown estructurado del show, útil para LLMs y para leer."""
    show = proyecto.show
    curva = calcular_curva(proyecto)
    por_id = {p.id: p for p in proyecto.pistas}

    lineas: list[str] = [
        f"# {show.nombre or 'Set sin nombre'}",
        "",
        f"- **Artista:** {show.artista or 'Sin artista'}",
        f"- **Pistas:** {len(proyecto.orden)}",
        f"- **Duración total:** {_mmss(curva['duracion_total_s'])}",
        "",
        "## Setlist",
        "",
        "| # | Título | Artista | BPM | E | Duración | Tonalidad | Notas |",
        "|---|--------|---------|-----|---|----------|-----------|-------|",
    ]

    for idx, pista_id in enumerate(proyecto.orden, start=1):
        pista = por_id.get(pista_id)
        if pista is None:
            continue
        lineas.append(
            f"| {idx} | {pista.titulo} | {pista.artista or '—'} | "
            f"{pista.bpm if pista.bpm is not None else '—'} | "
            f"{pista.energia if pista.energia is not None else '—'} | "
            f"{_mmss(pista.duracion_s)} | "
            f"{pista.tonalidad or '—'} | {pista.notas or '—'} |"
        )

    lineas.extend(
        [
            "",
            "## Curva de energía",
            "",
        ]
    )
    for punto in curva["puntos"]:
        lineas.append(
            f"- {punto['tiempo_min']:.1f} min — {punto['titulo']} (E={punto['energia']:.2f})"
        )

    lineas.extend(
        [
            "",
            "---",
            "",
            "Exportado desde Show Chango.",
            "",
        ]
    )
    return "\n".join(lineas)
