"""Константы приложения."""

from enum import Enum
from pathlib import Path


class DeliveryType(Enum):
    """Типы доставки."""

    POSTAL = "postal"
    PICKPOINT = "pickpoint"


# Пути к файлам
DEFAULT_CONFIG_PATH = Path("config")
DEFAULT_OUTPUT_DIR = Path("output")

# Названия выходных файлов
POSTAL_CLIENTS_FILENAME = "postal_clients.xlsx"
ALTERNATIVE_CLIENTS_FILENAME = "alternative_clients.xlsx"

# Ключи конфигурации
CONFIG_COLUMNS_KEY = "columns"
CONFIG_OUTPUT_KEY = "output"
CONFIG_VALIDATION_KEY = "validation"
