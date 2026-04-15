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
  models/test_history.py   # Modelo TestHistory (historico de testes)
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
- **Ativos Totais**: `buscar_ativos()` usa `codigo_situacao=1` e le `total_veiculos` (Atomos dev ~8130). Nao tem como filtrar "apenas ativos que geram boleto" sem acesso a tela especifica do Hinova — ja investigado.
- **Boletos do dia**:
  - **Pagos**: boletos do mes com `data_pagamento = hoje`
  - **Abertos**: boletos com `data_vencimento <= hoje` ainda nao baixados (acumulado do inicio do mes ate hoje, nao apenas emitidos hoje)
- **Boletos do mes**: usa APENAS `data_vencimento_inicial/final` (01 ao ultimo dia). NAO enviar `mes_referente` — esse parametro filtra por mensalidade, excluindo atrasados/antecipados que vencem no mes (ex: mensalidade de marco vencendo em 05/04 era ignorada). Bug descoberto 10/04/2026: com `mes_referente` vinham 817 boletos, sem ele vem ~9991 (numero real).
- **Paginacao (criterio de parada)**: paginar ate `numero_paginas` retornado pela API, NAO parar quando a pagina veio com menos que `page_size`. A Hinova devolve paginas intermediarias com 499 em vez de 500 e o loop antigo parava cedo perdendo ~10k boletos.
- **Cancelamentos**: codigos CANCELADO(7), INATIVO(2), PRE-CANCELAMENTO(16)
- **Situacoes**: cacheadas via `_buscar_situacoes()`
- **Timeout**: 240s para POST (boletos paginam em blocos de 500, fallback para 100)
- **Paginacao**: `inicio_paginacao` e INDICE DE PAGINA (0,1,2,3...) NAO offset absoluto
- **406 tratado como vazio**: `_post()` retorna `None` em vez de erro
- **Boletos CANCELADOS**: filtrados automaticamente no `_buscar_boletos_periodo()`
- **Restricao de horario**: Hinova bloqueia acesso fora do horario comercial
- **Performance**: pipeline de um tenant leva ~2 minutos agora (23 paginas x 500 boletos com re-auth). Aceitavel para job das 19h.

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
- Aba "Historico": mostra ultimos 5 testes com resultado, mensagem e logs (expansivel)
- Botao "Disparar para WhatsApp": envia a mensagem do preview (com confirmacao + countdown 10s)
- Edicao de tenant carrega credenciais descriptografadas via `/detalhe`
- Token Quepasa e URL ja preenchidos automaticamente no cadastro
- Modo suave (noturno leve): toggle lua/sol no nav, persiste em localStorage
- Animacoes fade-in nas transicoes de aba (Teste/Logs/Historico)

---

## ⚠️ AGUARDANDO VALIDAÇÃO DO CHEFE (10/04/2026)

A remocao do `mes_referente` no `buscar_boletos_mes()` multiplicou os numeros do
relatorio em ~11x (Atomos dev: R$ 99k → R$ 1.09M aberto). A mudanca esta baseada
na analise do arquivo `Modelo - APV.xlsx` (export da Hinova enviado pelo chefe).

**SE o chefe validar que os novos numeros NAO batem com o que ele espera,
reverter o commit `ec7d9ca`** — voltando a usar `mes_referente` e a logica de
paginacao antiga. Arquivo afetado: `src/hinova/client.py` (`buscar_boletos_mes`
e `_buscar_boletos_periodo`).

Comando: `git revert ec7d9ca`

---

## 6. Estado atual (atualizado em 10/04/2026 — tarde)

### Tudo integrado e funcionando
- Backend: 36/36 testes passando
- Frontend React conectado ao backend (CRUD + testar + disparar + historico)
- Tenants "Atomos dev" e "Atomos - Miriam" cadastrados e testados com dados reais
- Relatorios enviados e recebidos no WhatsApp com sucesso
- Scheduler configurado para 19:00
- Paginacao Hinova corrigida duas vezes: (1) indice de pagina (nao offset), (2) parar por num_paginas (nao por page_size)
- Boletos do mes: sem `mes_referente` — pega TODOS que vencem em abril (~10x mais que antes, numeros agora batem com o Hinova real)
- Boletos do dia: pagos hoje + abertos com vencimento <= hoje (acumulado do mes ate hoje)
- Historico de testes com sub-abas (Mensagem/Logs) e visao expandida
- Modo suave (noturno leve) com toggle no nav — persiste em localStorage
- Mensagem de erro clara quando tenta disparar para tenant inativo

### Endpoints da API
- `GET /tenants/` — listar tenants
- `POST /tenants/` — criar tenant
- `PUT /tenants/{id}` — atualizar tenant
- `DELETE /tenants/{id}` — remover tenant
- `GET /tenants/{id}/detalhe` — dados completos com credenciais (para edicao)
- `POST /tenants/{id}/testar` — testar pipeline (sem enviar)
- `POST /tenants/{id}/disparar` — enviar mensagem ao WhatsApp
- `GET /tenants/{id}/historico` — ultimos 5 testes do tenant
- `GET /tenants/{id}/status` — status do ultimo envio

---

## 7. Melhorias futuras

### Prioridade media
- [ ] Salvar ultimo relatorio no banco para exibir no frontend
- [x] Avaliar boletos do dia (emitidos vs vencendo) — implementado (abertos com venc<=hoje + pagos hoje)
- [x] Historico de relatorios enviados — implementado (tabela test_history + aba no frontend)

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
