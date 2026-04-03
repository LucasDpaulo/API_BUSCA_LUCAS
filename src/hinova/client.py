"""Cliente HTTP para a API SGA Hinova (RF03, RF04, RF05, RF06)."""

import logging
from datetime import date, datetime

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.hinova.com.br/api/sga/v2"


class HinovaClient:
    """Encapsula todas as chamadas à API Hinova para um tenant."""

    def __init__(self, token_api: str, usuario: str, senha: str) -> None:
        self.token_api = token_api
        self.usuario = usuario
        self.senha = senha
        self.token_usuario: str | None = None
        self._situacoes_cache: list[dict] | None = None

    def _headers(self) -> dict[str, str]:
        """Headers padrão com autenticação."""
        token = self.token_usuario or self.token_api
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def _post(self, endpoint: str, payload: dict) -> dict | list | None:
        """Faz POST e retorna o JSON. Re-autentica em caso de 401."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=120)
            if resp.status_code == 401 and "autenticar" not in endpoint:
                logger.warning("Token expirado, re-autenticando...")
                if self.autenticar():
                    resp = requests.post(url, json=payload, headers=self._headers(), timeout=120)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Erro ao chamar %s: %s", url, e)
            return None

    def _get(self, endpoint: str) -> dict | list | None:
        """Faz GET e retorna o JSON. Re-autentica em caso de 401."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=60)
            if resp.status_code == 401:
                logger.warning("Token expirado, re-autenticando...")
                if self.autenticar():
                    resp = requests.get(url, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Erro ao chamar %s: %s", url, e)
            return None

    # ── Autenticação ──────────────────────────────────────────────

    def autenticar(self) -> bool:
        """Autentica o usuário e obtém o token_usuario. Retorna True se OK."""
        payload = {"usuario": self.usuario, "senha": self.senha}
        data = self._post("usuario/autenticar", payload)
        if data and data.get("mensagem") == "OK":
            self.token_usuario = data["token_usuario"]
            logger.info("Autenticação Hinova OK.")
            return True
        logger.error("Falha na autenticação Hinova: %s", data)
        return False

    # ── Situações (cache para reuso) ─────────────────────────────

    def _buscar_situacoes(self) -> list[dict]:
        """Busca e cacheia todas as situações de veículo/associado.

        Endpoint: GET listar/situacao/:situacao
        Retorna lista com codigo_situacao e descricao_situacao.
        """
        if self._situacoes_cache is not None:
            return self._situacoes_cache

        data = self._get("listar/situacao/todos")
        if not data:
            self._situacoes_cache = []
            return []

        if isinstance(data, dict):
            data = [data]

        self._situacoes_cache = data
        logger.info(
            "Situações carregadas: %s",
            [(s.get("codigo_situacao"), s.get("descricao_situacao")) for s in data],
        )
        return data

    def _codigos_por_descricao(self, *termos: str) -> set[str]:
        """Retorna códigos de situação cujas descrições contêm algum dos termos.

        Busca case-insensitive.
        """
        situacoes = self._buscar_situacoes()
        codigos = set()
        for sit in situacoes:
            desc = (sit.get("descricao_situacao") or "").upper()
            for termo in termos:
                if termo.upper() in desc:
                    codigos.add(str(sit.get("codigo_situacao", "")))
                    break
        return codigos

    # ── RF03: Coleta de Ativos ────────────────────────────────────

    def buscar_ativos(self) -> int:
        """Retorna o total de veículos com status ativo."""
        situacoes = self._buscar_situacoes()

        # Busca o código da situação "ATIVO"
        codigo_ativo = None
        for sit in situacoes:
            desc = (sit.get("descricao_situacao") or "").upper()
            if desc == "ATIVO":
                codigo_ativo = str(sit.get("codigo_situacao", "1"))
                break

        if not codigo_ativo:
            # Fallback: tenta o endpoint específico
            data_sit = self._get("listar/situacao/ativo")
            if data_sit:
                if isinstance(data_sit, list):
                    codigo_ativo = str(data_sit[0].get("codigo_situacao", "1"))
                else:
                    codigo_ativo = str(data_sit.get("codigo_situacao", "1"))
            else:
                codigo_ativo = "1"

        payload = {
            "codigo_situacao": codigo_ativo,
            "quantidade_por_pagina": 1,
            "inicio_paginacao": 0,
        }
        data = self._post("listar/veiculo", payload)
        if data and "total_veiculos" in data:
            total = int(data["total_veiculos"])
            logger.info("Total de veículos ativos: %d", total)
            return total
        return 0

    # ── RF04: Relatório de Vendas do Dia ──────────────────────────

    def buscar_vendas_dia(self, dia: date | None = None) -> int:
        """Retorna o total de veículos cadastrados na data informada (hoje por padrão)."""
        dia = dia or date.today()
        dia_str = dia.strftime("%Y-%m-%d")

        payload = {
            "data_cadastro": dia_str,
            "data_cadastro_final": dia_str,
            "quantidade_por_pagina": 1,
            "inicio_paginacao": 0,
        }
        data = self._post("listar/veiculo", payload)
        if data and "total_veiculos" in data:
            total = int(data["total_veiculos"])
            logger.info("Vendas do dia %s: %d", dia_str, total)
            return total
        return 0

    # ── RF05: Monitoramento de Cancelamentos ──────────────────────

    def buscar_cancelamentos_dia(self, dia: date | None = None) -> int:
        """Retorna o total de veículos cancelados no dia (alterações de status).

        Usa o endpoint listar/alteracao-veiculos filtrando apenas alterações
        de codigo_situacao cujo valor_posterior corresponde a uma situação
        de cancelamento (descrição contendo CANCEL, EXCLU ou INATIV).
        """
        dia = dia or date.today()
        dia_str = dia.strftime("%d/%m/%Y")

        # Primeiro carrega os códigos de cancelamento
        codigos_cancelamento = self._codigos_por_descricao(
            "CANCEL", "EXCLU", "INATIV",
        )
        logger.info("Códigos de cancelamento identificados: %s", codigos_cancelamento)

        if not codigos_cancelamento:
            logger.warning(
                "Nenhuma situação de cancelamento encontrada nas situações da Hinova. "
                "Verifique as descrições de situação no SGA."
            )
            return 0

        payload = {
            "data_inicial": dia_str,
            "data_final": dia_str,
            "ultima_alteracao": "Y",
            "campos": ["codigo_situacao"],
        }
        data = self._post("listar/alteracao-veiculos", payload)
        if not data or not isinstance(data, list):
            return 0

        # Filtra apenas alterações onde:
        # 1. O campo alterado é codigo_situacao
        # 2. O valor_posterior é um código de cancelamento
        cancelamentos = [
            alt for alt in data
            if alt.get("nome_campo_tabela") == "codigo_situacao"
            and str(alt.get("valor_posterior", "")) in codigos_cancelamento
        ]
        total = len(cancelamentos)
        logger.info(
            "Cancelamentos do dia %s: %d (de %d alterações de situação)",
            dia_str, total, len(data),
        )
        return total

    # ── RF06: Resumo Financeiro (Boletos) ───────────────────────────

    def _buscar_boletos_periodo(
        self, mes_ref: str | None, data_ini: str, data_fim: str,
    ) -> list[dict]:
        """Busca boletos de um período com paginação completa."""
        todos: list[dict] = []
        pagina = 0
        page_size = 100
        max_paginas = 50

        while pagina < max_paginas:
            payload = {
                "data_vencimento_inicial": data_ini,
                "data_vencimento_final": data_fim,
                "quantidade_por_pagina": page_size,
                "inicio_paginacao": pagina,
            }
            if mes_ref:
                payload["mes_referente"] = mes_ref
            data = self._post("listar/boleto-associado/periodo", payload)
            if not data:
                break

            if isinstance(data, list):
                boletos = data
            elif isinstance(data, dict):
                boletos = data.get("boletos", [])
                if not boletos and "valor_boleto" in data:
                    boletos = [data]
            else:
                break

            if not boletos:
                break

            todos.extend(boletos)

            if len(boletos) < page_size:
                break

            pagina += 1

        return todos

    def buscar_boletos_dia(self, dia: date | None = None) -> list[dict]:
        """Retorna a lista de boletos do dia, com paginação completa."""
        dia = dia or date.today()
        dia_str = dia.strftime("%d/%m/%Y")

        # Não envia mes_referente — a API rejeita (406) quando combinado
        # com filtro de um único dia.
        boletos = self._buscar_boletos_periodo(None, dia_str, dia_str)
        logger.info("Boletos do dia %s: %d encontrados", dia_str, len(boletos))
        return boletos

    def buscar_boletos_mes(
        self, ano: int | None = None, mes: int | None = None,
    ) -> list[dict]:
        """Retorna a lista de boletos do mês corrente (dia 01 até último dia)."""
        import calendar

        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month

        mes_ref = f"{mes:02d}/{ano}"
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        data_ini = f"01/{mes:02d}/{ano}"
        data_fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"

        boletos = self._buscar_boletos_periodo(mes_ref, data_ini, data_fim)
        logger.info("Boletos do mês %s: %d encontrados", mes_ref, len(boletos))
        return boletos

    @staticmethod
    def _status_boleto_upper(boleto: dict) -> str:
        """Extrai e normaliza o status de um boleto."""
        return (
            boleto.get("descricao_situacao_boleto")
            or boleto.get("situacao_boleto")
            or boleto.get("situacao")
            or boleto.get("descricao_situacao")
            or boleto.get("status_boleto")
            or boleto.get("status")
            or ""
        ).strip().upper()
