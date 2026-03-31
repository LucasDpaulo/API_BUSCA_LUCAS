"""Testes do pipeline de automação (Etapa 5)."""

from unittest.mock import patch, MagicMock
from datetime import datetime

from src.scheduler.job import _processar_tenant, run_daily_report


def _mock_tenant(nome="Locadora Teste", ativo=True):
    """Cria um tenant mock para testes."""
    tenant = MagicMock()
    tenant.id = "abc-123"
    tenant.nome = nome
    tenant.ativo = ativo
    tenant.hinova_usuario = "user"
    tenant.whatsapp_destino = "5531999999999"
    tenant.get_hinova_token.return_value = "token_hinova"
    tenant.get_hinova_senha.return_value = "senha_hinova"
    tenant.get_quepasa_token.return_value = "token_quepasa"
    return tenant


@patch("src.scheduler.job.enviar_relatorio", return_value=True)
@patch("src.scheduler.job.HinovaClient")
def test_processar_tenant_sucesso(mock_hinova_cls, mock_enviar):
    """Pipeline completo deve funcionar para um tenant."""
    mock_hinova = MagicMock()
    mock_hinova.autenticar.return_value = True
    mock_hinova.buscar_ativos.return_value = 100
    mock_hinova.buscar_vendas_dia.return_value = 5
    mock_hinova.buscar_cancelamentos_dia.return_value = 1
    mock_hinova.buscar_boletos_mes.return_value = [
        {"status_boleto": "Aberto", "valor_boleto": "1000.00"},
        {"status_boleto": "Baixado", "valor_boleto": "500.00"},
    ]
    mock_hinova_cls.return_value = mock_hinova

    db = MagicMock()
    tenant = _mock_tenant()

    resultado = _processar_tenant(db, tenant)

    assert resultado is True
    mock_hinova.autenticar.assert_called_once()
    mock_enviar.assert_called_once()
    # Verifica que a mensagem contém o nome da empresa
    msg_enviada = mock_enviar.call_args[0][3]
    assert "Locadora Teste" in msg_enviada


@patch("src.scheduler.job.HinovaClient")
def test_processar_tenant_falha_autenticacao(mock_hinova_cls):
    """Se a autenticação Hinova falhar, deve retornar False."""
    mock_hinova = MagicMock()
    mock_hinova.autenticar.return_value = False
    mock_hinova_cls.return_value = mock_hinova

    db = MagicMock()
    tenant = _mock_tenant()

    resultado = _processar_tenant(db, tenant)

    assert resultado is False


@patch("src.scheduler.job.enviar_relatorio", return_value=False)
@patch("src.scheduler.job.HinovaClient")
def test_processar_tenant_falha_envio(mock_hinova_cls, mock_enviar):
    """Se o envio Quepasa falhar, deve retornar False."""
    mock_hinova = MagicMock()
    mock_hinova.autenticar.return_value = True
    mock_hinova.buscar_ativos.return_value = 50
    mock_hinova.buscar_vendas_dia.return_value = 0
    mock_hinova.buscar_cancelamentos_dia.return_value = 0
    mock_hinova.buscar_boletos_mes.return_value = []
    mock_hinova_cls.return_value = mock_hinova

    db = MagicMock()
    tenant = _mock_tenant()

    resultado = _processar_tenant(db, tenant)

    assert resultado is False


@patch("src.scheduler.job._processar_tenant")
@patch("src.scheduler.job.SessionLocal")
def test_run_daily_report_multiplos_tenants(mock_session_cls, mock_processar):
    """Deve processar todos os tenants ativos."""
    tenant1 = _mock_tenant("Empresa A")
    tenant2 = _mock_tenant("Empresa B")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [tenant1, tenant2]
    mock_session_cls.return_value = mock_db

    mock_processar.return_value = True

    run_daily_report()

    assert mock_processar.call_count == 2


@patch("src.scheduler.job._processar_tenant")
@patch("src.scheduler.job.SessionLocal")
def test_run_daily_report_erro_nao_para_outros(mock_session_cls, mock_processar):
    """Erro em um tenant NÃO deve impedir o processamento dos outros."""
    tenant1 = _mock_tenant("Empresa Falha")
    tenant2 = _mock_tenant("Empresa OK")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [tenant1, tenant2]
    mock_session_cls.return_value = mock_db

    # Primeiro tenant lança exceção, segundo funciona
    mock_processar.side_effect = [Exception("Erro inesperado"), True]

    run_daily_report()

    # Os dois devem ter sido chamados
    assert mock_processar.call_count == 2


@patch("src.scheduler.job.SessionLocal")
def test_run_daily_report_sem_tenants(mock_session_cls):
    """Se não há tenants ativos, deve sair sem erro."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_session_cls.return_value = mock_db

    run_daily_report()  # Não deve lançar exceção
