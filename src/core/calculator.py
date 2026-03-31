"""Motor de cálculo — processa dados brutos da Hinova e gera métricas (RN01)."""

import calendar
import logging
from datetime import date
from decimal import Decimal

from src.core.models import ReportData
from src.hinova.schemas import DadosHinova

logger = logging.getLogger(__name__)

# Status de boleto usados pela Hinova (descricao_situacao_boleto)
_STATUS_PAGO = "BAIXADO"
_STATUS_CANCELADO = "CANCELADO"


def periodo_mes(referencia: date | None = None) -> tuple[date, date]:
    """Retorna (primeiro_dia, ultimo_dia) do mês de referência (RN01).

    Sempre do dia 01 até o último dia do mês corrente,
    garantindo a mesma base de comparação em qualquer dia.
    """
    hoje = referencia or date.today()
    primeiro = hoje.replace(day=1)
    ultimo = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
    return primeiro, ultimo


def _valor_boleto(boleto: dict) -> Decimal:
    """Extrai o valor de um boleto, tratando formatos diferentes."""
    raw = boleto.get("valor_boleto") or boleto.get("valor") or "0"
    if isinstance(raw, str):
        # Formato brasileiro "1.250,00" → converte para "1250.00"
        # Formato padrão "1250.00" → mantém como está
        if "," in raw:
            raw = raw.replace(".", "").replace(",", ".")
    return Decimal(str(raw))


def _status_boleto(boleto: dict) -> str:
    """Extrai o status de um boleto."""
    return (
        boleto.get("descricao_situacao_boleto")
        or boleto.get("status_boleto")
        or boleto.get("status")
        or ""
    )


def calcular_boletos(boletos: list[dict]) -> tuple[Decimal, Decimal]:
    """Soma boletos abertos e pagos.

    Returns:
        (valor_abertos, valor_pagos)
    """
    abertos = Decimal("0.00")
    pagos = Decimal("0.00")

    for boleto in boletos:
        status = _status_boleto(boleto)
        valor = _valor_boleto(boleto)

        if status == _STATUS_PAGO:
            pagos += valor
        elif status != _STATUS_CANCELADO:
            # Tudo que não é BAIXADO nem CANCELADO é considerado aberto
            abertos += valor

    return abertos, pagos


def processar(dados: DadosHinova) -> ReportData:
    """Transforma dados brutos da Hinova em métricas do relatório.

    Entrada: DadosHinova (coletados na Etapa 2)
    Saída:   ReportData  (pronto para formatar na Etapa 4)
    """
    abertos, pagos = calcular_boletos(dados.boletos or [])

    report = ReportData(
        total_ativos=dados.total_ativos,
        vendas_hoje=dados.vendas_dia,
        cancelamentos_hoje=dados.cancelamentos_dia,
        valor_boletos_abertos=abertos,
        valor_boletos_pagos=pagos,
    )

    logger.info(
        "Relatório calculado: ativos=%d vendas=%d cancel=%d aberto=R$%s pago=R$%s (%s%%)",
        report.total_ativos,
        report.vendas_hoje,
        report.cancelamentos_hoje,
        report.valor_boletos_abertos,
        report.valor_boletos_pagos,
        report.percentual_conversao,
    )
    return report
