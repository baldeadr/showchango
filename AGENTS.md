# AGENTS.md — Instrucciones para asistentes de IA

> **Puerta de entrada para cualquier LLM que trabaje en Show Chango.** Léelo completo antes de tocar código o docs. Está en Markdown plano para que funcione con cualquier herramienta.

---

## 1. Qué es Show Chango

- Producto web independiente para armar, ordenar y exportar setlists de shows en vivo.
- Nace del universo `architecting-a-band`, pero el repo es autónomo: código, docs y bitácora viven aquí.
- Idioma de trabajo: **español**.

## 2. Rol del asistente de IA

- **Apoyo:** documentación, análisis, estrategia, consistencia, gestión y código.
- **No toma decisiones creativas o finales:** propone, el artista decide.
- **No inventa datos ni hechos.**

## 3. Leyes del proyecto

1. **El audio nunca se persiste.** Se sube, se analiza y se descarta.
2. **La información del usuario no se almacena.** El set vive en sesión temporal (RAM + `localStorage`); la persistencia es el JSON exportado.
3. **El esquema JSON es un contrato.** `"schema": 1` define el formato de round-trip. Un cambio que rompa compatibilidad exige una nueva versión y un migrador.
4. **El núcleo (`core`) es puro.** No importa FastAPI, ni la DB, ni librerías de UI. Define interfaces (`Analyzer`, repositorios) que las capas externas implementan (inversión de dependencias).
5. **Español y Markdown plano.** Documentación, comunicación y campos del esquema JSON en español.

## 4. Orden de lectura

1. `AGENTS.md` (este archivo).
2. `README.md` — qué es, funciones, stack, setup.
3. `docs/ARQUITECTURA.md` — capas, flujos y decisiones técnicas.
4. `docs/ESQUEMA-JSON.md` — contrato del archivo de proyecto.
5. `docs/FASES.md` — roadmap con checkboxes.
6. `bitacora/YYYY-MM.md` — historial de sesiones.

## 5. Convenciones

- **`[PENDIENTE]`** = falta por definir. No inventar contenido.
- **`[PROPUESTA]`** = propuesta del asistente. Nada queda decidido sin confirmación.
- **`✔`** = tarea hecha.
- **Checkboxes:** `- [ ]` pendiente, `- [x]` hecho.
- **Bitácora:** una entrada por sesión en `bitacora/YYYY-MM.md` con el formato:
  ```
  ### YYYY-MM-DD — Título breve
  **Qué hice:** ...
  **Qué aprendí:** ...
  **Decisión tomada:** ...
  **Siguiente paso:** ...
  ```
- **Una sola verdad:** si un dato cambia, actualizar todas las referencias.
- **Datos y cifras:** deben tener fuente. No inventar.

## 6. Cómo trabajar

1. Al recibir información nueva, actualizar el documento correspondiente **y** agregar una entrada en `bitacora/`.
2. Preferir editar documentos existentes; crear archivos nuevos solo si aportan valor real.
3. Si una instrucción es ambigua o requiere una decisión, preguntar al artista antes de actuar.
4. Cada sesión termina con **commit**.

## 7. Desarrollo

Comandos estándar del repo:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
python -m uvicorn showchango.web.app:app --reload
```

Mantén el código bajo principios SOLID: responsabilidad única, contratos claros, extensión sin modificación del núcleo.

## 8. Portabilidad

Todo es Markdown plano. Si la herramienta de IA cambia, copiar `AGENTS.md` y seguir. La fuente de verdad técnica vive en este repo; `architecting-a-band/show-chango/README.md` es solo archivo histórico.
