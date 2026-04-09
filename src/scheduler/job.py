"""
Job Scheduler (RNF02) — Pipeline diário às 19:00.

Duas opções de execução:
  1. Via crontab do sistema (recomendado para produção):
     0 19 * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python -m src.scheduler.job

  2. Via APScheduler (para desenvolvimento ou execução contínua):
     python -m src.scheduler.job
"""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from src.database import SessionLocal
from src.models.tenant import Tenant
from src.hinova.client import HinovaClient
from src.hinova.schemas import DadosHinova
from src.core.calculator import processar
from src.quepasa.formatter import formatar_relatorio
from src.quepasa.client import enviar_relatorio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _testar_tenant(tenant: Tenant) -> str:
    """Executa o pipeline sem enviar — retorna a mensagem formatada."""
    logger.info("Testando pipeline para tenant: %s (%s)", tenant.nome, tenant.id)

    hinova = HinovaClient(
        token_api=tenant.get_hinova_token(),
        usuario=tenant.hinova_usuario,
        senha=tenant.get_hinova_senha(),
    )

    if not hinova.autenticar():
        logger.error("Falha na autenticação Hinova para tenant %s", tenant.nome)
        return ""

    dados = DadosHinova(
        total_ativos=hinova.buscar_ativos(),
        vendas_dia=hinova.buscar_vendas_dia(),
        cancelamentos_dia=hinova.buscar_cancelamentos_dia(),
        boletos_mes=hinova.buscar_boletos_mes(),
    )

    if not dados.coleta_ok:
        logger.warning("Nenhum dado coletado para tenant %s", tenant.nome)

    report = processar(dados)
    mensagem = formatar_relatorio(tenant.nome, report)
    logger.info("Teste concluído — mensagem gerada com sucesso.")
    return mensagem


def _processar_tenant(db, tenant: Tenant) -> bool:
    """Executa o pipeline completo para um único tenant.

    Returns:
        True se o relatório foi enviado com sucesso.
    """
    logger.info("Processando tenant: %s (%s)", tenant.nome, tenant.id)

    # 1. Conectar na Hinova com as credenciais decifradas
    hinova = HinovaClient(
        token_api=tenant.get_hinova_token(),
        usuario=tenant.hinova_usuario,
        senha=tenant.get_hinova_senha(),
    )

    if not hinova.autenticar():
        logger.error("Falha na autenticação Hinova para tenant %s", tenant.nome)
        return False

    # 2. Buscar dados brutos (Etapa 2)
    dados = DadosHinova(
        total_ativos=hinova.buscar_ativos(),
        vendas_dia=hinova.buscar_vendas_dia(),
        cancelamentos_dia=hinova.buscar_cancelamentos_dia(),
        boletos_mes=hinova.buscar_boletos_mes(),
    )

    if not dados.coleta_ok:
        logger.warning("Nenhum dado coletado para tenant %s", tenant.nome)

    # 3. Calcular métricas (Etapa 3)
    report = processar(dados)

    # 4. Formatar mensagem (Etapa 4)
    mensagem = formatar_relatorio(tenant.nome, report)

    # 5. Enviar via Quepasa e atualizar status (Etapa 4)
    sucesso = enviar_relatorio(db, tenant, tenant.quepasa_base_url, mensagem)

    if sucesso:
        logger.info("Relatório enviado com sucesso para %s", tenant.nome)
    else:
        logger.error("Falha no envio para %s", tenant.nome)

    return sucesso


def run_daily_report() -> None:
    """Executa o pipeline completo para TODOS os tenants ativos."""
    logger.info("Iniciando pipeline do relatório diário...")

    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.ativo == True).all()

        if not tenants:
            logger.warning("Nenhum tenant ativo encontrado.")
            return

        logger.info("Tenants ativos encontrados: %d", len(tenants))

        sucesso = 0
        falhas = 0

        for tenant in tenants:
            try:
                if _processar_tenant(db, tenant):
                    sucesso += 1
                else:
                    falhas += 1
            except Exception:
                logger.exception("Erro inesperado ao processar tenant %s", tenant.nome)
                falhas += 1

        logger.info(
            "Pipeline concluído: %d sucesso, %d falhas de %d tenants.",
            sucesso, falhas, len(tenants),
        )
    finally:
        db.close()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_daily_report, "cron", hour=19, minute=0)
    logger.info("Scheduler iniciado — relatório agendado para 19:00 diariamente.")
    scheduler.start()
