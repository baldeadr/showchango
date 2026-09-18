from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class Cache:
    """Caché SQLite de atributos derivados por hash de archivo.

    No almacena audio, solo atributos anónimos. Su objetivo es evitar
    re-analizar el mismo archivo durante una sesión o entre sesiones.
    """

    def __init__(self, ruta: str | Path = ".data/cache.db") -> None:
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar()

    def _conexion(self) -> sqlite3.Connection:
        return sqlite3.connect(self.ruta)

    def _inicializar(self) -> None:
        with self._conexion() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    hash TEXT PRIMARY KEY,
                    features TEXT NOT NULL,
                    analyzer_version TEXT NOT NULL,
                    analyzed_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )

    def guardar(
        self,
        hash_archivo: str,
        features: dict,
        analyzer_version: str,
    ) -> None:
        with self._conexion() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO analysis_cache
                (hash, features, analyzer_version, analyzed_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (hash_archivo, json.dumps(features), analyzer_version),
            )

    def obtener(self, hash_archivo: str) -> dict | None:
        with self._conexion() as conn:
            row = conn.execute(
                "SELECT features FROM analysis_cache WHERE hash = ?",
                (hash_archivo,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])
