from __future__ import annotations

import math
from pathlib import Path

import librosa
import librosa.feature.rhythm as _rhythm
import numpy as np

from showchango.analytics import ErrorDeAnalisis

_VERSION = "librosa-1.0-v1"

# Perfiles de Krumhansl-Kessler (C = índice 0)
_PERFIL_MAJOR = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
_PERFIL_MINOR = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)
_NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class LibrosaAnalyzer:
    """Motor de análisis MVP usando librosa.

    Todos los atributos son estimaciones heurísticas. El usuario puede
    editarlos después; este motor solo da un punto de partida honesto.
    """

    def version(self) -> str:
        return _VERSION

    def analyze(self, ruta: Path) -> dict:
        try:
            return self._analyze(ruta)
        except Exception as exc:
            raise ErrorDeAnalisis(f"No se pudo analizar {ruta}: {exc}") from exc

    def _analyze(self, ruta: Path) -> dict:
        duracion_total = librosa.get_duration(path=str(ruta))
        # Cargar solo los primeros 10 minutos, mono, 22.05 kHz, para acotar RAM.
        y, sr = librosa.load(str(ruta), sr=22050, mono=True, duration=min(duracion_total, 600))

        if y.size == 0:
            raise ErrorDeAnalisis("El archivo de audio está vacío.")

        bpm = float(_rhythm.tempo(y=y, sr=sr)[0])
        if not np.isfinite(bpm) or bpm <= 0:
            raise ErrorDeAnalisis("No se pudo detectar el tempo del audio.")

        duracion_s = float(librosa.get_duration(y=y, sr=sr))

        rms = float(np.sqrt(np.mean(y**2)))
        loudness_db = 20.0 * math.log10(rms) if rms > 0 else -96.0
        energia = _normalizar_db(loudness_db)

        bailabilidad = _heuristica_bailabilidad(bpm)

        tonalidad, es_mayor = _estimar_tonalidad(y, sr)
        if not tonalidad:
            raise ErrorDeAnalisis(
                "No se pudo estimar la tonalidad (audio demasiado silencioso o corto)."
            )

        valencia = 0.65 if es_mayor else 0.35

        return {
            "bpm": round(bpm, 1),
            "energia": round(energia, 3),
            "bailabilidad": round(bailabilidad, 3),
            "duracion_s": round(duracion_s, 2),
            "loudness_db": round(loudness_db, 2),
            "valencia": round(valencia, 3),
            "voz": None,
            "genero": None,
            "tonalidad": tonalidad,
            "notas": "",
        }


def _normalizar_db(db: float) -> float:
    # -60 dBFS → 0, 0 dBFS → 1
    return max(0.0, min(1.0, (db + 60.0) / 60.0))


def _heuristica_bailabilidad(bpm: float) -> float:
    # Baile típico entre ~80 y ~160 BPM, pico en 120. Muy editable.
    if bpm <= 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - abs(bpm - 120.0) / 120.0))


def _estimar_tonalidad(y: np.ndarray, sr: int) -> tuple[str, bool]:
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    perfil = np.sum(chroma, axis=1)
    if perfil.sum() == 0:
        return ("", False)
    perfil = perfil / perfil.sum()

    mejor_score = -np.inf
    mejor_tonica = 0
    es_mayor = True

    for tonica in range(12):
        mayor = np.corrcoef(np.roll(_PERFIL_MAJOR, tonica), perfil)[0, 1]
        menor = np.corrcoef(np.roll(_PERFIL_MINOR, tonica), perfil)[0, 1]
        if mayor > mejor_score:
            mejor_score = mayor
            mejor_tonica = tonica
            es_mayor = True
        if menor > mejor_score:
            mejor_score = menor
            mejor_tonica = tonica
            es_mayor = False

    nota = _NOTAS[mejor_tonica]
    tonalidad = nota if es_mayor else f"{nota}m"
    return tonalidad, es_mayor
