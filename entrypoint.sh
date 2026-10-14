#!/bin/sh
set -e

echo "[entrypoint] Preparando credenciales de Copernicus..."

if [ -n "$CDSAPI_KEY" ]; then
  cat > /root/.cdsapirc <<EOF
url: ${CDSAPI_URL:-https://cds.climate.copernicus.eu/api}
key: ${CDSAPI_KEY}
EOF
  chmod 600 /root/.cdsapirc
  echo "[entrypoint] .cdsapirc creado"
else
  echo "[entrypoint] AVISO: CDSAPI_KEY no definida; ERA5 no funcionará"
fi

exec "$@"