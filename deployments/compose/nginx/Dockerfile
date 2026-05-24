FROM nginx:alpine

COPY deployments/compose/nginx/nginx.conf /etc/nginx/nginx.conf
COPY deployments/compose/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf
COPY deployments/compose/nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
