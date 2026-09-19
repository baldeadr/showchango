from showchango.core.diagnostico import (
    detectar_bloques_repetidos,
    detectar_posiciones_desperdiciadas,
    detectar_valles_picos,
    diagnosticar,
    listar_plantillas,
)
from showchango.core.esquema import Pista, Proyecto, nuevo_id, nuevo_proyecto


def _proyecto_con_pistas(*pistas: Pista) -> Proyecto:
    proyecto = nuevo_proyecto("Set", "Test")
    proyecto.pistas = list(pistas)
    proyecto.orden = [p.id for p in pistas]
    return proyecto


def test_listar_plantillas():
    plantillas = listar_plantillas()
    ids = {p.id for p in plantillas}
    assert ids == {
        "climax_70",
        "construccion_dj",
        "picos_rock",
        "electronica",
        "rock",
        "cumbia",
        "industrial_bailable",
    }


def test_detectar_pico():
    pistas = [
        Pista(id=nuevo_id(), titulo="Baja", energia=0.3, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Pico", energia=0.8, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Baja2", energia=0.3, duracion_s=60),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    alertas = detectar_valles_picos(proyecto)
    assert any(a.tipo == "pico" and "Pico" in a.mensaje for a in alertas)


def test_detectar_valle():
    pistas = [
        Pista(id=nuevo_id(), titulo="Alta", energia=0.8, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Valle", energia=0.2, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Alta2", energia=0.8, duracion_s=60),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    alertas = detectar_valles_picos(proyecto)
    assert any(a.tipo == "valle" and "Valle" in a.mensaje for a in alertas)


def test_detectar_bloque_repetido():
    pistas = [
        Pista(id=nuevo_id(), titulo="A", bpm=120, energia=0.5, duracion_s=60),
        Pista(id=nuevo_id(), titulo="B", bpm=122, energia=0.52, duracion_s=60),
        Pista(id=nuevo_id(), titulo="C", bpm=121, energia=0.51, duracion_s=60),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    alertas = detectar_bloques_repetidos(proyecto)
    assert len(alertas) == 1
    assert alertas[0].tipo == "bloque_repetido"
    assert "A, B, C" in alertas[0].mensaje


def test_detectar_posicion_pico_temprano():
    pistas = [
        Pista(id=nuevo_id(), titulo="Pico temprano", energia=0.9, duracion_s=30),
        Pista(id=nuevo_id(), titulo="Resto", energia=0.4, duracion_s=300),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    alertas = detectar_posiciones_desperdiciadas(proyecto)
    assert any(a.tipo == "posicion_desperdiciada" and "temprano" in a.mensaje for a in alertas)


def test_diagnostico_climax_70_alerta_fuera_de_rango():
    # Clímax al inicio, debería alertar
    pistas = [
        Pista(id=nuevo_id(), titulo="Inicio", energia=0.2, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Climax", energia=0.9, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Final", energia=0.3, duracion_s=300),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    diag = diagnosticar(proyecto, "climax_70")
    assert diag.plantilla_id == "climax_70"
    assert any(a.tipo == "arco" and "70%" in a.mensaje for a in diag.alertas)


def test_diagnostico_construccion_dj_detecta_bajon():
    pistas = [
        Pista(id=nuevo_id(), titulo="A", energia=0.3, duracion_s=60),
        Pista(id=nuevo_id(), titulo="B", energia=0.6, duracion_s=60),
        Pista(id=nuevo_id(), titulo="C", energia=0.2, duracion_s=60),
        Pista(id=nuevo_id(), titulo="D", energia=0.7, duracion_s=60),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    diag = diagnosticar(proyecto, "construccion_dj")
    assert any(a.tipo == "arco" and "Bajón" in a.mensaje for a in diag.alertas)


def test_diagnostico_picos_rock_detecta_monotonia():
    pistas = [
        Pista(id=nuevo_id(), titulo="A", energia=0.2, duracion_s=60),
        Pista(id=nuevo_id(), titulo="B", energia=0.4, duracion_s=60),
        Pista(id=nuevo_id(), titulo="C", energia=0.6, duracion_s=60),
        Pista(id=nuevo_id(), titulo="D", energia=0.3, duracion_s=60),
    ]
    proyecto = _proyecto_con_pistas(*pistas)
    diag = diagnosticar(proyecto, "picos_rock")
    assert any(a.tipo == "arco" and "monótona" in a.mensaje for a in diag.alertas)


def test_diagnostico_set_vacio():
    proyecto = nuevo_proyecto("Vacio", "Test")
    diag = diagnosticar(proyecto, "climax_70")
    assert diag.alertas == []
