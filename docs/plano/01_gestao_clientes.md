# Etapa 1 — Gestão de Clientes (SaaS Simplificado)

## Requisitos cobertos

- **RF01** — Cadastro de Tenant (ID único por empresa)
- **RF02** — Configuração de Credenciais (tokens Hinova, Quepasa, número WhatsApp)
- **RNF01** — Isolamento de Credenciais (um cliente nunca acessa tokens de outro)
- **RNF03** — Interface minimalista (configurar tokens + ver status do último envio)

## O que será construído

### 1.1 — Modelo de dados (Tenant)

Tabela `tenants` no SQLite:

| Campo              | Tipo     | Descrição                              |
|--------------------|----------|----------------------------------------|
| id                 | UUID     | Identificador único da empresa         |
| nome               | TEXT     | Nome da empresa                        |
| hinova_token       | TEXT     | Token de acesso à API Hinova           |
| quepasa_token      | TEXT     | Token de acesso à API Quepasa          |
| whatsapp_destino   | TEXT     | Número WhatsApp para receber relatório |
| ativo              | BOOLEAN  | Se o tenant está ativo                 |
| ultimo_envio       | DATETIME | Data/hora do último relatório enviado  |
| ultimo_status      | TEXT     | Status do último envio (sucesso/erro)  |
| criado_em          | DATETIME | Data de criação                        |

### 1.2 — Endpoints da API REST

| Método | Rota                  | Ação                                    |
|--------|-----------------------|-----------------------------------------|
| POST   | /tenants              | Cadastrar nova empresa                  |
| GET    | /tenants              | Listar todas as empresas                |
| GET    | /tenants/{id}         | Ver detalhes de uma empresa             |
| PUT    | /tenants/{id}         | Atualizar credenciais                   |
| DELETE | /tenants/{id}         | Remover empresa                         |
| GET    | /tenants/{id}/status  | Ver status do último envio (RNF03)      |

### 1.3 — Segurança (RNF01)

- Cada operação filtra pelo `tenant_id` — impossível acessar dados de outro tenant
- Tokens armazenados no banco (futuro: criptografia com Fernet)
- `.env` guarda apenas config do sistema, não credenciais de clientes

### 1.4 — Arquivos que serão criados

```
src/
├── models/
│   └── tenant.py          # Modelo SQLAlchemy do Tenant
├── routes/
│   └── tenant_routes.py   # Endpoints FastAPI
├── database.py            # Conexão e setup do SQLite
└── main.py                # Entrypoint da aplicação FastAPI
```

## Processos de implementação

1. Configurar FastAPI + SQLAlchemy + SQLite
2. Criar modelo Tenant com todos os campos
3. Criar endpoints CRUD
4. Adicionar validação (Pydantic schemas)
5. Testar via Swagger (FastAPI gera automaticamente em /docs)

## Critério de conclusão

- Consigo cadastrar um tenant via POST /tenants
- Consigo atualizar credenciais via PUT /tenants/{id}
- Consigo ver o status do último envio via GET /tenants/{id}/status
- Um tenant não consegue ver dados de outro
