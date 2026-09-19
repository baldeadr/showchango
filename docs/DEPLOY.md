# Deploy

Show Chango es stateless y no requiere cuentas de usuario, por lo que encaja bien en free tiers.

## Requisitos

- Docker (opcional) o Python 3.12+.
- Variables de entorno opcionales:
  - `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET` para búsqueda de metadata (ver `SPOTIFY.md` si aplica).

## Docker local

```bash
docker build -t showchango .
docker run -p 8000:8000 showchango
```

## Fly.io

1. Instala `flyctl` y autentícate.
2. Revisa `fly.toml` (app `showchango`, puerto `8000`, 512 MB).
3. Ejecuta:
   ```bash
   fly launch
   fly deploy
   ```
4. La app no necesita volúmenes persistentes ni base de datos.

## Render

1. Crea un Web Service conectado al repo.
2. Usa `render.yaml` o configura manualmente:
   - Runtime: Docker
   - Plan: free
   - Health check path: `/health`
3. Render detectará el `Dockerfile` y levantará el servicio.

## Notas

- La sesión vive en RAM; reiniciar el servicio borra los sets en curso. La persistencia real es el JSON exportado por el usuario.
- El caché de análisis (`./.data/cache.db`) se puede borrar sin perder información del usuario.
- En producción, exporta `SHOWCHANGO_ENV=production` para desactivar `/docs` y `/openapi.json`.
