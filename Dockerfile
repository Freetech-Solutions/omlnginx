FROM nginx:1.29.4-alpine as run

ENV INSTALL_PREFIX /opt/omnileads

RUN mkdir -p $INSTALL_PREFIX/asterisk \
    && apk add bash \
    && addgroup -g 1000 -S omnileads &&  adduser -u 1000 -S omnileads -G omnileads -h $INSTALL_PREFIX -s /bin/bash

COPY source/conf/ /etc/nginx/
COPY source/certs/* /etc/omnileads/certs/
COPY source/set_environment.sh /docker-entrypoint.d/90-set-environment.sh

RUN chown -R omnileads:omnileads $INSTALL_PREFIX && chmod g+s $INSTALL_PREFIX/asterisk

EXPOSE 443/tcp

COPY templates/ /etc/nginx/templates/
