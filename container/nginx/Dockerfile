FROM nginx:stable

RUN rm /etc/nginx/conf.d/default.conf

ADD conf.d/* /etc/nginx/conf.d/

ARG NGINX_CONF

ADD ${NGINX_CONF} /etc/nginx/nginx.conf
