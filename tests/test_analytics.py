import numpy as np
import pytest
import soundfile as sf

from showchango.analytics import ErrorDeAnalisis
from showchango.analytics.librosa_analyzer import LibrosaAnalyzer
from showchango.db import Cache


def _crear_click_track(ruta: str, bpm: float = 120.0, duracion: float = 5.0) -> None:
    sr = 22050
    muestras = int(sr * duracion)
    y = np.zeros(muestras, dtype=np.float32)
    intervalo = int(sr * 60.0 / bpm)
    t_sine = np.linspace(0, 1, int(sr * 0.02), endpoint=False)
    burst = 0.5 * np.sin(2 * np.pi * 1000 * t_sine).astype(np.float32)
    for inicio in range(0, muestras - len(burst), intervalo):
        y[inicio : inicio + len(burst)] += burst
    y = np.clip(y, -1.0, 1.0)
    sf.write(ruta, y, sr)


class TestLibrosaAnalyzer:
    def test_analisis_click_track(self, tmp_path):
        ruta = tmp_path / "click.wav"
        _crear_click_track(str(ruta), bpm=120.0, duracion=5.0)

        analizador = LibrosaAnalyzer()
        features = analizador.analyze(ruta)

        assert 110 <= features["bpm"] <= 130
        assert 4.9 <= features["duracion_s"] <= 5.1
        assert 0.0 < features["energia"] <= 1.0
        assert 0.0 < features["bailabilidad"] <= 1.0
        assert -60.0 <= features["loudness_db"] <= 0.0
        assert features["tonalidad"] != ""
        assert features["voz"] is None
        assert features["genero"] is None

    def test_archivo_vacio_falla(self, tmp_path):
        ruta = tmp_path / "silencio.wav"
        sf.write(str(ruta), np.zeros(1000, dtype=np.float32), 22050)

        with pytest.raises(ErrorDeAnalisis):
            LibrosaAnalyzer().analyze(ruta)


class TestCache:
    def test_guardar_y_obtener(self, tmp_path):
        cache = Cache(tmp_path / "cache.db")
        features = {"bpm": 128.0, "energia": 0.8}
        cache.guardar("abc123", features, "librosa-1.0-v1")
        assert cache.obtener("abc123") == features

    def test_cache_inexistente(self, tmp_path):
        cache = Cache(tmp_path / "cache.db")
        assert cache.obtener("noexiste") is None
