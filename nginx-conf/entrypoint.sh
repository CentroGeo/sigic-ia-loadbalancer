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
IFS=',' read -ra ADDR <<< "$IA_ENGINE_SERVERS"

for HOST in "${ADDR[@]}"; do
  SERVER_LINES="${SERVER_LINES}    server ${HOST};\n"
done

# Renderizar template
sed "s|{{IA_ENGINE_SERVERS}}|$SERVER_LINES|" \
    /etc/nginx/upstreams/ia-engine.conf.template \
    > "$IA_ENGINE_CONF"

echo "[entrypoint] Upstream generado:"
cat "$IA_ENGINE_CONF"

###############################################

exec /usr/local/openresty/bin/openresty -g "daemon off;"
