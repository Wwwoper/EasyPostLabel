"""Конфигурация реестра стратегий."""

from pathlib import Path
from typing import Optional

import yaml


class RegistryManager:
    """Менеджер реестра стратегий."""

    def __init__(self, config_path: Path) -> None:
        """Инициализация менеджера реестра.

        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Загрузка конфигурации из файла.

        Returns:
            dict: Загруженная конфигурация
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Файл конфигурации не найден: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_config(self) -> dict:
        """Получение конфигурации реестра.

        Returns:
            dict: Конфигурация реестра
        """
        return self.config
