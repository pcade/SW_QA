#!/usr/bin/python3
# ============================================================================
# Название: serial_devices.py
# Родитель: Наследуемый
# Автор:    Григорий Пахомов
# Версия:   0.1
# Дата:     23.09.2025
# Описание: Класс для работы с устройством по serial-интерфейсу.
# ============================================================================


# ============================================================================
# Импорт модулей и глобальных переменных
# ============================================================================
from typing import Optional
from src.logger import setup_logger
import re


# ============================================================================
# Основной класс
# ============================================================================
class DeviceSerial:
    """
    Класс для работы с устройством по serial-интерфейсу.
    """

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 timeout: float = 1.0,
                 ser=None,
                 log_file: str = "log/sw_qa_serial_device.log") -> None:
        """
        Инициализирует соединение с устройством.

        Args:
            port: COM-порт (например 'COM3' или '/dev/ttyUSB0')
            baudrate: Скорость соединения (по умолчанию 9600)
            timeout: Таймаут чтения в секундах
            ser: Готовый объект serial.Serial (для тестирования)
        """

        self.ser = ser
        self._logger = setup_logger(__name__, log_file)
        if self.ser is None:
            try:
                import serial
                self._serial = serial.Serial(
                    port=port, 
                    baudrate=baudrate, 
                    timeout=timeout
                )
                self._logger.info(f"Успешное подключение к порту {port}")
            except Exception as error:
                self._logger.error(f"Ошибка подключения к порту {port}: {error}")
                raise
        else:
            self._logger.info("Используется переданный serial объект")

    def _clean_response(self, response: str) -> str:
        """
        Очищает ответ от служебных символов и лишних пробелов.

        Args:
            response: Сырой ответ от устройства

        Returns:
            Очищенная строка ответа
        """
        if not response:
            return ""

        # Удаляем нулевые байты и другие управляющие символы
        cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response)
        
        # Удаляем лишние пробелы и символы возврата каретки
        cleaned_response = cleaned_response.strip().replace('\r', '').replace('\n', '')
        
        self._logger.debug(f"Очистка ответа: '{response}' -> '{cleaned_response}'")

        return cleaned_response

    def send_command(self, command: str) -> Optional[str]:
        """
        Отправляет команду устройству и возвращает ответ.

        Args:
            command: Команда для отправки

        Returns:
            Ответ от устройства или None в случае ошибки
        """
        if not command or not command.strip():
            self._logger.warning("Попытка отправки пустой команды")
            return None

        try:
            self._logger.info(f"Отправка команды: '{command}'")

            if not self.ser.is_open:
                self._logger.info("Открытие serial соединения")
                self.ser.open()

            # Очищаем буфер перед отправкой
            self.ser.reset_input_buffer()
            self._logger.debug("Буфер ввода очищен")

            # Отправляем команду
            command_to_send = command.strip() + '\r\n'
            self.ser.write(command_to_send.encode('utf-8'))
            self._logger.debug(f"Команда отправлена: '{command_to_send.strip()}'")

            # Читаем ответ
            response_bytes = self.ser.readline()
            response = response_bytes.decode('utf-8', errors='ignore')

            self._logger.info(f"Получен ответ: '{response}'")

            cleaned_response = self._clean_response(response) if response else None
            self._logger.debug(f"Очищенный ответ: '{cleaned_response}'")

            return cleaned_response

        except Exception as error:
            self._logger.error(f"Ошибка при отправке команды '{command}': {error}")
            return None

    def get_voltage(self) -> Optional[str]:
        """Запрашивает напряжение."""
        self._logger.info("Запрос напряжения")
        result = self.send_command('GET_V')
        self._logger.info(f"Результат запроса напряжения: {result}")
        return result

    def get_current(self) -> Optional[str]:
        """Запрашивает ток."""
        self._logger.info("Запрос тока")
        result = self.send_command('GET_A')
        self._logger.info(f"Результат запроса тока: {result}")
        return result

    def get_serial(self) -> Optional[str]:
        """Запрашивает серийный номер."""
        self._logger.info("Запрос серийного номера")
        result = self.send_command('GET_S')
        self._logger.info(f"Результат запроса серийного номера: {result}")
        return result

    def close(self)-> None:
        """Закрыть соединение."""
        if hasattr(self, 'ser') and self.ser.is_open:
            self._logger.info("Закрытие serial соединения")
            self.ser.close()
            self._logger.info("Serial соединение закрыто")
        else:
            self._logger.debug("Соединение уже закрыто или не существует")

    def __enter__(self)-> 'DeviceSerial':
        """Поддержка контекстного менеджера."""
        self._logger.debug("Вход в контекстный менеджер")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb)-> None:
        """Автоматическое закрытие соединения."""
        self._logger.debug("Выход из контекстного менеджера")
        self.close()