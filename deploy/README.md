# Despliegue de GEOFORA

GEOFORA se publica en el VPS de Hetzner junto a las demos del portafolio, con el mismo sistema: **Docker + Caddy**, configurado en el repo `despliegue-vps` (`/opt/portafolio` en el servidor).

- `Dockerfile` (raíz de este repo): compila la web y crea un único contenedor en el que FastAPI sirve la API (`/api`) y la web.
- `despliegue-vps/docker-compose.yml`: servicio `geofora` (código en `apps/geofora`, caché en el volumen `geofora-data`).
- `despliegue-vps/Caddyfile`: `GEOFORA_HOST` → `geofora:8000`, con HTTPS automático.
- El DNS comodín `*.andresrami.com` ya apunta al VPS, así que no hay que crear registros.

Variables en `/opt/portafolio/.env`, todas opcionales salvo el host:

```
GEOFORA_HOST=geofora.andresrami.com
GEOFORA_DEEPL_API_KEY=
```

Actualizar tras subir cambios a GitHub: `/opt/portafolio/actualizar.sh`.

Regenerar los datos de países (ocasional, en local): `cd backend && .venv\Scripts\python -m scripts.build_countries`, y subir el resultado.
