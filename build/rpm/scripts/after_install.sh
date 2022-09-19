#!/bin/bash
set -e
source /etc/default/nginx.env
# Script that runs after nginx install
echo "Modifying user in nginx.conf"
sed -i 's/^user.*/user omnileads;/' /etc/nginx/nginx.conf
echo "Modify server name in ominicontacto.conf"
sed -i "s/server_name.*/server_name     $(hostname);/" /etc/nginx/conf.d/ominicontacto.conf
