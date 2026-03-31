"""Entrypoint da aplicação FastAPI."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db
from src.routes.tenant_routes import router as tenant_router


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

app.include_router(tenant_router)


@app.get("/")
def root():
    return {"status": "online", "versao": "0.1.0"}
