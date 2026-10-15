import click
from core.utils import auto_discover_commands

@click.group()
def cli():
    """Interface de linha de comando para gerenciar a aplicação."""
    pass

auto_discover_commands(cli, "commands")
auto_discover_commands(cli, "core.commands")

if __name__ == "__main__":
    cli()
