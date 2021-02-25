#!/bin/bash
# Script that runs after nginx remove
echo "Removing nginx folders"
rm -rf /etc/nginx/
rm -rf /opt/omnileads/nginx_certs
rm -rf /opt/omnileads/kamailio
