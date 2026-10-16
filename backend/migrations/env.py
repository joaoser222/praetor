import asyncio
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

# `migrations/env.py` vive em `backend/migrations/`: sobe para o backend (raiz de
# importação da aplicação) e, daí, para a raiz do repositório (onde fica o .env).
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
sys.path.insert(0, _BACKEND_DIR)


from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Carrega as variáveis de ambiente do .env central (raiz do repositório).
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"))
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuração do Alembic
config = context.config
fileConfig(config.config_file_name)

# Importa seus modelos
from core.base_model import BaseModel
from core.utils import auto_discover_apps

# Descobre todos os apps registrados.
# A própria descoberta importa o pacote de models de cada app, o que popula
# o BaseModel.metadata usado pelo autogenerate.
auto_discover_apps()

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
