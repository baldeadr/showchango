from __future__ import annotations

import time


class Sesiones:
    """Estado temporal por visitante en RAM. Nada se guarda en disco."""

    def __init__(self, expiracion_s: int = 8 * 3600) -> None:
        self._expiracion_s = expiracion_s
        self._datos: dict[str, dict] = {}

    def _limpiar_expiradas(self) -> None:
        ahora = time.time()
        expiradas = [
            sid for sid, datos in self._datos.items()
            if ahora - datos.get("tacto", 0) > self._expiracion_s
        ]
        for sid in expiradas:
            del self._datos[sid]

    def nueva(self) -> str:
        self._limpiar_expiradas()
        sid = _generar_sid()
        self._datos[sid] = {"tacto": time.time(), "proyecto": None}
        return sid

    def _obtener(self, sid: str) -> dict | None:
        self._limpiar_expiradas()
        datos = self._datos.get(sid)
        if datos is None:
            return None
        datos["tacto"] = time.time()
        return datos

    def obtener_proyecto(self, sid: str):
        datos = self._obtener(sid)
        if datos is None:
            return None
        return datos.get("proyecto")

    def guardar_proyecto(self, sid: str, proyecto) -> bool:
        datos = self._obtener(sid)
        if datos is None:
            return False
        datos["proyecto"] = proyecto
        datos["tacto"] = time.time()
        return True

    def limpiar_proyecto(self, sid: str) -> None:
        datos = self._obtener(sid)
        if datos is not None:
            datos["proyecto"] = None


def _generar_sid() -> str:
    import secrets
    return secrets.token_hex(16)
