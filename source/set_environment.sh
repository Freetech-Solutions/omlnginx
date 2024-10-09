#!/bin/bash

# Verificar y crear el directorio de configuración si no existe
if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

# Generar la configuración principal de Nginx
cat > /etc/nginx/conf.d/environment/oml_env.conf <<EOF
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
}

location ~ ^/(channels) {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer \$http_referer;
  proxy_pass http://${DAPHNE_HOSTNAME}:${ASGI_PORT};
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}

location ~* ^/ws$ {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
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
}

location /consumers {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
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
}

# Configuración para grabaciones
location /grabaciones {
  alias /opt/omnileads/asterisk/var/spool/asterisk/monitor/;
  autoindex on;
  allow all;
}

EOF

# Agregar configuración para archivos multimedia si no se usa S3
if [[ "${CALLREC_DEVICE}" != "s3-aws" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location ~* ^/omnileads/.*\.(mp3|wav)$ {
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

# Agregar configuración de entorno para producción
if [[ "${ENV}" == "prodenv" ]]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location /static/ {
  alias /opt/omnileads/static/;
  autoindex on;
  allow all;
}

EOF
fi

# Cambiar archivos de configuración según el modo WEBUI
(
  cd /etc/nginx/conf.d/environment/ || exit
  if [[ "${WEBUI_MODE}" == "rproxy" && -f "webui-rproxy.conf.disabled" ]]; then
    mv webui-rproxy.conf.disabled webui-rproxy.conf
  elif [[ "${WEBUI_MODE}" == "static" && -f "webui-static.conf.disabled" ]]; then
    mv webui-static.conf.disabled webui-static.conf
  fi
)

echo "***[oml-nginx] Configuration generated successfully"
