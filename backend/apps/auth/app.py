from pathlib import Path
from core.base_app_config import BaseAppConfig


class AuthAppConfig(BaseAppConfig):
    """Classe de configuração do app 'auth'."""

    # No futuro, você pode sobrescrever atributos ou adicionar novos métodos aqui.
    # Por exemplo, para definir um label personalizado para a documentação:
    # label = "Authentication"
    pass


# Esta instância será descoberta e registrada automaticamente.
app_config = AuthAppConfig(app_path=Path(__file__).parent)
