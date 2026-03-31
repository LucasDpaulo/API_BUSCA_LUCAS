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

    def _headers(self) -> dict[str, str]:
        """Headers padrão com autenticação."""
        token = self.token_usuario or self.token_api
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def _post(self, endpoint: str, payload: dict) -> dict | list | None:
        """Faz POST e retorna o JSON, logando erros (RNF04)."""
        url = f"{BASE_URL}/{endpoint}"
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error("Erro ao chamar %s: %s", url, e)
            return None

    def _get(self, endpoint: str) -> dict | list | None:
        """Faz GET e retorna o JSON, logando erros (RNF04)."""
        url = f"{BASE_URL}/{endpoint}"
        try:
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

    # ── RF03: Coleta de Ativos ────────────────────────────────────

    def buscar_ativos(self) -> int:
        """Retorna o total de veículos com status ativo."""
        # Primeiro descobre o código de situação "ativo"
        situacoes = self._get("listar/situacao/ativo")
        if not situacoes:
            return 0

        # Pode retornar uma lista ou um dict
        if isinstance(situacoes, list):
            codigo_ativo = str(situacoes[0].get("codigo_situacao", "1"))
        else:
            codigo_ativo = str(situacoes.get("codigo_situacao", "1"))

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
        """Retorna o total de veículos cancelados no dia (alterações de status)."""
        dia = dia or date.today()
        dia_str = dia.strftime("%d/%m/%Y")

        payload = {
            "data_inicial": dia_str,
            "data_final": dia_str,
            "ultima_alteracao": "Y",
            "campos": ["codigo_situacao"],
        }
        data = self._post("listar/alteracao-veiculos", payload)
        if not data or not isinstance(data, list):
            return 0

        # Filtra apenas alterações onde o valor_posterior indica cancelamento
        # O campo nome_campo_tabela == "codigo_situacao" e valor_posterior != valor ativo
        cancelamentos = [
            alt for alt in data
            if alt.get("nome_campo_tabela") == "codigo_situacao"
            and self._eh_cancelamento(alt.get("valor_posterior", ""))
        ]
        total = len(cancelamentos)
        logger.info("Cancelamentos do dia %s: %d", dia_str, total)
        return total

    @staticmethod
    def _eh_cancelamento(valor_posterior: str) -> bool:
        """Verifica se o valor_posterior indica cancelamento.

        Pela convenção Hinova, situações de cancelamento geralmente têm
        descrição contendo 'CANCEL'. Aqui verificamos pelo código.
        Ajustar conforme os códigos reais do cliente.
        """
        # TODO: mapear códigos reais de cancelamento do cliente
        # Por enquanto, qualquer alteração de codigo_situacao é contada
        # Em produção, filtrar apenas os códigos de cancelamento
        return True

    # ── RF06: Resumo Financeiro (Boletos do Mês) ──────────────────

    def buscar_boletos_mes(
        self, ano: int | None = None, mes: int | None = None
    ) -> list[dict]:
        """Retorna a lista de boletos do mês (RN01: dia 01 até último dia)."""
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month

        import calendar
        ultimo_dia = calendar.monthrange(ano, mes)[1]

        data_ini = f"01/{mes:02d}/{ano}"
        data_fim = f"{ultimo_dia:02d}/{mes:02d}/{ano}"

        todos_boletos: list[dict] = []
        pagina = 0
        page_size = 100

        while True:
            payload = {
                "data_inicial": data_ini,
                "data_final": data_fim,
                "quantidade_por_pagina": page_size,
                "inicio_paginacao": pagina,
            }
            data = self._post("listar/boleto", payload)
            if not data:
                break

            boletos = data if isinstance(data, list) else data.get("boletos", [])
            if not boletos:
                break

            todos_boletos.extend(boletos)
            break  # Por enquanto busca apenas a primeira página

        logger.info(
            "Boletos do mês %02d/%d: %d encontrados", mes, ano, len(todos_boletos)
        )
        return todos_boletos
