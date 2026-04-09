"""Testes unitários do motor de cálculo (Etapa 3)."""

from datetime import date
from decimal import Decimal

from src.core.calculator import calcular_boletos, periodo_mes, processar
from src.core.models import ReportData
from src.hinova.schemas import DadosHinova


# ── Testes de periodo_mes (RN01) ────────────────────────────────────


def test_periodo_mes_inicio_do_mes():
    """Dia 1 deve retornar o mês inteiro."""
    primeiro, ultimo = periodo_mes(date(2026, 3, 1))
    assert primeiro == date(2026, 3, 1)
    assert ultimo == date(2026, 3, 31)


def test_periodo_mes_meio_do_mes():
    """Dia 15 deve retornar o mesmo mês inteiro."""
    primeiro, ultimo = periodo_mes(date(2026, 3, 15))
    assert primeiro == date(2026, 3, 1)
    assert ultimo == date(2026, 3, 31)


def test_periodo_mes_fim_do_mes():
    """Último dia deve retornar o mesmo mês inteiro."""
    primeiro, ultimo = periodo_mes(date(2026, 3, 31))
    assert primeiro == date(2026, 3, 1)
    assert ultimo == date(2026, 3, 31)


def test_periodo_mes_fevereiro_bissexto():
    """Fevereiro em ano bissexto deve ter 29 dias."""
    primeiro, ultimo = periodo_mes(date(2028, 2, 10))
    assert primeiro == date(2028, 2, 1)
    assert ultimo == date(2028, 2, 29)


def test_periodo_mes_fevereiro_normal():
    """Fevereiro em ano normal deve ter 28 dias."""
    primeiro, ultimo = periodo_mes(date(2027, 2, 5))
    assert primeiro == date(2027, 2, 1)
    assert ultimo == date(2027, 2, 28)


# ── Testes de calcular_boletos ──────────────────────────────────────


def test_calcular_boletos_abertos_e_pagos():
    boletos = [
        {"descricao_situacao_boleto": "ABERTO", "valor_boleto": "1000.00"},
        {"descricao_situacao_boleto": "ABERTO", "valor_boleto": "500.00"},
        {"descricao_situacao_boleto": "BAIXADO", "valor_boleto": "750.00"},
        {"descricao_situacao_boleto": "BAIXADO", "valor_boleto": "250.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("1500.00")
    assert pagos == Decimal("1000.00")


def test_calcular_boletos_formato_brasileiro():
    """Valores com formato 1.250,00 devem ser parseados corretamente."""
    boletos = [
        {"descricao_situacao_boleto": "ABERTO", "valor_boleto": "1.250,00"},
        {"descricao_situacao_boleto": "BAIXADO", "valor_boleto": "3.500,50"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("1250.00")
    assert pagos == Decimal("3500.50")


def test_calcular_boletos_lista_vazia():
    abertos, pagos = calcular_boletos([])
    assert abertos == Decimal("0.00")
    assert pagos == Decimal("0.00")


def test_calcular_boletos_ignora_cancelados():
    """Boletos CANCELADOS não entram em nenhuma soma."""
    boletos = [
        {"descricao_situacao_boleto": "CANCELADO", "valor_boleto": "999.00"},
        {"descricao_situacao_boleto": "ABERTO", "valor_boleto": "100.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("100.00")
    assert pagos == Decimal("0.00")


def test_calcular_boletos_status_pago_e_liquidado():
    """Status PAGO e LIQUIDADO devem ser somados como pagos."""
    boletos = [
        {"situacao_boleto": "PAGO", "valor_boleto": "200.00"},
        {"situacao_boleto": "Liquidado", "valor_boleto": "300.00"},
        {"descricao_situacao_boleto": "BAIXADO", "valor_boleto": "100.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert pagos == Decimal("600.00")
    assert abertos == Decimal("0.00")


def test_calcular_boletos_ignora_estornado_excluido():
    """Status ESTORNADO e EXCLUÍDO não entram em nenhuma soma."""
    boletos = [
        {"situacao": "ESTORNADO", "valor_boleto": "500.00"},
        {"descricao_situacao": "Excluído", "valor_boleto": "300.00"},
        {"descricao_situacao_boleto": "ABERTO", "valor_boleto": "100.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("100.00")
    assert pagos == Decimal("0.00")


def test_calcular_boletos_campos_alternativos():
    """Deve extrair status de campos alternativos (situacao, status_boleto)."""
    boletos = [
        {"situacao": "Aberto", "valor_boleto": "400.00"},
        {"status_boleto": "Baixado", "valor_boleto": "200.00"},
        {"status": "Pendente", "valor_boleto": "150.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("550.00")
    assert pagos == Decimal("200.00")


def test_calcular_boletos_status_com_espacos():
    """Status com espaços extras devem ser tratados corretamente."""
    boletos = [
        {"descricao_situacao_boleto": "  ABERTO  ", "valor_boleto": "100.00"},
        {"descricao_situacao_boleto": " BAIXADO ", "valor_boleto": "200.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("100.00")
    assert pagos == Decimal("200.00")


# ── Testes de processar (fluxo completo) ────────────────────────────


def test_processar_dados_completos():
    from datetime import date
    hoje = date.today().strftime("%Y-%m-%d")
    boletos = [
        {"situacao_boleto": "ABERTO", "valor_boleto": "50000.00", "data_emissao": hoje, "data_vencimento": "2026-04-20"},
        {"situacao_boleto": "BAIXADO", "valor_boleto": "35000.00", "data_pagamento": hoje, "data_emissao": "2025-01-01"},
    ]
    dados = DadosHinova(
        total_ativos=1250,
        vendas_dia=5,
        cancelamentos_dia=2,
        boletos_mes=boletos,
    )
    report = processar(dados)

    assert report.total_ativos == 1250
    assert report.vendas_hoje == 5
    assert report.cancelamentos_hoje == 2
    # Dia (emitidos hoje abertos + pagos hoje)
    assert report.dia_abertos == Decimal("50000.00")
    assert report.dia_pagos == Decimal("35000.00")
    assert report.dia_percentual_pagos == Decimal("41.2")
    # Mês
    assert report.mes_abertos == Decimal("50000.00")
    assert report.mes_pagos == Decimal("35000.00")
    assert report.mes_percentual_pagos == Decimal("41.2")


def test_processar_sem_boletos():
    dados = DadosHinova(total_ativos=100, vendas_dia=0, cancelamentos_dia=0)
    report = processar(dados)

    assert report.dia_abertos == Decimal("0.00")
    assert report.mes_abertos == Decimal("0.00")
    assert report.mes_percentual_pagos == Decimal("0.0")


def test_processar_100_porcento_pago():
    from datetime import date
    hoje = date.today().strftime("%Y-%m-%d")
    boletos = [{"descricao_situacao_boleto": "BAIXADO", "valor_boleto": "10000.00", "data_pagamento": hoje}]
    dados = DadosHinova(
        total_ativos=50,
        vendas_dia=1,
        cancelamentos_dia=0,
        boletos_mes=boletos,
    )
    report = processar(dados)
    assert report.dia_percentual_pagos == Decimal("100.0")
    assert report.mes_percentual_pagos == Decimal("100.0")


def test_processar_boletos_none():
    """Se boletos vier como None, deve tratar como lista vazia."""
    dados = DadosHinova(total_ativos=10)
    report = processar(dados)
    assert report.dia_total == Decimal("0.00")
    assert report.mes_total == Decimal("0.00")
