from __future__ import annotations

import base64
import os
from typing import Any

import httpx


class SpotifyClient:
    """Cliente mínimo para buscar tracks en Spotify vía Client Credentials.

    Nota: Spotify deprecó el endpoint de audio features en noviembre de 2024,
    por lo que este cliente solo devuelve metadata básica (título, artista,
    duración, álbum, imagen). Los atributos de energía/BPM deben completarse
    con el análisis de audio local o a mano.
    """

    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        self.client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET")
        self._token: str | None = None

    def configurado(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def _auth(self) -> str:
        if self._token:
            return self._token
        if not self.configurado():
            raise RuntimeError("Spotify no está configurado")

        creds = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        async with httpx.AsyncClient() as client:
            respuesta = await client.post(
                self.TOKEN_URL,
                headers={"Authorization": f"Basic {creds}"},
                data={"grant_type": "client_credentials"},
                timeout=30,
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
        self._token = datos["access_token"]
        return self._token

    async def buscar(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        token = await self._auth()
        async with httpx.AsyncClient() as client:
            respuesta = await client.get(
                f"{self.API_URL}/search",
                headers={"Authorization": f"Bearer {token}"},
                params={"q": query, "type": "track", "limit": limit},
                timeout=30,
            )
            respuesta.raise_for_status()
            items = respuesta.json().get("tracks", {}).get("items", [])

        resultado: list[dict[str, Any]] = []
        for item in items:
            artistas = ", ".join(a["name"] for a in item.get("artists", []))
            album = item.get("album", {})
            imagenes = album.get("images", [])
            resultado.append(
                {
                    "id": item["id"],
                    "titulo": item["name"],
                    "artista": artistas,
                    "album": album.get("name", ""),
                    "duracion_s": item.get("duration_ms", 0) / 1000,
                    "url": item.get("external_urls", {}).get("spotify", ""),
                    "imagen": imagenes[0]["url"] if imagenes else "",
                }
            )
        return resultado
