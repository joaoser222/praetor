import click
import os
from jinja2 import Environment, FileSystemLoader
from core.utils import create_from_template,to_pascal_case,to_plural
from config.settings import settings

def _load_template_env():
    # Setup Jinja2 environment
    template_path = os.path.join(settings.BASE_DIR, "core", "templates")
    return Environment(loader=FileSystemLoader(template_path))

@click.group('make')
def make_cli():
    """A group of commands to generate boilerplate code."""
    pass

@make_cli.command("make:app")
@click.argument("name")
def make_app(name: str):
    """Creates a new app with a default structure."""
    app_dir = os.path.join(settings.BASE_DIR, "apps", name)
    env = _load_template_env()
    class_name = to_pascal_case(name)


    if os.path.exists(app_dir):
        click.secho(f"App '{name}' already exists.", fg="yellow")
        return
    
    # Create app directory
    os.makedirs(app_dir)

    # Create __init__.py file in app directory
    open(os.path.join(app_dir, "__init__.py"), "w").close()
    
    # Create app.py file in app directory
    create_from_template(env, 'app.py.j2', os.path.join(app_dir, "app.py"), {"name": name, "class_name": class_name})

    # Create tasks.py file in app directory
    create_from_template(env, 'tasks.py.j2', os.path.join(app_dir, "tasks.py"), {"name": name})

    # Create dependencies.py file in app directory
    create_from_template(env, 'dependencies.py.j2', os.path.join(app_dir, "dependencies.py"), {"name": name})

    # Create app base directories
    for subdir in ["repositories", "services", "models", "schemas","tests", "routers", "permissions"]:
        path = os.path.join(app_dir, subdir)
        os.makedirs(path)
        open(os.path.join(path, "__init__.py"), "w").close()
    
    click.secho(f"App '{name}' created successfully in '{app_dir}'.", fg="green")
    click.echo("The app router will be automatically discovered.")
    click.echo(f"Now, you can create an entity inside it with: python manage.py make:entity <entity_name> --app {name}")


@make_cli.command("make:entity")
@click.argument("name")
@click.option("--app", required=True, help="The app where the entity will be created.")
@click.option("--only", help="Generate only specific components (comma-separated: model,schema,repository,service,router,permission,test)")
@click.option("--except", "except_", help="Generate all components except these (comma-separated)")
@click.option("--minimal", is_flag=True, help="Generate only model and schema (shortcut for --only model,schema)")
@click.option("--table-name", "custom_table_name" ,help="Override the default table name")
@click.option("--no-prefix" , is_flag=True,help="Disable prefix name of app in table name")

def make_entity(name: str, app: str, only: str, except_: str, minimal: bool, custom_table_name: str, no_prefix: bool):
    """Creates a new entity (model, schema, repo, service) inside an app."""
    app_dir = os.path.join(settings.BASE_DIR, "apps", app)
    env = _load_template_env()

    if not os.path.exists(app_dir):
        click.secho(f"App '{app}' not found. Please create it first with 'make:app {app}'.", fg="red")
        return

    # Validate conflicting options
    if only and except_:
        click.secho("Cannot use --only and --except together. Choose one.", fg="red")
        return
    
    if minimal and (only or except_):
        click.secho("Cannot use --minimal with --only or --except.", fg="red")
        return

    # Handle minimal flag
    if minimal:
        only = "model,schema"

    pascal_name = to_pascal_case(name)
    
    # Process name to plural - more readable approach
    name_parts = name.split('_')
    name_parts[-1] = to_plural(name_parts[-1])
    plural_name = '_'.join(name_parts)
    
    # Table name logic with clear conditional flow
    table_name = custom_table_name or plural_name
    if not no_prefix:
        table_name = f"{app}_{table_name}"
    
    context = {
        "name": name,
        "app_name": app,
        "class_name": to_pascal_case(name),
        "repo_name": f"{pascal_name}Repository",
        "service_name": f"{pascal_name}Service",
        "table_name": table_name,
        "plural_name": plural_name,
        "attributes": {}  # Required for schema template compatibility
    }


    # All possible files to generate
    # Format: (template_file, target_file, init_dir, import_class)
    # init_dir and import_class are None when __init__.py shouldn't be updated
    all_template_files = {
        "model": ("entity/model.py.j2", f"models/{name}.py", "models", context["class_name"]),
        "schema": ("entity/schema.py.j2", f"schemas/{name}.py", None, None),  # schemas import the whole module
        "repository": ("entity/repository.py.j2", f"repositories/{name}.py", "repositories", context["repo_name"]),
        "service": ("entity/service.py.j2", f"services/{name}.py", "services", context["service_name"]),
        "router": ("entity/router.py.j2", f"routers/{name}.py", None, None),
        "permission": ("entity/permission.py.j2", f"permissions/{name}.py", None, None),
        "test": ("entity/test.py.j2", f"tests/{name}.py", None, None),
    }

    # Determine which files to generate
    if only:
        components_to_generate = [c.strip() for c in only.split(",")]
        # Validate components
        invalid = [c for c in components_to_generate if c not in all_template_files]
        if invalid:
            click.secho(f"Invalid components: {', '.join(invalid)}", fg="red")
            click.secho(f"Valid options: {', '.join(all_template_files.keys())}", fg="yellow")
            return
        
        files_to_generate = {k: v for k, v in all_template_files.items() if k in components_to_generate}
    
    elif except_:
        components_to_exclude = [c.strip() for c in except_.split(",")]
        # Validate components
        invalid = [c for c in components_to_exclude if c not in all_template_files]
        if invalid:
            click.secho(f"Invalid components to exclude: {', '.join(invalid)}", fg="red")
            click.secho(f"Valid options: {', '.join(all_template_files.keys())}", fg="yellow")
            return
        
        files_to_generate = {k: v for k, v in all_template_files.items() if k not in components_to_exclude}
    
    else:
        # Generate all components (default behavior)
        files_to_generate = all_template_files.copy()

    # Component dependencies (optional warning)
    dependencies = {
        "repository": ["model"],
        "service": ["repository"],
        "router": ["service", "schema"],
    }

    # Check dependencies (warning only)
    components_list = list(files_to_generate.keys())
    for component in components_list:
        if component in dependencies:
            missing_deps = [dep for dep in dependencies[component] if dep not in components_list]
            if missing_deps:
                click.secho(
                    f"⚠ Warning: '{component}' typically depends on {', '.join(missing_deps)} which will not be generated.",
                    fg="yellow"
                )

    # Generate files
    generated_components = []
    for component, (template_file, target_file, init_dir, import_class) in files_to_generate.items():
        target_path = os.path.join(app_dir, target_file)
        
        # Check if file already exists
        if os.path.exists(target_path):
            click.secho(f"⚠ File already exists: {target_file}", fg="yellow")
            if not click.confirm(f"  Overwrite?", default=False):
                click.secho(f"  Skipped: {component}", fg="yellow")
                continue
        
        create_from_template(env, template_file, target_path, context)
        generated_components.append(component)
        
        # Update __init__.py if applicable
        if init_dir and import_class:
            target_dir = os.path.join(app_dir, init_dir)
            init_file = os.path.join(target_dir, "__init__.py")
            import_line = f"from .{name} import {import_class}\n"
            
            # Check if import already exists
            if os.path.exists(init_file):
                with open(init_file, "r") as f:
                    content = f.read()
                if import_line not in content:
                    with open(init_file, "a") as f:
                        f.write(import_line)
    # Summary output
    if generated_components:
        click.secho(f"\n✓ Entity '{name}' created in app '{app}'", fg="green", bold=True)
        click.secho(f"  Generated: {', '.join(generated_components)}", fg="cyan")
    
    skipped = [k for k in all_template_files.keys() if k not in generated_components]
    if skipped:
        click.secho(f"  Skipped: {', '.join(skipped)}", fg="yellow")
        
@make_cli.command("make:command")
@click.argument("name")
def make_command(name: str):
    """Creates a new custom command file in the root commands/ directory."""
    command_root = os.path.join(settings.BASE_DIR, "commands")
    command_path = os.path.join(command_root, f"{name}.py")
    env = _load_template_env()

    # Create commands directory if nos exists
    if not os.path.exists(command_root):
        os.makedirs(command_root)
        open(os.path.join(command_root, f"__init__.py"), "w").close()

    if os.path.exists(command_path):
        click.echo(f"Command file 'commands/{name}.py' already exists.")
        return
    
    create_from_template(env, "command.py.j2", command_path, {"name": name})

    click.secho(f"Command file 'commands/{name}.py' created successfully.", fg="green")

@make_cli.command("make:middleware")
@click.argument("name")
def make_middleware(name: str):
    """Creates a new middleware file in the root middlewares/ directory."""
    
    middleware_root = os.path.join(settings.BASE_DIR, "middlewares")
    middleware_path = os.path.join(middleware_root, f"{name}.py")
    env = _load_template_env()
    pascal_name = to_pascal_case(name)

    # Create commands directory if nos exists
    if not os.path.exists(middleware_root):
        os.makedirs(middleware_root)
        open(os.path.join(middleware_root, f"__init__.py"), "w").close()

    if os.path.exists(middleware_path):
        click.echo(f"Middleware file 'middlewares/{name}.py' already exists.")
        return

    create_from_template(env, "middleware.py.j2", middleware_path, {"class_name": pascal_name})

    click.secho(f"Middleware file 'middlewares/{name}.py' created successfully.", fg="green")
