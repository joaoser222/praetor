---
name: python-comments
description: >
  Comment and docstring standard for api/: Google Python Style Guide §3.8
  applied strictly (spacing, punctuation, never narrate the code, docstring
  summary line plus Args/Returns/Yields/Raises/Attributes sections, TODO
  format) while keeping the house language split: comments and docstrings are
  written in Brazilian Portuguese (pt-BR), code identifiers stay in English.
  Also defines which comments are unnecessary or stale and may be removed,
  which must never be removed, and how to verify. Load when writing,
  reviewing or cleaning any Python comment, docstring or TODO under api/.
---

# Python comments: house rules

The Google Python Style Guide (§3.8) is the standard for **form**. This skill
adds what the guide does not decide for us: the **language** (pt-BR, per
AGENTS.md §5), **what may be deleted**, and **how to verify**.

This file is written in English because it instructs the model. The comments
and docstrings it governs are written in **pt-BR**; every example below
follows that.

## When to load

- Writing any `#` comment, docstring or `TODO` under `api/`.
- Reviewing a diff that touches comments.
- A request to clean up, remove or standardize comments.
- Before declaring a comment-related task done.

## Decision tree (apply before writing anything)

1. Do the name, signature and type hints already say it? → **Write nothing.**
2. Is it public contract (module, class, non-trivial public function)? → **Docstring.**
3. Is it the *why* behind something non-obvious inside a body? → **`#` comment.**
4. Is it trackable future work? → **`TODO` in the standard format.**
5. None of the above? → **Nothing.** Uncommented code is acceptable.

## Block comments

```python
# Política de upload: o limite vem do Settings, não deste módulo.
max_size = settings.max_zip_size
```

1. `#` followed by **one space**, then the text.
2. Complete sentences: capitalized, punctuated, ending in a period. They must
   read as narrative text (§3.8.6).
3. **Never describe the code** (§3.8.5). The reader knows Python. If the
   comment would survive deleting the code line, it is narration: delete it
   instead of writing it.
4. A comment must earn its place: explain *why*, name a contract, or record a
   non-obvious constraint. If it does none of these, it is unnecessary.
5. Place block comments **above** the code they explain, at the same
   indentation, covering a single topic. Separate paragraphs with a line
   containing only `#`.
6. For genuinely tricky logic, comment **before** the hard operation instead
   of line by line.

## Inline comments (end of line)

```python
search_ids = []  # Placeholder intencional; ver AGENTS §7 (F841).
```

1. **Two or more spaces** between code and `#`, then **one space** after it.
2. Same sentence rules as block comments.
3. Only for the non-obvious. Longer explanations go on the line above.
4. Do not align `#` into columns across consecutive lines; alignment breaks on
   every edit.

## TODO

```python
# TODO: PROJ-123 - Remover quando o endpoint v1 for desativado.
```

1. Format: `# TODO: <link or id> - <action and removal condition>.`
2. Without a link or id a TODO has no owner and no deadline: state the removal
   condition or do not write it.
3. A TODO pointing at work that is already done is a *dead instruction* (see
   "What may be removed").

## Docstrings

### General form

1. Triple double quotes `"""`.
2. **Summary line**: a single line, at most 80 characters, ending in `.`, `?`
   or `!`. Use the third person present in Portuguese ("Retorna", "Cria",
   "Valida"). Describe what the function does, not how.
3. Blank line, then the body at the same column as the opening quotes.
4. A one-line docstring keeps the closing quotes on the same line.
5. A multi-line docstring puts the closing quotes on their own line.

```python
def is_expired(token: Token) -> bool:
    """Indica se o token já passou da validade."""
```

### Google sections

Headers end with a colon; content uses a 4-space hanging indent, consistent
within the file. Supported: `Args:`, `Returns:`, `Yields:`, `Raises:`,
`Attributes:`, `Example:`.

```python
async def get_tenant_orders(
    tenant_id: UUID,
    *,
    status: OrderStatus | None = None,
    limit: int = 50,
) -> list[Order]:
    """Lista os pedidos de um tenant, do mais recente ao mais antigo.

    Sempre aplica o filtro de tenant; nunca retorna pedidos de outro tenant.

    Args:
        tenant_id: Identificador do tenant dono dos pedidos.
        status: Se informado, restringe a pedidos nesse status.
        limit: Máximo de pedidos retornados. Deve ser positivo.

    Returns:
        Pedidos ordenados por criação decrescente. Lista vazia se não houver.

    Raises:
        ValueError: Se `limit` não for positivo.
    """
```

Per-section rules:

- **`Args:`** lists **every** parameter, in signature order, as
  `name: description.`. Include `*args` and `**kwargs` with the asterisks.
  **Do not repeat the type** when a type annotation exists; describe meaning,
  constraints and relevant defaults.
- **`Returns:`** describes the returned value and its meaning, not just its
  type. Omit it when the function returns `None` or the summary already says
  everything. Never write `Returns: None.`.
- **`Yields:`** replaces `Returns:` for generators.
- **`Raises:`** lists only exceptions that are **part of the contract**
  (raised deliberately or relevant to callers). Do not list incidental
  exceptions, nor those that signal a violation of the `Args:` contract.
- **`Attributes:`** on classes, for public attributes (dataclasses, Pydantic
  models, ORM models). Same format as `Args:`.
- **`Example:`** only when usage is non-obvious. Use doctest format only if
  doctests run in CI; otherwise use a plain code block.

### Modules, classes and functions

1. **Module**: docstring at the top (after shebang/encoding) with a one-line
   summary and, if useful, the module's role in the architecture and what it
   does **not** do.
2. **Class**: summary plus `Attributes:` when there are public attributes.
   Document the constructor in the class docstring, not in `__init__`, unless
   `__init__` has relevant logic.
3. **Function/method**: required when it is public **and** non-trivial, has
   more than ~10 lines, or its contract is not deducible from the signature.
4. **Exempt** (§3.8.1): test modules, trivial functions (simple getters,
   one-line wrappers), obvious private methods, and `@override` methods (the
   documentation lives in the base; document only if behavior changes).
5. **Decorated functions** describe the behavior **after** decoration.
6. **Properties** describe the value as an attribute ("Tamanho em bytes."), not
   as a method ("Retorna o tamanho...").

### FastAPI routes and Pydantic models

When a docstring feeds OpenAPI it is read by API consumers:

- The route **summary** must make sense to someone consuming the endpoint.
- Use `Args:` only for parameters **not** already described in
  `Query(...)`, `Path(...)` or `Field(description=...)`, to avoid duplication.
- Keep internal details (table names, layers) out of exposed route
  docstrings; put them in a `#` comment inside the body.
- In Pydantic models prefer `Field(description=...)` for exposed fields and
  use `Attributes:` only for what does not appear in the schema.

## Language

- Comments and docstrings: **pt-BR** (AGENTS.md §5, the defining split). The
  Google guide prescribes form, not language.
- Identifiers (variables, functions, classes, modules): **English**.
- Established technical terms may stay in English inside a Portuguese
  sentence (`tenant`, `payload`, `middleware`); wrap symbol names in
  backticks (`` `tenant_id` ``).
- Never "fix" the split by translating comments to English or identifiers to
  Portuguese.
- Exception messages and log messages follow their own AGENTS.md rule; this
  skill covers only comments and docstrings.

## Right × wrong

| ✗ Wrong | ✓ Right |
|---|---|
| `# incrementa o contador` | *(delete)* |
| `#Valida o usuário` | `# Valida o usuário antes de abrir a sessão.` |
| `x = 1 # timeout` | `x = 1  # Timeout em segundos; ver SLA do gateway.` |
| `"""Função que cria usuário"""` | `"""Cria um usuário e envia o e-mail de boas-vindas."""` |
| `Returns: str: o nome.` | `Returns: Nome de exibição, sem espaços nas pontas.` |
| `Args: user_id (int): o id` | `Args: user_id: Identificador do usuário no tenant atual.` |
| `# TODO: arrumar isso` | `# TODO: PROJ-123 - Remover após migração do schema v2.` |
| `# print(df.head())` | *(delete; git keeps history)* |

## What may be removed

- **Narration**: restates the adjacent code (`# incrementa o contador`).
- **Stale architecture**: references to paths or layers that no longer exist
  (`app/shared/`, `app/views/`, `features/*/`, "fatia", "vertical slice").
  Rewrite if the *why* still applies to the new structure; delete otherwise.
- **Dead instructions**: "descomente para…", TODOs pointing at finished work,
  commented-out code blocks (git history keeps them).
- **Debug leftovers**: temporary prints/flags and their explanations.
- **Duplication**: a line comment repeating the docstring above it, or a
  docstring that only repeats the signature (names and types) without adding
  meaning.
- **Noise headers**: banners (`# ======`), author/date signatures and inline
  changelogs. Git is the source of truth.

## What must never be removed

- **Why-comments**: the reason behind a non-obvious choice (AGENTS §8: bug
  fixes come with the reason).
- **Contract notes**: frontend/backend contracts ("não renomeie essa chave"),
  security invariants (httpOnly, tenant filter) and known-issue notes
  (AGENTS §7).
- **Test intent**: characterization comments saying what an assertion
  protects.
- **Justified suppressions**: `# noqa`, `# type: ignore` and `# pragma` with
  their reason. Removing the reason while keeping the suppression is a
  regression.

## Editing existing comments

1. Comment-only changes **must not alter behavior**: do not mix them with code
   refactors in the same commit.
2. When changing code, update or delete the affected comment. A comment that
   contradicts the code is worse than none.
3. Do not reformat docstrings that already follow the file's convention; fix
   only what is broken (malformed section, missing period, indentation).
4. When unsure whether to delete a why-comment, **keep it**.

## Tooling

Suggested `pyproject.toml` configuration so `ruff` covers form automatically
(language and semantics remain human review):

```toml
[tool.ruff.lint]
extend-select = ["D", "E501", "W291", "W293"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D"]
```

## Verification

- `grep -rn '#[^#! \t]' api --include='*.py'` → only shebang/`noqa` remain.
- `grep -rnE '\S #' api/app --include='*.py'` → no inline comment closer than
  two spaces to the code.
- `grep -rnE '#.*(shared/|app\.views|features/|fatia)' api` → empty.
- `grep -rnP '#\s*TODO(?!:)' api --include='*.py'` → empty (TODO without colon).
- `grep -rnE '^\s*#\s*(print|import|def |return )' api --include='*.py'` →
  empty (commented-out code).
- `ruff check api` → count does not grow; `ruff check api --select D` → no new
  violations.
- `pytest` → green.

## Final checklist

- [ ] Every comment says *why*, not *what*.
- [ ] Complete sentences with a period, in pt-BR; identifiers in English.
- [ ] Docstrings have a summary ≤ 80 characters and correct Google sections.
- [ ] No type repeated in `Args:` when an annotation exists.
- [ ] No why-comment, contract note or justified suppression removed.
- [ ] Verifications above executed and `pytest` green.
