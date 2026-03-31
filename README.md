# API Busca Lucas

Sistema que envia automaticamente um relatório diário via WhatsApp com dados de locadoras extraídos da API Hinova.

## O que é?

Todo dia às 16:30, cada empresa cadastrada recebe no WhatsApp uma mensagem assim:

```
📊 Relatório Diário - Locadora ABC

🚗 Ativos Totais: 7,630
✅ Vendas hoje: 27
❌ Cancelados hoje: 675

💰 Financeiro Mensal:
  • Aberto: R$ 12.000,00
  • Pago: R$ 5.327,50 (30.75%)
```

## Como funciona?

```
Agendador (16:30) → Hinova (busca dados) → Calculadora (faz as contas) → WhatsApp (envia)
```

O sistema busca na Hinova: veículos ativos, vendas do dia, cancelamentos e boletos do mês. Calcula os totais e envia o relatório formatado pelo Quepasa (WhatsApp).

Suporta múltiplas empresas — cada uma com suas credenciais isoladas e criptografadas.

## Como instalar

### 1. Clonar e configurar o projeto

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
# Instalar Docker (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
# Sair e entrar novamente no terminal para aplicar permissão

# Subir o Quepasa
cd quepasa
docker compose up -d
```

Acesse **http://localhost:31000**, faça login e escaneie o QR Code com seu WhatsApp para conectar.

**Credenciais padrão do Quepasa:**
- Email: `admin@quepasa.io`
- Senha: `admin123`

Depois de escanear, copie o **token do bot** gerado.

### 3. Iniciar a API

```bash
cd API_BUSCA_LUCAS
source venv/bin/activate
uvicorn src.main:app --reload
```

Acesse **http://localhost:8000** para abrir o painel de gestão.

### 4. Cadastrar uma empresa

No painel (http://localhost:8000), clique em **"+ Novo Cliente"** e preencha:

| Campo | O que colocar |
|-------|---------------|
| Nome | Nome da empresa |
| Token API Hinova | Token gerado no SGA Hinova |
| Usuário SGA | Usuário de integração Hinova |
| Senha SGA | Senha de integração Hinova |
| Token Quepasa | Token do bot (copiado no passo 2) |
| URL Base Quepasa | `http://localhost:31000` |
| WhatsApp Destino | Número sem nono dígito (ex: `558799514353`) |

**Importante:** o número do WhatsApp deve ser sem o nono dígito. Exemplo: `+55 87 9 9951-4353` vira `558799514353`.

### 5. Testar o envio

```bash
source venv/bin/activate
python3 -c "from src.scheduler.job import run_daily_report; run_daily_report()"
```

Se tudo estiver certo, o relatório chega no WhatsApp em alguns segundos.

### 6. Agendar envio automático

```bash
# Opção A: Rodar o scheduler (fica executando)
python -m src.scheduler.job
# Envia todo dia às 16:30 automaticamente

# Opção B: Crontab (produção)
crontab -e
# Adicionar a linha:
30 16 * * * cd /caminho/do/projeto && /caminho/do/venv/bin/python -m src.scheduler.job
```

## Testes

```bash
python3 -m pytest tests/ -v
# 32 testes passando
```

## Tecnologias

Python 3.12, FastAPI, SQLite, SQLAlchemy, Pydantic, APScheduler, Cryptography (Fernet), Docker, Quepasa.
