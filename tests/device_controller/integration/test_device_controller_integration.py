#!/usr/bin/python3
# ============================================================================
# Название: test_device_controller_integration.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Интеграционные тесты для device_controller.py
# Примечание: Тестирует взаимодействие всех компонентов системы
# ============================================================================

import pytest
from unittest.mock import Mock, patch
from src.device_controller import DeviceController

SERIAL_PORT = "/dev/ttyUSB0"
TIMEOUT = 1
RESULT_GET_V = "V_12V"
RESULT_GET_A = "A_5A"
RESULT_GET_S = "S_ABC123"


class TestDeviceControllerIntegration:
    """
    Интеграционные тесты для класса DeviceController
    """
    @patch('serial.Serial')
    def test_serial_connection_establishment(self, mock_serial):
        """
        Тест проверки соединения с serial портом
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True

        device = DeviceController(SERIAL_PORT)

        mock_serial.assert_called_once_with(SERIAL_PORT, timeout=TIMEOUT)
        assert device.ser.is_open

    @patch('serial.Serial')
    def test_voltage_measurement_workflow(self, mock_serial):
        """
        Интеграционный тест полного цикла измерения напряжения
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = f"{RESULT_GET_V}\r\n"

        device = DeviceController(SERIAL_PORT)
        result = device.get_voltage()

        mock_serial.assert_called_once_with(SERIAL_PORT, timeout=TIMEOUT)
        mock_serial_instance.write.assert_called_once_with(b"GET_V\n")
        mock_serial_instance.readline.assert_called_once()

        assert result == RESULT_GET_V

    @patch('serial.Serial')
    def test_current_measurement_workflow(self, mock_serial):
        """
        Интеграционный тест полного цикла измерения тока
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = f"{RESULT_GET_A}\r\n"

        device = DeviceController(SERIAL_PORT)
        result = device.get_ampere()

        mock_serial.assert_called_once_with(SERIAL_PORT, timeout=TIMEOUT)
        mock_serial_instance.write.assert_called_once_with(b"GET_A\n")
        mock_serial_instance.readline.assert_called_once()

        assert result == "RESULT_GET_A"

    @patch('serial.Serial')
    def test_serial_number_retrieval_workflow(self, mock_serial):
        """
        Интеграционный тест полного цикла получения серийного номера
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = f"{RESULT_GET_S}\r\n"

        device = DeviceController(SERIAL_PORT)
        result = device.get_serial()

        mock_serial.assert_called_once_with(SERIAL_PORT, timeout=TIMEOUT)
        mock_serial_instance.write.assert_called_once_with(b"GET_S\n")
        mock_serial_instance.readline.assert_called_once()

        assert result == "RESULT_GET_S"

    @patch('serial.Serial')
    def test_multiple_operations_in_sequence(self, mock_serial):
        """
        Интеграционный тест последовательных операций
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True

        mock_serial_instance.readline.side_effect = [
            f"{RESULT_GET_V}\r\n",
            f"{RESULT_GET_A}\r\n",
            f"{RESULT_GET_S}\r\n"
        ]

        device = DeviceController(SERIAL_PORT)

        voltage_result = device.get_voltage()
        current_result = device.get_ampere()
        serial_result = device.get_serial()

        assert mock_serial_instance.write.call_count == 3
        mock_serial_instance.write.assert_any_call(b"GET_V\n")
        mock_serial_instance.write.assert_any_call(b"GET_A\n")
        mock_serial_instance.write.assert_any_call(b"GET_S\n")

        assert voltage_result == RESULT_GET_V
        assert current_result == RESULT_GET_A
        assert serial_result == RESULT_GET_S

    @patch('serial.Serial')
    def test_error_handling_integration(self, mock_serial):
        """
        Интеграционный тест обработки ошибок
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = b"INVALID_RESPONSE\r\n"

        device = DeviceController(SERIAL_PORT)

        with pytest.raises(ValueError,
                           match="Invalid voltage response format"):
            device.get_voltage()

        mock_serial_instance.write.assert_called_once_with(b"GET_V\n")
        mock_serial_instance.readline.assert_called_once()

    @patch('serial.Serial')
    def test_connection_management_integration(self, mock_serial):
        """
        Интеграционный тест управления соединением
        """
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.return_value = f"{RESULT_GET_V}\r\n"

        device = DeviceController(SERIAL_PORT)

        mock_serial.assert_called_once_with(SERIAL_PORT, timeout=TIMEOUT)
        device.close_connection()
        mock_serial_instance.close.assert_called_once()
