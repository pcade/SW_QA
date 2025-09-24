#!/usr/bin/python3
# ============================================================================
# Название: test_error_handling.py
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


class TestErrorHandling:
    """
    Тесты обработки ошибок
    """

    @patch('serial.Serial')
    def test_response_with_whitespace(self, mock_serial):
        """Тест обработки ответа с пробелами"""
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"  V_12V  \r\n"

        device = DeviceController("COM1")
        result = device.send_command("GET_V")

        assert result == "V_12V"

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
        """Тест пограничных случаев серийного номера"""
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
