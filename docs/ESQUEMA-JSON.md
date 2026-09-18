# Esquema JSON del archivo de proyecto

> Versión 1 del contrato de round-trip de Show Chango. Fuente de verdad: `src/showchango/core/esquema.py`.

## Ejemplo

```json
{
  "schema": 1,
  "app": "showchango",
  "show": {
    "nombre": "Apex Ultra — Trve Café",
    "artista": "Apex Ultra",
    "fecha": "2026-09-25",
    "tipo": "banda",
    "arco_objetivo": "climax-70",
    "notas": "Set completo, sin bis."
  },
  "pistas": [
    {
      "id": "p9f2a1b3",
      "titulo": "Futuro",
      "artista": "Apex Ultra",
      "bpm": 183,
      "energia": 0.92,
      "bailabilidad": 0.72,
      "duracion_s": 215,
      "loudness_db": -7.2,
      "valencia": 0.35,
      "voz": "vocal",
      "genero": "rock electrónico industrial",
      "tonalidad": "Dm",
      "fuente": "analisis",
      "notas": "loop de intro, cambio de guitarra"
    }
  ],
  "orden": ["p9f2a1b3"],
  "transiciones": [
    {"despues_de": "p9f2a1b3", "nota": "crossfade 8s"}
  ]
}
```

## Campos

### Raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `schema` | entero | Versión del esquema. Ahora `1`. |
| `app` | cadena | Identificador `"showchango"`. |
| `show` | objeto | Datos generales del show. |
| `pistas` | lista | Todas las pistas disponibles (banco + colocadas). |
| `orden` | lista de cadenas | IDs de pistas colocadas en el set, en orden. |
| `transiciones` | lista | Notas de transición entre pistas. |

### `show`

| Campo | Tipo | Descripción |
|---|---|---|
| `nombre` | cadena | Título del set/show. |
| `artista` | cadena | Nombre del artista/DJ. |
| `fecha` | cadena | Fecha del show (formato libre por ahora, recomendado `YYYY-MM-DD`). |
| `tipo` | `"dj" \| "banda" \| null` | Tipo de show. |
| `arco_objetivo` | cadena \| null | ID de la plantilla de arco (ej. `climax-70`). |
| `notas` | cadena | Notas generales. |

### `pistas`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | cadena | Identificador único dentro del proyecto (opaco, generado). |
| `titulo` | cadena | Título de la canción. |
| `artista` | cadena | Artista/DJ. |
| `bpm` | decimal \| null | Tempo en BPM. |
| `energia` | decimal 0–1 \| null | Energía percibida. |
| `bailabilidad` | decimal 0–1 \| null | Bailabilidad. |
| `duracion_s` | decimal > 0 \| null | Duración en segundos. |
| `loudness_db` | decimal \| null | Sonoridad en dB (aproximada). |
| `valencia` | decimal 0–1 \| null | Ánimo (positivo/negativo, aproximado). |
| `voz` | `"vocal" \| "instrumental" \| "mixto" \| null` | Presencia de voz. |
| `genero` | cadena \| null | Género (manual o inferido). |
| `tonalidad` | cadena \| null | Tonalidad musical. |
| `fuente` | `"manual" \| "csv" \| "analisis" \| "spotify"` | Origen de los atributos. |
| `notas` | cadena | Notas de la pista. |

### `orden`

Lista de IDs de `pistas`. Solo pueden aparecer IDs existentes; no puede haber duplicados. Las pistas que no están en `orden` forman el banco/bakstage.

### `transiciones`

| Campo | Tipo | Descripción |
|---|---|---|
| `despues_de` | cadena | ID de la pista anterior a la transición. |
| `nota` | cadena | Nota textual (crossfade, cambio de guitarra, etc.). |

## Invariantes

- `schema` debe ser `1`. Versiones desconocidas rechazan la importación.
- Todos los IDs en `orden` deben existir en `pistas`.
- `orden` no tiene IDs duplicados.
- Cada `despues_de` en `transiciones` debe existir en `pistas`.
- Campos numéricos acotados (energía, bailabilidad, valencia ∈ [0, 1]; duración > 0).

## Política de versionado

- El campo `schema` indica la versión del contrato.
- Un cambio que rompa la importación de archivos antiguos requiere una nueva versión (`schema: 2`) y un migrador.
- La implementación en `core/esquema.py` es la fuente de verdad del formato.

## Round-trip

El test de oro: exportar un proyecto a JSON → importarlo → exportar de nuevo → el resultado es idéntico. Esto garantiza que el JSON es un archivo de proyecto confiable.
