"""Entrypoint da aplicação FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.database import init_db
from src.routes.tenant_routes import router as tenant_router

_STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos ao subir e limpa ao desligar."""
    init_db()
    yield


app = FastAPI(
    title="API Busca Lucas",
    description="API de automação para extração de dados Hinova e disparo via Quepasa.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenant_router)
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/")
def root():
    """Serve o painel de gestão."""
    return FileResponse(_STATIC_DIR / "index.html")
