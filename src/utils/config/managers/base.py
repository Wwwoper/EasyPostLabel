"""Базовый класс для менеджеров конфигурации."""

from pathlib import Path
from typing import Any, Dict

import yaml


class BaseConfigManager:
    """Базовый менеджер конфигурации."""

    def __init__(self, config_path: Path) -> None:
        """Инициализация менеджера конфигурации.

        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Загрузка конфигурации из YAML файла."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)
                self.config = loaded_config or {}
        except Exception as e:
            raise ValueError(f"Ошибка загрузки конфигурации: {str(e)}") from e

    def get_config(self) -> Dict[str, Any]:
        """Получение всей конфигурации."""
        return self.config

    def validate_config(self) -> None:
        """Валидация конфигурации."""
        raise NotImplementedError("Метод должен быть переопределен в дочернем классе")
