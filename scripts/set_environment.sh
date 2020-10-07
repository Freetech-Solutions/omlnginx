#!/bin/sh

echo "***[oml-nginx] Adding configuration of desired environment"
if [ $DJANGO_SETTINGS_MODULE == "ominicontacto.settings.develop" ]; then
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
EOF
elif [ $DJANGO_SETTINGS_MODULE == "ominicontacto.settings.production" ]; then
  cat <<EOF >> /etc/nginx/conf.d/environment/prodenv.conf
location / {
  uwsgi_pass         app:8099;
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
EOF
fi
