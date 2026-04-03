"""Modelos de dados do relatório diário."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReportData:
    """Métricas calculadas para o relatório de um tenant."""

    total_ativos: int = 0
    vendas_hoje: int = 0
    cancelamentos_hoje: int = 0

    # Resumo do dia
    dia_abertos: Decimal = Decimal("0.00")
    dia_pagos: Decimal = Decimal("0.00")

    # Resumo do mês
    mes_abertos: Decimal = Decimal("0.00")
    mes_pagos: Decimal = Decimal("0.00")

    # ── Dia ──

    @property
    def dia_total(self) -> Decimal:
        return self.dia_abertos + self.dia_pagos

    @property
    def dia_percentual_abertos(self) -> Decimal:
        if self.dia_total == 0:
            return Decimal("0.0")
        return (self.dia_abertos / self.dia_total * 100).quantize(Decimal("0.1"))

    @property
    def dia_percentual_pagos(self) -> Decimal:
        if self.dia_total == 0:
            return Decimal("0.0")
        return (self.dia_pagos / self.dia_total * 100).quantize(Decimal("0.1"))

    # ── Mês ──

    @property
    def mes_total(self) -> Decimal:
        return self.mes_abertos + self.mes_pagos

    @property
    def mes_percentual_abertos(self) -> Decimal:
        if self.mes_total == 0:
            return Decimal("0.0")
        return (self.mes_abertos / self.mes_total * 100).quantize(Decimal("0.1"))

    @property
    def mes_percentual_pagos(self) -> Decimal:
        if self.mes_total == 0:
            return Decimal("0.0")
        return (self.mes_pagos / self.mes_total * 100).quantize(Decimal("0.1"))

    # ── Compat ──

    @property
    def valor_boletos_abertos(self) -> Decimal:
        return self.mes_abertos

    @property
    def valor_boletos_pagos(self) -> Decimal:
        return self.mes_pagos

    @property
    def valor_boletos_total(self) -> Decimal:
        return self.mes_total

    @property
    def percentual_conversao(self) -> Decimal:
        return self.mes_percentual_pagos
