#!/bin/bash

if [ ! -d /etc/nginx/conf.d/environment ]; then
  echo "***[oml-nginx] Creating environment directory"
  mkdir -p /etc/nginx/conf.d/environment/
fi

echo "***[oml-nginx] Adding configuration of desired environment"
if [ ${ENV} == "prodenv" ]; then
  cat > /etc/nginx/conf.d/environment/oml_env.conf <<EOF
location /static/ {
  alias /opt/omnileads/static/;
  autoindex on;
  allow all;
}
EOF
fi
