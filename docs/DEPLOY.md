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
2. `fly launch --image showchango` o usa el `Dockerfile` existente.
3. Expón el puerto `8000`.
4. La app no necesita volúmenes persistentes ni base de datos (salvo el caché de análisis, que puede recrearse).

## Render

1. Crea un Web Service conectado al repo.
2. Usa el `Dockerfile` o el comando de inicio:
   ```bash
   pip install -e ".[dev]"
   python -m uvicorn showchango.web.app:app --host 0.0.0.0 --port $PORT
   ```
3. Plan gratuito suficiente para uso personal.

## Notas

- La sesión vive en RAM; reiniciar el servicio borra los sets en curso. La persistencia real es el JSON exportado por el usuario.
- El caché de análisis (`./.data/cache.db`) se puede borrar sin perder información del usuario.
