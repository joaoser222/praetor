# Plano de correções (auditoria)

Documento de trabalho gerado a partir de uma auditoria do repositório. Reúne os
defeitos encontrados e o plano de execução para corrigi-los, com critérios de
aceite e verificação. Cada item traz o `arquivo:linha`, a evidência e a correção
proposta.

> Escopo: apenas defeitos verificáveis (bugs, incoerências de config, docs
> desatualizadas, lacunas de CI). Itens de mera preferência de estilo ficam de fora.

## Resumo

| # | Severidade | Item | Arquivo(s) | Status |
|---|------------|------|------------|--------|
| 1 | 🔴 Alta | Autenticação por cookie inalcançável | `apps/auth/dependencies.py:18-24,39` | ✅ |
| 2 | 🔴 Alta | `db:reset` deixa o banco vazio e inutilizável | `core/commands/db.py:87-96` | ⬜ |
| 3 | 🟠 Média | Logout do frontend não revoga a sessão no servidor | `web/src/features/auth/action/service.ts` | ✅ |
| 4 | 🟠 Média | Tokens em `localStorage` anulam o `HttpOnly` | `web/src/lib/auth.ts` | ✅ |
| 5 | 🟠 Média | Interceptor de refresh exclui `/profile` | `web/src/lib/api.ts:36-38` | ✅ |
| 6 | 🟠 Média | Cookie `Secure` em produção servido por HTTP | `apps/auth/routers/action.py:19` | ✅ |
| 7 | 🟠 Média | `docs/background_tasks.md` divergente do real | `docs/background_tasks.md:11` | ⬜ |
| 8 | 🟡 Baixa | `docs/cli.md` aponta caminho errado do teste gerado | `docs/cli.md:39` | ⬜ |
| 9 | 🟡 Baixa | `CONTRIBUTING.md` com bootstrap desatualizado | `CONTRIBUTING.md:137` | ⬜ |
| 10 | 🟡 Baixa | Stub de teste do app `auth` não é coletado | `apps/auth/tests/user.py` | ⬜ |
| 11 | 🟡 Baixa | CI `codegen` não valida o backend gerado | `.github/workflows/ci.yml:94-110` | ⬜ |
| 12 | 🟡 Baixa | `version` duplicada (`pyproject` × `settings`) | `pyproject.toml` × `config/settings.py:11` | ⬜ |

> **Lote A (itens 1, 3, 4, 5, 6) implementado.** Itens 2, 7–12 pendentes.

---

## 🔴 Alta

### 1. Autenticação por cookie inalcançável

- **Problema**: `OAuth2PasswordBearerWithCookie.__call__` chama `super().__call__`
  com `auto_error=True` (padrão), que **lança `401` antes** de o fallback de
  cookie ser executado (`dependencies.py:20` e `:24`). Logo, o cookie
  `access_token` nunca é aceito — o método não cumpre o que promete.
- **Evidência**: `apps/auth/dependencies.py:18-24` e `:39`; contradiz
  `docs/authentication.md:9` ("aceito pelo backend e usado pelo Swagger UI").
- **Correção**:
  - Instanciar com `auto_error=False`:
    `oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/action/login", auto_error=False)`.
  - Em `get_token_payload` (`:43-65`), tratar `token is None` levantando `401`
    (hoje `is_jwt_token(None)` já cairia em 401, mas explicitar é mais claro).
  - Remover/ajustar o bloco `if self.auto_error:` interno (`:26-33`), que fica morto.
- **Teste de regressão**: `GET /api/auth/action/profile` **apenas com o cookie**
  `access_token` → `200`; sem header e sem cookie → `401`.
- **Aceite**: cookie autentica; ausência de ambos segue 401.

### 2. `db:reset` deixa o banco vazio e inutilizável

- **Problema**: `db_reset` (`db.py:87-96`) chama `_drop_all()`
  (`db.py:41-43`, `metadata.drop_all`), que **não remove a tabela
  `alembic_version`**. Em seguida `command.upgrade(alembic_cfg, "head")` é no-op,
  porque o Alembic ainda acredita estar em `head`. Resultado: banco sem tabelas e
  `db:migrate` posterior sem efeito.
- **Evidência**: `core/commands/db.py:87-96` (verificado em execução: após
  `db:reset`, só resta `alembic_version`).
- **Correção**: em `db_reset`, antes do `upgrade`, alinhar o Alembic ao estado
  real, por exemplo:
  ```python
  asyncio.run(_drop_all())
  command.downgrade(alembic_cfg, "base")   # ou command.stamp(alembic_cfg, "base")
  command.upgrade(alembic_cfg, "head")
  ```
- **Teste de regressão**: após `db:reset`, todas as tabelas dos models **e**
  `alembic_version` existem.
- **Aceite**: `db:reset` recria o schema integralmente.

---

## 🟠 Média

### 3. Logout do frontend não revoga a sessão no servidor

- **Problema**: `authService.logout` só faz `clearSession()`
  (`service.ts:24-27`); não chama `/auth/action/logout`. O refresh token segue
  válido no banco e os cookies `HttpOnly` não são limpos.
- **Correção**: `await api.post('/auth/action/logout', { refresh_token })` (usando
  o `getRefreshToken()` atual) **antes** do `clearSession()`, tratando falhas.
- **Aceite**: após logout, o refresh token é revogado no servidor e os cookies
  são removidos.

### 4. Tokens em `localStorage` anulam a proteção do `HttpOnly`

- **Problema**: `saveTokens` grava access **e refresh** em `localStorage`
  (`auth.ts:10-13`), legíveis por JS — anulando o motivo do cookie `HttpOnly`. O
  `refreshAccessToken` (`api.ts:20-24`) usa o refresh do storage; o cookie
  `refresh_token` do backend é write-only (nunca lido).
- **Decisão tomada**: **(A) cookie-first completo** — nenhum token no JS. O estado
  do SPA é reconstruído via `/profile` (`AuthProvider`), refresh/logout leem o
  cookie `refresh_token`, e o front deixa de usar o header `Authorization` (que
  segue aceito pela API e pelo Swagger).
- **Aceite**: nenhum token legível por JS; sessão continua funcionando (validado
  por smoke test real: login → cookie → profile/refresh/logout sem corpo → 401).

### 5. Interceptor de refresh exclui o próprio endpoint autenticado

- **Problema**: `isAuthEndpoint = url.includes('/auth/action/')` (`api.ts:36`)
  também casa com `/auth/action/profile`, então um `401` no único GET autenticado
  **nunca dispara** o refresh.
- **Correção**: excluir apenas `login`, `refresh` e `logout` (comparação por
  caminho exato em vez de `includes`).
- **Aceite**: `401` em `/profile` dispara o refresh uma vez e repete a requisição.

### 6. Cookie `Secure` em produção servido por HTTP

- **Problema**: `secure = not settings.DEBUG` (`action.py:19`) → em produção
  (`DEBUG=False`) o cookie sai `Secure`, mas o nginx publica HTTP (`8080:80`).
  Browsers **descartam** cookie `Secure` sobre HTTP → sessão por cookie não
  persiste. (Só passa a "morder" depois de corrigir o item 1.)
- **Correção**: exposto como `COOKIE_SECURE: Optional[bool]` em
  `config/settings.py` (property `cookie_secure` deriva de `DEBUG` quando `None`);
  `action.py` usa `secure=settings.cookie_secure`. Documentado no `.env.example`
  que produção **deve** servir HTTPS (ou definir `COOKIE_SECURE=false`).
- **Aceite**: cookie coerente com o esquema em uso; funciona em dev e em prod
  (atrás de TLS).

### 7. `docs/background_tasks.md` divergente do real

- **Problema**: o doc mostra `CELERY_RESULT_BACKEND="db+sqlite:///celery_results.db"`
  (`background_tasks.md:11`), mas `.env.example:57` e `docker/compose/base.yml`
  usam `redis://.../1`, e o extra instalado é `celery[redis]` (o backend `db+`
  exigiria `celery[sqlalchemy]`).
- **Correção**: alinhar o exemplo para `redis://localhost:6379/1`; se quiser citar
  a alternativa `db+`, marcá-la como opcional **e** citar a dependência extra.
- **Aceite**: doc bate com `.env.example` e com o `AGENTS.md`.

---

## 🟡 Baixa

### 8. `docs/cli.md` aponta caminho errado do teste gerado

- **Problema**: `docs/cli.md:39` diz `tests/{entity}.py`; o gerador cria
  `tests/test_{name}.py` (`core/commands/make.py:134`).
- **Correção**: ajustar o doc.

### 9. `CONTRIBUTING.md` com bootstrap desatualizado

- **Problema**: `CONTRIBUTING.md:137` afirma "ships with `master` only", mas
  `develop` já existe localmente e remoto (`origin/HEAD -> develop`). Mesmo tom em
  `AGENTS.md:19`.
- **Correção**: atualizar o texto para o estado atual (bootstrap já feito).

### 10. Stub de teste do app `auth` não é coletado

- **Problema**: `apps/auth/tests/user.py` contém só um comentário; não casa com
  `python_files = ["test_*.py","*_test.py"]` e o diretório não tem `__init__.py`.
- **Correção**: renomear para `test_user.py` (com `__init__.py`) se for virar
  teste real, ou remover o arquivo morto.

### 11. CI `codegen` não valida o backend gerado

- **Problema**: o job `codegen` (`.github/workflows/ci.yml:94-110`) roda
  `make:app`/`make:entity` e só faz `npm run build`; o backend gerado (model,
  router, **template de teste**) nunca passa por `ruff`/`pytest`.
- **Correção**: no job, rodar `ruff check apps/` e
  `pytest apps/<sample>/tests` após gerar.
- **Aceite**: template Python quebrado reprova o CI.

### 12. `version` duplicada

- **Problema**: `pyproject.toml` (`version = "0.1.0"`) duplica
  `config/settings.py:11` (`APP_VERSION`).
- **Correção** (opcional): fonte única — ex. `dynamic = ["version"]` lendo de um
  local comum, ou manter a duplicação consciente e comentada.

---

## Ordem de execução sugerida (lotes)

1. **Lote A — Autenticação/sessão** (itens 1, 6, 3, 5, 4): resolve o que quebra
   funcionalidade hoje. ✅ **Concluído** (item 4 decidido: cookie-first completo).
2. **Lote B — CLI/DB** (item 2): pequeno e independente.
3. **Lote C — Documentação** (itens 7, 8, 9).
4. **Lote D — Higiene/CI** (itens 10, 11, 12).

## Verificação

- **Backend**: `ruff check .`; `pytest` — **adicionar testes de regressão** para os
  itens 1 (cookie) e 2 (`db:reset`).
- **Frontend**: `npm run lint` e `npm run build` (em `web/`).
- **Docker**: `docker compose config -q` (dev e prod); `docker compose build` +
  smoke test (`/health`, web `200`) e prod (`migrate` aplicado).
- **CI**: após o item 11, simular o job `codegen` localmente
  (`make:app sample` + `make:entity product` + `ruff`/`pytest` no gerado).

## Fora de escopo

- Migrar a fila para banco (decisão registrada: manter Redis — ver `AGENTS.md`).
- TLS/HTTPS de ponta a ponta: o item 6 cobre apenas a **coerência cookie ×
  esquema**; a terminação TLS é infraestrutura à parte.
