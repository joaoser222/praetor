import click
import os
import shutil
from config.settings import settings

@click.group('rm')
def rm_cli():
    """A group of commands to remove generated structures."""
    pass

@rm_cli.command("rm:app")
@click.argument("name")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def rm_app(name: str, force: bool):
    """Removes an app and all its contents."""
    app_dir = os.path.join(settings.BASE_DIR, "apps", name)
    
    if not os.path.exists(app_dir):
        click.secho(f"App '{name}' not found.", fg="yellow")
        return
    
    # Confirmation prompt
    if not force:
        click.secho(f"⚠ This will permanently delete the app '{name}' and all its contents.", fg="red", bold=True)
        if not click.confirm("Are you sure you want to continue?", default=False):
            click.secho("Operation cancelled.", fg="yellow")
            return
    
    # Remove the app directory
    try:
        shutil.rmtree(app_dir)
        
        # Remove frontend feature directory if it exists
        web_dir = os.path.join(settings.BASE_DIR, "web")
        feature_dir = os.path.join(web_dir, "src", "features", name)
        if os.path.exists(feature_dir):
            shutil.rmtree(feature_dir)
            click.secho(f"✓ Frontend feature '{name}' removed successfully.", fg="green")
            
        click.secho(f"✓ App '{name}' removed successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error removing app: {e}", fg="red")


@rm_cli.command("rm:entity")
@click.argument("name")
@click.option("--app", required=True, help="The app where the entity is located.")
@click.option("--only", help="Remove only specific components (comma-separated: model,schema,repository,service,router,permission,test)")
@click.option("--except", "except_", help="Remove all components except these (comma-separated)")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def rm_entity(name: str, app: str, only: str, except_: str, force: bool):
    """Removes an entity and its components from an app."""
    app_dir = os.path.join(settings.BASE_DIR, "apps", app)
    
    if not os.path.exists(app_dir):
        click.secho(f"App '{app}' not found.", fg="red")
        return
    
    # Validate conflicting options
    if only and except_:
        click.secho("Cannot use --only and --except together. Choose one.", fg="red")
        return
    
    # All possible files to remove
    all_files = {
        "model": (f"models/{name}.py", "models"),
        "schema": (f"schemas/{name}.py", "schemas"),
        "repository": (f"repositories/{name}.py", "repositories"),
        "service": (f"services/{name}.py", "services"),
        "router": (f"routers/{name}.py", None),
        "permission": (f"permissions/{name}.py", None),
        "test": (f"tests/{name}.py", None),
        "fe_service": (os.path.join(settings.BASE_DIR, "web/src/features", app, name, "service.ts"), "frontend"),
        "fe_list": (os.path.join(settings.BASE_DIR, "web/src/features", app, name, "pages/List.tsx"), "frontend"),
        "fe_routes": (os.path.join(settings.BASE_DIR, "web/src/features", app, name, "routes.tsx"), "frontend"),
        "fe_types": (os.path.join(settings.BASE_DIR, "web/src/features", app, name, "types.ts"), "frontend"),
        "fe_schema": (os.path.join(settings.BASE_DIR, "web/src/features", app, name, "schema.ts"), "frontend"),
    }



    
    # Determine which files to remove
    if only:
        components_to_remove = [c.strip() for c in only.split(",")]
        invalid = [c for c in components_to_remove if c not in all_files]
        if invalid:
            click.secho(f"Invalid components: {', '.join(invalid)}", fg="red")
            click.secho(f"Valid options: {', '.join(all_files.keys())}", fg="yellow")
            return
        files_to_remove = {k: v for k, v in all_files.items() if k in components_to_remove}
    
    elif except_:
        components_to_exclude = [c.strip() for c in except_.split(",")]
        invalid = [c for c in components_to_exclude if c not in all_files]
        if invalid:
            click.secho(f"Invalid components to exclude: {', '.join(invalid)}", fg="red")
            click.secho(f"Valid options: {', '.join(all_files.keys())}", fg="yellow")
            return
        files_to_remove = {k: v for k, v in all_files.items() if k not in components_to_exclude}
    
    else:
        files_to_remove = all_files.copy()
    
    # Check which files actually exist
    existing_files = {}
    for component, (file_path, init_dir) in files_to_remove.items():
        full_path = os.path.join(app_dir, file_path)
        if os.path.exists(full_path):
            existing_files[component] = (file_path, init_dir)
    
    if not existing_files:
        click.secho(f"No files found for entity '{name}' in app '{app}'.", fg="yellow")
        return
    
    # Confirmation prompt
    if not force:
        click.secho(f"⚠ The following components will be removed:", fg="yellow", bold=True)
        for component in existing_files.keys():
            click.echo(f"  - {component}")
        if not click.confirm("\nAre you sure you want to continue?", default=False):
            click.secho("Operation cancelled.", fg="yellow")
            return
    
    # Remove files and update __init__.py
    removed_components = []
    from core.utils import to_pascal_case
    
    for component, (file_path, init_dir) in existing_files.items():
        if init_dir == "frontend":
            full_path = file_path
        else:
            full_path = os.path.join(app_dir, file_path)

        try:
            # Remove the file
            os.remove(full_path)
            removed_components.append(component)

            # For frontend components, if the directory is now empty, remove it
            if init_dir == "frontend":
                parent_dir = os.path.dirname(full_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    click.secho(f"  Empty frontend directory removed: {os.path.relpath(parent_dir, settings.BASE_DIR)}", fg="cyan")

            
            # Update __init__.py if applicable
            if init_dir:
                init_file = os.path.join(app_dir, init_dir, "__init__.py")
                if os.path.exists(init_file):
                    # Determine the class name to remove
                    pascal_name = to_pascal_case(name)
                    if component == "repository":
                        class_name = f"{pascal_name}Repository"
                    elif component == "service":
                        class_name = f"{pascal_name}Service"
                    else:
                        class_name = pascal_name
                    
                    import_line = f"from .{name} import {class_name}\n"
                    
                    # Remove the import line
                    with open(init_file, "r") as f:
                        lines = f.readlines()
                    
                    with open(init_file, "w") as f:
                        for line in lines:
                            if line != import_line:
                                f.write(line)
        
        except Exception as e:
            click.secho(f"Error removing {component}: {e}", fg="red")
    
    # Summary output
    if removed_components:
        click.secho(f"\n✓ Entity '{name}' components removed from app '{app}'", fg="green", bold=True)
        click.secho(f"  Removed: {', '.join(removed_components)}", fg="cyan")
    
    not_found = [k for k in files_to_remove.keys() if k not in removed_components]
    if not_found:
        click.secho(f"  Not found: {', '.join(not_found)}", fg="yellow")
        
@rm_cli.command("rm:command")
@click.argument("name")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def rm_command(name: str, force: bool):
    """Removes a custom command file from the commands/ directory."""
    command_path = os.path.join(settings.BASE_DIR, "commands", f"{name}.py")
    
    if not os.path.exists(command_path):
        click.secho(f"Command 'commands/{name}.py' not found.", fg="yellow")
        return
    
    # Confirmation prompt
    if not force:
        if not click.confirm(f"Remove command 'commands/{name}.py'?", default=False):
            click.secho("Operation cancelled.", fg="yellow")
            return
    
    try:
        os.remove(command_path)
        click.secho(f"✓ Command 'commands/{name}.py' removed successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error removing command: {e}", fg="red")

@rm_cli.command("rm:middleware")
@click.argument("name")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def rm_middleware(name: str, force: bool):
    """Removes a middleware file from the middlewares/ directory."""
    middleware_path = os.path.join(settings.BASE_DIR, "middlewares", f"{name}.py")
    
    if not os.path.exists(middleware_path):
        click.secho(f"Middleware 'middlewares/{name}.py' not found.", fg="yellow")
        return
    
    # Confirmation prompt
    if not force:
        if not click.confirm(f"Remove middleware 'middlewares/{name}.py'?", default=False):
            click.secho("Operation cancelled.", fg="yellow")
            return
    
    try:
        os.remove(middleware_path)
        click.secho(f"✓ Middleware 'middlewares/{name}.py' removed successfully.", fg="green")
    except Exception as e:
        click.secho(f"Error removing middleware: {e}", fg="red")