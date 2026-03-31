# Diretrizes do Projeto — API_BUSCA_LUCAS

## 1. Padrão de Código

- **Linguagem:** Python 3.11+
- **Style Guide:** PEP 8
- **Tipagem:** Estática com `typing` (type hints obrigatórios em funções públicas)
- **Linter:** flake8 / ruff
- **Formatter:** black

## 2. Padrão de Commits

Usar prefixos semânticos (Conventional Commits):

| Prefixo    | Uso                                      |
|------------|------------------------------------------|
| `feat:`    | Nova funcionalidade                      |
| `fix:`     | Correção de bug                          |
| `docs:`    | Alteração em documentação                |
| `refactor:`| Refatoração sem mudança de comportamento |
| `test:`    | Adição ou correção de testes             |
| `chore:`   | Tarefas de manutenção (deps, CI, etc.)   |

Exemplo: `feat: adicionar coleta de veículos ativos via Hinova`

## 3. Arquitetura

O sistema é dividido em **3 módulos isolados + 1 agendador**:

```
src/
├── hinova/       # [B] Extração de dados — chamadas GET à API Hinova
├── quepasa/      # [C] Entrega — formatação e envio via WhatsApp
├── core/         # Cálculos financeiros, regras de negócio (RN01)
└── scheduler/    # Agendamento (Cron Job) — RNF02
```

### Fluxo de Dados

1. **Trigger** — Cron Job dispara o script às 19:00 (RNF02)
2. **Auth** — Recupera credenciais isoladas por tenant (RNF01)
3. **Fetch** — GET Hinova: Veículos, Alterações, Financeiro (RF03-RF06)
4. **Parse** — Cálculos de porcentagem, limpeza de dados (RN01)
5. **Dispatch** — POST Quepasa: mensagem formatada (RF07-RF08)

## 4. Segurança e Credenciais (RNF01)

- **NUNCA** versionar tokens ou senhas no repositório
- Credenciais ficam em variáveis de ambiente ou arquivo `.env`
- O `.env` está no `.gitignore`
- Cada tenant possui suas próprias credenciais isoladas

## 5. Regra de Negócio (RN01)

O cálculo de boletos "do mês" deve sempre considerar do **dia 01 até o último dia do mês corrente**, independente do dia em que o relatório é gerado.
