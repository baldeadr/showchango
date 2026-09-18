from __future__ import annotations

import secrets
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

APP = "showchango"
SCHEMA_VERSION = 1

Fuente = Literal["manual", "csv", "analisis", "spotify"]
TipoShow = Literal["dj", "banda"]
Voz = Literal["vocal", "instrumental", "mixto"]


class Show(BaseModel):
    nombre: str = ""
    artista: str = ""
    fecha: str = ""
    tipo: TipoShow | None = None
    arco_objetivo: str | None = None
    notas: str = ""


class Pista(BaseModel):
    id: str
    titulo: str
    artista: str = ""
    bpm: float | None = None
    energia: float | None = Field(None, ge=0.0, le=1.0)
    bailabilidad: float | None = Field(None, ge=0.0, le=1.0)
    duracion_s: float | None = Field(None, gt=0.0)
    loudness_db: float | None = None
    valencia: float | None = Field(None, ge=0.0, le=1.0)
    voz: Voz | None = None
    genero: str | None = None
    tonalidad: str | None = None
    fuente: Fuente = "manual"
    notas: str = ""


class Transicion(BaseModel):
    despues_de: str
    nota: str = ""


class Proyecto(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = Field(default=SCHEMA_VERSION, alias="schema")
    app: Literal["showchango"] = APP
    show: Show = Field(default_factory=Show)
    pistas: list[Pista] = Field(default_factory=list)
    orden: list[str] = Field(default_factory=list)
    transiciones: list[Transicion] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validar_orden(self) -> Proyecto:
        ids = {p.id for p in self.pistas}
        if len(self.orden) != len(set(self.orden)):
            raise ValueError("El orden contiene ids duplicados.")
        desconocidos = [pid for pid in self.orden if pid not in ids]
        if desconocidos:
            raise ValueError(f"El orden referencia ids inexistentes: {desconocidos}")
        return self

    @model_validator(mode="after")
    def _validar_transiciones(self) -> Proyecto:
        ids = {p.id for p in self.pistas}
        for t in self.transiciones:
            if t.despues_de not in ids:
                raise ValueError(f"Transición referencia id inexistente: {t.despues_de}")
        return self


def nuevo_id() -> str:
    return secrets.token_hex(4)


def nuevo_proyecto(nombre: str = "", artista: str = "") -> Proyecto:
    return Proyecto(show=Show(nombre=nombre, artista=artista))


def a_texto(proyecto: Proyecto) -> str:
    return proyecto.model_dump_json(indent=2, ensure_ascii=False)


def de_texto(texto: str) -> Proyecto:
    return Proyecto.model_validate_json(texto)


def de_dict(datos: dict) -> Proyecto:
    return Proyecto.model_validate(datos)


class OrdenPayload(BaseModel):
    orden: list[str]
