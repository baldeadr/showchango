# Show Chango

> **El orquestador de tus setlists.** Arma, ordena y exporta el setlist de tu show sobre su curva de energía.

- **Nombre:** Show Chango — decisión del artista (2026-09-18).
- **Tagline:** *El orquestador de tus setlists.*
- **Estado:** Fase 1 — MVP en curso (M1 importar pistas ✔; M2 curva + drag & drop ✔; M3 diagnóstico ✔; M4 export completo pendiente).
- **Repo:** código, docs y bitácora viven aquí (`~/Projects/showchango`).
- **Principio clave:** **nada se almacena** — ni audio ni sets. El set vive en sesión temporal; la persistencia real es el JSON que exportas.

## Qué es

Una herramienta web donde cualquier artista o DJ **sube o importa sus canciones**, la herramienta **analiza cada pista** (BPM, bailabilidad, duración, energía, etc.) y permite **ordenarlas con drag & drop** sobre una **curva de energía**, para que el show tenga un arco: apertura → desarrollo → clímax → respiro → cierre.

Referencia de producto: el *Audio Finder* de Soundcharts + edición drag & drop tipo timeline.

## La metáfora del nombre

El chango / bufón: en el escenario **somos los changuitos que entretienen**; el público tiene que salir entretenido. Show Chango es la herramienta que ayuda a orquestar ese espectáculo.

## Problema que resuelve

Ordenar un setlist a mano (Excel) no deja **ver** la energía del show: cuesta detectar valles, picos, bloques repetidos y posiciones desperdiciadas. Show Chango convierte ese orden en algo visual y manipulable en segundos, para que el show no se sienta plano y sea **inolvidable**.

## Público

- **Primario:** artistas y DJs que preparan shows en vivo.
- **Uso propio:** Apex Ultra y el proyecto solista de `architecting-a-band`.

## Funciones

1. **Importar** canciones (subir archivos, CSV/Excel) **o crearlas a mano** si no se cuenta con el audio (título, BPM, energía, bailabilidad, duración, etc.) y **editar cualquier parámetro**.
2. **Analizar** cada pista y asignarle atributos. El audio se analiza y **se descarta**; no se guarda.
3. **Ver la curva**: gráfica de energía/baile a lo largo del set.
4. **Ordenar** arrastrando bloques sobre la curva; la gráfica se recalcula en vivo.
5. **Exportar** el show completo: imagen de la gráfica (PNG/SVG), PDF del show, CSV, JSON/Markdown estructurado legible por un LLM.
6. **Reimportar** el JSON para seguir trabajando (round-trip): el JSON es el archivo de proyecto.

Spotify/búsqueda por metadata queda para F2.

## Atributos por canción

- BPM / tempo
- Energía (0–1)
- Bailabilidad (*danceability*, 0–1)
- Duración
- Intensidad / sonoridad (*loudness*)
- Valencia / ánimo (*mood*, 0–1)
- Presencia de voz / instrumental / mixto
- Género y tonalidad (si está disponible)

## La curva de show

- Vista tipo timeline con la energía como altura.
- Plantillas de arco reutilizables (arranque suave → clímax al 70% → cierre).
- Detección automática de valles y picos.
- Alertas de bloques repetidos y posiciones desperdiciadas.

## Privacidad: nada se almacena

- El audio se recibe, se analiza y se **elimina**; no se guarda de forma persistente.
- **Los sets tampoco se guardan.** El set vive en sesión temporal (RAM del servidor + autosave en `localStorage` del navegador) mientras trabajas.
- **El JSON exportado es la única persistencia real:** "guardar" = descargar tu archivo de proyecto.
- Solo hay una excepción anónima: la **caché de atributos por hash** del archivo, para no repetir análisis. Es solo atributos derivados, nunca audio.

Esto convierte la privacidad en una característica: Show Chango nunca tiene tu música ni tu show.

## Exportación y consumo por LLM

- **JSON:** archivo de proyecto (`schema: 1`). Es el formato de round-trip.
- **CSV:** datos de las pistas y su orden.
- **Markdown:** reporte estructurado (resumen + tabla + curva como texto) para que un LLM razone sobre el set.
- **PNG/SVG:** gráfica de la curva.
- **PDF:** reporte del show para ensayo, venue o rider.

El esquema JSON está documentado en [`docs/ESQUEMA-JSON.md`](docs/ESQUEMA-JSON.md).

## Stack (decidido 2026-09-18)

| Capa | Tecnología |
|---|---|
| UI | FastAPI + HTMX + SortableJS (drag & drop) + Chart.js (curva) |
| Backend | Python; core puro desacoplado del framework |
| Motor de análisis | librosa (MVP) detrás de una interfaz `Analyzer`; Essentia/MusiCNN/Essentia.js (navegador) como motores alternativos futuros |
| Datos | SQLite **solo para caché de análisis por hash**; nada del usuario se persiste |
| Export | matplotlib (PNG/SVG) + WeasyPrint (PDF) |
| Hosting | free tier (Render / Fly / Hugging Face) — decidir en F2 |

## Arquitectura

Ver [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) para el diagrama de capas, el modelo sin persistencia, el flujo de audio efímero y el contrato del esquema.

## Fases

Ver [`docs/FASES.md`](docs/FASES.md) para el plan completo con checkboxes.

- **F0 — Cimiento (✔):** repo, docs, esquema v1, esqueleto FastAPI.
- **F1 — MVP (en curso):** M1 importar pistas ✔; M2 curva + drag & drop ✔; M3 diagnóstico ✔; M4 export completo.
- **F2 — Producto público:** deploy, landing, Spotify metadata, decidir modelo de acceso.
- **F3 — Inteligencia:** recomendador de orden + diagnóstico explicado + LLM sobre export.

## Desarrollo

Crea un entorno virtual e instala editable:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Corre tests y lint:

```bash
pytest
ruff check .
```

Sirve localmente:

```bash
python -m uvicorn showchango.web.app:app --reload
```

En `http://127.0.0.1:8000`.

## Método y reglas

Heredado de `architecting-a-band`:

- **Idioma:** español.
- **La IA propone, el artista decide:** nada queda cerrado sin confirmación. Lo propuesto se marca `[PROPUESTA]`; lo que falta, `[PENDIENTE]`.
- **Documentar siempre:** cada sesión termina con commit y bitácora.
- **Una sola verdad:** si algo cambia, actualizar referencias.
- **Portabilidad:** Markdown plano, sin depender de una herramienta.

Ver [`AGENTS.md`](AGENTS.md) para la guía completa de asistentes de IA.

## Relación con `architecting-a-band`

Show Chango nació del universo `architecting-a-band` (caso real: setlist de Apex Ultra). La ficha original queda como archivo histórico en `architecting-a-band/show-chango/README.md`; el desarrollo activo y la bitácora viven en este repo.

## Pendientes

- [x] F0 completar y commit inicial.
- [x] F1-M1: importar + análisis efímero + caché hash.
- [x] F1-M2: curva + drag & drop.
- [x] F1-M3: diagnóstico (arcos, valles/picos, bloques).
- [ ] F1-M4: export completo (CSV, Markdown, PNG/SVG, PDF).
- [ ] Definir licencia del proyecto `[PENDIENTE]`.
- [ ] Validar colisión de marca, dominio y handles `[PENDIENTE]`.
