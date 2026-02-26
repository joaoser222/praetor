# Authentication & Security

Praetor implements a high-security, hybrid authentication model using JWT and Opaque Refresh Tokens.

## The Hybrid Model

### 1. Access Tokens (JWT)
- **Type**: JSON Web Token (JWT).
- **Storage**: Sent via the `Authorization: Bearer <token>` header or as a `HttpOnly` cookie.
- **Validation**: Stateless. Validated using the `SECRET_KEY` without database lookups, ensuring high performance.
- **Lifespan**: Typically short-lived (e.g., 30 minutes).

### 2. Refresh Tokens (Opaque)
- **Type**: Random secure string (Opaque).
- **Storage**: Stored in the database and linked to a user.
- **Validation**: Stateful. Requires a database lookup to check if the token is valid and not revoked.
- **Lifespan**: Typically long-lived (e.g., 7 days).
- **Security**: Can be revoked instantly (e.g., on logout or password change), providing a "kill switch" for active sessions.

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
