#!/usr/bin/python3
# ============================================================================
# Название: test_device_controller.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Мок тесты для device_controller.py
# Примечание: Используется unittest.mock для эмуляции поведения serial.Serial
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import pytest
from unittest.mock import Mock, patch
from src.device_controller import DeviceController


class TestDeviceController:
    """
    Тесты для класса DeviceController
    """
    @patch('serial.Serial')
    def test_various_voltage_formats(self, mock_serial):
        """Тест различных форматов напряжения"""
        test_cases = [
            (b"V_5V\r\n", True),      # Valid
            (b"V_12V\r\n", True),     # Valid
            (b"V_0V\r\n", True),      # Valid
            (b"V_12.5V\r\n", False),  # Invalid (decimal)
            (b"V_12\r\n", False),     # Invalid (missing V)
            (b"VOLT_12V\r\n", False)  # Invalid prefix
        ]

        for i, (response, should_be_valid) in enumerate(test_cases):
            mock_serial_instance = Mock()
            mock_serial.return_value = mock_serial_instance
            mock_serial_instance.is_open = True
            mock_serial_instance.readline.return_value = response

            device = DeviceController("COM1")

            if should_be_valid:
                result = device.get_voltage()
                assert (
                    result == response.decode().strip()
                    ), f"Test case {i} failed"
            else:
                with pytest.raises(ValueError,
                                   match="Invalid voltage response format"):
                    device.get_voltage()

    @patch('serial.Serial')
    def test_various_ampere_formats(self, mock_serial):
        """Тест различных форматов тока"""
        test_cases = [
            (b"A_5A\r\n", True),      # Valid
            (b"A_12A\r\n", True),     # Valid
            (b"A_0A\r\n", True),      # Valid
            (b"A_12.5A\r\n", False),  # Invalid (decimal)
            (b"A_12\r\n", False),     # Invalid (missing A)
            (b"AMP_12A\r\n", False)   # Invalid prefix
        ]

        for i, (response, should_be_valid) in enumerate(test_cases):
            mock_serial_instance = Mock()
            mock_serial.return_value = mock_serial_instance
            mock_serial_instance.is_open = True
            mock_serial_instance.readline.return_value = response

            device = DeviceController("COM1")

            if should_be_valid:
                result = device.get_ampere()
                assert (
                    result == response.decode().strip()
                ), f"Test case {i} failed"
            else:
                with pytest.raises(ValueError,
                                   match="Invalid ampere response format"):
                    device.get_ampere()

    @patch('serial.Serial')
    def test_serial_number_edge_cases(self, mock_serial):
        """
        Тест пограничных случаев серийного номера
        """
        test_cases = [
            (b"S_ABC123\r\n", True),     # Valid
            (b"S_123\r\n", True),        # Valid (digits only)
            (b"S_A\r\n", True),          # Valid (single char)
            (b"S_AB@123\r\n", False),    # Invalid (special char)
            (b"S_ab123\r\n", False),     # Invalid (lowercase)
            (b"S_AB 123\r\n", False)     # Invalid (space)
        ]

        for response, should_be_valid in test_cases:
            mock_serial_instance = Mock()
            mock_serial.return_value = mock_serial_instance
            mock_serial_instance.is_open = True
            mock_serial_instance.readline.return_value = response

            device = DeviceController("COM1")

            if should_be_valid:
                result = device.get_serial()
                assert result == response.decode().strip()
            else:
                with pytest.raises(ValueError):
                    device.get_serial()

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
        with pytest.raises(ValueError) as exc_info:
            device.send_command("TEST_CMD")

        expected_error = "Invalid command: \
TEST_CMD. Valid commands are: ['GET_V', 'GET_A', 'GET_S']"
        assert str(exc_info.value) == expected_error

        mock_serial_instance.write.assert_not_called()

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
        with pytest.raises(ValueError) as exc_info:
            device.send_command("CMD")

        expected_error = "Invalid command: \
CMD. Valid commands are: ['GET_V', 'GET_A', 'GET_S']"
        assert str(exc_info.value) == expected_error

        mock_serial_instance.write.assert_not_called()

    @patch('serial.Serial')
    def test_send_command_closed_connection(self, mock_serial):
        """
        Тест обработки ошибки при закрытом соединении
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = False

        device = DeviceController("COM1")

        with pytest.raises(RuntimeError,
                           match="Serial connection is not open"):
            device.send_command("TEST_CMD")

        with pytest.raises(RuntimeError,
                           match="Serial connection is not open"):
            device.send_command("TEST_CMD")
