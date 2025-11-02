#!/bin/sh
# genera la lista de nameservers desde el resolv.conf del host
RESOLVERS=$(awk '/^nameserver/{printf "%s ", $2}' /etc/resolv.conf)

# crea un fragmento temporal
echo "resolver $RESOLVERS ipv6=off valid=30s;" > /etc/nginx/conf.d/resolvers.conf

# arranca OpenResty normalmente
exec /usr/local/openresty/bin/openresty -g "daemon off;"