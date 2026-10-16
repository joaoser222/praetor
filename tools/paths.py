"""Caminhos das ferramentas de geração (dev-only).

A raiz do projeto é derivada do próprio arquivo, de modo que a geração funcione
independentemente do diretório de trabalho em que o comando é executado.
"""

from pathlib import Path

# Diretório deste pacote (`tools/`).
TOOLS_DIR = Path(__file__).resolve().parent
# Raiz do repositório (onde vivem `backend/`, `frontend/`, `docker/` e o `.env`).
PROJECT_ROOT = TOOLS_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
# Templates Jinja2 usados pela geração.
TEMPLATES_DIR = TOOLS_DIR / "templates"
