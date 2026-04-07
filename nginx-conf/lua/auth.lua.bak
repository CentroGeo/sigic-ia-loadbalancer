local oidc = require("resty.openidc")

local oidc_config_url = os.getenv("OIDC_CONFIG_URL")

if not oidc_config_url then
    ngx.log(ngx.ERR, "No se encontró la variable de entorno OIDC_CONFIG_URL")
else
    ngx.log(ngx.NOTICE, "OIDC_CONFIG_URL = ", oidc_config_url)
end

local opts = {
    discovery = oidc_config_url,
    ssl_verify = "yes",
    cafile = "/etc/ssl/certs/ca-certificates.crt",
    timeout = 10000
}

local res, err = oidc.bearer_jwt_verify(opts)

if err then
    ngx.status = 401
    ngx.say('{"error": "Authentication failed: ' .. (err or "unknown") .. '"}')
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end