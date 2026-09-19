from showchango.core.esquema import Pista, nuevo_id, nuevo_proyecto
from showchango.core.recomendador import recomendar_orden


def _proyecto_de_ejemplo():
    proyecto = nuevo_proyecto("Set", "Test")
    pistas = [
        Pista(id=nuevo_id(), titulo="Apertura", energia=0.2, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Medio", energia=0.5, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Climax", energia=0.9, duracion_s=60),
        Pista(id=nuevo_id(), titulo="Cierre", energia=0.4, duracion_s=60),
    ]
    proyecto.pistas = pistas
    proyecto.orden = [p.id for p in pistas]
    return proyecto


def test_recomendar_climax_70_pone_pico_cerca_del_70():
    proyecto = _proyecto_de_ejemplo()
    rec = recomendar_orden(proyecto, "climax_70")
    assert rec.plantilla_id == "climax_70"
    assert "Climax" in rec.titulos
    # La pista de mayor energía debería quedar en posición 1 o 2 (65% aprox)
    idx_climax = rec.titulos.index("Climax")
    assert 1 <= idx_climax <= 2


def test_recomendar_industrial_orden_descendente():
    proyecto = _proyecto_de_ejemplo()
    rec = recomendar_orden(proyecto, "industrial_bailable")
    assert rec.titulos[0] == "Climax"


def test_recomendar_vacio():
    proyecto = nuevo_proyecto("Vacio", "Test")
    rec = recomendar_orden(proyecto, "climax_70")
    assert rec.orden == []
    assert rec.explicacion == ""
