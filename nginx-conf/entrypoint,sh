#!/bin/sh
# Detecta DNS automáticamente
if [ -z "$NGINX_RESOLVER" ]; then
  export NGINX_RESOLVER=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)
  echo "[entrypoint] Resolver auto-detectado: $NGINX_RESOLVER"
fi

exec /usr/local/openresty/bin/openresty -g "daemon off;"
