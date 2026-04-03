"""Testes do formatador de mensagem (Etapa 4 — RF07)."""

from decimal import Decimal

from src.core.models import ReportData
from src.quepasa.formatter import formatar_relatorio, _formatar_moeda


# ── Testes de formatação de moeda ───────────────────────────────────


def test_formatar_moeda_simples():
    assert _formatar_moeda(Decimal("1000.00")) == "R$ 1.000,00"


def test_formatar_moeda_grande():
    assert _formatar_moeda(Decimal("50000.00")) == "R$ 50.000,00"


def test_formatar_moeda_centavos():
    assert _formatar_moeda(Decimal("1234.56")) == "R$ 1.234,56"


def test_formatar_moeda_zero():
    assert _formatar_moeda(Decimal("0.00")) == "R$ 0,00"


def test_formatar_moeda_milhao():
    assert _formatar_moeda(Decimal("1500000.00")) == "R$ 1.500.000,00"


# ── Testes do relatório formatado ───────────────────────────────────


def test_relatorio_completo():
    report = ReportData(
        total_ativos=1250,
        vendas_hoje=5,
        cancelamentos_hoje=2,
        dia_abertos=Decimal("5000.00"),
        dia_pagos=Decimal("3000.00"),
        mes_abertos=Decimal("50000.00"),
        mes_pagos=Decimal("35000.00"),
    )
    msg = formatar_relatorio("Locadora ABC", report)

    assert "Locadora ABC" in msg
    assert "1,250" in msg
    assert "Resumo do Dia" in msg
    assert "Resumo do Mês" in msg
    assert "R$ 5.000,00" in msg  # dia aberto
    assert "R$ 3.000,00" in msg  # dia pago
    assert "R$ 50.000,00" in msg  # mês aberto
    assert "R$ 35.000,00" in msg  # mês pago


def test_relatorio_sem_dados():
    report = ReportData()
    msg = formatar_relatorio("Empresa Vazia", report)

    assert "Empresa Vazia" in msg
    assert "R$ 0,00" in msg
    assert "0.0%" in msg


def test_relatorio_100_porcento():
    report = ReportData(
        total_ativos=100,
        vendas_hoje=10,
        cancelamentos_hoje=0,
        dia_abertos=Decimal("0.00"),
        dia_pagos=Decimal("25000.00"),
        mes_abertos=Decimal("0.00"),
        mes_pagos=Decimal("25000.00"),
    )
    msg = formatar_relatorio("Empresa Top", report)

    assert "100.0%" in msg  # pagos
    assert "0.0%" in msg  # abertos
    assert "R$ 25.000,00" in msg
