# Etapa 3 — Motor de Cálculo (Core)

## Requisitos cobertos

- **RN01** — Cálculo de boletos do dia 01 até o último dia do mês corrente

## Dependência

- **Etapa 2 concluída** — precisa dos dados brutos da Hinova

## O que será construído

### 3.1 — Processador de dados

Recebe os dados brutos da Hinova e gera métricas prontas para o relatório:

| Métrica                   | Lógica                                                    |
|---------------------------|-----------------------------------------------------------|
| total_ativos              | Contagem de veículos com status "Ativo"                   |
| vendas_hoje               | Contagem de veículos cadastrados na data de hoje          |
| cancelamentos_hoje        | Contagem de alterações para "Cancelado" no dia            |
| valor_boletos_abertos     | Soma dos boletos com status "Aberto" no mês              |
| valor_boletos_pagos       | Soma dos boletos com status "Baixado" no mês             |
| percentual_conversao      | (pagos / total) * 100                                     |

### 3.2 — Regra RN01 (crucial)

```python
# SEMPRE do dia 01 até o último dia do mês corrente
import calendar
from datetime import date

hoje = date.today()
primeiro_dia = hoje.replace(day=1)
ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])
```

Isso garante que o relatório do dia 5 e do dia 28 usam a **mesma base de comparação**.

### 3.3 — Arquivos que serão criados

```
src/core/
├── calculator.py    # Funções de cálculo e agregação
└── models.py        # Dataclass ReportData com todas as métricas
```

## Processos de implementação

1. Definir dataclass com as métricas do relatório
2. Implementar filtros de data (RN01)
3. Implementar cálculos de totalização e percentual
4. Testes unitários para garantir que RN01 funciona em qualquer dia do mês

## Critério de conclusão

- Dados brutos entram → métricas calculadas saem
- RN01 funciona corretamente em qualquer dia do mês
- Testes unitários passando
