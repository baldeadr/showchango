from __future__ import annotations

from showchango.core.esquema import Proyecto


def calcular_curva(proyecto: Proyecto) -> dict:
    """Devuelve los puntos de la curva de energía/baile del set.

    Cada punto representa el inicio de una pista. Se usa `stepped: 'after'`
    en Chart.js para mantener el valor constante durante toda la duración.

    El resultado es un dict puro y serializable; la UI lo convierte en
    el formato que Chart.js necesite.
    """
    puntos: list[dict] = []
    tiempo_s = 0.0

    for pista_id in proyecto.orden:
        pista = next((p for p in proyecto.pistas if p.id == pista_id), None)
        if pista is None:
            continue
        puntos.append(
            {
                "id": pista.id,
                "titulo": pista.titulo,
                "tiempo_min": round(tiempo_s / 60.0, 2),
                "energia": pista.energia if pista.energia is not None else 0.0,
                "bailabilidad": (
                    pista.bailabilidad if pista.bailabilidad is not None else 0.0
                ),
                "duracion_s": pista.duracion_s if pista.duracion_s is not None else 0.0,
            }
        )
        tiempo_s += pista.duracion_s if pista.duracion_s is not None else 0.0

    return {
        "puntos": puntos,
        "duracion_total_s": round(tiempo_s, 2),
        "duracion_total_min": round(tiempo_s / 60.0, 2),
    }


def datos_para_chartjs(proyecto: Proyecto) -> dict:
    """Adapta la curva al formato más cómodo para Chart.js.

    Devuelve:
    - Puntos de línea `{x: tiempo_min, y: valor}` con `stepped: 'before'`
      para representar la energía/bailabilidad de cada pista durante su
      duración real.
    - Puntos de marcador en el centro de cada pista para identificarla
      visualmente sin confundir los límites.
    """
    curva = calcular_curva(proyecto)
    puntos = curva["puntos"]

    puntos_energia = [{"x": p["tiempo_min"], "y": p["energia"]} for p in puntos]
    puntos_bailabilidad = [
        {"x": p["tiempo_min"], "y": p["bailabilidad"]} for p in puntos
    ]

    if puntos:
        fin = curva["duracion_total_min"]
        puntos_energia.append({"x": fin, "y": puntos[-1]["energia"]})
        puntos_bailabilidad.append({"x": fin, "y": puntos[-1]["bailabilidad"]})

    marcadores_energia = [
        {
            "x": round(p["tiempo_min"] + (p["duracion_s"] / 60.0) / 2, 2),
            "y": p["energia"],
        }
        for p in puntos
    ]
    marcadores_bailabilidad = [
        {
            "x": round(p["tiempo_min"] + (p["duracion_s"] / 60.0) / 2, 2),
            "y": p["bailabilidad"],
        }
        for p in puntos
    ]

    return {
        "etiquetas": [p["titulo"] for p in puntos],
        "energia": [p["energia"] for p in puntos],
        "bailabilidad": [p["bailabilidad"] for p in puntos],
        "tiempos_min": [p["tiempo_min"] for p in puntos],
        "puntos_energia": puntos_energia,
        "puntos_bailabilidad": puntos_bailabilidad,
        "marcadores_energia": marcadores_energia,
        "marcadores_bailabilidad": marcadores_bailabilidad,
        "duraciones_s": [p["duracion_s"] for p in puntos],
        "titulos": [p["titulo"] for p in puntos],
        **curva,
    }
