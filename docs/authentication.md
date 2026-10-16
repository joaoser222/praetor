# Authentication & Security

Praetor implements a high-security, hybrid authentication model using JWT and Opaque Refresh Tokens.

## The Hybrid Model

### 1. Access Tokens (JWT)
- **Type**: JSON Web Token (JWT).
- **Storage**: No login, o backend grava o token em um cookie `HttpOnly` (`access_token`). O SPA (cookie-first) **não lê nem envia** o token — o cookie viaja automaticamente (`withCredentials`). A API também aceita `Authorization: Bearer <token>`, usado pelo Swagger UI e por clientes externos.
- **Validation**: Stateless. Validated using the `SECRET_KEY` without database lookups, ensuring high performance.
- **Lifespan**: Short-lived (15 minutes by default). Como é stateless, o logout **não** o invalida antes do `exp` — o TTL curto limita essa janela.

### 2. Refresh Tokens (Opaque)
- **Type**: Random secure string (Opaque).
- **Storage**: Stored in the database and linked to a user. Também é gravado no cookie `HttpOnly` `refresh_token`.
- **Validation**: Stateful. Requires a database lookup to check if the token is valid and not revoked.
- **Lifespan**: Typically long-lived (e.g., 7 days).
- **Security**: Can be revoked instantly (e.g., on logout or password change), providing a "kill switch" for active sessions.

## SPA Session (Cookie-first)

O SPA não armazena tokens em `localStorage`/JS — ambos vivem em cookies `HttpOnly`:

- Os endpoints `/auth/action/refresh` e `/auth/action/logout` leem o refresh token **do corpo (se enviado) ou do cookie** `refresh_token`, então o front chama-os **sem corpo**.
- O estado de autenticação do SPA é reconstruído no boot via `GET /auth/action/profile` (`AuthProvider`); um `401` dispara o refresh transparente no interceptor do axios uma única vez.
- O logout revoga o refresh token no servidor e limpa os cookies; o access JWT expira sozinho dentro do TTL.
- Cookies usam `SameSite=Lax` (bloqueia POST cross-site) e `Secure` conforme `COOKIE_SECURE` (deriva de `DEBUG` quando não definido).

## Role-Based Access Control (RBAC)

Permissions are defined granularly within each app's `permissions/` directory.

### Checking Permissions
You can protect endpoints using the `require_permission` dependency:

```python
from core.dependencies import require_permission

@router.get("/", dependencies=[Depends(require_permission("user:list"))])
async def list_users():
    ...
```

### Syncing Permissions
Whenever you add or modify permissions in your code, sync them with the database:

```bash
python manage.py auth:makepermissions
```

## OAuth2 & Swagger Integration

The system uses `OAuth2PasswordBearerWithCookie`, which is fully compatible with FastAPI's OpenAPI generation. The **"Authorize"** button in Swagger UI works out-of-the-box, even with our hybrid header/cookie support.
