"""Ferramentas de desenvolvimento (geração de código).

Este pacote NÃO faz parte da imagem de produção: ele fica fora de `backend/` e só
é registrado no CLI quando está presente. Aqui colocamos `backend/` no `sys.path`
para que as ferramentas possam importar os pacotes do backend (`config`, `core`).
"""

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
