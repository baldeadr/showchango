from __future__ import annotations

from pydantic import BaseModel

from showchango.core.curva import calcular_curva
from showchango.core.esquema import Pista, Proyecto


class Alerta(BaseModel):
    tipo: str
    mensaje: str
    sugerencia: str = ""
    pista_ids: list[str] = []
    posicion: int | None = None


class ArcoPlantilla(BaseModel):
    id: str
    nombre: str
    descripcion: str


class Diagnostico(BaseModel):
    plantilla_id: str
    alertas: list[Alerta]
    plantilla_nombre: str = ""


PLANTILLAS: dict[str, ArcoPlantilla] = {
    "climax_70": ArcoPlantilla(
        id="climax_70",
        nombre="Clímax al 70%",
        descripcion="Energía creciente con el pico principal cerca del 70% del show.",
    ),
    "construccion_dj": ArcoPlantilla(
        id="construccion_dj",
        nombre="Construcción DJ",
        descripcion="Subida progresiva y plateau alto; evitar bajones bruscos.",
    ),
    "picos_rock": ArcoPlantilla(
        id="picos_rock",
        nombre="Picos rock",
        descripcion="Picos y valles alternados para mantener la tensión.",
    ),
    "electronica": ArcoPlantilla(
        id="electronica",
        nombre="Electrónica",
        descripcion="Construcción tipo DJ con bailabilidad sostenida y cierre alto.",
    ),
    "rock": ArcoPlantilla(
        id="rock",
        nombre="Rock",
        descripcion="Picos y valles alternados entre canciones de distinta intensidad.",
    ),
    "cumbia": ArcoPlantilla(
        id="cumbia",
        nombre="Cumbia",
        descripcion="Energía y bailabilidad altas y estables; evitar bajones largos.",
    ),
    "industrial_bailable": ArcoPlantilla(
        id="industrial_bailable",
        nombre="Industrial bailable",
        descripcion="Alta energía con picos agresivos y pocos descansos.",
    ),
}


def listar_plantillas() -> list[ArcoPlantilla]:
    return list(PLANTILLAS.values())


def _pistas_ordenadas(proyecto: Proyecto) -> list[Pista]:
    por_id = {p.id: p for p in proyecto.pistas}
    return [por_id[pid] for pid in proyecto.orden if pid in por_id]


def _energia(pista: Pista) -> float:
    return pista.energia if pista.energia is not None else 0.0


def _bailabilidad(pista: Pista) -> float:
    return pista.bailabilidad if pista.bailabilidad is not None else 0.0


def _bpm(pista: Pista) -> float | None:
    return pista.bpm


def detectar_valles_picos(proyecto: Proyecto, umbral: float = 0.15) -> list[Alerta]:
    puntos = calcular_curva(proyecto)["puntos"]
    alertas: list[Alerta] = []
    for i in range(1, len(puntos) - 1):
        prev_e = puntos[i - 1]["energia"]
        curr_e = puntos[i]["energia"]
        next_e = puntos[i + 1]["energia"]
        if curr_e > prev_e + umbral and curr_e > next_e + umbral:
            alertas.append(
                Alerta(
                    tipo="pico",
                    mensaje=f"Pico de energía en '{puntos[i]['titulo']}'.",
                    sugerencia=(
                        "Verifica que el pico sea intencional; "
                        "si no, rodealo de pistas de transición."
                    ),
                    pista_ids=[puntos[i]["id"]],
                    posicion=i,
                )
            )
        elif curr_e < prev_e - umbral and curr_e < next_e - umbral:
            alertas.append(
                Alerta(
                    tipo="valle",
                    mensaje=f"Valle de energía en '{puntos[i]['titulo']}'.",
                    sugerencia=(
                        "Si el valle no es deliberado, sube la energía "
                        "antes o después para mantener el impulso."
                    ),
                    pista_ids=[puntos[i]["id"]],
                    posicion=i,
                )
            )
    return alertas


def detectar_bloques_repetidos(
    proyecto: Proyecto, min_len: int = 3, umbral_bpm: float = 5.0, umbral_energia: float = 0.1
) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    alertas: list[Alerta] = []
    i = 0
    while i <= len(ordenadas) - min_len:
        bloque = ordenadas[i : i + min_len]
        bpms = [_bpm(p) for p in bloque]
        energias = [_energia(p) for p in bloque]
        if None in bpms:
            i += 1
            continue
        bpm_rango = max(bpms) - min(bpms)  # type: ignore[operator]
        energia_rango = max(energias) - min(energias)
        if bpm_rango <= umbral_bpm and energia_rango <= umbral_energia:
            nombres = ", ".join(p.titulo for p in bloque)
            alertas.append(
                Alerta(
                    tipo="bloque_repetido",
                    mensaje=f"Bloque de {min_len} pistas similares: {nombres}.",
                    sugerencia=(
                        "Intercala texturas, géneros o cambios de intensidad "
                        "para evitar la monotonía."
                    ),
                    pista_ids=[p.id for p in bloque],
                    posicion=i,
                )
            )
            i += min_len
        else:
            i += 1
    return alertas


def detectar_posiciones_desperdiciadas(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if not ordenadas:
        return []

    curva = calcular_curva(proyecto)
    duracion_total = curva["duracion_total_s"]
    alertas: list[Alerta] = []
    tiempo_acumulado = 0.0

    for i, pista in enumerate(ordenadas):
        duracion = pista.duracion_s if pista.duracion_s is not None else 0.0
        energia = _energia(pista)
        progreso = (tiempo_acumulado + duracion / 2) / duracion_total if duracion_total else 0.0

        if energia >= 0.8 and progreso <= 0.2:
            alertas.append(
                Alerta(
                    tipo="posicion_desperdiciada",
                    mensaje=f"'{pista.titulo}' es un pico de energía muy temprano.",
                    sugerencia=(
                        "Reserva los picos altos para la mitad o el final del set; "
                        "al inicio usa pistas de apertura más suaves."
                    ),
                    pista_ids=[pista.id],
                    posicion=i,
                )
            )
        if energia <= 0.3 and progreso >= 0.8:
            alertas.append(
                Alerta(
                    tipo="posicion_desperdiciada",
                    mensaje=f"'{pista.titulo}' baja la energía cerca del final.",
                    sugerencia=(
                        "El cierre suele necesitar energía alta; "
                        "considera subir la intensidad en las últimas pistas."
                    ),
                    pista_ids=[pista.id],
                    posicion=i,
                )
            )
        if duracion == 0:
            alertas.append(
                Alerta(
                    tipo="posicion_desperdiciada",
                    mensaje=f"'{pista.titulo}' no tiene duración, no aporta a la curva.",
                    sugerencia=(
                        "Agrega la duración para que esta pista influya en el "
                        "tiempo total y la curva de energía."
                    ),
                    pista_ids=[pista.id],
                    posicion=i,
                )
            )
        tiempo_acumulado += duracion

    return alertas


def _comparar_climax_70(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if len(ordenadas) < 3:
        return []
    curva = calcular_curva(proyecto)
    duracion_total = curva["duracion_total_s"]
    if not duracion_total:
        return []

    max_energia = max(_energia(p) for p in ordenadas)
    idx_max = max(range(len(ordenadas)), key=lambda i: _energia(ordenadas[i]))
    pista_max = ordenadas[idx_max]
    tiempo_max = curva["puntos"][idx_max]["tiempo_min"] * 60.0
    progreso_max = tiempo_max / duracion_total

    alertas: list[Alerta] = []
    if progreso_max < 0.6 or progreso_max > 0.8:
        msg = (
            f"El clímax ('{pista_max.titulo}') está al {int(progreso_max * 100)}%; "
            "la plantilla 'Clímax al 70%' lo espera cerca del 70%."
        )
        alertas.append(
            Alerta(
                tipo="arco",
                mensaje=msg,
                sugerencia=(
                    "Mueve la pista de mayor energía hacia el 60-80% del set "
                    "o elige otra como clímax."
                ),
                pista_ids=[pista_max.id],
                posicion=idx_max,
            )
        )
    if max_energia < 0.7:
        alertas.append(
            Alerta(
                tipo="arco",
                mensaje=(
                    f"El clímax del set no alcanza una energía alta "
                    f"(máximo {max_energia * 100:.0f}%)."
                ),
                sugerencia=(
                    "Incluye al menos una pista con energía ≥ 0.7 "
                    "para dar un punto alto al show."
                ),
                pista_ids=[pista_max.id],
            )
        )
    return alertas


def _comparar_construccion_dj(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if len(ordenadas) < 3:
        return []
    alertas: list[Alerta] = []
    for i in range(1, len(ordenadas) - 1):
        prev_e = _energia(ordenadas[i - 1])
        curr_e = _energia(ordenadas[i])
        next_e = _energia(ordenadas[i + 1])
        if curr_e < prev_e - 0.2 and curr_e < next_e - 0.2:
            alertas.append(
                Alerta(
                    tipo="arco",
                    mensaje=(
                        f"Bajón de energía en '{ordenadas[i].titulo}' "
                        "rompe la construcción DJ."
                    ),
                    sugerencia=(
                        "Sube la energía de esta pista o reubícala "
                        "para mantener la escalada del set."
                    ),
                    pista_ids=[ordenadas[i].id],
                    posicion=i,
                )
            )
    ultima = ordenadas[-1]
    max_e = max(_energia(p) for p in ordenadas)
    if _energia(ultima) < max_e - 0.25:
        alertas.append(
            Alerta(
                tipo="arco",
                mensaje=(
                    f"La última pista ('{ultima.titulo}') no cierra "
                    "en la energía más alta del set."
                ),
                sugerencia=(
                    "Termina con una pista de energía similar al clímax "
                    "para un cierre contundente."
                ),
                pista_ids=[ultima.id],
                posicion=len(ordenadas) - 1,
            )
        )
    return alertas


def _comparar_picos_rock(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if len(ordenadas) < 4:
        return []
    alertas: list[Alerta] = []
    energias = [_energia(p) for p in ordenadas]
    # Buscar tramos monótonos de >= 3 pistas (falta de contraste)
    i = 0
    while i < len(energias) - 2:
        sube = energias[i] < energias[i + 1] < energias[i + 2]
        baja = energias[i] > energias[i + 1] > energias[i + 2]
        if sube or baja:
            nombres = ", ".join(ordenadas[j].titulo for j in range(i, i + 3))
            tipo_txt = "subida" if sube else "bajada"
            alertas.append(
                Alerta(
                    tipo="arco",
                    mensaje=(
                        f"{tipo_txt.capitalize()} monótona de 3 pistas ({nombres}); "
                        "'Picos rock' necesita más contraste."
                    ),
                    sugerencia=(
                        "Intercambia el orden de estas pistas para crear "
                        "picos y valles alternados."
                    ),
                    pista_ids=[ordenadas[j].id for j in range(i, i + 3)],
                    posicion=i,
                )
            )
            i += 3
        else:
            i += 1
    return alertas


def _comparar_cumbia(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if len(ordenadas) < 3:
        return []
    alertas: list[Alerta] = []
    for i, pista in enumerate(ordenadas):
        if _bailabilidad(pista) < 0.4:
            alertas.append(
                Alerta(
                    tipo="arco",
                    mensaje=(
                        f"'{pista.titulo}' tiene baja bailabilidad "
                        "para una noche de cumbia."
                    ),
                    sugerencia=(
                        "Busca versiones o pistas que mantengan "
                        "el piso de baile activo."
                    ),
                    pista_ids=[pista.id],
                    posicion=i,
                )
            )
    for i in range(1, len(ordenadas)):
        prev_e = _energia(ordenadas[i - 1])
        curr_e = _energia(ordenadas[i])
        if prev_e - curr_e > 0.25:
            alertas.append(
                Alerta(
                    tipo="arco",
                    mensaje=(
                        f"Bajón de energía entre '{ordenadas[i - 1].titulo}' "
                        f"y '{ordenadas[i].titulo}'."
                    ),
                    sugerencia=(
                        "Evita caídas bruscas; la cumbia funciona mejor "
                        "con energía estable."
                    ),
                    pista_ids=[ordenadas[i - 1].id, ordenadas[i].id],
                    posicion=i,
                )
            )
    return alertas


def _comparar_industrial(proyecto: Proyecto) -> list[Alerta]:
    ordenadas = _pistas_ordenadas(proyecto)
    if len(ordenadas) < 3:
        return []
    alertas: list[Alerta] = []
    for i, pista in enumerate(ordenadas):
        if i >= len(ordenadas) // 2 and _energia(pista) < 0.5:
            alertas.append(
                Alerta(
                    tipo="arco",
                    mensaje=(
                        f"'{pista.titulo}' baja mucho la energía "
                        "en la segunda mitad."
                    ),
                    sugerencia=(
                        "Mantén la intensidad alta; el industrial bailable "
                        "no suele dar descansos largos."
                    ),
                    pista_ids=[pista.id],
                    posicion=i,
                )
            )
    picos = sum(1 for i in range(1, len(ordenadas) - 1) if _energia(ordenadas[i]) > 0.8)
    if picos < 2:
        alertas.append(
            Alerta(
                tipo="arco",
                mensaje="Faltan picos de energía agresivos en el set.",
                sugerencia=(
                    "Incluye al menos dos pistas con energía muy alta "
                    "para marcar momentos de impacto."
                ),
            )
        )
    return alertas


_COMPARADORES = {
    "climax_70": _comparar_climax_70,
    "construccion_dj": _comparar_construccion_dj,
    "picos_rock": _comparar_picos_rock,
    "electronica": _comparar_construccion_dj,
    "rock": _comparar_picos_rock,
    "cumbia": _comparar_cumbia,
    "industrial_bailable": _comparar_industrial,
}


def diagnosticar(proyecto: Proyecto, plantilla_id: str = "climax_70") -> Diagnostico:
    if not proyecto.orden:
        return Diagnostico(plantilla_id=plantilla_id, alertas=[], plantilla_nombre="")

    plantilla = PLANTILLAS.get(plantilla_id)
    if plantilla is None:
        plantilla = PLANTILLAS["climax_70"]
        plantilla_id = plantilla.id

    alertas: list[Alerta] = []
    alertas.extend(detectar_valles_picos(proyecto))
    alertas.extend(detectar_bloques_repetidos(proyecto))
    alertas.extend(detectar_posiciones_desperdiciadas(proyecto))

    comparador = _COMPARADORES.get(plantilla_id)
    if comparador is not None:
        alertas.extend(comparador(proyecto))

    return Diagnostico(
        plantilla_id=plantilla_id,
        plantilla_nombre=plantilla.nombre,
        alertas=alertas,
    )
