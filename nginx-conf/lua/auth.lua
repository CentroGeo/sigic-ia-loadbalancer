local oidc = require("resty.openidc")
local cjson = require("cjson.safe")

local oidc_config_url_dev = os.getenv("OIDC_CONFIG_URL_DEV")
local oidc_config_url_prod = os.getenv("OIDC_CONFIG_URL_PROD")

if not oidc_config_url_dev or not oidc_config_url_prod then
    ngx.log(ngx.ERR, "Faltan variables OIDC_CONFIG_URL")
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
end

-- ISS permitidos
local TRUSTED_ISSUERS = {
    [oidc_config_url_dev] = true,
    [oidc_config_url_prod] = true
}

local auth_header = ngx.var.http_authorization
if not auth_header then
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

local token = auth_header:match("Bearer%s+(.+)")
if not token then
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

local payload_b64 = token:match("^[^.]+%.([^.]+)%.")
if not payload_b64 then
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

local payload_json = ngx.decode_base64(payload_b64)
local payload = cjson.decode(payload_json)

if not payload or not payload.iss then
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

if not TRUSTED_ISSUERS[payload.iss] then
    ngx.log(ngx.ERR, "Issuer no permitido: ", payload.iss)
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

local discovery = payload.iss .. "/.well-known/openid-configuration"

local opts = {
    discovery = discovery,
    ssl_verify = "yes",
    cafile = "/etc/ssl/certs/ca-certificates.crt",
    timeout = 10000,
    accepted_algs = { "RS256" }
}

local res, err = oidc.bearer_jwt_verify(opts)

if err then
    ngx.status = 401
    ngx.say('{"error": "Authentication failed: ' .. (err or "unknown") .. '"}')
    ngx.exit(ngx.HTTP_UNAUTHORIZED)
end