from showchango.core.curva import calcular_curva, datos_para_chartjs
from showchango.core.esquema import Pista, Proyecto


def test_curva_vacia():
    proyecto = Proyecto()
    curva = calcular_curva(proyecto)
    assert curva["puntos"] == []
    assert curva["duracion_total_s"] == 0.0


def test_curva_acumula_tiempos():
    a = Pista(id="a", titulo="A", energia=0.2, duracion_s=120)
    b = Pista(id="b", titulo="B", energia=0.8, duracion_s=180)
    proyecto = Proyecto(pistas=[a, b], orden=["a", "b"])

    curva = calcular_curva(proyecto)
    assert len(curva["puntos"]) == 2
    assert curva["puntos"][0]["tiempo_min"] == 0.0
    assert curva["puntos"][1]["tiempo_min"] == 2.0
    assert curva["duracion_total_min"] == 5.0
    assert curva["puntos"][1]["energia"] == 0.8


def test_curva_respeta_orden():
    a = Pista(id="a", titulo="A", energia=0.2, duracion_s=60)
    b = Pista(id="b", titulo="B", energia=0.9, duracion_s=60)
    proyecto = Proyecto(pistas=[a, b], orden=["b", "a"])

    curva = calcular_curva(proyecto)
    assert curva["puntos"][0]["titulo"] == "B"
    assert curva["puntos"][1]["titulo"] == "A"


def test_curva_valores_por_defecto():
    a = Pista(id="a", titulo="A")
    proyecto = Proyecto(pistas=[a], orden=["a"])

    curva = calcular_curva(proyecto)
    assert curva["puntos"][0]["energia"] == 0.0
    assert curva["puntos"][0]["bailabilidad"] == 0.0
    assert curva["puntos"][0]["duracion_s"] == 0.0


def test_datos_para_chartjs():
    a = Pista(id="a", titulo="A", energia=0.5, bailabilidad=0.6, duracion_s=100)
    proyecto = Proyecto(pistas=[a], orden=["a"])
    datos = datos_para_chartjs(proyecto)
    assert datos["etiquetas"] == ["A"]
    assert datos["energia"] == [0.5]
    assert datos["bailabilidad"] == [0.6]
    assert datos["tiempos_min"] == [0.0]
    assert datos["puntos_energia"][0] == {"x": 0.0, "y": 0.5}
    assert datos["puntos_energia"][-1] == {
        "x": datos["duracion_total_min"],
        "y": 0.5,
    }
    assert datos["puntos_bailabilidad"][0] == {"x": 0.0, "y": 0.6}
    assert datos["puntos_bailabilidad"][-1] == {
        "x": datos["duracion_total_min"],
        "y": 0.6,
    }
    assert datos["radios_energia"] == [0, 4]
    assert datos["radios_bailabilidad"] == [0, 4]
    assert datos["duraciones_s"] == [100]
    assert datos["titulos"] == ["A"]
    assert datos["titulos_marcadores"] == ["", "A"]
