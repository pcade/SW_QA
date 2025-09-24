#!/usr/bin/python3
# ============================================================================
# Название: test_webscoket_client.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Мок тесты для webscoket_client.py
# Примечание: Используется unittest.mock для эмуляции поведения serial.Serial
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import pytest
from unittest.mock import patch, Mock
from src.webscoket_client import WebsocketClient


class TestWSClient:
    """
    Тесты для класса WSClient
    """

    @patch("websocket.create_connection")
    def test_get_voltage(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_V","payload":"V_12V"}'
        mock_ws_create.return_value = mock_ws

        client = WebsocketClient("ws://fake", timeout=1.0)
        result = client.get_voltage()

        mock_ws.send.assert_called_with('{"cmd": "GET_V"}')
        assert result == "V_12V"

    @patch("websocket.create_connection")
    def test_get_ampere(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_A","payload":"A_1A"}'
        mock_ws_create.return_value = mock_ws

        client = WebsocketClient("ws://fake")
        result = client.get_ampere()

        mock_ws.send.assert_called_with('{"cmd": "GET_A"}')
        assert result == "A_1A"

    @patch("websocket.create_connection")
    def test_get_serial(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_S","payload":"S_DSA123"}'
        mock_ws_create.return_value = mock_ws

        client = WebsocketClient("ws://fake")
        result = client.get_serial()

        mock_ws.send.assert_called_with('{"cmd": "GET_S"}')
        assert result == "S_DSA123"

    @patch("websocket.create_connection")
    def test_send_command_closed_connection(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws_create.return_value = mock_ws

        client = WebsocketClient("ws://fake")
        client.close()

        with pytest.raises(RuntimeError,
                           match="WebSocket connection is not open"):
            client.send_command("GET_V")
