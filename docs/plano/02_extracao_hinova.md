# Etapa 2 — Extração de Dados (Hinova)

## Requisitos cobertos

- **RF03** — Coleta de Ativos (veículos com status ativo)
- **RF04** — Relatório de Vendas (veículos cadastrados no dia)
- **RF05** — Monitoramento de Cancelamentos (status alterado para "Cancelado" no dia)
- **RF06** — Resumo Financeiro (boletos do mês: abertos vs. baixados)

## Dependência

- **Etapa 1 concluída** — precisa do token Hinova armazenado no tenant

## O que será construído

### 2.1 — Cliente HTTP da Hinova

Um módulo que encapsula todas as chamadas à API Hinova:

| Função                  | Endpoint Hinova       | Retorno                         |
|-------------------------|-----------------------|---------------------------------|
| buscar_ativos()         | GET /veiculos         | Total de veículos ativos        |
| buscar_vendas_dia()     | GET /veiculos         | Veículos cadastrados hoje       |
| buscar_cancelamentos()  | GET /alteracoes       | Cancelamentos do dia            |
| buscar_boletos_mes()    | GET /financeiro       | Boletos do mês corrente         |

### 2.2 — Tratamento de erros (RNF04)

- Se a Hinova retornar erro (4xx, 5xx), registrar log detalhado
- Não interromper o fluxo — tentar buscar os outros dados mesmo se um falhar

### 2.3 — Arquivos que serão criados

```
src/hinova/
├── client.py       # Classe HinovaClient com as 4 chamadas
└── schemas.py      # Tipagem dos dados retornados pela Hinova
```

## Processos de implementação

1. Estudar documentação da API Hinova (endpoints, headers, paginação)
2. Criar HinovaClient com autenticação via token do tenant
3. Implementar cada uma das 4 funções de busca
4. Adicionar logging de erros (RNF04)
5. Testar com token real

## Critério de conclusão

- Consigo buscar ativos, vendas, cancelamentos e boletos de um tenant
- Erros da API são logados sem quebrar a aplicação
