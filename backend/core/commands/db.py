import asyncio
import click
from pathlib import Path
from alembic.config import Config
from alembic import command

from config.database import engine
from core.base_model import BaseModel
from config.settings import settings

alembic_cfg = Config(str(settings.BASE_DIR / "alembic.ini"))
alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

VERSIONS_DIR = Path(settings.BASE_DIR) / "migrations" / "versions"


def _has_revisions() -> bool:
    """Indica se existe ao menos um arquivo de revisão em migrations/versions."""
    return VERSIONS_DIR.is_dir() and any(VERSIONS_DIR.glob("*.py"))


@click.group('db')
def db_cli():
    """Comandos de gerenciamento de banco de dados."""
    pass


async def _create_all():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


@db_cli.command("db:create")
def db_create():
    """Cria todas as tabelas do banco de dados."""
    click.echo("Creating database tables...")
    asyncio.run(_create_all())
    click.echo("Done.")


async def _drop_all(drop_version_table: bool = False) -> None:
    """
    Remove todas as tabelas conhecidas pelo metadata do SQLAlchemy.

    A tabela de controle do Alembic (`alembic_version`) não faz parte do
    metadata; com `drop_version_table=True` ela também é removida, para que o
    `upgrade` seguinte reconheça o banco como vazio e recrie o schema.
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        if drop_version_table:
            await conn.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")


@db_cli.command("db:drop")
def db_drop():
    """Remove todas as tabelas do banco de dados."""
    if click.confirm("Are you sure you want to drop all tables?"):
        click.echo("Dropping database tables...")
        asyncio.run(_drop_all(drop_version_table=True))
        click.echo("Done.")


@db_cli.command("db:makemigrations")
@click.option("-m", "--message", required=True, help="Revision message")
def db_makemigrations(message: str):
    """Cria um novo arquivo de revisão (makemigrations)."""
    click.echo(f"Creating new migration: {message}")
    command.revision(alembic_cfg, message=message, autogenerate=True)


@db_cli.command("db:migrate")
def db_migrate():
    """Aplica todas as migrações pendentes."""
    if not _has_revisions():
        click.secho(
            "Nenhuma revisão encontrada em migrations/versions. "
            "Gere uma com 'python manage.py db:makemigrations -m \"mensagem\"'.",
            fg="yellow",
        )
        return
    click.echo("Applying migrations...")
    command.upgrade(alembic_cfg, "head")
    click.echo("Migrations applied.")


@db_cli.command("db:rollback")
@click.option("--steps", default=1, help="Number of migrations to rollback.")
def db_rollback(steps: int):
    """Reverte migrações."""
    click.echo(f"Rolling back {steps} migration(s)...")
    command.downgrade(alembic_cfg, f"-{steps}")
    click.echo("Rollback complete.")


@db_cli.command("db:reset")
def db_reset():
    """Reseta o banco de dados (remove todas as tabelas e aplica as migrações)."""
    if click.confirm(
        "This will delete all data. Are you sure you want to reset the database?"
    ):
        click.echo("Resetting database...")
        # Alinha o Alembic ao estado real: além das tabelas dos models, remove a
        # tabela de controle (sem isso o `upgrade` abaixo seria no-op e o banco
        # ficaria vazio, só com `alembic_version`).
        asyncio.run(_drop_all(drop_version_table=True))
        if _has_revisions():
            command.upgrade(alembic_cfg, "head")
        else:
            click.secho(
                "Nenhuma revisão encontrada; recriando o schema direto dos models.",
                fg="yellow",
            )
            asyncio.run(_create_all())
        click.echo("Database has been reset.")


@db_cli.command("db:current")
def db_current():
    """Mostra a revisão de migração atual."""
    command.current(alembic_cfg)


@db_cli.command("db:history")
def db_history():
    """Mostra o histórico de migrações."""
    command.history(alembic_cfg)
