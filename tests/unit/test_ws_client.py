import pytest
from unittest.mock import patch, Mock
from src.ws_client import WSClient


class TestWSClient:
    """Тесты для класса WSClient"""

    @patch("websocket.create_connection")
    def test_get_voltage(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_V","payload":"V_12V"}'
        mock_ws_create.return_value = mock_ws

        client = WSClient("ws://fake", timeout=1.0)
        result = client.get_voltage()

        mock_ws.send.assert_called_with('{"cmd": "GET_V"}')
        assert result == "V_12V"

    @patch("websocket.create_connection")
    def test_get_ampere(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_A","payload":"A_1A"}'
        mock_ws_create.return_value = mock_ws

        client = WSClient("ws://fake")
        result = client.get_ampere()

        mock_ws.send.assert_called_with('{"cmd": "GET_A"}')
        assert result == "A_1A"

    @patch("websocket.create_connection")
    def test_get_serial(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws.recv.return_value = '{"cmd":"GET_S","payload":"S_DSA123"}'
        mock_ws_create.return_value = mock_ws

        client = WSClient("ws://fake")
        result = client.get_serial()

        mock_ws.send.assert_called_with('{"cmd": "GET_S"}')
        assert result == "S_DSA123"

    @patch("websocket.create_connection")
    def test_send_command_closed_connection(self, mock_ws_create):
        mock_ws = Mock()
        mock_ws_create.return_value = mock_ws

        client = WSClient("ws://fake")
        client.close()

        with pytest.raises(RuntimeError,
                           match="WebSocket connection is not open"):
            client.send_command("GET_V")
