# GEOFORA en un solo contenedor: la API (FastAPI) sirve también la web compilada.

# 1) Compilar el frontend
FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# 2) Backend + web estática
FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml ./backend/
COPY backend/app ./backend/app
COPY backend/data ./backend/data
RUN pip install --no-cache-dir ./backend
COPY --from=web /web/dist ./static

ENV STATIC_DIR=/app/static \
    COUNTRIES_PATH=/app/backend/data/countries.json \
    DB_PATH=/data/geofora.db \
    PYTHONUNBUFFERED=1
VOLUME /data
EXPOSE 8000
# un solo worker: con varios, la precarga de noticias se ejecutaría varias veces
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]
