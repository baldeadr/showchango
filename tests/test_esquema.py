import pytest
from pydantic import ValidationError

from showchango.core.esquema import (
    Pista,
    Proyecto,
    Transicion,
    a_texto,
    de_texto,
    nuevo_id,
    nuevo_proyecto,
)


def test_nuevo_proyecto_vacio():
    p = nuevo_proyecto()
    assert p.schema_version == 1
    assert p.app == "showchango"
    assert p.pistas == []
    assert p.orden == []


def test_round_trip():
    proyecto = nuevo_proyecto(nombre="Test", artista="DJ")
    p1 = Pista(id=nuevo_id(), titulo="Canción A", bpm=128, energia=0.8)
    p2 = Pista(id=nuevo_id(), titulo="Canción B", bpm=90, energia=0.4)
    proyecto.pistas = [p1, p2]
    proyecto.orden = [p1.id, p2.id]
    proyecto.transiciones = [Transicion(despues_de=p1.id, nota="crossfade")]

    texto = a_texto(proyecto)
    restaurado = de_texto(texto)
    assert a_texto(restaurado) == texto
    assert restaurado.show.nombre == "Test"
    assert len(restaurado.pistas) == 2
    assert restaurado.orden == [p1.id, p2.id]


def test_energia_fuera_de_rango():
    with pytest.raises(ValidationError):
        Pista(id=nuevo_id(), titulo="X", energia=1.5)


def test_duracion_negativa():
    with pytest.raises(ValidationError):
        Pista(id=nuevo_id(), titulo="X", duracion_s=-10)


def test_orden_con_id_desconocido():
    with pytest.raises(ValidationError):
        Proyecto(pistas=[Pista(id="abc", titulo="A")], orden=["xyz"])


def test_orden_con_id_duplicado():
    with pytest.raises(ValidationError):
        Proyecto(pistas=[Pista(id="abc", titulo="A")], orden=["abc", "abc"])


def test_transicion_con_id_desconocido():
    with pytest.raises(ValidationError):
        Proyecto(
            pistas=[Pista(id="abc", titulo="A")],
            transiciones=[Transicion(despues_de="xyz")],
        )


def test_schema_desconocido():
    with pytest.raises(ValidationError):
        de_texto('{"schema": 2, "app": "showchango"}')


def test_campo_extra_rechazado():
    with pytest.raises(ValidationError):
        Proyecto(campo_desconocido=True)
