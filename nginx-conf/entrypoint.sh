#!/bin/sh
RESOLVER=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)
export NGINX_RESOLVER=$RESOLVER
echo "[entrypoint] Resolver auto-detectado: $NGINX_RESOLVER"

# Sustituye variables del template
envsubst < /usr/local/openresty/nginx/conf/nginx.conf.template > /usr/local/openresty/nginx/conf/nginx.conf

exec /usr/local/openresty/bin/openresty -g "daemon off;"
