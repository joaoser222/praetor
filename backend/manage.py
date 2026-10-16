import sys
from pathlib import Path

import click

from core.utils import auto_discover_commands


@click.group()
def cli():
    """Interface de linha de comando para gerenciar a aplicação."""
    pass


# Comandos de runtime (ops): sempre registrados — a imagem de produção precisa
# deles (`run:server` é o CMD; o serviço `migrate` roda `db:migrate`).
auto_discover_commands(cli, "commands")
auto_discover_commands(cli, "core.commands")

# Ferramentas de geração (dev-only): só existem quando o pacote `tools/` está
# presente (na imagem de produção o contexto de build é `backend/`, então ele
# não existe e os comandos de geração ficam de fora).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if (_PROJECT_ROOT / "tools" / "commands").is_dir():
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    auto_discover_commands(cli, "tools.commands", root=_PROJECT_ROOT)


if __name__ == "__main__":
    cli()
