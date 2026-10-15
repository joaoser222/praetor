import asyncio
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

# Adiciona o diretório raiz do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
import importlib

# Carrega as variáveis de ambiente do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração do Alembic
config = context.config
fileConfig(config.config_file_name)

# Importa seus modelos
from core.base_model import BaseModel
from core.utils import auto_discover_apps
from core.apps import app_registry

# Descobre todos os apps registrados
auto_discover_apps()

# Importa o módulo de models de cada app para popular BaseModel.metadata
for app_config in app_registry.apps:
    try:
        importlib.import_module(f"{app_config.module_path}.models")
    except ImportError:
        # Se um app não tiver models.py, apenas ignora
        pass

target_metadata = BaseModel.metadata
def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# Modo online assíncrono
async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await connectable.dispose()

# Modo offline (síncrono)
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Decide se deve rodar em modo offline ou online
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
