import asyncio
import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
import importlib

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Alembic config
config = context.config
fileConfig(config.config_file_name)

# Import your models
from core.base_model import BaseModel
from core.utils import auto_discover_apps
from core.apps import app_registry

# Discover all registered apps
auto_discover_apps()

# Import the models module from each app to populate BaseModel.metadata
for app_config in app_registry.apps:
    try:
        importlib.import_module(f"{app_config.module_path}.models")
    except ImportError:
        # If an app doesn't have a models.py, just ignore it
        pass

target_metadata = BaseModel.metadata
def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# Async online mode
async def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.begin() as conn:
        await conn.run_sync(do_run_migrations)
    await connectable.dispose()

# Offline mode (synchronous)
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Decide whether to run in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
