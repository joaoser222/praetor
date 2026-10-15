import importlib
from pathlib import Path
from typing import Optional, cast
from fastapi import APIRouter
from config.logging import logger


class BaseAppConfig:
    """
    Classe de configuração base para um app.

    Cada app deve ter um arquivo app.py com uma classe que herda desta.
    Esta classe é responsável por carregar seus próprios componentes, como os routers.
    """

    def __init__(self, app_path: Path):
        self.name: str = app_path.name
        self.label: str = self.name.capitalize()
        self.path: Path = app_path
        self.module_path: str = f"apps.{self.name}"
        self._router: Optional[APIRouter] = None

    @property
    def router(self) -> APIRouter:
        """
        Carrega de forma preguiçosa (lazy) e retorna o APIRouter agregado do app.
        """
        if self._router is None:
            self._router = self._load_router()
        return cast(APIRouter, self._router)

    def _load_router(self) -> APIRouter:
        """
        Descobre e agrega todos os APIRouters do diretório 'routers' do app.

        Varre todos os arquivos .py do subdiretório routers, importa-os,
        encontra qualquer instância de APIRouter (convencionalmente chamada 'router') e a
        inclui em um router principal do app.
        """
        app_level_router = APIRouter()
        routers_dir = self.path / "routers"

        if not routers_dir.is_dir():
            return app_level_router  # Retorna um router vazio se não houver diretório de routers

        for router_file in routers_dir.glob("*.py"):
            if router_file.stem.startswith("_"):
                continue

            module_name = f"{self.module_path}.routers.{router_file.stem}"
            try:
                router_module = importlib.import_module(module_name)
                if hasattr(router_module, "router") and isinstance(getattr(router_module, "router"), APIRouter):
                    entity_router = getattr(router_module, "router")
                    app_level_router.include_router(entity_router)
                    logger.debug(f"Router from '{module_name}' included in app '{self.name}'.")
            except ImportError as e:
                logger.error(f"Failed to import router module '{module_name}': {e}")

        return app_level_router
