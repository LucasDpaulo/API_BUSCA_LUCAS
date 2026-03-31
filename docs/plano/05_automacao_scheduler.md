# Etapa 5 — Automação (Scheduler)

## Requisitos cobertos

- **RNF02** — Execução automática diária às 19:00

## Dependência

- **Etapas 1 a 4 concluídas** — o pipeline completo precisa funcionar

## O que será construído

### 5.1 — Pipeline completo

Uma função que executa o fluxo inteiro para TODOS os tenants ativos:

```
Para cada tenant ativo:
  1. Buscar credenciais do tenant (Etapa 1)
  2. Fetch dados Hinova com o token do tenant (Etapa 2)
  3. Calcular métricas (Etapa 3)
  4. Formatar e enviar via Quepasa (Etapa 4)
  5. Atualizar status do tenant
```

### 5.2 — Agendamento

Duas opções (ambas serão implementadas):

**Opção A — Cron do sistema (produção):**
```
0 19 * * * cd /caminho/projeto && python -m src.scheduler.job
```

**Opção B — APScheduler (desenvolvimento):**
```python
scheduler.add_job(run_pipeline, "cron", hour=19, minute=0)
```

### 5.3 — Arquivos que serão atualizados

```
src/scheduler/
└── job.py          # Pipeline completo + agendamento
```

## Processos de implementação

1. Criar função pipeline que orquestra todas as etapas
2. Iterar sobre todos os tenants ativos
3. Tratar erros por tenant (um tenant falhando não impede os outros)
4. Configurar agendamento via APScheduler
5. Documentar configuração via crontab para produção
6. Teste end-to-end completo

## Critério de conclusão

- Às 19:00, o sistema roda sozinho para todos os tenants
- Se um tenant falha, os outros continuam normalmente
- Logs registram sucesso/erro de cada tenant
