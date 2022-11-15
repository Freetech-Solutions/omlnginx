FROM nginx:1.23.2-alpine as run

RUN apk add bash

COPY source/conf/ /etc/nginx/
COPY source/certs/* /etc/omnileads/certs/
COPY source/set_environment.sh /docker-entrypoint.d/

EXPOSE 443/tcp
