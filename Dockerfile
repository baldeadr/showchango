FROM python:3.12-slim

# Dependencias del sistema: ffmpeg (librosa), Pango/Cairo (WeasyPrint) y fuentes básicas.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN groupadd -r showchango && useradd -r -g showchango showchango

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir ".[dev]" && \
    mkdir -p .data && \
    chown -R showchango:showchango /app

USER showchango

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "showchango.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
