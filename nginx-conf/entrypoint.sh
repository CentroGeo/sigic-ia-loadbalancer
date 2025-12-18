#!/bin/sh
set -e

RESOLVER=$(awk '/^nameserver/{print $2; exit}' /etc/resolv.conf)
echo "[entrypoint] Resolver auto-detectado: $RESOLVER"

# Sustituye resolver
sed -i "s|\$NGINX_RESOLVER|$RESOLVER|g" /usr/local/openresty/nginx/conf/nginx.conf

###############################################
# Generar upstream dinámico para ia-engine
###############################################

IA_ENGINE_CONF="/etc/nginx/upstreams/ia-engine.conf"

echo "[entrypoint] Generando upstream dinámico: ia-engine"

SERVER_LINES=""

IA_ENGINE_SERVERS="${IA_ENGINE_SERVERS//,/ }"

{
    echo "upstream ia-engine {"
    for HOST in $IA_ENGINE_SERVERS; do
        echo "    server $HOST;"
    done
    echo "}"
} > "$IA_ENGINE_CONF"

echo "[entrypoint] Upstream generado:"
cat "$IA_ENGINE_CONF"

###############################################

exec /usr/local/openresty/bin/openresty -g "daemon off;"
