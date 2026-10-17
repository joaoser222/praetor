import logging
import sys

from config.settings import settings

# Cria o logger
logger = logging.getLogger(settings.APP_NAME)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Cria o handler de console e define o nível
handler = logging.StreamHandler(sys.stdout)

# Cria o formatador
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Adiciona o formatador ao handler
handler.setFormatter(formatter)

# Evita registrar handlers duplicados em recarregamentos (uvicorn --reload).
if not logger.handlers:
    logger.addHandler(handler)
