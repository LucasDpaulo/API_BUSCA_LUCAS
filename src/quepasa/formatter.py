"""Formatador de mensagem do relatório diário (RF07)."""

from decimal import Decimal

from src.core.models import ReportData


def _formatar_moeda(valor: Decimal) -> str:
    """Formata Decimal para padrão brasileiro: R$ 50.000,00"""
    # Converte para float para usar formatação de milhar
    v = float(valor)
    # Formato com separador de milhar e 2 decimais
    formatado = f"{v:,.2f}"
    # Converte de 50,000.00 para 50.000,00
    formatado = formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatado}"


def formatar_relatorio(nome_empresa: str, report: ReportData) -> str:
    """Monta a mensagem formatada com emojis para envio via WhatsApp.

    Args:
        nome_empresa: Nome da empresa (tenant).
        report: Métricas calculadas na Etapa 3.

    Returns:
        Texto pronto para envio.
    """
    return (
        f"\U0001f4ca Relatório Diário - {nome_empresa}\n"
        f"\n"
        f"\U0001f697 Ativos Totais: {report.total_ativos:,}\n"
        f"\u2705 Vendas hoje: {report.vendas_hoje:02d}\n"
        f"\u274c Cancelados hoje: {report.cancelamentos_hoje:02d}\n"
        f"\n"
        f"\U0001f4b0 Resumo do Dia:\n"
        f"  \u2022 Aberto: {_formatar_moeda(report.dia_abertos)} ({report.dia_percentual_abertos}%)\n"
        f"  \u2022 Pago: {_formatar_moeda(report.dia_pagos)} ({report.dia_percentual_pagos}%)\n"
        f"\n"
        f"\U0001f4c5 Resumo do Mês:\n"
        f"  \u2022 Aberto: {_formatar_moeda(report.mes_abertos)} ({report.mes_percentual_abertos}%)\n"
        f"  \u2022 Pago: {_formatar_moeda(report.mes_pagos)} ({report.mes_percentual_pagos}%)"
    )
