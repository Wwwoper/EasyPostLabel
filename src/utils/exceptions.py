"""Модуль с исключениями приложения."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EasyPostLabelError(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения.

        Args:
            message: Основное сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        logger.debug("Создание исключения EasyPostLabelError")
        self.message = message
        self.details = details
        super().__init__(self.full_message)
        logger.error("Исключение: %s", self.full_message)

    @property
    def full_message(self) -> str:
        """Полное сообщение об ошибке."""
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ConfigError(EasyPostLabelError):
    """Ошибка конфигурации."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения конфигурации."""
        logger.debug("Создание исключения ConfigError")
        super().__init__(f"Ошибка конфигурации: {message}", details)


class ValidationError(EasyPostLabelError):
    """Ошибка валидации данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения валидации."""
        logger.debug("Создание исключения ValidationError")
        super().__init__(f"Ошибка валидации: {message}", details)


class ProcessingError(EasyPostLabelError):
    """Ошибка обработки данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения обработки."""
        logger.debug("Создание исключения ProcessingError")
        super().__init__(f"Ошибка обработки: {message}", details)


class FileError(EasyPostLabelError):
    """Ошибка работы с файлами."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения файловой операции."""
        logger.debug("Создание исключения FileError")
        super().__init__(f"Ошибка файла: {message}", details)


class DataError(EasyPostLabelError):
    """Ошибка в данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Инициализация исключения данных."""
        logger.debug("Создание исключения DataError")
        super().__init__(f"Ошибка данных: {message}", details)


def handle_exception(e: Exception) -> str:
    """Обработка исключения с логированием.

    Args:
        e: Исключение для обработки

    Returns:
        str: Сообщение об ошибке
    """
    try:
        logger.debug("Обработка исключения: %s", type(e).__name__)
        
        if isinstance(e, EasyPostLabelError):
            logger.error(e.full_message)
            return e.full_message
        
        # Для неизвестных исключений
        error_msg = f"Неизвестная ошибка: {str(e)}"
        logger.exception(error_msg)
        return error_msg

    except Exception as ex:
        logger.exception("Ошибка при обработке исключения: %s", str(ex))
        return "Критическая ошибка при обработке исключения" 