"""Motor de cálculo — processa dados brutos da Hinova e gera métricas (RN01)."""

import calendar
import logging
from datetime import date, datetime
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
    """Extrai o status de um boleto (normalizado para UPPER)."""
    return (
        boleto.get("descricao_situacao_boleto")
        or boleto.get("situacao_boleto")
        or boleto.get("situacao")
        or boleto.get("descricao_situacao")
        or boleto.get("status_boleto")
        or boleto.get("status")
        or ""
    ).strip()


def calcular_boletos(boletos: list[dict]) -> tuple[Decimal, Decimal]:
    """Soma boletos abertos e pagos (ignora cancelados/excluídos).

    Returns:
        (valor_abertos, valor_pagos)
    """
    abertos = Decimal("0.00")
    pagos = Decimal("0.00")

    contadores: dict[str, int] = {}

    for boleto in boletos:
        status = _status_boleto(boleto).upper()
        valor = _valor_boleto(boleto)

        contadores[status] = contadores.get(status, 0) + 1

        if status in (_STATUS_PAGO, "PAGO", "LIQUIDADO"):
            pagos += valor
        elif status in (_STATUS_CANCELADO, "ESTORNADO", "EXCLUIDO", "EXCLUÍDO"):
            pass  # Ignorar cancelados/estornados/excluídos
        else:
            abertos += valor

    logger.info("Distribuição de status dos boletos: %s", contadores)
    return abertos, pagos


def _filtrar_pagos_hoje(boletos: list[dict], referencia: date | None = None) -> list[dict]:
    """Filtra boletos do mês que foram pagos hoje (por data_pagamento)."""
    hoje_str = (referencia or date.today()).strftime("%Y-%m-%d")
    pagos_hoje = []
    for b in boletos:
        data_pgto = b.get("data_pagamento")
        if data_pgto and str(data_pgto).startswith(hoje_str):
            pagos_hoje.append(b)
    return pagos_hoje


def _parse_data_boleto(valor: str) -> date | None:
    """Parseia data de boleto em formato ISO (YYYY-MM-DD) ou BR (DD/MM/YYYY)."""
    if not valor:
        return None
    valor = str(valor).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            continue
    return None


def _filtrar_abertos_ate_hoje(boletos: list[dict], referencia: date | None = None) -> list[dict]:
    """Filtra boletos abertos cujo vencimento é até hoje (acumulado do mês)."""
    hoje = referencia or date.today()
    abertos = []
    for b in boletos:
        venc = _parse_data_boleto(b.get("data_vencimento") or "")
        if venc is None or venc > hoje:
            continue
        status = (
            b.get("descricao_situacao_boleto")
            or b.get("situacao_boleto")
            or b.get("situacao")
            or b.get("status")
            or ""
        ).strip().upper()
        if status not in ("BAIXADO", "PAGO", "LIQUIDADO", "CANCELADO", "ESTORNADO", "EXCLUIDO", "EXCLUÍDO"):
            abertos.append(b)
    return abertos


def processar(dados: DadosHinova) -> ReportData:
    """Transforma dados brutos da Hinova em métricas do relatório.

    Entrada: DadosHinova (coletados na Etapa 2)
    Saída:   ReportData  (pronto para formatar na Etapa 4)
    """
    boletos_mes = dados.boletos_mes or []

    # Resumo do dia: pagos hoje (data_pagamento) + abertos com vencimento até hoje (acumulado)
    pagos_hoje = _filtrar_pagos_hoje(boletos_mes)
    abertos_ate_hoje = _filtrar_abertos_ate_hoje(boletos_mes)
    logger.info(
        "Boletos pagos hoje: %d | Abertos até hoje (venc≤hoje): %d",
        len(pagos_hoje), len(abertos_ate_hoje),
    )

    _, dia_pagos = calcular_boletos(pagos_hoje)
    dia_abertos, _ = calcular_boletos(abertos_ate_hoje)

    mes_abertos, mes_pagos = calcular_boletos(boletos_mes)

    report = ReportData(
        total_ativos=dados.total_ativos,
        vendas_hoje=dados.vendas_dia,
        cancelamentos_hoje=dados.cancelamentos_dia,
        dia_abertos=dia_abertos,
        dia_pagos=dia_pagos,
        mes_abertos=mes_abertos,
        mes_pagos=mes_pagos,
    )

    logger.info(
        "Relatório calculado: ativos=%d vendas=%d cancel=%d "
        "dia(aberto=R$%s pago=R$%s) mes(aberto=R$%s pago=R$%s)",
        report.total_ativos,
        report.vendas_hoje,
        report.cancelamentos_hoje,
        report.dia_abertos, report.dia_pagos,
        report.mes_abertos, report.mes_pagos,
    )
    return report
