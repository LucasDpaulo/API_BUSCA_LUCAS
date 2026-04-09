"""Endpoints CRUD de Tenant (RF01, RF02, RNF01, RNF03)."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.tenant import Tenant
from src.schemas.tenant_schema import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantDetailResponse,
    TestHistoryResponse,
    TenantStatusResponse,
)
from src.security.crypto import encrypt, decrypt
from src.scheduler.job import _processar_tenant, _testar_tenant
from src.quepasa.client import enviar_relatorio
from src.models.test_history import TestHistory

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


@router.get("/{tenant_id}/detalhe", response_model=TenantDetailResponse)
def detalhe_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Retorna dados completos do tenant com credenciais descriptografadas (para edição)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return TenantDetailResponse(
        id=tenant.id,
        nome=tenant.nome,
        hinova_token=decrypt(tenant.hinova_token),
        hinova_usuario=tenant.hinova_usuario,
        hinova_senha=decrypt(tenant.hinova_senha),
        quepasa_token=decrypt(tenant.quepasa_token),
        quepasa_base_url=tenant.quepasa_base_url,
        whatsapp_destino=tenant.whatsapp_destino,
        ativo=tenant.ativo,
        ultimo_envio=tenant.ultimo_envio,
        ultimo_status=tenant.ultimo_status,
        criado_em=tenant.criado_em,
    )


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


@router.post("/{tenant_id}/testar")
def testar_relatorio(tenant_id: str, db: Session = Depends(get_db)):
    """Testa o pipeline sem enviar — retorna a mensagem e logs."""
    import logging
    import io

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        mensagem = _testar_tenant(tenant)
        logs = log_capture.getvalue()
        sucesso = bool(mensagem)
        msg_final = mensagem or "Falha ao gerar relatório."

        # Salvar no histórico
        historico = TestHistory(
            tenant_id=tenant.id,
            sucesso=sucesso,
            mensagem=msg_final,
            logs=logs,
        )
        db.add(historico)
        db.commit()

        return {
            "sucesso": sucesso,
            "mensagem": msg_final,
            "logs": logs,
        }
    except Exception as e:
        logs = log_capture.getvalue()
        msg_erro = f"Erro: {str(e)}"

        # Salvar erro no histórico
        historico = TestHistory(
            tenant_id=tenant.id,
            sucesso=False,
            mensagem=msg_erro,
            logs=logs,
        )
        db.add(historico)
        db.commit()

        return {
            "sucesso": False,
            "mensagem": msg_erro,
            "logs": logs,
        }
    finally:
        root_logger.removeHandler(handler)


class MensagemDisparo(BaseModel):
    """Mensagem já gerada para enviar ao WhatsApp."""
    mensagem: str


@router.post("/{tenant_id}/disparar")
def disparar_relatorio(tenant_id: str, body: MensagemDisparo, db: Session = Depends(get_db)):
    """Envia a mensagem já gerada ao WhatsApp (sem re-processar o pipeline)."""
    import logging
    import io

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    if not tenant.ativo:
        raise HTTPException(status_code=400, detail="Tenant está inativo")

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    try:
        sucesso = enviar_relatorio(db, tenant, tenant.quepasa_base_url, body.mensagem)
        logs = log_capture.getvalue()
        return {
            "sucesso": sucesso,
            "mensagem": "Relatório enviado com sucesso!" if sucesso else "Falha no envio ao WhatsApp.",
            "logs": logs,
        }
    except Exception as e:
        logs = log_capture.getvalue()
        return {
            "sucesso": False,
            "mensagem": f"Erro: {str(e)}",
            "logs": logs,
        }
    finally:
        root_logger.removeHandler(handler)


@router.get("/{tenant_id}/historico", response_model=list[TestHistoryResponse])
def historico_testes(tenant_id: str, db: Session = Depends(get_db)):
    """Retorna os últimos 5 resultados de teste do tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return (
        db.query(TestHistory)
        .filter(TestHistory.tenant_id == tenant_id)
        .order_by(TestHistory.criado_em.desc())
        .limit(5)
        .all()
    )


@router.get("/{tenant_id}/status", response_model=TenantStatusResponse)
def status_tenant(tenant_id: str, db: Session = Depends(get_db)):
    """Ver status do último envio (RNF03)."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    return tenant
