from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Analyzer(Protocol):
    """Contrato puro para motores de análisis de audio."""

    def analyze(self, ruta: Path) -> dict:
        """Devuelve un dict con atributos derivados de la pista."""
        ...

    def version(self) -> str:
        """Identificador de la versión del motor (para invalidar caché)."""
        ...


class ErrorDeAnalisis(Exception):
    """Fallo durante el análisis de un archivo de audio."""
