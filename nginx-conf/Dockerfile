FROM openresty/openresty:alpine-fat

# Instala dependencias SSL y CA certificates
RUN apk add --no-cache bash curl git lua5.1 lua5.1-dev build-base \
    openssl openssl-dev ca-certificates unzip wget

# Actualiza certificados CA
RUN update-ca-certificates --fresh

# Configura certificados SSL para Lua
RUN mkdir -p /etc/ssl/certs/lua && \
    cp /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/lua/

RUN luarocks install lua-cjson 2.1.0.9-1
RUN luarocks install lua-resty-string
RUN luarocks install luaossl CRYPTO_DIR=/usr LIBDIR=/usr/lib
RUN luarocks install lua-resty-jwt
RUN luarocks install lua-resty-http
RUN luarocks install lua-resty-openidc

RUN mkdir -p /usr/local/openresty/lualib/

# COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf.template
COPY lua/auth.lua /usr/local/openresty/lualib/auth.lua

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# CMD ["/usr/local/openresty/bin/openresty", "-g", "daemon off;"]