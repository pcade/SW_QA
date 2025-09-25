#!/usr/bin/python3
# ============================================================================
# Название: test_websocket_client_integration.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Интеграционные тесты для websocket_client.py с реальным сервером
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import pytest
import time
import os
from src.websocket_client import WebsocketClient


# ============================================================================
# Объявление переменных для тестирования
# ============================================================================
URL = "ws://localhost:8765"
TIMEOUT = 0.1
RESULT_GET_V = "V_12V"
RESULT_GET_A = "A_5A"
RESULT_GET_S = "S_ABC123"


class TestWebsocketClientIntegration:
    """
    Интеграционные тесты для класса WebsocketClient с реальным сервером
    """
    @pytest.fixture
    def server_url(self):
        return os.getenv('WEBSOCKET_SERVER_URL', URL)

    def test_connection_establishment(self, server_url):
        """
        Тест установки соединения
        """
        client = WebsocketClient(server_url)
        assert client.ws is not None
        assert client.ws.connected is True
        client.close()

    def test_get_voltage_integration(self, server_url):
        """
        Интеграционный тест получения напряжения
        """
        client = WebsocketClient(server_url)
        voltage = client.get_voltage()

        assert voltage == RESULT_GET_V

        client.close()

    def test_get_ampere_integration(self, server_url):
        """
        Интеграционный тест получения силы тока
        """
        client = WebsocketClient(server_url)
        ampere = client.get_ampere()

        assert ampere == RESULT_GET_A

        client.close()

    def test_get_serial_integration(self, server_url):
        """
        Интеграционный тест получения серийного номера
        """
        client = WebsocketClient(server_url)
        serial = client.get_serial()

        assert serial == RESULT_GET_S

        client.close()

    def test_sequential_commands(self, server_url):
        """
        Тест последовательного выполнения команд
        """
        client = WebsocketClient(server_url)

        results = []
        results.append(client.get_voltage())
        time.sleep(TIMEOUT)
        results.append(client.get_ampere())
        time.sleep(TIMEOUT)
        results.append(client.get_serial())

        assert results[0] == RESULT_GET_V
        assert results[1] == RESULT_GET_A
        assert results[2] == RESULT_GET_S

        client.close()

    def test_context_manager(self, server_url):
        """
        Тест работы контекстного менеджера
        """
        with WebsocketClient(server_url) as client:
            voltage = client.get_voltage()
            assert voltage == RESULT_GET_V

        assert client.ws is None

    def test_reconnection(self, server_url):
        """
        Тест переподключения
        """
        client = WebsocketClient(server_url)
        original_ws = client.ws

        client.close()
        client.open()

        assert client.ws is not None
        assert client.ws != original_ws

        voltage = client.get_voltage()
        assert voltage == RESULT_GET_V

        client.close()
