FROM nginx:1.19.0-alpine

COPY conf/* /etc/nginx/

EXPOSE 443/tcp
