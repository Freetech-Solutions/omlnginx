#!/bin/bash
if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

echo "***[oml-nginx] Adding configuration of desired environment"
if [ $ENV == "devenv" ]; then
  cat > /etc/nginx/conf.d/environment/devenv.conf <<EOF
location / {
  proxy_set_header X-Real-IP \$remote_addr;
  proxy_set_header Host \$host;
  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Port \$server_port;
  proxy_set_header X-Forwarded-Proto \$scheme;
  proxy_set_header Referer 	     \$http_referer;
  proxy_pass http://app:8099;
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
  proxy_pass http://app:8099;
  proxy_read_timeout 600s;
  proxy_connect_timeout 600s;
  proxy_send_timeout 600s;

  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}
EOF
elif [ $ENV == "prodenv" ]; then
  if [ $INFRA == "docker" ]; then
    UWSGI_PASS="  uwsgi_pass         app:8099;"
  elif [ $INFRA == "onpremise" ]; then
    UWSGI_PASS="  uwsgi_pass      unix:/opt/omnileads/run/oml_uwsgi.socket;"
    sed -i "s/alias \/var\/spool\/asterisk\/monitor.*/alias \/opt\/omnileads\/asterisk\/var\/spool\/asterisk\/monitor;/g" /etc/nginx/conf.d/ominicontacto.conf
  fi
  cat > /etc/nginx/conf.d/environment/prodenv.conf <<EOF
location / {
  ${UWSGI_PASS}
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

location ~ ^/(channels) {
  ${UWSGI_PASS}
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

  proxy_http_version 1.1;
  proxy_set_header Connection "upgrade";
  proxy_set_header Upgrade \$http_upgrade;
}

location /static/ {
  alias /opt/omnileads/static/;
  autoindex on;
  allow all;
}
EOF
fi
