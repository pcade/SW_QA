#!/usr/bin/python3
# ============================================================================
# Название: weboscoket_client.py
# Родитель: Наследуемый
# Автор:    Григорий Пахомов
# Версия:   1
# Дата:     24.09.2025
# Описание: Класс для работы с устройством как WebSocket-клиент.
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
import json
import re
import websocket


class WebsocketClient:
    """Класс WebSocket-клиента для взаимодействия с сервером"""

    COMMANDS = {
        'VOLTAGE': 'GET_V',
        'AMPERE': 'GET_A',
        'SERIAL': 'GET_S'
    }

    RESPONSE_PATTERNS = {
        'VOLTAGE': re.compile(r'^V_\d+V$'),
        'AMPERE': re.compile(r'^A_\d+A$'),
        'SERIAL': re.compile(r'^S_[A-Z0-9]+$')
    }

    def __init__(self, url: str = "ws://localhost:8765", timeout: float = 2.0):
        """
        url: адрес WebSocket-сервера
        timeout: таймаут на чтение ответа
        """
        self.url = url
        self.timeout = timeout
        self.ws = None
        self.open()

    def open(self):
        """
        Устанавливает  соединение
        """
        self.ws = websocket.create_connection(self.url, timeout=self.timeout)

    def send_command(self, cmd: str) -> dict:
        """
        Отправляет команду устройству и возвращает ответ (dict).
        """
        if self.ws is None:
            raise RuntimeError("WebSocket connection is not open")

        if not self.is_valid_command(cmd):
            raise ValueError(
                f"Invalid command: {cmd}. \
Valid commands are: {list(self.COMMANDS.values())}"
            )

        request = {"cmd": cmd}
        self.ws.send(json.dumps(request))
        raw_response = self.ws.recv()
        return json.loads(raw_response)

    def is_valid_command(self, cmd: str) -> bool:
        """
        Проверяет, является ли команда допустимой
        """
        return cmd in self.COMMANDS.values()

    def validate_response(self, response_type: str, response: dict) -> bool:
        """
        Валидирует формат ответа от WebSocket сервера.
        """
        if (
            not isinstance(response, dict)
            or 'cmd' not in response
            or 'payload' not in response
        ):
            return False

        if response['cmd'] != self.COMMANDS[response_type]:
            return False

        pattern = self.RESPONSE_PATTERNS.get(response_type)

        if not pattern:
            return False

        return pattern.match(response['payload']) is not None

    def get_voltage(self) -> str:
        """
        Запрашивает напряжение.
        """
        response = self.send_command(self.COMMANDS['VOLTAGE'])
        if not self.validate_response('VOLTAGE', response):
            raise ValueError(f"Invalid voltage response format: {response}")
        return response["payload"]

    def get_ampere(self) -> str:
        """
        Запрашивает ток.
        """
        response = self.send_command(self.COMMANDS['AMPERE'])
        if not self.validate_response('AMPERE', response):
            raise ValueError(f"Invalid ampere response format: {response}")
        return response["payload"]

    def get_serial(self) -> str:
        """
        Запрашивает серийный номер.
        """
        response = self.send_command(self.COMMANDS['SERIAL'])
        if not self.validate_response('SERIAL', response):
            raise ValueError(f"Invalid serial response format: {response}")
        return response["payload"]

    def close(self):
        """
        Закрывает соединение.
        """
        if self.ws and self.ws.connected:
            self.ws.close()
            self.ws = None

    def __enter__(self):
        """
        Поддерживает контекстный менеджер.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Автоматически закрывает соединения.
        """
        self.close()
