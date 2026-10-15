from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from config.database import close_db
from config.logging import logger
from config.settings import settings
from core.exceptions import BaseAPIException 
from core.utils import auto_discover_apps, auto_discover_routers
from core.middlewares.logging import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Encerramento
    await close_db()
    logger.info("Database connections closed.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_str,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

# Manipuladores de exceções
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# --- Descoberta de apps ---
# 1. Descobre e registra todos os apps do diretório 'apps'.
auto_discover_apps()

# 2. Inclui os routers de todos os apps registrados.
auto_discover_routers(app)
