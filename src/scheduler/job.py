"""
Job Scheduler (RNF02) — Esboço do agendamento diário às 19:00.

Duas opções de execução:
  1. Via crontab do sistema (recomendado para produção):
     0 19 * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python -m src.scheduler.job

  2. Via APScheduler (para desenvolvimento ou execução contínua):
     python -m src.scheduler.job
"""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_daily_report() -> None:
    """Executa o pipeline completo: Fetch → Parse → Dispatch."""
    logger.info("Iniciando pipeline do relatório diário...")
    # TODO: implementar chamada ao pipeline principal
    # 1. Buscar credenciais do tenant
    # 2. Fetch dados Hinova (ativos, vendas, cancelamentos, financeiro)
    # 3. Calcular métricas (core)
    # 4. Formatar e enviar via Quepasa
    logger.info("Pipeline concluído.")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_daily_report, "cron", hour=19, minute=0)
    logger.info("Scheduler iniciado — relatório agendado para 19:00 diariamente.")
    scheduler.start()
