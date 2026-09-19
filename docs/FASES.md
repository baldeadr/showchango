# Fases

> Roadmap vivo de Show Chango. Marcar `- [x]` solo cuando la tarea esté hecha y verificada.

---

## F0 — Cimiento (en curso)

Objetivo: repo funcional, esquema congelado, app web servible.

- [x] `git init` + estructura de carpetas.
- [x] `.gitignore`, `pyproject.toml`, `Dockerfile` base.
- [x] `README.md` (absorbe la ficha y decisiones).
- [x] `AGENTS.md` (puerta LLM con leyes del proyecto).
- [x] `docs/ARQUITECTURA.md`, `docs/ESQUEMA-JSON.md`, `docs/FASES.md`.
- [x] `bitacora/2026-09.md` (entrada de la sesión).
- [x] `core/esquema.py` con esquema JSON v1 + tests de round-trip.
- [x] Esqueleto FastAPI: home, crear set, set vacío en sesión RAM + exportar JSON + tests.
- [x] `pytest` y `ruff check` en verde; `uvicorn` sirve la app.
- [x] Actualizar `architecting-a-band` (ficha archivo, referencias, bitácora).
- [x] Commit inicial en ambos repos.

---

## F1 — MVP usable

Criterio de salida: armar el setlist de Apex Ultra del 25-sep 100% en Show Chango; el PDF sirve para ensayo y el JSON reimporta idéntico.

### M1 — Importar (y guardar con JSON desde el día 1)

- [x] Formulario manual de pista (título, artista, BPM, energía, bailabilidad, duración, etc.).
- [x] Importar CSV/Excel (caso real de los setlists en Excel).
- [x] Subir audio: análisis efímero con librosa, caché por hash, HTMX polling.
- [x] Editar cualquier atributo a mano.
- [x] **Exportar e importar JSON** como mecanismo de persistencia desde el inicio.

### M2 — Curva + drag & drop

- [x] Renderizar lista de pistas con SortableJS.
- [x] Curva con Chart.js; recalcular en vivo al reordenar.
- [x] Persistir el orden en la sesión temporal.

### M3 — Diagnóstico

- [x] Plantillas de arco objetivo (al menos: clímax al 70%, construcción DJ, picos rock).
- [x] Detección de valles y picos.
- [x] Alerta de bloques repetidos (≥3 pistas con BPM/energía similares).
- [x] Alerta de posiciones desperdiciadas.

### M4 — Export completo + round-trip

- [x] CSV de datos.
- [x] Markdown estructurado legible por LLM.
- [x] PNG/SVG de la gráfica (matplotlib).
- [x] PDF del show (WeasyPrint).
- [x] Test de oro: exportar → importar → exportar = idéntico.

---

## F2 — Producto público

- [x] Landing con explicación y privacidad.
- [x] Deploy en free tier (stateless, sin cuentas).
- [x] Búsqueda/metadata con Spotify (metadata básica; audio features deprecadas por Spotify).
- [x] Decidir modelo de acceso: **gratis con full access**; donaciones o monetización futura posible `[DECIDIDO]`.
- [x] Evaluar sin almacenamiento: **se mantiene como feature permanente por ahora**; el almacenamiento podría ser una feature paga si algún día se monetiza `[DECIDIDO]`.
- [ ] Definir licencia del proyecto `[OMITIDO POR AHORA]`.
- [ ] Validar marca/dominio/handles `[OMITIDO POR AHORA; proyecto personal, se renombra si es necesario]`.

---

## F3 — Inteligencia `[PROPUESTA]`

- [ ] Recomendador de orden según curva objetivo + género/tipo de evento + contexto.
- [ ] Perfiles/plantillas de arco por género (electrónica, rock, cumbia, industrial bailable, etc.).
- [ ] Diagnóstico explicado con sugerencias y porqué.
- [ ] Consumo del export Markdown por LLM para razonar sobre el set.

---

## Fuera del MVP

- Cuentas de usuario.
- Colaboración en tiempo real.
- Multi-idioma.
- App nativa de escritorio o móvil.
