from __future__ import annotations

from pydantic import BaseModel

from showchango.core.diagnostico import _bailabilidad, _energia
from showchango.core.esquema import Pista, Proyecto


class Recomendacion(BaseModel):
    orden: list[str]
    titulos: list[str]
    explicacion: str
    plantilla_id: str


def _pistas_ordenadas(proyecto: Proyecto) -> list[Pista]:
    por_id = {p.id: p for p in proyecto.pistas}
    return [por_id[pid] for pid in proyecto.orden if pid in por_id]


def _insertar_pico(pistas: list[Pista]) -> list[Pista]:
    if not pistas:
        return []
    por_energia = sorted(pistas, key=_energia)
    pico = por_energia.pop()
    n = len(por_energia)
    pos = max(1, int(n * 0.65))
    return por_energia[:pos] + [pico] + por_energia[pos:]


def _alternar_intensidad(pistas: list[Pista]) -> list[Pista]:
    ordenadas = sorted(pistas, key=_energia, reverse=True)
    resultado: list[Pista] = []
    altas = ordenadas[::2]
    bajas = list(reversed(ordenadas[1::2]))
    for i, alta in enumerate(altas):
        resultado.append(alta)
        if i < len(bajas):
            resultado.append(bajas[i])
    return resultado


def recomendar_orden(proyecto: Proyecto, plantilla_id: str = "climax_70") -> Recomendacion:
    pistas = _pistas_ordenadas(proyecto)
    if not pistas:
        return Recomendacion(orden=[], titulos=[], explicacion="", plantilla_id=plantilla_id)

    if plantilla_id in {"climax_70"}:
        orden = _insertar_pico(pistas)
        explicacion = (
            "Orden de energía creciente con el pico principal cerca del 65-70% "
            "del set para construir tensión antes del clímax."
        )
    elif plantilla_id in {"construccion_dj", "electronica"}:
        orden = sorted(pistas, key=_energia)
        explicacion = (
            "Construcción progresiva: pistas suaves al inicio y cierre en la energía "
            "más alta, manteniendo la pista de baile activa."
        )
    elif plantilla_id in {"picos_rock", "rock"}:
        orden = _alternar_intensidad(pistas)
        explicacion = (
            "Alternancia de pistas intensas y de respiro para mantener la atención "
            "y la dinámica propia del rock."
        )
    elif plantilla_id == "cumbia":
        orden = sorted(
            pistas, key=lambda p: (_energia(p) * _bailabilidad(p), _bailabilidad(p)), reverse=True
        )
        explicacion = (
            "Prioriza pistas con alta energía y alta bailabilidad de principio a fin, "
            "evitando bajones en la pista."
        )
    elif plantilla_id == "industrial_bailable":
        orden = sorted(pistas, key=_energia, reverse=True)
        explicacion = (
            "Comienza fuerte y mantén la intensidad alta; pocas pausas para un set "
            "agresivo y bailable."
        )
    else:
        orden = pistas
        explicacion = "Se mantiene el orden actual."

    return Recomendacion(
        orden=[p.id for p in orden],
        titulos=[p.titulo for p in orden],
        explicacion=explicacion,
        plantilla_id=plantilla_id,
    )
