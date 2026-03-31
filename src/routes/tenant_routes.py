"""Endpoints CRUD de Tenant (RF01, RF02, RNF01, RNF03)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.tenant import Tenant
from src.schemas.tenant_schema import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantStatusResponse,
)
from src.security.crypto import encrypt, decrypt

# Campos que devem ser cifrados no banco
_CAMPOS_CIFRADOS = {"hinova_token", "hinova_senha", "quepasa_token"}

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post("/", response_model=TenantResponse, status_code=201)
def criar_tenant(dados: TenantCreate, db: Session = Depends(get_db)):
    """Cadastrar nova empresa (RF01)."""
    tenant = Tenant(
        nome=dados.nome,
        hinova_token=encrypt(dados.hinova_token),
        hinova_usuario=dados.hinova_usuario,
        hinova_senha=encrypt(dados.hinova_senha),
        quepasa_token=encrypt(dados.quepasa_token),
        quepasa_base_url=dados.quepasa_base_url,
        whatsapp_destino=dados.whatsapp_destino,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.get("/", response_model=list[TenantResponse])
def listar_tenants(db: Session = Depends(get_db)):
    """Listar todas as empresas cadastradas."""
    return db.query(Tenant).all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def buscar_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Ver detalhes de uma empresa."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def atualizar_tenant(
    tenant_id: str, dados: TenantUpdate, db: Session = Depends(get_db)
):
    """Atualizar credenciais de uma empresa (RF02)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    campos = dados.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        if campo in _CAMPOS_CIFRADOS:
            valor = encrypt(valor)
        setattr(tenant, campo, valor)

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=204)
def remover_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Remover uma empresa."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    db.delete(tenant)
    db.commit()


@router.get("/{tenant_id}/status", response_model=TenantStatusResponse)
def status_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Ver status do último envio (RNF03)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant
