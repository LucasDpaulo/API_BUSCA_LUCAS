# CLAUDE.md — Memoria de Curto Prazo Estruturada

> Leia este arquivo toda vez que o usuario disser "vamos voltar onde paramos" ou iniciar uma nova conversa.

---

## 1. O que e este projeto

**API Busca Lucas** — Sistema automatizado que:
1. Coleta dados da API SGA Hinova (veiculos ativos, vendas, cancelamentos, boletos)
2. Calcula metricas financeiras (dia e mes)
3. Formata um relatorio e envia via WhatsApp (Quepasa)

Envio automatico diario as **19:00** (configuravel em `src/scheduler/job.py:147`).

---

## 2. Como rodar o sistema

### Pre-requisitos
```bash
# Ativar venv (SEMPRE usar este python)
source venv/bin/activate
# OU usar diretamente:
venv/bin/python
```

### Subir o Quepasa (WhatsApp)
```bash
docker ps --filter "name=quepasa"
docker start quepasa
# Container: quepasa | Imagem: quepasa-fixed | Porta: 31000
# IMPORTANTE: aguardar ~10s apos start para sincronizar
```

### Backend (API FastAPI)
```bash
venv/bin/uvicorn src.main:app --reload --port 8000
# Acesso: http://localhost:8000
```

### Frontend React (Painel de Gestao)
```bash
# Node 20 via nvm
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
cd frontend && npx vite --host 0.0.0.0
# Acesso: http://localhost:5173
```

### Rodar testes
```bash
venv/bin/python -m pytest tests/ -v
# 36 testes passando
```

### Scheduler automatico (modo continuo)
```bash
venv/bin/python -m src.scheduler.job
# Fica rodando e dispara as 19:00 todo dia
```

---

## 3. Servicos e portas

| Servico          | Porta | Como subir                                      |
|------------------|-------|-------------------------------------------------|
| Quepasa (WA)     | 31000 | `docker start quepasa`                          |
| FastAPI (Backend) | 8000  | `venv/bin/uvicorn src.main:app --reload`        |
| Frontend React   | 5173  | `cd frontend && npx vite --host 0.0.0.0`       |
| SQLite (DB)      | —     | Arquivo local `data.db` (raiz do projeto)       |

### Quepasa — Credenciais
- URL: http://localhost:31000
- Email: `admin@quepasa.io` / Senha: `admin123`
- Token API: `319f5001-82c5-46ab-a900-0a4d0b17bc79` (fixo para todos os tenants)

### Frontend — Login
- Usuario: `Atomos` / Senha: `atomos_1234`

---

## 4. Arquitetura do Pipeline

```
Hinova API ──> HinovaClient ──> DadosHinova ──> Calculator ──> ReportData ──> Formatter ──> QuepasaClient ──> WhatsApp
  (coleta)     src/hinova/      src/hinova/     src/core/      src/core/      src/quepasa/   src/quepasa/
               client.py        schemas.py      calculator.py  models.py      formatter.py   client.py
```

Orquestrado por: `src/scheduler/job.py` → `_processar_tenant()` (disparo automatico)

### Fluxo do Frontend (manual)
```
Testar → _testar_tenant() → gera mensagem (sem enviar)
Disparar → POST /tenants/{id}/disparar → envia mensagem ja gerada ao WhatsApp
```

### Estrutura de arquivos principais
```
src/
  main.py                  # FastAPI app + CORS
  database.py              # SQLite + SQLAlchemy
  models/tenant.py         # Modelo Tenant (multi-tenant)
  routes/tenant_routes.py  # CRUD tenants + endpoints testar/disparar
  schemas/tenant_schema.py # Schemas Pydantic
  security/crypto.py       # Criptografia Fernet
  hinova/
    client.py              # Cliente HTTP Hinova
    schemas.py             # DadosHinova (dados brutos)
  core/
    calculator.py          # Processa dados brutos → ReportData
    models.py              # ReportData (metricas dia + mes)
  quepasa/
    client.py              # Cliente HTTP Quepasa (envio WhatsApp)
    formatter.py           # Formata mensagem do relatorio
  scheduler/
    job.py                 # Pipeline diario + APScheduler (19:00)
frontend/
  src/App.jsx              # Aplicacao React (Vite + Tailwind CSS v4)
tests/
  test_calculator.py       # Testes do motor de calculo
  test_formatter.py        # Testes de formatacao
  test_pipeline.py         # Testes do pipeline completo
  test_quepasa_client.py   # Testes do cliente Quepasa
```

---

## 5. Detalhes tecnicos importantes

### API Hinova — Particularidades
- **Token expira rapido**: re-autenticacao automatica em caso de 401
- **Boletos do dia**: NAO enviar `mes_referente` no payload (erro 406)
- **Boletos do mes**: DEVE enviar `mes_referente`
- **Cancelamentos**: codigos CANCELADO(7), INATIVO(2), PRE-CANCELAMENTO(16)
- **Situacoes**: cacheadas via `_buscar_situacoes()`
- **Timeout**: 120s para POST (boletos paginam ate 10 paginas de 100)
- **Restricao de horario**: Hinova bloqueia acesso fora do horario comercial

### WhatsApp / Quepasa
- Container Docker `quepasa-fixed`, porta 31000
- Numero conectado: Lucas `558799514353`
- Token fixo para todos os tenants: `319f5001-82c5-46ab-a900-0a4d0b17bc79`
- URL fixa: `http://localhost:31000`
- Endpoint: `POST /v4/send` com header `X-QUEPASA-TOKEN`

### Banco de dados
- SQLite em `data.db` (raiz do projeto)
- Credenciais criptografadas com **Fernet** (`src/security/crypto.py`)
- Multi-tenant: cada tenant tem credenciais Hinova proprias

### Frontend React
- **Vite + React + Tailwind CSS v4 + lucide-react**
- Node 20 via nvm
- Login: `Atomos` / `atomos_1234`
- CRUD de tenants integrado com backend via fetch
- Aba "Teste": roda pipeline sem enviar, mostra preview da mensagem
- Aba "Logs": mostra logs reais do pipeline (erros e sucessos)
- Botao "Disparar para WhatsApp": envia a mensagem do preview (com confirmacao + countdown 10s)
- Token Quepasa e URL ja preenchidos automaticamente no cadastro

---

## 6. Estado atual (atualizado em 03/04/2026)

### Tudo integrado e funcionando
- Backend: 36/36 testes passando
- Frontend React conectado ao backend (CRUD + testar + disparar)
- Tenant "Atomos dev" cadastrado e testado com dados reais
- Relatorios enviados e recebidos no WhatsApp com sucesso
- Scheduler configurado para 19:00

### Endpoints da API
- `GET /tenants/` — listar tenants
- `POST /tenants/` — criar tenant
- `PUT /tenants/{id}` — atualizar tenant
- `DELETE /tenants/{id}` — remover tenant
- `POST /tenants/{id}/testar` — testar pipeline (sem enviar)
- `POST /tenants/{id}/disparar` — enviar mensagem ao WhatsApp
- `GET /tenants/{id}/status` — status do ultimo envio

---

## 7. Melhorias futuras

### Prioridade media
- [ ] Salvar ultimo relatorio no banco para exibir no frontend
- [ ] Avaliar boletos do dia (emitidos vs vencendo)
- [ ] Historico de relatorios enviados

### Prioridade baixa
- [ ] Multiplos destinatarios por tenant
- [ ] Agendamento configuravel por tenant
- [ ] Testes de integracao contra Hinova real
- [ ] Autenticacao real (JWT) no frontend

---

## 8. Comandos rapidos

```bash
# Testes
venv/bin/python -m pytest tests/ -v

# Backend
venv/bin/uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend && npx vite --host 0.0.0.0

# Quepasa
docker start quepasa

# Scheduler
venv/bin/python -m src.scheduler.job

# Ver tenants no banco
venv/bin/python -c "
from src.models.tenant import Tenant
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
db = sessionmaker(bind=create_engine('sqlite:///data.db'))()
for t in db.query(Tenant).all():
    print(t.nome, t.ativo, t.whatsapp_destino)
"
```
