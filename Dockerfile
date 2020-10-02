FROM nginx:1.19.0-alpine

COPY conf/* /etc/nginx/
COPY scripts/* /root/

EXPOSE 443/tcp
