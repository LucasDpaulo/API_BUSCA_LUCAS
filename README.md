# API Busca Lucas

Sistema de automacao que coleta dados financeiros de locadoras via API Hinova e envia relatorios diarios por WhatsApp.

## O que faz?

Todos os dias as 19:00, o sistema:

1. Conecta na **API Hinova (SGA)** e busca dados da locadora (veiculos ativos, vendas, cancelamentos e boletos)
2. Calcula metricas financeiras do dia e do mes
3. Formata e envia um relatorio via **WhatsApp** usando o Quepasa

Exemplo de relatorio recebido no WhatsApp:

```
📊 Relatorio Diario - Locadora ABC

🚗 Ativos Totais: 7,945
✅ Cadastro hoje: 23
❌ Cancelados hoje: 12

💰 Resumo de ontem:
  • Aberto: R$ 125,27 (2.4%)
  • Pago: R$ 5.117,80 (97.6%)

📅 Resumo do Mes:
  • Aberto: R$ 104.384,09 (97.0%)
  • Pago: R$ 3.209,00 (3.0%)
```

Suporta **multiplas empresas** — cada uma com suas credenciais isoladas e criptografadas.

## Arquitetura

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Hinova  │────>│ Calculadora│────>│Formatador│────>│ WhatsApp │
│  (API)   │     │  (Python) │     │          │     │(Quepasa) │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                       ↑                                 ↑
                  Dados brutos                     Mensagem pronta
```

**Backend:** Python 3.12, FastAPI, SQLite, SQLAlchemy, APScheduler, Fernet (criptografia)

**Frontend:** React, Vite, Tailwind CSS v4, lucide-react

## Frontend — Painel de Gestao

O projeto inclui um painel web em React para gerenciamento:

- **Login** com autenticacao
- **CRUD de clientes** — cadastrar, editar e remover empresas
- **Testar pipeline** — roda a coleta de dados e mostra o preview da mensagem sem enviar
- **Disparar para WhatsApp** — envia a mensagem testada com confirmacao visual
- **Logs em tempo real** — acompanha erros de conexao, status da Hinova e resultados

O painel e voltado para desenvolvedores acompanharem o funcionamento do sistema. O envio automatico diario e feito pelo scheduler (separado).

## Como instalar

### 1. Clonar e configurar

```bash
git clone https://github.com/LucasDpaulo/API_BUSCA_LUCAS.git
cd API_BUSCA_LUCAS

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Instalar o Quepasa (WhatsApp)

Precisa de Docker instalado.

```bash
# Subir o Quepasa
cd quepasa
docker compose up -d
```

Acesse http://localhost:31000, faca login (`admin@quepasa.io` / `admin123`) e escaneie o QR Code com seu WhatsApp.

### 3. Subir o sistema

```bash
# Terminal 1 — Backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npx vite --host 0.0.0.0
```

Acesse o painel em http://localhost:5173

### 4. Cadastrar uma empresa

No painel, clique em **"+ Novo Cliente"** e preencha:

| Campo | O que colocar |
|-------|---------------|
| Nome | Nome da empresa |
| Token API Hinova | Token gerado no SGA Hinova |
| Usuario SGA | Usuario de integracao |
| Senha SGA | Senha de integracao |
| WhatsApp Destino | Numero completo (ex: `558799514353`) |

O token e URL do Quepasa ja vem preenchidos automaticamente.

### 5. Testar

No painel, abra o cliente cadastrado e:

1. Clique em **"Testar / Verificacao de Dados"** — o sistema busca os dados e mostra o preview
2. Confira a mensagem na aba de preview
3. Se estiver tudo certo, clique em **"Disparar para WhatsApp"** para enviar

### 6. Agendar envio automatico

```bash
# Opcao A: Scheduler Python (fica executando)
python -m src.scheduler.job
# Envia todo dia as 19:00

# Opcao B: Crontab (producao)
crontab -e
# Adicionar:
0 19 * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python -c "from src.scheduler.job import run_daily_report; run_daily_report()"
```

## Testes

```bash
python3 -m pytest tests/ -v
# 36 testes passando
```

## Servicos e portas

| Servico | Porta | Funcao |
|---------|-------|--------|
| Backend (FastAPI) | 8000 | API REST + CRUD de tenants |
| Frontend (React) | 5173 | Painel de gestao |
| Quepasa | 31000 | Gateway WhatsApp |
| SQLite | — | Banco de dados local (`data.db`) |

## Tecnologias

**Backend:** Python 3.12, FastAPI, SQLite, SQLAlchemy, Pydantic, APScheduler, Cryptography (Fernet), Docker, Quepasa

**Frontend:** React 19, Vite, Tailwind CSS v4, lucide-react
