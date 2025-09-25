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
    def test_get_voltage(self, mock_create_connection):
        """
        Тест запроса напряжения
        """
        # Настраиваем mock для WebSocket соединения
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        # Эмулируем корректный ответ от сервера
        expected_response = {"cmd": "GET_V", "payload": "V_220V"}
        mock_ws.recv.return_value = json.dumps(expected_response)

        # Тестируем реальный код
        client = WebsocketClient("ws://localhost:8765")
        result = client.get_voltage()

        # Проверяем вызовы mock
        mock_ws.send.assert_called_with(json.dumps({"cmd": "GET_V"}))
        assert result == "V_220V"

    @patch('src.websocket_client.websocket.create_connection')
    def test_get_ampere(self, mock_create_connection):
        """
        Тест запроса тока
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        expected_response = {"cmd": "GET_A", "payload": "A_10A"}
        mock_ws.recv.return_value = json.dumps(expected_response)

        client = WebsocketClient("ws://localhost:8765")
        result = client.get_ampere()

        mock_ws.send.assert_called_with(json.dumps({"cmd": "GET_A"}))
        assert result == "A_10A"

    @patch('src.websocket_client.websocket.create_connection')
    def test_get_serial(self, mock_create_connection):
        """
        Тест запроса серийного номера
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        expected_response = {"cmd": "GET_S", "payload": "S_ABC123"}
        mock_ws.recv.return_value = json.dumps(expected_response)

        client = WebsocketClient("ws://localhost:8765")
        result = client.get_serial()

        mock_ws.send.assert_called_with(json.dumps({"cmd": "GET_S"}))
        assert result == "S_ABC123"

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
    def test_invalid_response_voltage(self, mock_create_connection):
        """
        Тест обработки неверного формата ответа get_voltage
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        invalid_response = {"wrong_key": "wrong_value"}
        mock_ws.recv.return_value = json.dumps(invalid_response)

        expected_msg = f"Invalid voltage response format: {invalid_response}"
        client = WebsocketClient("ws://localhost:8765")

        with pytest.raises(ValueError,
                           match=expected_msg):
            client.get_voltage()

    @patch('src.websocket_client.websocket.create_connection')
    def test_invalid_response_ampere(self, mock_create_connection):
        """
        Тест обработки неверного формата ответа get_ampere
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        invalid_response = {"wrong_key": "wrong_value"}
        mock_ws.recv.return_value = json.dumps(invalid_response)

        expected_msg = f"Invalid ampere response format: {invalid_response}"
        client = WebsocketClient("ws://localhost:8765")

        with pytest.raises(ValueError,
                           match=expected_msg):
            client.get_ampere()

    @patch('src.websocket_client.websocket.create_connection')
    def test_invalid_response_serial(self, mock_create_connection):
        """
        Тест обработки неверного формата ответа get_serial
        """
        mock_ws = Mock()
        mock_create_connection.return_value = mock_ws

        invalid_response = {"wrong_key": "wrong_value"}
        mock_ws.recv.return_value = json.dumps(invalid_response)

        expected_msg = f"Invalid serial response format: {invalid_response}"
        client = WebsocketClient("ws://localhost:8765")

        with pytest.raises(ValueError,
                           match=expected_msg):
            client.get_serial()
