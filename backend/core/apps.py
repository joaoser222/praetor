from typing import List
from .base_app_config import BaseAppConfig

class AppRegistry:
    """Registro central para armazenar instâncias de AppConfig."""

    def __init__(self):
        self.apps: List[BaseAppConfig] = []

    def register(self, app_config: BaseAppConfig):
        """Registra uma nova configuração de app."""
        self.apps.append(app_config)


# Instância global do registro de apps, pronta para ser importada e usada.
app_registry = AppRegistry()
