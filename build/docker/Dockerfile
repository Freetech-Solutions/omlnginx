FROM nginx:1.19.0-alpine

RUN apk add bash

COPY source/conf/ /etc/nginx/
COPY source/certs/* /etc/omnileads/certs/
COPY source/set_environment.sh /docker-entrypoint.d/

EXPOSE 443/tcp
