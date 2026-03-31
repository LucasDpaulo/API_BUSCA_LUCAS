"""Testes do cliente Quepasa (Etapa 4 — RF08)."""

from unittest.mock import patch, MagicMock

import requests

from src.quepasa.client import QuepasaClient


def test_enviar_mensagem_sucesso():
    """Deve retornar True quando o POST retorna 200."""
    client = QuepasaClient("http://localhost:31000", "token_teste")

    with patch("src.quepasa.client.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        resultado = client.enviar_mensagem("5531999999999", "Olá!")

    assert resultado is True
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs[1]["json"]["chatid"] == "5531999999999"
    assert call_kwargs[1]["json"]["text"] == "Olá!"
    assert call_kwargs[1]["headers"]["X-QUEPASA-TOKEN"] == "token_teste"


def test_enviar_mensagem_falha_com_retry():
    """Deve tentar 2 vezes e retornar False se todas falharem."""
    client = QuepasaClient("http://localhost:31000", "token_teste")

    with patch("src.quepasa.client.requests.post") as mock_post:
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        resultado = client.enviar_mensagem("5531999999999", "Olá!")

    assert resultado is False
    assert mock_post.call_count == 2  # _MAX_RETRIES = 2


def test_enviar_mensagem_sucesso_na_segunda_tentativa():
    """Deve retornar True se a segunda tentativa funcionar."""
    client = QuepasaClient("http://localhost:31000", "token_teste")

    with patch("src.quepasa.client.requests.post") as mock_post:
        falha = requests.Timeout("Timeout")
        sucesso = MagicMock(status_code=200)
        sucesso.raise_for_status = MagicMock()
        mock_post.side_effect = [falha, sucesso]

        resultado = client.enviar_mensagem("5531999999999", "Olá!")

    assert resultado is True
    assert mock_post.call_count == 2


def test_headers_contem_token():
    """O header deve conter X-QUEPASA-TOKEN."""
    client = QuepasaClient("http://quepasa.example.com", "meu_token_123")
    headers = client._headers()

    assert headers["X-QUEPASA-TOKEN"] == "meu_token_123"
    assert headers["Content-Type"] == "application/json"


def test_url_montada_corretamente():
    """A URL deve ser base_url + /v4/send."""
    client = QuepasaClient("http://localhost:31000/", "tok")

    with patch("src.quepasa.client.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = MagicMock()

        client.enviar_mensagem("5531999999999", "teste")

    url_chamada = mock_post.call_args[0][0]
    assert url_chamada == "http://localhost:31000/v4/send"
