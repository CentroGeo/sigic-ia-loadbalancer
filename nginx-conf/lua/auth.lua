local oidc = require("resty.openidc")
local cjson = require("cjson.safe")

-- 🔹 detectar tenant desde nginx
local tenant = ngx.var.oidc_tenant

-- 🔹 cargar tenants (si existen)
local tenants_json = os.getenv("OIDC_TENANTS")
local tenants = nil

if tenants_json and tenants_json ~= "" then
    tenants = cjson.decode(tenants_json)
    if not tenants then
        ngx.log(ngx.ERR, "OIDC_TENANTS inválido")
        return ngx.exit(500)
    end
end

local opts = nil

-- 🔥 CASO 1: multi-tenant
if tenants then

    if not tenant or tenant == "" then
        tenant = os.getenv("OIDC_DEFAULT_TENANT")
    end

    if not tenant or tenant == "" then
        ngx.status = 500
        ngx.say('{"error":"No tenant definido"}')
        return ngx.exit(500)
    end

    local cfg = tenants[tenant]

    if not cfg then
        ngx.status = 403
        ngx.say('{"error":"Tenant no permitido"}')
        return ngx.exit(403)
    end

    if not cfg.discovery then
        ngx.log(ngx.ERR, "Tenant sin discovery: ", tenant)
        return ngx.exit(500)
    end

    opts = {
        discovery = cfg.discovery,
        ssl_verify = "yes",
        cafile = "/etc/ssl/certs/ca-certificates.crt",
        timeout = 10000,
        cache_segment = tenant
    }

-- 🔥 CASO 2: modo viejo (single keycloak)
else

    local oidc_config_url = os.getenv("OIDC_CONFIG_URL")

    if not oidc_config_url then
        ngx.log(ngx.ERR, "No hay OIDC_TENANTS ni OIDC_CONFIG_URL")
        return ngx.exit(500)
    end

    ngx.log(ngx.NOTICE, "Usando modo legacy OIDC_CONFIG_URL = ", oidc_config_url)

    opts = {
        discovery = oidc_config_url,
        ssl_verify = "yes",
        cafile = "/etc/ssl/certs/ca-certificates.crt",
        timeout = 10000
    }
end

-- 🔹 validar token
local res, err = oidc.bearer_jwt_verify(opts)

if err then
    ngx.status = 401
    ngx.say(cjson.encode({
        error = "Authentication failed",
        detail = err,
        tenant = tenant
    }))
    return ngx.exit(ngx.HTTP_UNAUTHORIZED)
end

-- 🔹 headers útiles
if res then
    if res.sub then
        ngx.req.set_header("X-Auth-User", res.sub)
    end
    if res.iss then
        ngx.req.set_header("X-Auth-Issuer", res.iss)
    end
end