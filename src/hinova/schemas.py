"""Tipagem dos dados retornados pela API Hinova."""

from dataclasses import dataclass


@dataclass
class DadosHinova:
    """Dados brutos coletados da Hinova para um tenant."""

    total_ativos: int = 0
    vendas_dia: int = 0
    cancelamentos_dia: int = 0
    boletos_dia: list[dict] | None = None
    boletos_mes: list[dict] | None = None

    @property
    def coleta_ok(self) -> bool:
        """Retorna True se pelo menos algum dado foi coletado."""
        return (
            self.total_ativos > 0
            or self.vendas_dia > 0
            or self.cancelamentos_dia > 0
            or bool(self.boletos_dia)
            or bool(self.boletos_mes)
        )
