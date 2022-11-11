#!/bin/bash

if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

echo "***[oml-nginx] Adding configuration of desired environment"
if [ ${ENV} == "devenv" ]; then
  cat > /etc/nginx/conf.d/environment/devenv.conf <<EOF
location / {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer 	     \$http_referer;
  proxy_pass http://${DJANGO_HOSTNAME}:8099;
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
  proxy_pass http://${DAPHNE_HOSTNAME}:8098;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}

location ~* (ws) {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
  proxy_pass https://${KAMAILIO_HOSTNAME}:14443;
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
  proxy_pass http://${WEBSOCKETS_HOSTNAME}:8000;
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

else
  cat > /etc/nginx/conf.d/environment/prodenv.conf <<EOF
location / {
  uwsgi_pass ${DJANGO_HOSTNAME}:8098;
  include         uwsgi_params;
  uwsgi_send_timeout 600s;
  uwsgi_read_timeout 600s;
  uwsgi_connect_timeout 600s;
  keepalive_timeout 600s;
  send_timeout      600s;
  uwsgi_param HTTP_X_REAL_IP \$remote_addr;
  uwsgi_param HTTP_X_FORWARDED_FOR \$proxy_add_x_forwarded_for;
  uwsgi_param HTTP_X_FORWARDED_PORT \$server_port;
  uwsgi_param HTTP_X_FORWARDED_PROTO \$scheme;
  uwsgi_param HTTP_REFERER \$http_referer;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;
}

location ~* (ws) {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
  proxy_pass https://${KAMAILIO_HOSTNAME}:14443;
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
  proxy_pass http://${WEBSOCKETS_HOSTNAME}:8000;
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

location ~ ^/(channels) {
  alias /opt/omnileads/static/ominicontacto/JS/socket.io.js;
  proxy_pass http://${DJANGO_HOSTNAME}:8099;
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer  \$http_referer;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}

location /static/ {
  alias /opt/omnileads/static/;
  autoindex on;
  allow all;
}

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
