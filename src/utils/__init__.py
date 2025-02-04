"""Пакет с утилитами."""

# Можно оставить пустым или добавить импорты для удобства
from .config import ConfigManager, ReceiverType
from .utils import get_client_full_name, process_dataframe

__all__ = ["ConfigManager", "ReceiverType", "get_client_full_name", "process_dataframe"]
