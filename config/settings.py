"""Configurações centralizadas — carrega variáveis de ambiente (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega .env da raiz do projeto
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def get_tenant_config(tenant_id: str | None = None) -> dict[str, str]:
    """Retorna as credenciais isoladas do tenant (RNF01)."""
    prefix = f"{tenant_id.upper()}_" if tenant_id else ""
    return {
        "hinova_token": os.environ[f"{prefix}HINOVA_API_TOKEN"],
        "quepasa_token": os.environ[f"{prefix}QUEPASA_API_TOKEN"],
        "quepasa_dest": os.environ[f"{prefix}QUEPASA_DEST_NUMBER"],
    }
