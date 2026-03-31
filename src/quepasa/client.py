"""Cliente HTTP para a API Quepasa — envio de mensagens WhatsApp (RF08)."""

import logging
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from src.models.tenant import Tenant

logger = logging.getLogger(__name__)

# Timeout para chamadas HTTP (segundos)
_TIMEOUT = 30

# Máximo de tentativas em caso de falha temporária
_MAX_RETRIES = 2


class QuepasaClient:
    """Envia mensagens via Quepasa para um tenant específico."""

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-QUEPASA-TOKEN": self.token,
        }

    def enviar_mensagem(self, destino: str, texto: str) -> bool:
        """Envia uma mensagem de texto via WhatsApp.

        Args:
            destino: Número do WhatsApp (ex: 5531999999999).
            texto: Mensagem formatada.

        Returns:
            True se enviou com sucesso, False caso contrário.
        """
        url = f"{self.base_url}/v4/send"
        payload = {"chatid": destino, "text": texto}

        for tentativa in range(1, _MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    url, json=payload, headers=self._headers(), timeout=_TIMEOUT
                )
                resp.raise_for_status()
                logger.info("Mensagem enviada para %s (tentativa %d)", destino, tentativa)
                return True
            except requests.RequestException as e:
                logger.error(
                    "Erro ao enviar para %s (tentativa %d/%d): %s",
                    destino, tentativa, _MAX_RETRIES, e,
                )

        return False


def enviar_relatorio(
    db: Session,
    tenant: Tenant,
    base_url: str,
    mensagem: str,
) -> bool:
    """Envia o relatório e atualiza o status do tenant no banco.

    Args:
        db: Sessão do banco de dados.
        tenant: Tenant que receberá o relatório.
        base_url: URL base da API Quepasa.
        mensagem: Texto formatado do relatório.

    Returns:
        True se enviou com sucesso.
    """
    client = QuepasaClient(base_url, tenant.get_quepasa_token())
    sucesso = client.enviar_mensagem(tenant.whatsapp_destino, mensagem)

    tenant.ultimo_envio = datetime.now()
    tenant.ultimo_status = "sucesso" if sucesso else "erro: falha no envio Quepasa"
    db.commit()

    return sucesso
