from __future__ import annotations

import base64

from weasyprint import HTML

from showchango.core.curva import calcular_curva
from showchango.core.esquema import Proyecto
from showchango.render.chart_exporter import renderizar_curva


def _mmss(segundos: float | None) -> str:
    if segundos is None or segundos == 0:
        return "—"
    total = int(round(segundos))
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def _fila(pista) -> str:
    return (
        "<tr>"
        f"<td>{pista.titulo}</td>"
        f"<td>{pista.artista or '—'}</td>"
        f"<td>{pista.bpm if pista.bpm is not None else '—'}</td>"
        f"<td>{pista.energia if pista.energia is not None else '—'}</td>"
        f"<td>{_mmss(pista.duracion_s)}</td>"
        f"<td>{pista.tonalidad or '—'}</td>"
        f"<td>{pista.notas or '—'}</td>"
        "</tr>"
    )


def exportar_pdf(proyecto: Proyecto) -> bytes:
    """Genera un PDF del show con setlist y curva de energía embebida."""
    show = proyecto.show
    curva = calcular_curva(proyecto)
    por_id = {p.id: p for p in proyecto.pistas}
    png_bytes = renderizar_curva(proyecto, formato="png")
    imagen_b64 = base64.b64encode(png_bytes).decode("ascii")

    filas = ""
    for pista_id in proyecto.orden:
        pista = por_id.get(pista_id)
        if pista is not None:
            filas += _fila(pista)

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  @page {{ margin: 2cm; }}
  body {{ font-family: system-ui, sans-serif; color: #e6e6e6; background: #0f0f11; margin: 0; }}
  h1 {{ color: #ff6b35; font-size: 1.8rem; margin-bottom: 0.2rem; }}
  .meta {{ color: #999; margin-bottom: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-top: 1rem; }}
  th, td {{ padding: 0.4rem; border-bottom: 1px solid #2a2a30; text-align: left; }}
  th {{ color: #999; font-weight: 600; }}
  .chart {{ width: 100%; margin-top: 1.5rem; }}
  .footer {{ margin-top: 2rem; color: #666; font-size: 0.8rem; }}
</style>
</head>
<body>
  <h1>{show.nombre or 'Set sin nombre'}</h1>
  <p class="meta">
    {show.artista or 'Sin artista'} · {len(proyecto.orden)} pistas
    · {_mmss(curva['duracion_total_s'])}
  </p>

  <h2>Setlist</h2>
  <table>
    <thead>
      <tr><th>Título</th><th>Artista</th><th>BPM</th><th>E</th><th>Dur.</th><th>Tonalidad</th><th>Notas</th></tr>
    </thead>
    <tbody>
      {filas}
    </tbody>
  </table>

  <h2>Curva de energía</h2>
  <img class="chart" src="data:image/png;base64,{imagen_b64}" alt="Curva de energía">

  <p class="footer">Exportado desde Show Chango — nada se almacena.</p>
</body>
</html>"""

    return HTML(string=html).write_pdf()
