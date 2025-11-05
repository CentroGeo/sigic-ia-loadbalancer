#!/bin/sh
RESOLVER=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)
echo "[entrypoint] Resolver auto-detectado: $RESOLVER"

# Sustituye la variable en nginx.conf
sed -i "s|\$NGINX_RESOLVER|$RESOLVER|g" /usr/local/openresty/nginx/conf/nginx.conf

exec /usr/local/openresty/bin/openresty -g "daemon off;"
