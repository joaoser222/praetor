import click
import code

@click.command()
def shell():
    """Abre um shell Python interativo com o contexto da aplicação."""
    try:
        from IPython import start_ipython
        click.echo("Starting IPython shell...")
        start_ipython(argv=[])
    except ImportError:
        click.echo("IPython not found, falling back to standard Python shell.")
        
        vars = globals()
        vars.update(locals())
        
        # Você pode importar e adicionar models/services ao contexto do shell aqui
        # from apps.users.models import User
        # vars.update({"User": User})
        
        code.InteractiveConsole(vars).interact()
