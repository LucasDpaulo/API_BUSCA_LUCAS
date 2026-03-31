# Etapa 4 — Entrega (Quepasa)

## Requisitos cobertos

- **RF07** — Formatação de Mensagem (emojis, quebras de linha)
- **RF08** — Disparo via Quepasa (POST para o número configurado)
- **RNF04** — Tratamento de erros (log se Quepasa falhar)

## Dependência

- **Etapa 3 concluída** — precisa das métricas calculadas
- **Token Quepasa e número WhatsApp** do tenant (Etapa 1)

## O que será construído

### 4.1 — Formatador de mensagem (RF07)

Transforma as métricas em texto amigável:

```
📊 Relatório Diário - [Nome da Empresa]

🚗 Ativos Totais: 1.250
✅ Vendas hoje: 05
❌ Cancelados hoje: 02

💰 Financeiro Mensal:
  • Aberto: R$ 50.000,00
  • Pago: R$ 35.000,00 (70%)
```

### 4.2 — Cliente Quepasa (RF08)

- POST para o endpoint de envio de mensagem
- Autenticação com token do tenant
- Retry simples em caso de falha temporária

### 4.3 — Atualização de status do tenant

Após o envio, atualizar na tabela `tenants`:
- `ultimo_envio` = agora
- `ultimo_status` = "sucesso" ou "erro: [motivo]"

Isso alimenta o endpoint GET /tenants/{id}/status (RNF03).

### 4.4 — Arquivos que serão criados

```
src/quepasa/
├── client.py       # Classe QuepasaClient (envio de mensagem)
└── formatter.py    # Função que monta o texto do relatório
```

## Processos de implementação

1. Estudar documentação da API Quepasa (endpoint de envio, formato do body)
2. Criar formatador de mensagem com template
3. Criar QuepasaClient com autenticação via token do tenant
4. Implementar atualização de status no banco após envio
5. Adicionar logging de erros (RNF04)
6. Testar envio real para um número de teste

## Critério de conclusão

- Métricas entram → mensagem formatada sai no WhatsApp
- Status do envio é salvo no tenant
- Erros são logados sem quebrar a aplicação
