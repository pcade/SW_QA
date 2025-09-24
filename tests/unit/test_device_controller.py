# tests/unit/test_device_controller.py
import pytest
from unittest.mock import Mock, patch
from src.device_controller import DeviceController


class TestDeviceController:
    """Тесты для класса DeviceController"""

    @patch('serial.Serial')
    def test_get_voltage(self, mock_serial):
        """
        Тест запроса напряжения
        """
        # Настраиваем mock для полной эмуляции Serial
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance

        # Эмулируем открытое соединение
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"V_12V\n"

        # Тестируем реальный код
        device = DeviceController("COM1")
        result = device.get_voltage()

        # Проверяем вызовы mock
        mock_serial_instance.write.assert_called_with(b"GET_V\r\n")
        mock_serial_instance.reset_input_buffer.assert_called_once()
        assert result == "V_12V"

    @patch('serial.Serial')
    def test_get_ampere(self, mock_serial):
        """
        Тест запроса тока
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"A_1A\n"

        device = DeviceController("COM1")
        result = device.get_ampere()

        mock_serial_instance.write.assert_called_with(b"GET_A\r\n")
        assert result == "A_1A"

    @patch('serial.Serial')
    def test_get_serial(self, mock_serial):
        """
        Тест запроса серийного номера
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"S_DSA123\n"

        device = DeviceController("COM1")
        result = device.get_serial()

        mock_serial_instance.write.assert_called_with(b"GET_S\r\n")
        assert result == "S_DSA123"

    @patch('serial.Serial')
    def test_send_command_general(self, mock_serial):
        """
        Тест общего метода отправки команды
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"TEST_RESPONSE\n"

        device = DeviceController("COM1")
        result = device.send_command("TEST_CMD")

        mock_serial_instance.write.assert_called_with(b"TEST_CMD\r\n")
        assert result == "TEST_RESPONSE"

    @patch('serial.Serial')
    def test_send_command_with_stripping(self, mock_serial):
        """
        Тест обработки ответа с пробелами и переносами
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"  RESPONSE  \r\n"

        device = DeviceController("COM1")
        result = device.send_command("CMD")

        assert result == "RESPONSE"

    @patch('serial.Serial')
    def test_send_command_closed_connection(self, mock_serial):
        """
        Тест ошибки при закрытом соединении
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = False  # Эмулируем закрытое соединение

        device = DeviceController("COM1")

        with pytest.raises(RuntimeError,
                           match="Serial connection is not open"):
            device.send_command("TEST_CMD")

        with pytest.raises(RuntimeError,
                           match="Serial connection is not open"):
            device.send_command("TEST_CMD")


# Фикстура для переиспользования mock
@pytest.fixture
def mock_serial():
    with patch('serial.Serial') as mock_serial:
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        yield mock_serial_instance


def test_with_fixture(mock_serial):
    """
    Тест с использованием фикстуры
    """
    mock_serial.readline.return_value = b"V_12V\r\n"

    device = DeviceController("COM1")
    result = device.get_voltage()

    assert result == "V_12V"
    mock_serial.write.assert_called_with(b"GET_V\r\n")
