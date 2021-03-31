FROM nginx:1.19.0-alpine

COPY source/conf/* /etc/nginx/
COPY source/certs/* /opt/omnileads/nginx_certs/
COPY source/set_environment.sh /docker-entrypoint.d/

EXPOSE 443/tcp
