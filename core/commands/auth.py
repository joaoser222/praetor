import asyncio
import os
import click
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.auth.schemas.user import UserCreate
from apps.auth.services.user import UserService
from apps.auth.models import Permission, Role
from core.utils import PermissionDef
from config.database import AsyncSessionFactory

async def _check_user_exists(email: str) -> bool:
    async with AsyncSessionFactory() as session:
        user_service = UserService(session)
        has_user = await user_service.repo.get_by_email(email)

        if has_user:
            click.echo(f"User with email {email} already exists!",color="red")
            return True
        
        return False

async def _create_user(user_data: UserCreate):
    async with AsyncSessionFactory() as session:
        user_service = UserService(session)
        has_user = await user_service.repo.get_by_email(user_data.email)

        if has_user:
            click.echo(f"User with email {user_data.email} already exists!")

        user = await user_service.create_user(user_data)
        return user


async def _list_users():
    async with AsyncSessionFactory() as session:
        user_service = UserService(session)
        users = await user_service.repo.get_multi()
        return users


async def _delete_user(email: str):
    async with AsyncSessionFactory() as session:
        user_service = UserService(session)
        user = await user_service.repo.get_by_email(email)
        if not user:
            click.echo(f"User with email {email} not found.")
            return
        await user_service.repo.delete(pk=user.id)
        click.echo(f"User {email} deleted successfully.")

def _discover_permissions() -> list[PermissionDef]:
    """Discovers all permissions defined in the apps."""
    all_permissions = []
    base_dir = "apps"
    apps_path = Path(base_dir)
    
    for app_dir in apps_path.iterdir():
        if app_dir.is_dir():
            permissions_path = app_dir / "permissions"
            
            if permissions_path.exists() and permissions_path.is_dir():
                try:
                    package_name = f"{base_dir}.{app_dir.name}.permissions"
                    for py_file in permissions_path.glob("*.py"):
                        if py_file.name.startswith("_"):
                            continue  # Ignores private files
                        
                        module_name = py_file.stem
                        full_module_name = f"{package_name}.{module_name}"
                        
                        try:
                            module = __import__(full_module_name, fromlist=['DEFINED_PERMISSIONS'])
                            if hasattr(module, 'DEFINED_PERMISSIONS'):
                                all_permissions.extend(module.DEFINED_PERMISSIONS)
                        except ImportError as e:
                            click.secho(
                                f"Error importing permissions from {app_dir.name}.permissions.{module_name}: {e}", 
                                fg="red"
                            )
                        except AttributeError:
                            pass
                            
                except Exception as e:
                    click.secho(f"Error processing permissions directory in {app_dir.name}: {e}", fg="red")
    
    return all_permissions

async def _sync_permissions():
    """Synchronizes permissions defined in the code with the database."""
    click.echo("Starting permission synchronization...")
    defined_permissions = _discover_permissions()
    if not defined_permissions:
        click.secho("No permission definitions found in apps.", fg="yellow")
        return

    async with AsyncSessionFactory() as session:
        # Get all existing permissions from the database
        result = await session.execute(select(Permission.name))
        existing_permissions = {row[0] for row in result}

        defined_permissions_names = {p.name for p in defined_permissions}

        # Permissions to be added
        to_add = defined_permissions_names - existing_permissions

        if to_add:
            click.echo(f"Adding {len(to_add)} new permissions...")
            for perm_def in defined_permissions:
                if perm_def.name in to_add:
                    new_perm = Permission(name=perm_def.name, description=perm_def.description)
                    session.add(new_perm)
                    click.echo(f"  + {perm_def.name}")
            await session.commit()
        
        if not to_add:
            click.echo("Permissions are already synchronized.")

@click.group('auth')
def auth_cli():
    """Authentication management commands."""
    pass


@auth_cli.command("auth:createsuperuser")
def auth_createsuperuser():
    """Creates a superuser."""
    email = click.prompt("Email", type=str)
    username = click.prompt("Username", type=str)
    full_name = click.prompt("Full Name", type=str)
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    user_data = UserCreate(
        email=email,
        username=username,
        full_name=full_name,
        password=password,
        is_superuser=True,
        is_active=True,
    )

    async def _run_command():
        if await _check_user_exists(email):
            return
        user = await _create_user(user_data)
        click.echo(f"Superuser {user.email} created successfully.")

    asyncio.run(_run_command())


@auth_cli.command("auth:makepermissions")
def auth_makepermissions():
    """Generate permissions defined in the code with the database."""
    asyncio.run(_sync_permissions())