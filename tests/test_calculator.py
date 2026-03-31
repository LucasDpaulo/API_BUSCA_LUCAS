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
        {"status_boleto": "Aberto", "valor_boleto": "1000.00"},
        {"status_boleto": "Aberto", "valor_boleto": "500.00"},
        {"status_boleto": "Baixado", "valor_boleto": "750.00"},
        {"status_boleto": "Baixado", "valor_boleto": "250.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("1500.00")
    assert pagos == Decimal("1000.00")


def test_calcular_boletos_formato_brasileiro():
    """Valores com formato 1.250,00 devem ser parseados corretamente."""
    boletos = [
        {"status_boleto": "Aberto", "valor_boleto": "1.250,00"},
        {"status_boleto": "Baixado", "valor_boleto": "3.500,50"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("1250.00")
    assert pagos == Decimal("3500.50")


def test_calcular_boletos_lista_vazia():
    abertos, pagos = calcular_boletos([])
    assert abertos == Decimal("0.00")
    assert pagos == Decimal("0.00")


def test_calcular_boletos_ignora_status_desconhecido():
    """Boletos com status diferente de Aberto/Baixado são ignorados."""
    boletos = [
        {"status_boleto": "Cancelado", "valor_boleto": "999.00"},
        {"status_boleto": "Aberto", "valor_boleto": "100.00"},
    ]
    abertos, pagos = calcular_boletos(boletos)
    assert abertos == Decimal("100.00")
    assert pagos == Decimal("0.00")


# ── Testes de processar (fluxo completo) ────────────────────────────


def test_processar_dados_completos():
    dados = DadosHinova(
        total_ativos=1250,
        vendas_dia=5,
        cancelamentos_dia=2,
        boletos=[
            {"status_boleto": "Aberto", "valor_boleto": "50000.00"},
            {"status_boleto": "Baixado", "valor_boleto": "35000.00"},
        ],
    )
    report = processar(dados)

    assert report.total_ativos == 1250
    assert report.vendas_hoje == 5
    assert report.cancelamentos_hoje == 2
    assert report.valor_boletos_abertos == Decimal("50000.00")
    assert report.valor_boletos_pagos == Decimal("35000.00")
    assert report.valor_boletos_total == Decimal("85000.00")
    assert report.percentual_conversao == Decimal("41.18")


def test_processar_sem_boletos():
    dados = DadosHinova(total_ativos=100, vendas_dia=0, cancelamentos_dia=0, boletos=[])
    report = processar(dados)

    assert report.valor_boletos_abertos == Decimal("0.00")
    assert report.valor_boletos_pagos == Decimal("0.00")
    assert report.percentual_conversao == Decimal("0.00")


def test_processar_100_porcento_pago():
    dados = DadosHinova(
        total_ativos=50,
        vendas_dia=1,
        cancelamentos_dia=0,
        boletos=[
            {"status_boleto": "Baixado", "valor_boleto": "10000.00"},
        ],
    )
    report = processar(dados)
    assert report.percentual_conversao == Decimal("100.00")


def test_processar_boletos_none():
    """Se boletos vier como None, deve tratar como lista vazia."""
    dados = DadosHinova(total_ativos=10, boletos=None)
    report = processar(dados)
    assert report.valor_boletos_total == Decimal("0.00")
