# Plano de Execução — API_BUSCA_LUCAS

## Objetivo Final

Um microserviço que, de forma automática e diária, coleta dados financeiros e operacionais
da API Hinova, processa os números e envia um relatório formatado via WhatsApp (Quepasa)
para cada empresa cadastrada. Simples para o cliente: cadastra, configura e recebe.

## Divisão em Etapas

O projeto foi dividido em **5 etapas sequenciais**. Cada etapa entrega algo funcional
e testável antes de avançar para a próxima.

| Etapa | Nome                        | O que entrega                                      | Requisitos   |
|-------|-----------------------------|----------------------------------------------------|--------------|
| 1     | Gestão de Clientes          | API para cadastrar empresas e suas credenciais     | RF01, RF02, RNF01, RNF03 |
| 2     | Extração de Dados (Hinova)  | Módulo que busca dados reais da API Hinova         | RF03, RF04, RF05, RF06 |
| 3     | Motor de Cálculo (Core)     | Processa os dados brutos e gera métricas           | RN01         |
| 4     | Entrega (Quepasa)           | Formata a mensagem e envia via WhatsApp            | RF07, RF08, RNF04 |
| 5     | Automação (Scheduler)       | Agendamento diário + pipeline completo             | RNF02        |

## Por que essa ordem?

1. **Etapa 1 primeiro** — É a fundação. Tudo depende de saber QUEM é o cliente e
   QUAIS credenciais usar. Sem isso, não dá pra chamar nenhuma API.

2. **Etapa 2 depois** — Com as credenciais do tenant, podemos buscar dados reais.
   Validamos se a integração com a Hinova funciona antes de construir qualquer lógica.

3. **Etapa 3 na sequência** — Os dados brutos precisam virar informação útil.
   Aqui entra a RN01 (cálculo do mês corrente completo).

4. **Etapa 4 em seguida** — Só faz sentido formatar e enviar quando temos dados
   processados. A mLocadora ABC
WhatsApp: 5531999999999 | Quepasa: http://localhost:31000

Nenhum envio realizado  ensagem do WhatsApp é o produto final visível ao cliente.

5. **Etapa 5 por último** — O scheduler amarra tudo. Só automatiza o que já funciona.

## Tecnologias Escolhidas

- **FastAPI** — Framework web leve e moderno para a API REST
- **SQLite** — Banco de dados simples, sem instalação, fácil de migrar depois
- **Requests** — Chamadas HTTP para Hinova e Quepasa
- **APScheduler** — Agendamento de tarefas em Python
- **python-dotenv** — Variáveis de ambiente seguras

### Por que FastAPI + SQLite?

- **FastAPI**: gera documentação automática (Swagger), é rápido, suporta tipagem nativa
- **SQLite**: zero configuração, arquivo único, perfeito para começar. Se crescer,
  migra para PostgreSQL trocando apenas a string de conexão
