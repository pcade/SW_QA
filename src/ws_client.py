#!/usr/bin/python3
# ============================================================================
# Название: ws_client.py
# Автор:    (Ваше имя)
# Версия:   0.1
# Дата:     24.09.2025
# Описание: Класс WebSocket-клиента для отправки команд GET_V, GET_A, GET_S
# Допущения:
# - Сервер доступен по ws://localhost:8765 (или другой URL)
# - Протокол обмена: JSON (UTF-8)
# - Каждый запрос -> один ответ
# - Соединение кратковременное (открываем при создании, закрываем в close)
# ============================================================================
import json
import websocket


class WSClient:
    """Класс WebSocket-клиента для взаимодействия с сервером"""

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
        """Открывает соединение"""
        self.ws = websocket.create_connection(self.url, timeout=self.timeout)

    def close(self):
        """Закрывает соединение"""
        if self.ws:
            self.ws.close()
            self.ws = None

    def send_command(self, cmd: str) -> dict:
        """
        Отправляет команду и возвращает ответ (dict)
        """
        if self.ws is None:
            raise RuntimeError("WebSocket connection is not open")

        request = {"cmd": cmd}
        self.ws.send(json.dumps(request))
        raw_response = self.ws.recv()
        return json.loads(raw_response)

    def get_voltage(self) -> str:
        """Запрос напряжения"""
        resp = self.send_command("GET_V")
        return resp["payload"]

    def get_ampere(self) -> str:
        """Запрос тока"""
        resp = self.send_command("GET_A")
        return resp["payload"]

    def get_serial(self) -> str:
        """Запрос серийного номера"""
        resp = self.send_command("GET_S")
        return resp["payload"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
