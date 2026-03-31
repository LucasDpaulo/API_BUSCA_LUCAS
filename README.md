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
3. **Core** — calcula totais e percentuais do mês corrente (RN01)
4. **Quepasa** — formata e envia o relatório via WhatsApp

## Modelo SaaS (multi-empresa)

O sistema suporta múltiplas empresas. Cada empresa cadastra:
- Token da API Hinova
- Token da API Quepasa
- Número de WhatsApp para receber o relatório

Cada empresa só acessa seus próprios dados — isolamento total de credenciais.
Tokens e senhas são **criptografados no banco** (Fernet/AES).

## Segurança

- Tokens e senhas cifrados com `cryptography.Fernet` (AES-128)
- Chave de criptografia em `.secret.key` (fora do repositório)
- Isolamento de credenciais entre tenants (RNF01)

## Estrutura do Projeto

```
src/
├── main.py                 # Entrypoint FastAPI
├── database.py             # Conexão SQLite + SQLAlchemy
├── models/
│   └── tenant.py           # Modelo do banco (empresas)
├── schemas/
│   └── tenant_schema.py    # Validação Pydantic
├── routes/
│   └── tenant_routes.py    # CRUD de tenants (API REST)
├── hinova/
│   ├── client.py           # Cliente HTTP da API Hinova
│   └── schemas.py          # Tipagem dos dados Hinova
├── core/
│   ├── calculator.py       # Motor de cálculo (RN01)
│   └── models.py           # Dataclass ReportData
├── quepasa/
│   ├── client.py           # Cliente HTTP do Quepasa
│   └── formatter.py        # Formatador de mensagem
├── scheduler/
│   └── job.py              # Pipeline diário + agendamento
└── security/
    └── crypto.py           # Criptografia de tokens
tests/
├── test_calculator.py      # 13 testes do motor de cálculo
├── test_formatter.py       # 8 testes do formatador
├── test_quepasa_client.py  # 5 testes do cliente Quepasa
└── test_pipeline.py        # 6 testes do pipeline
```

## Plano de Desenvolvimento

| Etapa | Descrição                        | Status |
|-------|----------------------------------|--------|
| 1     | Gestão de Clientes (cadastro)    | ✅ Concluída |
| 2     | Extração de Dados (API Hinova)   | ✅ Concluída |
| 3     | Motor de Cálculo (financeiro)    | ✅ Concluída |
| 4     | Entrega (WhatsApp via Quepasa)   | ✅ Concluída |
| 5     | Automação (agendamento diário)   | ✅ Concluída |

## Tecnologias

- **Python 3.12** — Linguagem principal
- **FastAPI** — API REST com documentação automática (Swagger)
- **SQLite + SQLAlchemy** — Banco de dados com ORM
- **Pydantic** — Validação de dados
- **Requests** — Chamadas HTTP às APIs externas
- **APScheduler** — Agendamento de tarefas
- **Cryptography (Fernet)** — Criptografia de credenciais

## Como rodar localmente

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar credenciais
cp .env.example .env
# Editar .env com seus tokens reais

# Iniciar a API
uvicorn src.main:app --reload

# Acessar documentação interativa
# http://localhost:8000/docs
```

## Como rodar o scheduler

```bash
# Opção 1: APScheduler (desenvolvimento)
python -m src.scheduler.job

# Opção 2: Crontab (produção)
# Adicionar ao crontab: crontab -e
0 19 * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python -m src.scheduler.job
```

## Testes

```bash
# Rodar todos os testes (32 testes)
python3 -m pytest tests/ -v
```
