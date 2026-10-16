import click
import uvicorn
import subprocess
from config.settings import settings

@click.group('run')
def run_cli():
    """ Um grupo de comandos destinados à execução operacional."""
    pass

@run_cli.command('run:server')
@click.option("--host", default=settings.SERVER_HOST, help="Host to bind.", show_default=True) # type: ignore
@click.option("--port", default=settings.SERVER_PORT, help="Port to bind.", show_default=True) # type: ignore
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload.") # type: ignore
def run_server(host: str, port: int, reload: bool):
    """Inicia o servidor de desenvolvimento."""
    uvicorn.run("main:app", host=host, port=port, reload=reload)

@run_cli.command("run:worker")
@click.option("--loglevel", default="info", help="Logging level for the worker.")
def run_worker(loglevel: str):
    """Inicia um processo worker do Celery."""
    click.echo("Starting Celery worker...")
    # A flag -A aponta para a instância do nosso app Celery.
    command = ["celery", "-A", "core.celery_app.celery_app", "worker", f"--loglevel={loglevel}"]
    subprocess.run(command)

@run_cli.command('run:test')
@click.argument("app_name", required=False) # type: ignore
def run_test(app_name: str | None):
    """Executa os testes, opcionalmente de um app específico."""
    # Import local: 'pytest' é dependência de dev e não deve ser exigida
    # para executar os demais comandos do CLI (ex.: make:*, db:*).
    import pytest

    tests_dir = settings.BASE_DIR / "tests"
    if app_name:
        app_tests = settings.BASE_DIR / "apps" / app_name / "tests"
        test_path = str(app_tests if app_tests.exists() else tests_dir)
    else:
        test_path = str(tests_dir)
    pytest.main(["-v", test_path])
