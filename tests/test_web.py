import io

import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient
from openpyxl import Workbook

from showchango.core.esquema import a_texto, de_texto, nuevo_proyecto
from showchango.web.app import crear_app


def client():
    return TestClient(crear_app())


def test_home():
    respuesta = client().get("/")
    assert respuesta.status_code == 200
    assert "Show Chango" in respuesta.text


def test_logo_svg():
    respuesta = client().get("/static/logo.svg")
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/svg+xml"
    assert "Show Chango" in respuesta.text

    home = client().get("/")
    assert "/static/logo.svg" in home.text
    assert "alt=\"Logo de Show Chango\"" in home.text


def test_crear_y_ver_set():
    c = client()
    respuesta = c.post(
        "/set/nuevo",
        data={"nombre": "Trve Café", "artista": "Apex Ultra"},
        follow_redirects=False,
    )
    assert respuesta.status_code == 303
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
    assert respuesta.status_code == 303
    assert respuesta.headers["location"] == "/"

    respuesta = c.get("/set", follow_redirects=False)
    assert respuesta.status_code == 303
    assert respuesta.headers["location"] == "/"


def test_agregar_pista_manual():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    c.post(
        "/pista/nueva",
        data={
            "titulo": "Futuro",
            "artista": "Apex Ultra",
            "bpm": "183",
            "energia": "0.9",
        },
    )
    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Futuro" in respuesta.text
    assert "Apex Ultra" in respuesta.text


def test_duracion_en_minutos_segundos():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    c.post(
        "/pista/nueva",
        data={"titulo": "Larga", "duracion_s": "3:10"},
    )
    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "3:10" in respuesta.text or "190" in respuesta.text


def test_duracion_invalida_muestra_error():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    respuesta = c.post(
        "/pista/nueva",
        data={"titulo": "Mala", "duracion_s": "foo"},
    )
    assert respuesta.status_code == 200
    assert "no válido" in respuesta.text


def test_editar_y_eliminar_pista():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    c.post("/pista/nueva", data={"titulo": "Original", "bpm": "100"})

    respuesta = c.get("/set")
    assert "Original" in respuesta.text

    # Extraer el id de la pista del formulario de edición
    inicio = respuesta.text.find('action="/pista/') + len('action="/pista/')
    fin = respuesta.text.find('/actualizar', inicio)
    pista_id = respuesta.text[inicio:fin]

    c.post(
        f"/pista/{pista_id}/actualizar",
        data={"titulo": "Editada", "bpm": "128", "energia": "0.7"},
    )
    respuesta = c.get("/set")
    assert "Editada" in respuesta.text
    assert "Original" not in respuesta.text

    c.post(f"/pista/{pista_id}/eliminar", follow_redirects=False)
    respuesta = c.get("/set")
    assert "Editada" not in respuesta.text


def test_importar_csv():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    contenido = "Título,Artista,BPM,Energía,Duración\nCanción CSV,Artista CSV,130,0.8,210\n"
    c.post(
        "/set/importar-csv",
        files={"archivo": ("setlist.csv", io.BytesIO(contenido.encode()), "text/csv")},
    )
    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Canción CSV" in respuesta.text
    assert "Artista CSV" in respuesta.text


def test_importar_excel():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})

    wb = Workbook()
    ws = wb.active
    ws.append(["Título", "Artista", "BPM"])
    ws.append(["Canción Excel", "Artista Excel", "125"])
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    c.post(
        "/set/importar-csv",
        files={
            "archivo": (
                "setlist.xlsx",
                buffer,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Canción Excel" in respuesta.text


def test_importar_json():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Viejo", "artista": "Test"})

    proyecto = nuevo_proyecto(nombre="Nuevo", artista="Importado")
    contenido = a_texto(proyecto)

    c.post(
        "/set/importar",
        files={"archivo": ("set.json", io.BytesIO(contenido.encode()), "application/json")},
    )
    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Nuevo" in respuesta.text
    assert "Viejo" not in respuesta.text


def _crear_click_track(ruta: str, bpm: float = 120.0, duracion: float = 4.0) -> None:
    sr = 22050
    muestras = int(sr * duracion)
    y = np.zeros(muestras, dtype=np.float32)
    intervalo = int(sr * 60.0 / bpm)
    t = np.linspace(0, 1, int(sr * 0.02), endpoint=False)
    burst = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
    for inicio in range(0, muestras - len(burst), intervalo):
        y[inicio : inicio + len(burst)] += burst
    y = np.clip(y, -1.0, 1.0)
    sf.write(ruta, y, sr)


def test_subir_audio():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})

    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        _crear_click_track(tmp.name)
        ruta = tmp.name

    with open(ruta, "rb") as f:
        respuesta = c.post(
            "/pista/subir-audio",
            files={"archivo": ("click.wav", f, "audio/wav")},
        )

    # TestClient ejecuta background tasks; si no, hacemos polling.
    if respuesta.status_code == 200 and "analizando" in respuesta.text.lower():
        from html.parser import HTMLParser

        class SimpleParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.job_id = None

            def handle_starttag(self, tag, attrs):
                if tag == "div":
                    for name, value in attrs:
                        if name == "hx-get" and "/pista/analisis/" in value:
                            self.job_id = value.split("/")[-1]

        parser = SimpleParser()
        parser.feed(respuesta.text)
        for _ in range(20):
            estado = c.get(f"/pista/analisis/{parser.job_id}/estado")
            if "analizando" not in estado.text.lower():
                break

    respuesta = c.get("/set")
    assert respuesta.status_code == 200
    assert "Click" in respuesta.text or "click" in respuesta.text.lower()


def test_curva_json():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    c.post("/pista/nueva", data={"titulo": "A", "energia": "0.2", "duracion_s": "120"})
    c.post("/pista/nueva", data={"titulo": "B", "energia": "0.8", "duracion_s": "180"})

    respuesta = c.get("/set/curva-json")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["etiquetas"] == ["A", "B"]
    assert datos["energia"] == [0.2, 0.8]
    assert datos["duracion_total_min"] == 5.0


def test_reordenar_pistas():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    c.post("/pista/nueva", data={"titulo": "A", "energia": "0.2", "duracion_s": "60"})
    c.post("/pista/nueva", data={"titulo": "B", "energia": "0.9", "duracion_s": "60"})

    # Obtener ids en orden original
    curva = c.get("/set/curva-json").json()
    ids = [p["id"] for p in curva["puntos"]]
    ids_invertidos = list(reversed(ids))

    respuesta = c.post("/set/reordenar", json={"orden": ids_invertidos})
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["etiquetas"] == ["B", "A"]
    assert datos["energia"] == [0.9, 0.2]


def test_spotify_buscar_sin_configurar():
    c = client()
    c.post("/set/nuevo", data={"nombre": "Set", "artista": "Test"})
    respuesta = c.get("/spotify/buscar?q=apex")
    assert respuesta.status_code == 200
    assert "Spotify no está configurado" in respuesta.text

