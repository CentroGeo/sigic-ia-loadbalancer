local oidc = require("resty.openidc")

local opts = {
    discovery = "https://iam.dev.geoint.mx/realms/sigic/.well-known/openid-configuration",
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