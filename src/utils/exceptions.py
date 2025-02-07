"""Модуль с исключениями приложения."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ErrorDetails:
    """Детали ошибки."""
    message: str
    code: str
    details: Optional[str] = None


class EasyPostLabelError(Exception):
    """Базовое исключение приложения."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        details: Optional[str] = None
    ):
        """Инициализация исключения.

        Args:
            message: Основное сообщение об ошибке
            code: Код ошибки
            details: Дополнительные детали ошибки
        """
        self.error = ErrorDetails(message, code, details)
        super().__init__(self.error.message)
        logger.error(
            "Исключение %s: %s [%s] %s",
            self.__class__.__name__,
            self.error.message,
            self.error.code,
            self.error.details or ""
        )


class ConfigError(EasyPostLabelError):
    """Ошибка конфигурации."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR", details)


class ValidationError(EasyPostLabelError):
    """Ошибка валидации данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class ProcessingError(EasyPostLabelError):
    """Ошибка обработки данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "PROCESSING_ERROR", details)


class FileError(EasyPostLabelError):
    """Ошибка работы с файлами."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "FILE_ERROR", details)


class DataError(EasyPostLabelError):
    """Ошибка в данных."""

    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, "DATA_ERROR", details)


def handle_exception(e: Exception) -> str:
    """Обработка исключения с логированием.

    Args:
        e: Исключение для обработки

    Returns:
        str: Сообщение об ошибке
    """
    try:
        if isinstance(e, EasyPostLabelError):
            error_msg = f"{e.error.message} [{e.error.code}]"
            if e.error.details:
                error_msg += f" - {e.error.details}"
            return error_msg

        # Для неизвестных исключений
        error_msg = f"Неизвестная ошибка: {str(e)}"
        logger.exception(error_msg)
        return error_msg

    except Exception as ex:
        logger.exception("Ошибка при обработке исключения: %s", str(ex))
        return "Критическая ошибка при обработке исключения" 