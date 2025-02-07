"""Константы приложения."""

from enum import Enum
from typing import Dict, Final

# Файлы
class FileNames(str, Enum):
    """Имена файлов."""
    POSTAL = "postal.xlsx"
    LABELS = "labels.xlsx"
    CONFIG = "config.yaml"


# Типы доставки
class DeliveryType(str, Enum):
    """Типы доставки."""
    POSTAL = "Почта"
    PICKUP = "Центр_Выдачи"


# Типы получателей
class ReceiverType(str, Enum):
    """Типы получателей."""
    SELF = "Лично я"
    OTHER = "Другой человек"


# Коды ошибок
class ErrorCode(str, Enum):
    """Коды ошибок."""
    CONFIG = "CONFIG_ERROR"
    VALIDATION = "VALIDATION_ERROR"
    PROCESSING = "PROCESSING_ERROR"
    FILE = "FILE_ERROR"
    DATA = "DATA_ERROR"
    UNKNOWN = "UNKNOWN_ERROR"


# Ключи конфигурации
class ConfigKey(str, Enum):
    """Ключи конфигурации."""
    COLUMNS = "columns"
    OUTPUT = "output"
    VALIDATION = "validation"
    DELIVERY_METHODS = "delivery_methods"
    EXCEL = "excel"


# Форматы файлов
SUPPORTED_FORMATS: Final[Dict[str, str]] = {
    "excel": ".xlsx",
    "csv": ".csv"
}
