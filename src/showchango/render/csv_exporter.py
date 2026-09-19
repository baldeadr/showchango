from __future__ import annotations

import csv
import io

from showchango.core.esquema import Proyecto

_CAMPOS = [
    "orden",
    "titulo",
    "artista",
    "bpm",
    "energia",
    "bailabilidad",
    "duracion_s",
    "duracion_mmss",
    "loudness_db",
    "valencia",
    "voz",
    "genero",
    "tonalidad",
    "notas",
    "fuente",
]


def _segundos_a_mmss(segundos: float | None) -> str:
    if segundos is None or segundos == 0:
        return ""
    total = int(round(segundos))
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def exportar_csv(proyecto: Proyecto) -> str:
    """Devuelve un CSV con las pistas en el orden del set."""
    por_id = {p.id: p for p in proyecto.pistas}
    salida = io.StringIO()
    writer = csv.DictWriter(salida, fieldnames=_CAMPOS)
    writer.writeheader()

    for idx, pista_id in enumerate(proyecto.orden, start=1):
        pista = por_id.get(pista_id)
        if pista is None:
            continue
        writer.writerow(
            {
                "orden": idx,
                "titulo": pista.titulo,
                "artista": pista.artista or "",
                "bpm": pista.bpm if pista.bpm is not None else "",
                "energia": pista.energia if pista.energia is not None else "",
                "bailabilidad": pista.bailabilidad if pista.bailabilidad is not None else "",
                "duracion_s": pista.duracion_s if pista.duracion_s is not None else "",
                "duracion_mmss": _segundos_a_mmss(pista.duracion_s),
                "loudness_db": pista.loudness_db if pista.loudness_db is not None else "",
                "valencia": pista.valencia if pista.valencia is not None else "",
                "voz": pista.voz or "",
                "genero": pista.genero or "",
                "tonalidad": pista.tonalidad or "",
                "notas": pista.notas or "",
                "fuente": pista.fuente or "",
            }
        )

    return salida.getvalue()
