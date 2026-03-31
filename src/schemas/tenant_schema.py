"""Schemas Pydantic para validação de entrada/saída dos endpoints de Tenant."""

from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    """Dados para cadastrar um novo tenant (RF01 + RF02)."""

    nome: str = Field(..., min_length=1, max_length=255, examples=["Empresa ABC"])
    hinova_token: str = Field(..., min_length=1, examples=["token_hinova_123"])
    hinova_usuario: str = Field(..., min_length=1, examples=["usuario_sga"])
    hinova_senha: str = Field(..., min_length=1, examples=["senha_sga"])
    quepasa_token: str = Field(..., min_length=1, examples=["token_quepasa_456"])
    whatsapp_destino: str = Field(
        ..., min_length=10, max_length=20, examples=["5531999999999"]
    )


class TenantUpdate(BaseModel):
    """Dados para atualizar credenciais de um tenant (RF02)."""

    nome: str | None = Field(None, min_length=1, max_length=255)
    hinova_token: str | None = Field(None, min_length=1)
    hinova_usuario: str | None = Field(None, min_length=1)
    hinova_senha: str | None = Field(None, min_length=1)
    quepasa_token: str | None = Field(None, min_length=1)
    whatsapp_destino: str | None = Field(None, min_length=10, max_length=20)
    ativo: bool | None = None


class TenantResponse(BaseModel):
    """Resposta com dados do tenant (sem expor tokens completos)."""

    id: str
    nome: str
    whatsapp_destino: str
    ativo: bool
    ultimo_envio: datetime | None
    ultimo_status: str | None
    criado_em: datetime

    model_config = {"from_attributes": True}


class TenantStatusResponse(BaseModel):
    """Resposta do endpoint de status (RNF03)."""

    id: str
    nome: str
    ativo: bool
    ultimo_envio: datetime | None
    ultimo_status: str | None

    model_config = {"from_attributes": True}
