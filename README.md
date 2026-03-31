# API_BUSCA_LUCAS

API de Automação para Extração de Dados Hinova e Disparo via Quepasa.

## O que este sistema faz?

De forma simples: **todo dia às 19h, cada empresa cadastrada recebe automaticamente no WhatsApp um relatório com os números do dia.**

O relatório contém:
- Total de veículos ativos
- Vendas realizadas no dia
- Cancelamentos do dia
- Resumo financeiro do mês (boletos abertos vs. pagos)

Exemplo da mensagem recebida no WhatsApp:

```
📊 Relatório Diário - Locadora ABC

🚗 Ativos Totais: 1.250
✅ Vendas hoje: 05
❌ Cancelados hoje: 02

💰 Financeiro Mensal:
  • Aberto: R$ 50.000,00
  • Pago: R$ 35.000,00 (70%)
```

## Como funciona?

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  19:00      │     │   Hinova    │     │  Cálculos   │     │  WhatsApp   │
│  Agendador  │────▶│  Busca      │────▶│  Financeiro │────▶│  Quepasa    │
│  automático │     │  dados      │     │  do mês     │     │  Envia msg  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Agendador** dispara o processo automaticamente às 19h
2. **Hinova** — coleta veículos ativos, vendas, cancelamentos e boletos
3. **Core** — calcula totais e percentuais do mês corrente
4. **Quepasa** — formata e envia o relatório via WhatsApp

## Modelo SaaS (multi-empresa)

O sistema suporta múltiplas empresas. Cada empresa cadastra:
- Token da API Hinova
- Token da API Quepasa
- Número de WhatsApp para receber o relatório

Cada empresa só acessa seus próprios dados — isolamento total de credenciais.

## Plano de Desenvolvimento

| Etapa | Descrição                        | Status |
|-------|----------------------------------|--------|
| 1     | Gestão de Clientes (cadastro)    | ✅ Concluída |
| 2     | Extração de Dados (API Hinova)   | 🔄 Em andamento |
| 3     | Motor de Cálculo (financeiro)    | ⏳ Pendente |
| 4     | Entrega (WhatsApp via Quepasa)   | ⏳ Pendente |
| 5     | Automação (agendamento diário)   | ⏳ Pendente |

## Tecnologias

- **Python 3.12** — Linguagem principal
- **FastAPI** — API REST com documentação automática (Swagger)
- **SQLite** — Banco de dados leve
- **Requests** — Chamadas HTTP às APIs externas
- **APScheduler** — Agendamento de tarefas

## Como rodar localmente

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar a API
uvicorn src.main:app --reload

# Acessar documentação interativa
# http://localhost:8000/docs
```
