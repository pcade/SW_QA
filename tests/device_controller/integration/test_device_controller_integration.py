#!/usr/bin/python3
# ============================================================================
# Название: test_device_controller_integration.py
# Родитель: Pytest
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Интеграционные тесты для device_controller.py
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import pytest
from src.device_controller import DeviceController


@pytest.mark.integration
def test_get_voltage_real_device(device_config):
    """
    Интеграционный тест запроса напряжения
    """
    with DeviceController(**device_config) as device:
        response = device.get_voltage()
        assert response.startswith("V_") and response.endswith("V"), \
            f"Неверный ответ: {response}"


@pytest.mark.integration
def test_get_ampere_real_device(device_config):
    """
    Интеграционный тест запроса тока
    """
    with DeviceController(**device_config) as device:
        response = device.get_ampere()
        assert response.startswith("A_") and response.endswith("A"), \
            f"Неверный ответ: {response}"


@pytest.mark.integration
def test_get_serial_real_device(device_config):
    """
    Интеграционный тест запроса серийного номера
    """
    with DeviceController(**device_config) as device:
        response = device.get_serial()
        assert response.startswith("S_"), f"Неверный ответ: {response}"
        assert len(response) > 2, "Серийный номер пустой"
