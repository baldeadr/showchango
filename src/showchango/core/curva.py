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

    Devuelve puntos `{x: tiempo_min, y: valor}` para poder usar el eje X como
    una escala lineal de tiempo real del show.
    """
    curva = calcular_curva(proyecto)
    puntos = curva["puntos"]
    return {
        "etiquetas": [p["titulo"] for p in puntos],
        "energia": [p["energia"] for p in puntos],
        "bailabilidad": [p["bailabilidad"] for p in puntos],
        "tiempos_min": [p["tiempo_min"] for p in puntos],
        "puntos_energia": [{"x": p["tiempo_min"], "y": p["energia"]} for p in puntos],
        "puntos_bailabilidad": [{"x": p["tiempo_min"], "y": p["bailabilidad"]} for p in puntos],
        "titulos": [p["titulo"] for p in puntos],
        **curva,
    }
