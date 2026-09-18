from fastapi.testclient import TestClient

from showchango.core.esquema import de_texto
from showchango.web.app import crear_app


def client():
    return TestClient(crear_app())


def test_home():
    respuesta = client().get("/")
    assert respuesta.status_code == 200
    assert "Show Chango" in respuesta.text


def test_crear_y_ver_set():
    c = client()
    respuesta = c.post(
        "/set/nuevo",
        data={"nombre": "Trve Café", "artista": "Apex Ultra"},
        follow_redirects=False,
    )
    assert respuesta.status_code == 302
    assert respuesta.headers["location"] == "/set"

    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Trve Café" in respuesta.text
    assert "Apex Ultra" in respuesta.text


def test_exportar_set():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Export", "artista": "Test"})
    respuesta = c.get("/set/exportar")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/json"

    proyecto = de_texto(respuesta.text)
    assert proyecto.schema_version == 1
    assert proyecto.show.nombre == "Export"


def test_cerrar_set():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Cerrar", "artista": "Test"})
    respuesta = c.post("/set/cerrar", follow_redirects=False)
    assert respuesta.status_code == 302
    assert respuesta.headers["location"] == "/"

    respuesta = c.get("/set", follow_redirects=False)
    assert respuesta.status_code == 302
    assert respuesta.headers["location"] == "/"
