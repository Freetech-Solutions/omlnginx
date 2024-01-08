#!/bin/bash

if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

cat > /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location / {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer 	     \$http_referer;
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
  proxy_set_header Referer 	     \$http_referer;
  proxy_pass http://${DAPHNE_HOSTNAME}:${ASGI_PORT};
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}

location ~* (ws) {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
  proxy_pass https://${KAMAILIO_HOSTNAME}:${KAMAILIO_PORT};
  proxy_http_version 1.1;
  proxy_set_header Upgrade \$http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header   X-Forwarded-Proto \$scheme;
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
  proxy_set_header   X-Forwarded-Proto \$scheme;
  proxy_connect_timeout 7d;
  proxy_send_timeout 7d;
  proxy_read_timeout 7d;
}

location /grabaciones {
  alias /opt/omnileads/asterisk/var/spool/asterisk/monitor/;
  autoindex on;
  allow all;
}

EOF

if [ ${CALLREC_DEVICE} != "s3-aws" ]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location ~*  \.(mp3|wav|gsm|mp4|pdf)$ {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Host \$http_host;

  proxy_connect_timeout 300;
  # Default is HTTP/1, keepalive is only enabled in HTTP/1.1
  proxy_http_version 1.1;
  proxy_set_header Connection "";
  chunked_transfer_encoding off;
  proxy_pass ${S3_ENDPOINT};
}

EOF
fi


echo "***[oml-nginx] Adding configuration of desired environment"
if [ ${ENV} == "prodenv" ]; then
  cat >> /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location /static/ {
  alias /opt/omnileads/static/;
  autoindex on;
  allow all;
}

EOF
fi
