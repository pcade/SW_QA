# tests/conftest.py
import pytest
from configparser import ConfigParser


def pytest_addoption(parser):
    """Добавляем опции командной строки"""
    parser.addini("device_port", help="Serial port for device")
    parser.addini("device_baudrate", help="Baudrate for device")
    parser.addini("device_timeout", help="Timeout for device")


@pytest.fixture(scope="session")
def device_config(pytestconfig):
    """Фикстура возвращает конфиг устройства"""
    # читаем pytest.ini через ConfigParser
    config = ConfigParser()
    config.read("pytest.ini")

    port = config.get("device", "port", fallback="/dev/ttyUSB0")
    baudrate = config.getint("device", "baudrate", fallback=9600)
    timeout = config.getfloat("device", "timeout", fallback=1.0)

    return {
        "port": port,
        "baudrate": baudrate,
        "timeout": timeout,
    }
