#!/bin/bash
set -e
source /etc/profile.d/omnileads_envars.sh
# Script that runs after nginx install
echo "Modifying user in nginx.conf"
sed -i 's/^user.*/user omnileads;/' /etc/nginx/nginx.conf
echo "Modify server name in ominicontacto.conf"
sed -i "s/server_name.*/server_name     $(hostname);/" /etc/nginx/conf.d/ominicontacto.conf
echo "Modify kamailio & websockets host in ominicontacto.conf"
sed -i "s/kamailio/${KAMAILIO_HOSTNAME}/" /etc/nginx/conf.d/ominicontacto.conf
sed -i "s/websockets/${WEBSOCKET_HOST}/" /etc/nginx/conf.d/ominicontacto.conf
chown -R omnileads. /opt/omnileads/nginx_certs
echo "Enabling nginx"
systemctl enable nginx
