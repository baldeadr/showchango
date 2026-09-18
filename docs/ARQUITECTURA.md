# Arquitectura

> Decisiones técnicas, capas y flujos de Show Chango. Actualizado: 2026-09-18.

## Capas

```
┌─ web (FastAPI + HTMX + SortableJS + Chart.js) ───────────────┐
│  Rutas, plantillas, formularios, drag & drop, polling de      │
│  análisis.                                                    │
├───────────────────────────────────────────────────────────────┤
│ core (PURO, sin framework, sin DB, sin librerías de UI)       │
│  • Dominio: Set/Show, Pista, Atributos                        │
│  • Curva: cálculo, plantillas de arco, diagnóstico            │
│  • Esquema: pydantic "schema": 1 (round-trip)                 │
│  • Export de datos: JSON / CSV / Markdown                     │
├──────────────┬─────────────────────┬──────────────────────────┤
│ analytics    │ db (SQLite)         │ render                   │
│ protocolo    │ solo caché de       │ matplotlib → PNG/SVG     │
│ Analyzer →   │ análisis por hash   │ WeasyPrint → PDF         │
│ librosa (MVP)│ (atributos derivados│ (reusa plantilla HTML)   │
└──────────────┴─────────────────────┴──────────────────────────┘
```

**Regla:** `core` no importa FastAPI ni la DB. Las capas externas dependen de `core` (interfaces, modelos) y viceversa no. Esto permite cambiar la UI, el motor de análisis o la base de datos sin tocar el dominio.

## Modelo sin persistencia

Decidido 2026-09-18:

- **El audio nunca se guarda.** Se sube, se analiza y se descarta.
- **Los sets no se guardan en servidor.** El set vive en **sesión temporal en RAM** mientras se trabaja, con autosave en `localStorage` del navegador como red de seguridad.
- **La persistencia real es el JSON exportado.** "Guardar" = descargar el archivo de proyecto.
- La única excepción anónima es la **caché de análisis por hash**: atributos derivados (BPM, energía, etc.) asociados a un hash de archivo, para no repetir análisis. Nunca audio, nunca sets.

Ventajas:

- Privacidad total como característica.
- El deploy en free tier no requiere disco persistente (Render efímero sirve).
- No hay cuentas, tokens de enlace ni responsabilidad de datos personales.

Costos:

- Si el servidor se reinicia, las sesiones activas se pierden. Se mitiga con export frecuente y `localStorage`.
- La caché de análisis se pierde si se borra el SQLite; la app simplemente re-analiza.

## Flujo de audio efímero

```
subida → SHA-256 del archivo
   ├─ hash en analysis_cache → atributos al instante; audio descartado
   └─ hash no existe → cola de análisis (estado: pendiente/analizando/listo/error)
           ↓
     librosa en background (ThreadPool)
           ↓
     atributos a BD (analysis_cache) con analyzer_version
           ↓
     tempfile borrado
```

La UI consulta el estado vía HTMX polling. Los atributos del análisis son un punto de partida editable; el artista siempre puede corregir cualquier valor.

## Esquema de la caché de análisis

Una sola tabla SQLite:

| Campo | Tipo |
|---|---|
| `hash` | TEXT PK |
| `features` | TEXT (JSON) |
| `analyzer_version` | TEXT |
| `analyzed_at` | TEXT (ISO) |

## Drag & drop + curva en vivo

- La lista de pistas se renderiza con HTMX y se hace arrastrable con SortableJS.
- Al soltar un bloque, un hook de JavaScript actualiza el orden y recalcula la curva **en el cliente** con Chart.js (respuesta instantánea). Un POST persistirá el orden en la sesión temporal.
- La curva usa: eje X = tiempo acumulado, eje Y = energía (0–1). Opcionalmente se superpone bailabilidad y plantillas de arco objetivo.

## Exportación

- **JSON:** directo desde `core.esquema`, contrato v1.
- **CSV:** tabla de pistas con posición y atributos.
- **Markdown:** reporte para humanos y LLMs.
- **PNG/SVG:** matplotlib (una sola fuente de estilo para impresión).
- **PDF:** WeasyPrint desde plantilla HTML (reutiliza estilos web).

## Interfaz del motor de análisis

```python
class Analyzer:
    def analyze(self, ruta_audio: Path) -> Atributos: ...
    def version(self) -> str: ...
```

MVP: implementación con `librosa`. En el futuro pueden agregarse Essentia, MusiCNN o incluso Essentia.js en el navegador, siempre produciendo el mismo tipo de atributos.

## Decisiones registradas

| Fecha | Decisión |
|---|---|
| 2026-09-18 | Show Chango será web, no app de escritorio. |
| 2026-09-18 | Audio no persistido; atributos + setlists como datos guardados. |
| 2026-09-18 | Export round-trip con JSON esquematizado (`schema`: 1). |
| 2026-09-18 | Stack: FastAPI + HTMX + SortableJS + Chart.js; librosa; SQLite; WeasyPrint. |
| 2026-09-18 | Repo nuevo para código/docs/bitácora; ficha de `architecting-a-band` como archivo histórico. |
| 2026-09-18 | **Nada se almacena:** sets temporales en RAM + localStorage; JSON es la persistencia. |
| 2026-09-18 | Spotify/metadata fuera del MVP; entra en F2. |

## Trade-offs abiertos

- **Valence/danceability con librosa** son estimaciones heurísticas, no los modelos de Spotify. Siempre editables y con transparencia en la UI.
- **ThreadPool en MVP** simplifica el deploy, pero el análisis bloquea CPU. Se acotan a 1–2 hilos concurrentes y se decodifica a mono 22.05 kHz para ahorrar RAM en free tier.
- **WeasyPrint** depende de Pango/Cairo; se usará en Docker para evitar problemas de hosting.

## Rutas de evolución

- **Motor de análisis:** librosa → Essentia/MusiCNN → Essentia.js (WASM en navegador).
- **Cómputo de análisis:** ThreadPool → worker dedicado (arq/RQ/Celery) cuando haya cola grande.
- **Datos:** si algún día hay cuentas, SQLite caché → Postgres/Supabase; los sets seguirían siendo propiedad del usuario (JSON exportable).
