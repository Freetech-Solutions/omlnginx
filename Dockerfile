FROM nginx:1.19.0-alpine

COPY conf/* /etc/nginx/
COPY scripts/* /docker-entrypoint.d/

EXPOSE 443/tcp
