from celery import Celery
from config.settings import settings
from core.utils import auto_discover_apps
from core.apps import app_registry

# Cria uma instância do Celery
celery_app = Celery(
    "praetor_api_worker",
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND),
    include=[],  # Será populado dinamicamente
)

# É fundamental descobrir os apps primeiro para que o registro seja populado.
auto_discover_apps()

# Usa o app_registry para informar ao Celery onde encontrar as tasks.
# Este é o ponto chave de integração com a arquitetura modular.
task_modules = [f"{app_config.module_path}.tasks" for app_config in app_registry.apps]
celery_app.autodiscover_tasks(task_modules)

celery_app.conf.update(task_track_started=True)
