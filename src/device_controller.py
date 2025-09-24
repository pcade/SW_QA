#!/usr/bin/python3
# ============================================================================
# Название: device_controller.py
# Родитель: Наследуемый
# Автор:    Григорий Пахомов
# Версия:   0.1
# Дата:     23.09.2025
# Описание: Класс для работы с устройством по serial-интерфейсу.
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import serial
import re


class DeviceController:
    """
    Класс вызова команд по serial-интерфейсу
    """

    COMMANDS = {
        'VOLTAGE': 'GET_V',
        'AMPERE': 'GET_A',
        'SERIAL': 'GET_S'
    }

    # Регулярные выражения для валидации ответов
    RESPONSE_PATTERNS = {
        'VOLTAGE': re.compile(r'^V_\d+V$'),
        'AMPERE': re.compile(r'^A_\d+A$'),
        'SERIAL': re.compile(r'^S_[A-Z0-9]+$')
    }

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.open_connection()

    def open_connection(self):
        """
        Устанавливает serial соединение
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
        except serial.SerialException as e:
            raise serial.SerialException(
                f"Failed to open port {self.port}: {str(e)}")

    def send_command(self, command: str) -> str:
        """
        Отправляет команду устройству и возвращает ответ
        """
        if (
            self.serial_connection is None
            or not self.serial_connection.is_open
        ):
            raise RuntimeError("Serial connection is not open")

        self.serial_connection.reset_input_buffer()
        self.serial_connection.write(f"{command}\r\n".encode())

        response = self.serial_connection.readline()

        if not response:
            raise serial.SerialTimeoutException("Read timeout occurred")

        decoded_response = response.decode('utf-8').strip()
        return decoded_response

    def validate_response(self, response_type: str, response: str) -> bool:
        """
        Валидирует формат ответа от устройства
        """
        pattern = self.RESPONSE_PATTERNS.get(response_type)
        return pattern.match(response) is not None if pattern else False

    def get_voltage(self) -> str:
        """Запрашивает напряжение"""
        response = self.send_command(self.COMMANDS['VOLTAGE'])
        if not self.validate_response('VOLTAGE', response):
            raise ValueError(f"Invalid voltage response format: {response}")
        return response

    def get_ampere(self) -> str:
        """Запрашивает ток"""
        response = self.send_command(self.COMMANDS['AMPERE'])
        if not self.validate_response('AMPERE', response):
            raise ValueError(f"Invalid ampere response format: {response}")
        return response

    def get_serial(self) -> str:
        """Запрашивает серийный номер"""
        response = self.send_command(self.COMMANDS['SERIAL'])
        if not self.validate_response('SERIAL', response):
            raise ValueError(f"Invalid serial response format: {response}")
        return response

    def close(self):
        """Закрывает соединение"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
