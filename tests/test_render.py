import io

from showchango.core.esquema import Pista, nuevo_id, nuevo_proyecto
from showchango.render import exportar_csv, exportar_markdown, exportar_pdf, renderizar_curva


def _proyecto_de_ejemplo():
    proyecto = nuevo_proyecto("Apex Ultra — Trve Café", "Apex Ultra")
    p1 = Pista(
        id=nuevo_id(),
        titulo="Intro",
        artista="Apex Ultra",
        bpm=120,
        energia=0.3,
        duracion_s=120,
        fuente="manual",
    )
    p2 = Pista(
        id=nuevo_id(),
        titulo="Climax",
        artista="Apex Ultra",
        bpm=140,
        energia=0.9,
        duracion_s=180,
        fuente="manual",
    )
    proyecto.pistas = [p1, p2]
    proyecto.orden = [p1.id, p2.id]
    return proyecto


def test_exportar_csv_contiene_pistas():
    proyecto = _proyecto_de_ejemplo()
    csv_texto = exportar_csv(proyecto)
    assert "Intro" in csv_texto
    assert "Climax" in csv_texto
    assert "duracion_mmss" in csv_texto


def test_exportar_markdown_contiene_setlist():
    proyecto = _proyecto_de_ejemplo()
    md = exportar_markdown(proyecto)
    assert "# Apex Ultra — Trve Café" in md
    assert "| 1 | Intro" in md
    assert "| 2 | Climax" in md
    assert "Curva de energía" in md


def test_renderizar_curva_png():
    proyecto = _proyecto_de_ejemplo()
    png = renderizar_curva(proyecto, formato="png")
    assert png.startswith(b"\x89PNG")


def test_renderizar_curva_svg():
    proyecto = _proyecto_de_ejemplo()
    svg = renderizar_curva(proyecto, formato="svg")
    assert svg.startswith(b"<?xml")
    assert b"Intro" in svg or b"Climax" in svg


def test_exportar_pdf_no_vacio():
    proyecto = _proyecto_de_ejemplo()
    pdf = exportar_pdf(proyecto)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_round_trip_json(client):
    c = client
    c.post("/set/nuevo", data={"nombre": "Round", "artista": "Trip"})
    c.post("/pista/nueva", data={"titulo": "A", "energia": "0.5", "duracion_s": "120"})

    primera = c.get("/set/exportar")
    assert primera.status_code == 200

    c.post(
        "/set/importar",
        files={"archivo": ("set.json", io.BytesIO(primera.content), "application/json")},
    )

    segunda = c.get("/set/exportar")
    assert segunda.status_code == 200
    assert primera.content == segunda.content
