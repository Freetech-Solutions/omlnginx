#!/bin/bash

# Verificar y crear el directorio de configuración si no existe
if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

# Generar la configuración principal de Nginx
cat > /etc/nginx/conf.d/environment/oml_env.conf <<EOF

location = /health {
  access_log off;
  return 200 'OK';
  add_header Content-Type text/plain;
}

# Configuración para archivos estáticos con MIME types correctos
location /static/ {
  alias /opt/omnileads/static/;
  expires 1y;
  add_header Cache-Control "public, immutable";
  
  # Configuración específica para archivos JavaScript
  location ~* \.js\$ {
    add_header Content-Type application/javascript;
    add_header Cache-Control "public, max-age=31536000";
    try_files \$uri =404;
  }
  
  # Configuración específica para archivos CSS
  location ~* \.css\$ {
    add_header Content-Type text/css;
    add_header Cache-Control "public, max-age=31536000";
    try_files \$uri =404;
  }
  
  # Configuración para fuentes web
  location ~* \.(woff|woff2|ttf|eot)\$ {
    add_header Content-Type font/woff;
    add_header Cache-Control "public, max-age=31536000";
    add_header Access-Control-Allow-Origin "*";
    try_files \$uri =404;
  }
  
  # Configuración para imágenes
  location ~* \.(png|jpg|jpeg|gif|ico|svg)\$ {
    add_header Cache-Control "public, max-age=31536000";
    try_files \$uri =404;
  }
  
  # Configuración para otros archivos estáticos
  try_files \$uri =404;
}

# Configuración mejorada para WebSockets - Django Channels
location ~ ^/(channels) {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header X-Forwarded-Host \$server_name;
  proxy_set_header X-Forwarded-Server \$host;
  proxy_set_header Referer \$http_referer;
  proxy_pass http://${DAPHNE_HOSTNAME}:${ASGI_PORT};
  proxy_read_timeout 86400s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
  
  # Configuraciones adicionales para WebSockets
  proxy_buffering off;
  proxy_cache off;
}

# Configuración para WebSocket - Kamailio
location ~* ^/ws\$ {
  proxy_pass https://${KAMAILIO_HOSTNAME}:${KAMAILIO_PORT};
  proxy_http_version 1.1;
  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_connect_timeout 7d;
  proxy_send_timeout 7d;
  proxy_read_timeout 7d;
  proxy_buffering off;
  proxy_cache off;
}

# Configuración para WebSocket - Consumers
location /consumers {
  proxy_pass http://${WEBSOCKETS_HOSTNAME}:${WEBSOCKETS_PORT};
  proxy_http_version 1.1;
  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_connect_timeout 7d;
  proxy_send_timeout 7d;
  proxy_read_timeout 7d;
  proxy_buffering off;
  proxy_cache off;
}

# Configuración para grabaciones
location /grabaciones {
  alias /opt/omnileads/asterisk/var/spool/asterisk/monitor/;
  autoindex on;
  allow all;
  
  # Configuración específica para archivos de audio
  location ~* \.(mp3|wav|ogg)\$ {
    add_header Content-Type audio/mpeg;
    add_header Cache-Control "public, max-age=3600";
    try_files \$uri =404;
  }
}

# Configuración principal para Django (debe ir al final)
location / {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer \$http_referer;
  proxy_pass http://${DJANGO_HOSTNAME}:${WSGI_PORT};
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  
  # Configuración para archivos grandes
  client_max_body_size 50M;
}

EOF

# Agregar configuración para archivos multimedia si no se usa S3
if [[ "${CALLREC_DEVICE}" != "s3-aws" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# Configuración para archivos multimedia S3
location ~* ^/omnileads/.*\.(mp3|wav)\$ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Host \$http_host;
  proxy_connect_timeout 300;
  proxy_http_version 1.1;
  proxy_set_header Connection "";
  chunked_transfer_encoding off;
  proxy_pass ${S3_ENDPOINT};
}

EOF
fi

# Configuración adicional para modo de desarrollo
if [[ "${ENV}" != "prod" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# Configuración para desarrollo - logs más detallados
location /api/ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_pass http://${DJANGO_HOSTNAME}:${WSGI_PORT};
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  
  # Logs detallados para desarrollo
  access_log /dev/stdout;
  error_log /dev/stderr debug;
}

EOF
fi

# Configuración específica para producción
if [[ "${ENV}" == "prod" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF

# Configuración adicional para producción
location /admin/ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_pass http://${DJANGO_HOSTNAME}:${WSGI_PORT};
  
  # Configuración de seguridad para admin
  add_header X-Frame-Options DENY;
  add_header X-Content-Type-Options nosniff;
  add_header X-XSS-Protection "1; mode=block";
}

# Configuración de compresión para producción
location ~* \.(js|css|html|xml|txt)\$ {
  gzip on;
  gzip_vary on;
  gzip_min_length 1024;
  gzip_proxied any;
  gzip_comp_level 6;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}

EOF
fi

# Cambiar archivos de configuración según el modo WEBUI
(
  cd /etc/nginx/conf.d/environment/ || exit
  if [[ "${WEBUI_MODE}" == "rproxy" && -f "webui-rproxy.conf.disabled" ]]; then
    echo "***[oml-nginx] Enabling reverse proxy mode for WebUI"
    mv webui-rproxy.conf.disabled webui-rproxy.conf
  elif [[ "${WEBUI_MODE}" == "static" && -f "webui-static.conf.disabled" ]]; then
    echo "***[oml-nginx] Enabling static mode for WebUI"
    mv webui-static.conf.disabled webui-static.conf
  fi
)

# Validar que las variables de entorno críticas estén definidas
echo "***[oml-nginx] Validating environment variables..."

REQUIRED_VARS=("DJANGO_HOSTNAME" "WSGI_PORT" "DAPHNE_HOSTNAME" "ASGI_PORT")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
  if [[ -z "${!var}" ]]; then
    MISSING_VARS+=("$var")
  fi
done

if [[ ${#MISSING_VARS[@]} -gt 0 ]]; then
  echo "***[oml-nginx] ERROR: Missing required environment variables: ${MISSING_VARS[*]}"
  echo "***[oml-nginx] Please set these variables before running nginx"
  exit 1
fi

# Mostrar configuración generada para depuración
if [[ "${DEBUG:-false}" == "true" ]]; then
  echo "***[oml-nginx] Generated configuration:"
  echo "DJANGO_HOSTNAME: ${DJANGO_HOSTNAME}"
  echo "WSGI_PORT: ${WSGI_PORT}"
  echo "DAPHNE_HOSTNAME: ${DAPHNE_HOSTNAME}"
  echo "ASGI_PORT: ${ASGI_PORT}"
  echo "ENV: ${ENV:-dev}"
  echo "WEBUI_MODE: ${WEBUI_MODE:-static}"
fi

echo "***[oml-nginx] Configuration generated successfully"

# Validar sintaxis de nginx antes de finalizar
if command -v nginx >/dev/null 2>&1; then
  echo "***[oml-nginx] Validating nginx configuration syntax..."
  if nginx -t; then
    echo "***[oml-nginx] Nginx configuration is valid"
  else
    echo "***[oml-nginx] ERROR: Invalid nginx configuration"
    exit 1
  fi
fi