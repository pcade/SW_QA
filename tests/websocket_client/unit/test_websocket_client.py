#!/usr/bin/python3
# ============================================================================
# Название: test_websocket_client.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Мок тесты для websocket_client.py
# Примечание: Используется unittest.mock для эмуляции поведения websocket
# ============================================================================

# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import pytest
import json
from unittest.mock import Mock, patch
from src.websocket_client import WebsocketClient


class TestWebsocketClient:
    """
    Тесты для класса WebsocketClient
    """
    @patch('src.websocket_client.websocket.create_connection')
    def test_various_voltage_formats(self, mock_create_connection):
        """
        Тест различных форматов напряжения
        """
        test_cases = [
            ({"cmd": "GET_V", "payload": "V_5V"}, True),      # Valid
            ({"cmd": "GET_V", "payload": "V_12V"}, True),     # Valid
            ({"cmd": "GET_V", "payload": "V_0V"}, True),      # Valid
            ({"cmd": "GET_V", "payload": "V_12.5V"}, False),  # Invalid
            ({"cmd": "GET_V", "payload": "V_12"}, False),     # Invalid
            ({"cmd": "GET_V", "payload": "VOLT_12V"}, False)  # Invalid
        ]

        for i, (response, should_be_valid) in enumerate(test_cases):
            mock_ws = Mock()
            mock_create_connection.return_value = mock_ws
            mock_ws.recv.return_value = json.dumps(response)

            client = WebsocketClient("ws://localhost:8765")

            if should_be_valid:
                result = client.get_voltage()
                assert result == response["payload"], f"Test case {i} failed"
            else:
                expected_msg = f"Invalid voltage response format: {response}"
                with pytest.raises(ValueError, match=expected_msg):
                    client.get_voltage()

    @patch('src.websocket_client.websocket.create_connection')
    def test_various_ampere_formats(self, mock_create_connection):
        """
        Тест различных форматов напряжения
        """
        test_cases = [
            ({"cmd": "GET_A", "payload": "A_5A"}, True),      # Valid
            ({"cmd": "GET_A", "payload": "A_12A"}, True),     # Valid
            ({"cmd": "GET_A", "payload": "A_0A"}, True),      # Valid
            ({"cmd": "GET_A", "payload": "A_12.5A"}, False),  # Invalid
            ({"cmd": "GET_A", "payload": "A_12"}, False),     # Invalid
            ({"cmd": "GET_A", "payload": "AOLT_12A"}, False)  # Invalid
        ]

        for i, (response, should_be_valid) in enumerate(test_cases):
            mock_ws = Mock()
            mock_create_connection.return_value = mock_ws
            mock_ws.recv.return_value = json.dumps(response)

            client = WebsocketClient("ws://localhost:8765")

            if should_be_valid:
                result = client.get_ampere()
                assert result == response["payload"], f"Test case {i} failed"
            else:
                expected_msg = f"Invalid ampere response format: {response}"
                with pytest.raises(ValueError, match=expected_msg):
                    client.get_ampere()

    @patch('src.websocket_client.websocket.create_connection')
    def test_various_serial_formats(self, mock_create_connection):
        """
        Тест различных форматов напряжения
        """
        test_cases = [
            ({"cmd": "GET_S", "payload": "S_ABC123"}, True),   # Valid
            ({"cmd": "GET_S", "payload": "S_123"}, True),      # Valid
            ({"cmd": "GET_S", "payload": "S_A"}, True),        # Valid
            ({"cmd": "GET_S", "payload": "S_AB@123"}, False),  # Invalid
            ({"cmd": "GET_S", "payload": "S_ab123"}, False),   # Invalid
            ({"cmd": "GET_S", "payload": "S_AB 123"}, False)   # Invalid
        ]

        for i, (response, should_be_valid) in enumerate(test_cases):
            mock_ws = Mock()
            mock_create_connection.return_value = mock_ws
            mock_ws.recv.return_value = json.dumps(response)

            client = WebsocketClient("ws://localhost:8765")

            if should_be_valid:
                result = client.get_serial()
                assert result == response["payload"], f"Test case {i} failed"
            else:
                expected_msg = f"Invalid serial response format: {response}"
                with pytest.raises(ValueError, match=expected_msg):
                    client.get_serial()

    @patch('src.websocket_client.websocket.create_connection')
    def test_send_command_general(self, mock_create_connection):
        """
        Тест общего метода отправки команды
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        client = WebsocketClient("ws://localhost:8765")

        # Проверяем, что при невалидной команде вызывается исключение
        with pytest.raises(ValueError) as exc_info:
            client.send_command("INVALID_CMD")

        # Проверяем текст исключения
        expected_error = "Invalid command: INVALID_CMD. Valid commands are:\
 ['GET_V', 'GET_A', 'GET_S']"
        assert str(exc_info.value) == expected_error

    @patch('src.websocket_client.websocket.create_connection')
    def test_send_command_closed_connection(self, mock_create_connection):
        """
        Тест ошибки при закрытом соединении
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        client = WebsocketClient("ws://localhost:8765")
        client.open()

        client.ws = None

        with pytest.raises(RuntimeError,
                           match="WebSocket connection is not open"):
            client.send_command(str("GET_V"))

        with pytest.raises(RuntimeError,
                           match="WebSocket connection is not open"):
            client.send_command(str("GET_V"))
