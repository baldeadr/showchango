from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from showchango.core.esquema import a_texto, nuevo_proyecto
from showchango.web.sesiones import Sesiones

PLANTILLAS = Path(__file__).parent / "plantillas"
STATIC = Path(__file__).parent / "static"
COOKIE_SESION = "sc_sesion"


def crear_app() -> FastAPI:
    app = FastAPI(title="Show Chango")
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    templates = Jinja2Templates(directory=PLANTILLAS)
    sesiones = Sesiones()

    def _sid(request: Request) -> str | None:
        return request.cookies.get(COOKIE_SESION)

    def _respuesta_con_sesion(sid: str, url: str) -> RedirectResponse:
        respuesta = RedirectResponse(url, status_code=302)
        respuesta.set_cookie(COOKIE_SESION, sid, max_age=8 * 3600, httponly=True)
        return respuesta

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        sid = _sid(request)
        proyecto = sesiones.obtener_proyecto(sid) if sid else None
        return templates.TemplateResponse(
            request,
            "index.html",
            {"proyecto": proyecto},
        )

    @app.post("/set/nuevo")
    def crear_set(
        request: Request,
        nombre: str = Form(""),
        artista: str = Form(""),
    ):
        sid = _sid(request) or sesiones.nueva()
        proyecto = nuevo_proyecto(nombre=nombre, artista=artista)
        sesiones.guardar_proyecto(sid, proyecto)
        return _respuesta_con_sesion(sid, "/set")

    @app.get("/set", response_class=HTMLResponse)
    def ver_set(request: Request):
        sid = _sid(request)
        proyecto = sesiones.obtener_proyecto(sid) if sid else None
        if proyecto is None:
            return RedirectResponse("/", status_code=302)
        return templates.TemplateResponse(
            request,
            "set.html",
            {"proyecto": proyecto},
        )

    @app.get("/set/exportar")
    def exportar_set(request: Request):
        sid = _sid(request)
        proyecto = sesiones.obtener_proyecto(sid) if sid else None
        if proyecto is None:
            return RedirectResponse("/", status_code=302)
        contenido = a_texto(proyecto)
        return Response(
            content=contenido,
            media_type="application/json",
            headers={
                "Content-Disposition": 'attachment; filename="showchango-set.json"',
            },
        )

    @app.post("/set/cerrar")
    def cerrar_set(request: Request):
        sid = _sid(request)
        if sid:
            sesiones.limpiar_proyecto(sid)
        respuesta = RedirectResponse("/", status_code=302)
        respuesta.delete_cookie(COOKIE_SESION)
        return respuesta

    return app


app = crear_app()
