"""Менеджер конфигурации."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, cast

import yaml

from .constants import DEFAULT_CONFIG_PATH


class ExcelConfig(TypedDict):
    """Конфигурация Excel."""

    sheet_index: int
    start_row: int


class ValidationRules(TypedDict):
    """Правила валидации."""

    postal_keyword: str


class ColumnConfig(TypedDict):
    """Конфигурация столбца."""

    source: str
    validation: ValidationRules


class OutputConfig(TypedDict):
    """Конфигурация вывода."""

    filename: str


class Config(TypedDict):
    """Структура конфигурации."""

    excel: ExcelConfig
    columns: Dict[str, ColumnConfig]
    output: Dict[str, OutputConfig]


class ReceiverType(Enum):
    """Типы получателей."""

    SELF = "Лично я"
    OTHER = "Другой человек"


class ConfigManager:
    """Менеджер конфигурации."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Инициализация менеджера конфигурации.

        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Загрузка конфигурации из YAML файла."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)
                self.config = cast(Dict[str, Any], loaded_config or {})
        except Exception as e:
            raise ValueError(f"Ошибка загрузки конфигурации: {str(e)}") from e

    def get_receiver_type_field(self) -> str:
        """Получение имени поля для определения типа получателя."""
        return str(self.config["columns"]["receiver_type"]["source"])

    def get_receiver_fields(self, receiver_type: str) -> Dict[str, str]:
        """Получение полей для определенного типа получателя."""
        fields = self.config["receivers"]["fields"].get(receiver_type, {})
        return {str(k): str(v) for k, v in fields.items()}

    def get_column_mapping(self) -> Dict[str, str]:
        """Получение маппинга столбцов."""
        return {
            str(k): str(v["source"]) for k, v in self.config.get("columns", {}).items()
        }

    def get_excel_columns(self) -> Dict[str, str]:
        """Получение маппинга Excel-столбцов."""
        use_columns = self.config.get("excel", {}).get("use_columns", True)
        column_key = "excel_column" if use_columns else "column_index"

        return {
            str(k): str(v[column_key])
            for k, v in self.config.get("columns", {}).items()
        }

    def get_excel_config(self) -> Dict[str, Any]:
        """Получение конфигурации Excel."""
        excel_config = self.config.get("excel", {})
        return cast(Dict[str, Any], excel_config)

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
        validation_rules = column_config.get("validation", {})
        return cast(Dict[str, Any], validation_rules)

    def get_output_config(self, delivery_type: str) -> Dict[str, Any]:
        """Получение конфигурации вывода для типа доставки."""
        output_config = self.config.get("output", {}).get(delivery_type, {})
        return cast(Dict[str, Any], output_config)

    def get_required_fields(self, delivery_type: str) -> list:
        """Получение списка обязательных полей для типа доставки.

        Args:
            delivery_type: Тип доставки ('Почта' или 'Центр_Выдачи')

        Returns:
            list: Список обязательных полей

        Raises:
            ValueError: Если тип доставки не найден
        """
        try:
            delivery_types = self.config.get("delivery_methods", {}).get("types", {})
            delivery_config = delivery_types.get(delivery_type)

            if not delivery_config:
                raise ValueError(f"Тип доставки не найден: {delivery_type}")

            # Получаем все поля для типа доставки
            required_fields = []

            # Добавляем общие поля
            common_fields = delivery_config.get("required_fields", {}).get("common", [])
            required_fields.extend(common_fields)

            # Добавляем поля для разных типов получателей
            receiver_fields = delivery_config.get("required_fields", {})
            for receiver_type, fields in receiver_fields.items():
                if receiver_type != "common" and isinstance(fields, list):
                    required_fields.extend(fields)

            return required_fields

        except Exception as e:
            logger.error("Ошибка при получении обязательных полей: %s", str(e))
            raise

    def get_output_template(self, template_type: str) -> Dict[str, Any]:
        """Получение шаблона вывода по типу.

        Args:
            template_type: Тип шаблона ('postal' или 'pickup_point')

        Returns:
            Dict[str, Any]: Конфигурация шаблона

        Raises:
            ValueError: Если шаблон не найден
        """
        try:
            templates = self.config.get("output", {}).get("templates", {})
            template = templates.get(template_type)

            if not template:
                raise ValueError(f"Шаблон вывода не найден: {template_type}")

            return cast(Dict[str, Any], template)

        except Exception as e:
            logger.error("Ошибка при получении шаблона вывода: %s", str(e))
            raise
