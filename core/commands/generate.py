import importlib
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy import inspect
from core.utils import to_pascal_case


@click.group("generate")
def generate_cli():
    """Comandos de geração de código."""
    pass


def get_model_attributes(model_class):
    """Inspeciona um modelo SQLAlchemy e retorna seus atributos de coluna com type hints."""
    attributes = {}
    dynamic_imports = {
        "typing": ["Optional"]
    }
    mapper = inspect(model_class).mapper
    for prop in mapper.iterate_properties:
        if isinstance(prop, ColumnProperty):
            column = prop.columns[0]
            python_type = column.type.python_type
            type_name = python_type.__name__
            module_name = python_type.__module__

            # Gera a importação de módulos de tipos dinamicamente
            if(module_name != "builtins"):
                if(not dynamic_imports.get(module_name)):
                    dynamic_imports[module_name] = []
            
                if(type_name not in dynamic_imports[module_name]):
                    dynamic_imports[module_name].append(type_name)

            # Envolve colunas anuláveis em Optional, exceto o id.
            # O template trata de tornar os campos opcionais para o schema de Update.
            if column.nullable and prop.key != 'id':
                attributes[prop.key] = f"Optional[{type_name}]"
            else:
                attributes[prop.key] = type_name
    return attributes,dynamic_imports


@generate_cli.command("generate:schemas")
@click.argument("entity")
@click.option(
    "--app",
    required=True,
    help="The name of the app where the entity model is located.",
)
@click.option("--force", is_flag=True, help="Force overwrite of existing file without confirmation.")
def generate_schemas(entity: str, app: str, force: bool):
    """
    Gera schemas Pydantic de CRUD com base no modelo de uma entidade.

    Este comando inspeciona as colunas de um modelo SQLAlchemy e gera
    os schemas Create, Update e Read usando templates Jinja2.
    """

    entity_name_lower = entity.lower()
    entity_name_pascal = to_pascal_case(entity)
    app_path = Path(f"apps/{app}")

    if not app_path.exists():
        click.secho(f"Error: App '{app}' not found at '{app_path}'.", fg="red")
        return

    model_path = app_path / "models" / f"{entity_name_lower}.py"
    if not model_path.exists():
        click.secho(
            f"Error: Model file not found at '{model_path}'.",
            fg="red",
        )
        return

    click.echo(f"Inspecting model '{entity_name_pascal}' in app '{app}'...")

    try:
        # Importa dinamicamente a classe do modelo
        module_path = f"apps.{app}.models.{entity_name_lower}"
        module = importlib.import_module(module_path)
        model_class = getattr(module, entity_name_pascal)

        # Obtém os atributos do modelo
        attributes,dynamic_imports = get_model_attributes(model_class)
        click.echo(f"Found attributes: {list(attributes.keys())}")

        # Verifica se há algum atributo além dos atributos base
        user_defined_attributes = {
            k for k in attributes.keys() if k not in ['id', 'created_at', 'updated_at']
        }

        if not user_defined_attributes:
            click.secho(
                f"Warning: Model '{entity_name_pascal}' has no custom attributes to generate schemas from.",
                fg="yellow",
            )
            click.secho("Generation skipped. Please add attributes to your model file.", fg="yellow")
            return
    except (ImportError, AttributeError) as e:
        click.secho(
            f"Error: Could not load model class '{entity_name_pascal}' from '{module_path}'.\n{e}",
            fg="red",
        )
        return
    
    # Configura o ambiente Jinja2
    template_dir = Path("core/templates/entity")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("schema.py.j2")

    # Prepara o contexto para o template
    context = {
        "class_name": entity_name_pascal,
        "attributes": attributes,
        "dynamic_imports": dynamic_imports
    }

    # Renderiza o template
    rendered_code = template.render(context)

    # Escreve o arquivo de schema gerado
    schema_output_path = app_path / "schemas" / f"{entity_name_lower}.py"

    # Verifica se o arquivo já existe e pede confirmação
    if schema_output_path.exists() and not force:
        click.secho(
            f"Warning: The file '{schema_output_path}' will be overwritten based on the model '{model_path}'.", fg="yellow"
        )
        if not click.confirm("Do you want to overwrite it?"):
            click.echo("Generation skipped.")
            return

    schema_output_path.parent.mkdir(parents=True, exist_ok=True) # Garante que o diretório exista
    schema_output_path.write_text(rendered_code)

    click.secho(
        f"Successfully generated schema file at '{schema_output_path}'.", fg="green"
    )
