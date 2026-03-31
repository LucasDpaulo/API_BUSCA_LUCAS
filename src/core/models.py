"""Modelos de dados do relatório diário."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReportData:
    """Métricas calculadas para o relatório de um tenant."""

    total_ativos: int = 0
    vendas_hoje: int = 0
    cancelamentos_hoje: int = 0
    valor_boletos_abertos: Decimal = Decimal("0.00")
    valor_boletos_pagos: Decimal = Decimal("0.00")

    @property
    def valor_boletos_total(self) -> Decimal:
        """Soma de boletos abertos + pagos."""
        return self.valor_boletos_abertos + self.valor_boletos_pagos

    @property
    def percentual_conversao(self) -> Decimal:
        """Percentual de boletos pagos em relação ao total."""
        total = self.valor_boletos_total
        if total == 0:
            return Decimal("0.00")
        return (self.valor_boletos_pagos / total * 100).quantize(Decimal("0.01"))
