"""Менеджер конфигурации."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .constants import DEFAULT_CONFIG_PATH


class ReceiverType(Enum):
    """Типы получателей."""

    SELF = "Лично я"
    OTHER = "Другой человек"


class ConfigManager:
    """Менеджер конфигурации."""

    def __init__(self, config_path: Optional[Path] = None):
        """Инициализация менеджера конфигурации.

        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Загрузка конфигурации из YAML файла."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Ошибка загрузки конфигурации: {str(e)}") from e

    def get_receiver_type_field(self) -> str:
        """Получение имени поля для определения типа получателя."""
        return self.config["columns"]["receiver_type"]["source"]

    def get_receiver_fields(self, receiver_type: str) -> Dict[str, str]:
        """Получение полей для определенного типа получателя."""
        return self.config["receivers"]["fields"][receiver_type]

    def get_column_mapping(self) -> Dict[str, str]:
        """Получение маппинга столбцов."""
        return {k: v["source"] for k, v in self.config.get("columns", {}).items()}

    def get_excel_columns(self) -> Dict[str, str]:
        """Получение маппинга Excel-столбцов."""
        use_columns = self.config.get("excel", {}).get("use_columns", True)
        column_key = "excel_column" if use_columns else "column_index"

        return {k: v[column_key] for k, v in self.config.get("columns", {}).items()}

    def get_excel_config(self) -> Dict[str, Any]:
        """Получение конфигурации Excel."""
        return self.config.get("excel", {})

    def get_required_columns(self) -> list[str]:
        """Получение списка обязательных столбцов."""
        return [
            k
            for k, v in self.config.get("columns", {}).items()
            if v.get("required", False)
        ]

    def get_validation_rules(self, column: str) -> Dict[str, Any]:
        """Получение правил валидации для столбца."""
        column_config = self.config.get("columns", {}).get(column, {})
        return column_config.get("validation", {})

    def get_output_config(self, delivery_type: str) -> Dict[str, Any]:
        """Получение конфигурации вывода для типа доставки."""
        return self.config.get("output", {}).get(delivery_type, {})
