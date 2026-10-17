---
name: celery-tasks
description: >
  Use when the user asks to create, call or run background tasks in
  Praetor with Celery. Covers defining a task in apps/<app>/tasks.py,
  calling it with .delay(), starting the worker, and the Redis requirement.
  Use it for long-running work such as email, file processing or external
  API calls, not for work that the request can finish in time.
compatibility:
  - python 3.12
  - celery[redis] 5
  - redis 7
---

# Celery Tasks — Praetor

## When to use

Use this skill when the user asks to:

- create a background task;
- queue a task from a service or router;
- start or debug the Celery worker.

Do not use a task for work that can finish within the HTTP request. Keep
the request fast and move only long-running work to Celery.

## Hard rules

- **Tasks live in `backend/apps/<app>/tasks.py`.** `core/celery_app.py`
  discovers the `tasks` module of every registered app, so no manual
  registration is needed. `make:app` creates the file.
- **Use an explicit task name.** Name it `<app>.<action>`, for example
  `notifications.send_welcome_email`. Explicit names keep the queue stable
  when modules move.
- **Pass serializable arguments.** Pass IDs and plain values, not ORM
  objects or open sessions, because the worker runs in another process.
- **Redis is required for the worker.** The broker and result backend are
  set by `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` in `.env`. The API
  does not use Redis; only the worker consumes it.
- Communicate with the user in **Portuguese (pt-BR)**. Code stays in
  **English**; docstrings and comments are in Portuguese, per `AGENTS.md`.

## Create a task

In `backend/apps/<app>/tasks.py`:

```python
from core.celery_app import celery_app


@celery_app.task(name="notifications.send_welcome_email")
def send_welcome_email(email: str) -> bool:
    """Envia o e-mail de boas-vindas.

    Args:
        email: Endereço do destinatário.

    Returns:
        True quando o envio foi concluído.
    """
    ...
    return True
```

## Call a task

From a service or router, queue it with `.delay()`. It returns immediately:

```python
from apps.notifications.tasks import send_welcome_email

send_welcome_email.delay("user@example.com")
```

## Run the worker

From `backend/`, with Redis running:

```bash
cd backend
python manage.py run:worker
```

The equivalent direct call is:

```bash
cd backend
celery -A core.celery_app.celery_app worker --loglevel=info
```

In Docker, the `worker` service of the Compose stack runs the same command,
and it is opt-in because no task exists in the template yet.

## Local Redis

Start Redis with Docker if it is not already running:

```bash
docker run --rm -p 6379:6379 redis:7-alpine
```

Make sure `.env` points to it, for example
`CELERY_BROKER_URL="redis://localhost:6379/0"`.

## Result storage

The default result backend is Redis. Storing results in the database
(`db+sqlite:///...` or `db+postgresql://...`) is a valid alternative. It
needs the `celery[sqlalchemy]` extra and a synchronous driver. Change it
only if the user asks, and document the choice in `AGENTS.md`.

## Red flags

- Calling the task synchronously (`send_welcome_email(...)`) when the goal is
  to queue it.
- Passing ORM objects or open database sessions as arguments.
- Using a task without an explicit name.
- Relying on the API to process tasks: only the worker consumes the queue.
- Starting work in a task that the HTTP response is waiting for.
