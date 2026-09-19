# Spotify

Show Chango puede buscar metadata básica de canciones en Spotify para agilizar la creación de pistas.

## Configuración

Crea una app en [Spotify for Developers](https://developer.spotify.com/dashboard/) y exporta:

```bash
export SPOTIFY_CLIENT_ID="..."
export SPOTIFY_CLIENT_SECRET="..."
```

Reinicia el servidor. Si no hay credenciales, la sección de búsqueda muestra un aviso.

## Qué trae y qué no

- **Sí:** título, artista(s), álbum, duración e imagen del álbum.
- **No:** BPM, energía, bailabilidad, valencia ni tonalidad.

Spotify [deprecó](https://developer.spotify.com/documentation/web-api/reference/get-audio-features) el endpoint `/audio-features` en noviembre de 2024. Por eso los atributos de energía deben completarse con el análisis de audio local (`librosa`) o a mano.

## Uso

En la página del set, escribe en el buscador de Spotify, selecciona un resultado y presiona **Agregar**. La pista se añade con título, artista y duración; el resto de campos queda vacío para que los completes.
