#!/bin/bash

# Verificar y crear el directorio de configuración si no existe
if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

# ============================================================================
# NUEVO: Limpieza y creación del Servidor Maestro
# ============================================================================

# 1. Borramos la configuración por defecto para que no estorbe (puerto 80)
if [ -f /etc/nginx/conf.d/default.conf ]; then
    rm /etc/nginx/conf.d/default.conf
fi

# 2. Creamos el archivo "Padre" que contiene el bloque SERVER
# Detectamos el DNS dinámico de la red de Podman/Docker
DNS_SERVER=$(awk '/^nameserver/ {print $2}' /etc/resolv.conf | head -n 1)
echo "***[oml-nginx] Detected DNS resolver: ${DNS_SERVER:-127.0.0.11}"

# Escribimos el resolver global y los server blocks
cat > /etc/nginx/conf.d/00-oml-app.conf <<EOF
# Resolver dinámico inyectado para soporte Podman/Netavark
resolver ${DNS_SERVER:-127.0.0.11} valid=10s ipv6=off;

server {
    listen 80;
    listen [::]:80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }

    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name _;

    access_log /dev/stdout;
    error_log /dev/stderr;

    ssl_certificate     /etc/omnileads/certs/cert.pem;
    ssl_certificate_key /etc/omnileads/certs/key.pem;

    include /etc/nginx/conf.d/environment/*.conf;
}
EOF

# ============================================================================
# 0. Configuración de WebSocket Upgrade (debe estar en contexto http)
# ============================================================================
cat > /etc/nginx/conf.d/websocket_upgrade.conf <<EOF
# Map para WebSocket upgrade
map \$http_upgrade \$connection_upgrade {
    default upgrade;
    '' close;
}
EOF

# ============================================================================
# 0. Validaciones previas
# ============================================================================
echo "***[oml-nginx] Validating environment variables..."

REQUIRED_VARS=(
  "DJANGO_HOSTNAME" "WSGI_PORT"
  "DAPHNE_HOSTNAME" "ASGI_PORT"
  "WEBSOCKETS_HOSTNAME" "WEBSOCKETS_PORT"
  "KAMAILIO_HOSTNAME" "KAMAILIO_PORT"
  "S3_ENDPOINT"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    MISSING_VARS+=("$var")
  fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
  echo "***[oml-nginx] ERROR: Missing required environment variables: ${MISSING_VARS[*]}"
  exit 1
fi

ENV="${ENV:-dev}"
WEBUI_MODE="${WEBUI_MODE:-static}"
DEBUG="${DEBUG:-false}"

mkdir -p /etc/nginx/conf.d/environment

# Extraer host[:puerto] sin el http:// para S3/MinIO
# Esto es vital para usar la variable Nginx limpiamente
S3_UPSTREAM="${S3_ENDPOINT%/}"
S3_HOST_HEADER="${S3_UPSTREAM#http://}"
S3_HOST_HEADER="${S3_HOST_HEADER#https://}"

# ============================================================================
# 1. Configuración Base
# ============================================================================
cat > /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# Definición de variables dinámicas para Nginx
# Esto fuerza a Nginx a resolver los DNS al recibir la petición (Lazy Loading),
# previniendo que el contenedor crashee si un backend está caído al iniciar.
set \$django_backend "${DJANGO_HOSTNAME}:${WSGI_PORT}";
set \$daphne_backend "${DAPHNE_HOSTNAME}:${ASGI_PORT}";
set \$websockets_backend "${WEBSOCKETS_HOSTNAME}:${WEBSOCKETS_PORT}";
set \$kamailio_backend "${KAMAILIO_HOSTNAME}:${KAMAILIO_PORT}";
set \$s3_backend "${S3_HOST_HEADER}";

location = /health {
  access_log off;
  default_type text/plain;
  return 200 'OK';
}

# ----------------------------------------------------------------------------
# Archivos estáticos
# ----------------------------------------------------------------------------
location /static/ {
  root /opt/omnileads;
  expires 1y;
  add_header Cache-Control "public, immutable";
  try_files \$uri =404;
}

# ----------------------------------------------------------------------------
# Channels / Daphne
# ----------------------------------------------------------------------------
location /channels {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header X-Forwarded-Host \$server_name;
  proxy_set_header X-Forwarded-Server \$host;
  proxy_set_header Referer \$http_referer;
  proxy_set_header Cookie \$http_cookie;

  proxy_pass http://\$daphne_backend;
  proxy_http_version 1.1;
  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection \$connection_upgrade;

  proxy_read_timeout 86400s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  proxy_buffering off;
  proxy_cache off;
}

# ----------------------------------------------------------------------------
# WebSocket - Kamailio
# ----------------------------------------------------------------------------
location = /ws {
  proxy_pass http://\$kamailio_backend;
  proxy_http_version 1.1;

  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection \$connection_upgrade;
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header X-Forwarded-Host \$server_name;
  proxy_set_header X-Forwarded-Server \$host;

  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  proxy_read_timeout 600s;

  proxy_buffering off;
  proxy_cache off;
}

# ----------------------------------------------------------------------------
# WebSocket - Consumers
# ----------------------------------------------------------------------------
location /consumers {
  proxy_pass http://\$websockets_backend;
  proxy_http_version 1.1;

  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection \$connection_upgrade;
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header X-Forwarded-Host \$server_name;
  proxy_set_header X-Forwarded-Server \$host;
  proxy_set_header Referer \$http_referer;
  proxy_set_header Cookie \$http_cookie;

  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  proxy_read_timeout 600s;

  proxy_buffering off;
  proxy_cache off;
}

# ----------------------------------------------------------------------------
# Grabaciones
# ----------------------------------------------------------------------------
location /grabaciones/ {
  alias /opt/omnileads/asterisk/var/spool/asterisk/monitor/;
  autoindex on;
  allow all;
  add_header Cache-Control "public, max-age=3600";
}

# ----------------------------------------------------------------------------
# MinIO / S3
# ----------------------------------------------------------------------------
location /minio/ {
  rewrite ^/minio/(.*)$ /\$1 break;

  proxy_pass http://\$s3_backend;
  proxy_set_header Host \$s3_backend;
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto \$scheme;

  client_max_body_size 0;
  proxy_buffering off;
  proxy_request_buffering off;
}

# ----------------------------------------------------------------------------
# Django principal
# ----------------------------------------------------------------------------
location / {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer \$http_referer;

  proxy_pass http://\$django_backend;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  client_max_body_size 50M;
}
EOF

# ============================================================================
# 2. Configuraciones por entorno
# ============================================================================
if [[ "${ENV}" != "prod" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# ----------------------------------------------------------------------------
# Desarrollo
# ----------------------------------------------------------------------------
location /api/ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;

  proxy_pass http://\$django_backend;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  access_log /dev/stdout;
  error_log /dev/stderr debug;
}
EOF
fi

if [[ "${ENV}" == "prod" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# ----------------------------------------------------------------------------
# Producción - admin
# ----------------------------------------------------------------------------
location /admin/ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;

  proxy_pass http://\$django_backend;

  add_header X-Frame-Options DENY;
  add_header X-Content-Type-Options nosniff;
  add_header X-XSS-Protection "1; mode=block";
}
EOF
fi

# ============================================================================
# 3. Configuración WebUI
# ============================================================================
(
  cd /etc/nginx/conf.d/environment/ || exit 1

  if [[ "${WEBUI_MODE}" == "rproxy" && -f "webui-rproxy.conf.disabled" ]]; then
    echo "***[oml-nginx] Enabling reverse proxy mode for WebUI"
    mv webui-rproxy.conf.disabled webui-rproxy.conf
  elif [[ "${WEBUI_MODE}" == "static" && -f "webui-static.conf.disabled" ]]; then
    echo "***[oml-nginx] Enabling static mode for WebUI"
    mv webui-static.conf.disabled webui-static.conf
  fi
)

# ============================================================================
# 4. Debug
# ============================================================================
if [[ "${DEBUG}" == "true" ]]; then
  echo "***[oml-nginx] Generated configuration variables:"
  echo "DJANGO_HOSTNAME=${DJANGO_HOSTNAME}"
  echo "WSGI_PORT=${WSGI_PORT}"
  echo "DAPHNE_HOSTNAME=${DAPHNE_HOSTNAME}"
  echo "ASGI_PORT=${ASGI_PORT}"
  echo "WEBSOCKETS_HOSTNAME=${WEBSOCKETS_HOSTNAME}"
  echo "WEBSOCKETS_PORT=${WEBSOCKETS_PORT}"
  echo "KAMAILIO_HOSTNAME=${KAMAILIO_HOSTNAME}"
  echo "KAMAILIO_PORT=${KAMAILIO_PORT}"
  echo "S3_ENDPOINT=${S3_ENDPOINT}"
  echo "S3_UPSTREAM=${S3_UPSTREAM}"
  echo "S3_HOST_HEADER=${S3_HOST_HEADER}"
  echo "ENV=${ENV}"
  echo "WEBUI_MODE=${WEBUI_MODE}"
  echo "***[oml-nginx] Generated file:"
  sed -n '1,240p' /etc/nginx/conf.d/environment/oml_env.conf
fi

# ============================================================================
# 5. Validación final
# ============================================================================
echo "***[oml-nginx] Configuration generated successfully"

if command -v nginx >/dev/null 2>&1; then
  echo "***[oml-nginx] Validating nginx configuration syntax..."
  nginx -t
fi