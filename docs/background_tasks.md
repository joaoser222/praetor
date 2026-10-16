# Background Tasks (Celery)

Praetor has built-in support for asynchronous background tasks using **Celery**. This is ideal for long-running operations like sending emails, processing files, or communicating with external APIs.

## Configuration

Settings are managed in your `.env` file:

```dotenv
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/1"
```

> O projeto usa **Redis** como broker e result backend (a dependência instalada é
> `celery[redis]`), em linha com o `.env.example` e o `docker/compose/base.yml`.
> Guardar os resultados no banco (`CELERY_RESULT_BACKEND="db+sqlite:///celery_results.db"`
> ou `db+postgresql://...`) é uma alternativa válida, mas exige o extra
> `celery[sqlalchemy]` e um driver síncrono.

The system is pre-configured to automatically discover tasks in your modular apps.

## Creating Tasks

When you create a new app with `python manage.py make:app <name>` (a partir de `backend/`), a `tasks.py` file is generated automatically inside `backend/apps/<name>/`.

To define a task, use the `@celery_app.task` decorator:

```python
from core.celery_app import celery_app

@celery_app.task(name="notifications.send_welcome_email")
def send_welcome_email(email: str):
    # Logic to send email
    print(f"Sending email to {email}")
    return True
```

## Running the Worker

To start a worker that will listen for and execute tasks (a partir de `backend/`):

```bash
cd backend
celery -A core.celery_app.celery_app worker --loglevel=info
```

If you are using Docker, the worker starts automatically as part of the `docker-compose` stack.

## Calling Tasks

In your services or routers, you can queue a task using `.delay()`:

```python
from .tasks import send_welcome_email

async def some_action():
    # This returns immediately, the task runs in the background
    send_welcome_email.delay("user@example.com")
```
