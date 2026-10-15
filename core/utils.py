from typing import Dict, Any, Optional, List, NamedTuple, Callable
import click
import importlib
from types import ModuleType
from fastapi import FastAPI

from config.settings import settings
from config.logging import logger
from core.apps import app_registry


def import_app_models(app_config) -> None:
    """
    Importa o pacote de models de um app para popular os metadados do SQLAlchemy.

    Os metadados só são preenchidos quando as classes de modelo são importadas.
    Sem esta importação, comandos como 'db:create' e o 'create_all' dos testes
    não enxergam as tabelas.

    Args:
        app_config: Instância de BaseAppConfig cujo pacote de models será importado.
    """
    models_module = f"{app_config.module_path}.models"
    try:
        importlib.import_module(models_module)
    except ImportError as e:
        logger.warning(f"App '{app_config.name}' has no importable models: {e}")


def auto_discover_apps():
    """
    Descobre e registra automaticamente todos os apps do diretório 'apps'.

    Esta função varre o diretório 'apps', procura por um arquivo 'app.py'
    em cada subdiretório, importa a instância 'app_config' e a registra
    no 'app_registry' global.
    """
    apps_dir = settings.BASE_DIR / "apps"
    if not apps_dir.is_dir():
        return

    logger.info("Starting automatic app discovery...")
    for app_path in apps_dir.iterdir():
        if not app_path.is_dir() or app_path.name.startswith("_"):
            continue

        app_config_file = app_path / "app.py"
        if app_config_file.is_file():
            module_name = f"apps.{app_path.name}.app"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "app_config"):
                    app_config_instance = getattr(module, "app_config")
                    app_registry.register(app_config_instance)
                    # Popula os metadados do SQLAlchemy com os models deste app.
                    import_app_models(app_config_instance)
                    logger.info(f"App '{app_config_instance.name}' registered successfully.")
            except ImportError as e:
                logger.error(f"Failed to import app '{app_path.name}': {e}")


def auto_discover_routers(app: FastAPI, base_prefix: str = "/api"):
    """
    Itera sobre os AppConfigs registrados e inclui seus routers no app FastAPI principal.
    """
    logger.info("Loading routers from registered apps...")
    for app_config in app_registry.apps:
        # Acessar .router dispara o carregamento preguiçoso (lazy) do router do app.
        # A propriedade garante que ele seja carregado apenas uma vez.
        if app_config.router.routes:
            app.include_router(
                app_config.router,
                prefix=f"{base_prefix}/{app_config.name}",
                tags=[app_config.label],
            )
            logger.info(f"Routes for app '{app_config.name}' loaded.")

def auto_discover_commands(cli, base_dir: str):
    """
    Descobre e registra automaticamente todos os comandos de CLI do diretório informado.
    """
    commands_path = settings.BASE_DIR / base_dir.replace(".", "/")

    def process_command_module(module: ModuleType, module_stem: str):
        # Procura por objetos do Click (Command ou Group)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, (click.Command, click.Group)):
                cli.add_command(attr)

    if not commands_path.is_dir():
        return

    for file in commands_path.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        module_name = f"{base_dir}.{file.stem}"
        module = importlib.import_module(module_name)
        process_command_module(module, file.stem)


def create_from_template(template_env, template_name, target_path, context):
    """Renderiza um template e o escreve em um arquivo."""
    template = template_env.get_template(template_name)
    rendered_content = template.render(context)
    with open(target_path, "w") as f:
        f.write(rendered_content)

def to_pascal_case(name: str) -> str:
    """Converte snake_case ou kebab-case para PascalCase"""
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))


def to_plural(word: str) -> str:
    """
    Converte uma palavra para o plural seguindo as regras de pluralização do inglês.
    """
    # Plurais irregulares especiais
    irregular_plurals = {
        'person': 'people',
        'child': 'children',
        'man': 'men',
        'woman': 'women',
        'tooth': 'teeth',
        'foot': 'feet',
        'mouse': 'mice',
        'goose': 'geese',
    }
    
    word_lower = word.lower()
    
    # Verifica plurais irregulares
    if word_lower in irregular_plurals:
        return irregular_plurals[word_lower]
    
    # Palavras terminadas em consoante + y -> ies
    if len(word) > 1 and word[-1] == 'y' and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    
    # Palavras terminadas em s, ss, sh, ch, x, z -> es
    if word.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    
    # Palavras terminadas em consoante + o -> es
    if len(word) > 1 and word[-1] == 'o' and word[-2] not in 'aeiou':
        return word + 'es'
    
    # Palavras terminadas em f ou fe -> ves
    if word.endswith('fe'):
        return word[:-2] + 'ves'
    if word.endswith('f'):
        return word[:-1] + 'ves'
    
    # Padrão: apenas adiciona s
    return word + 's'

class PermissionDef(NamedTuple):
    name: str
    description: str
