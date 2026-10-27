# Despliegue de GEOFORA en el VPS

Subdominio previsto: `geofora.andresrami.com` (pendiente de confirmar). Requiere Python ≥ 3.12, Node ≥ 20, Nginx y certbot. Todos los comandos de build se ejecutan como el usuario `geofora`, dueño de `/opt/geofora`.

## 1. DNS
Registro `A` de `geofora` apuntando a la IP del VPS.

## 2. Código y dependencias
```bash
sudo useradd --system --home /opt/geofora geofora
sudo git clone <repo> /opt/geofora
sudo chown -R geofora: /opt/geofora
cd /opt/geofora/backend
sudo -u geofora python3 -m venv .venv && sudo -u geofora .venv/bin/pip install .
cd ../frontend && sudo -u geofora npm ci && sudo -u geofora npm run build
sudo mkdir -p /var/lib/geofora && sudo chown geofora /var/lib/geofora
```

## 3. Variables de entorno (`/etc/geofora.env`, permisos 600)
```
DB_PATH=/var/lib/geofora/geofora.db
COUNTRIES_PATH=/opt/geofora/backend/data/countries.json
LASTFM_API_KEY=
DEEPL_API_KEY=
NEWS_INTERVAL_MIN=45
ENABLE_SCHEDULER=true
```
systemd no admite comentarios al final de una línea: cada valor va solo.

- `COUNTRIES_PATH` es necesario porque `pip install .` copia `app/` fuera del repo.
- `LASTFM_API_KEY`: se pide en https://www.last.fm/api/account/create (opcional).
- `DEEPL_API_KEY`: plan Free en https://www.deepl.com/pro-api (opcional).

Sin `LASTFM_API_KEY` la música usa solo artistas de MusicBrainz; sin `DEEPL_API_KEY` los titulares salen en su idioma original.

## 4. Servicios
```bash
sudo cp deploy/geofora-api.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now geofora-api
sudo cp deploy/nginx-geofora.conf /etc/nginx/sites-available/geofora
sudo ln -s /etc/nginx/sites-available/geofora /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d geofora.andresrami.com
```

## 5. Comprobación
- `curl https://geofora.andresrami.com/api/health` → `{"status":"ok"}`
- Abrir `https://geofora.andresrami.com/pais/afganistan` directamente → se carga el panel.
- En la pestaña Red del navegador no aparece ninguna clave de API.
- `journalctl -u geofora-api | grep "news cycle done"` → un ciclo completado (tarda ~20–40 min la primera vez).

## Actualizar
```bash
cd /opt/geofora && sudo -u geofora git pull
sudo -u geofora backend/.venv/bin/pip install ./backend
(cd frontend && sudo -u geofora npm ci && sudo -u geofora npm run build)
sudo systemctl restart geofora-api
```

## Regenerar los datos de países (ocasional)
```bash
cd /opt/geofora/backend && sudo -u geofora .venv/bin/python -m scripts.build_countries
```
