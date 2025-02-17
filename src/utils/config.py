"""Менеджер конфигурации."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, TypedDict, cast

from .config import ColumnsManager, SettingsManager, StrategyManager
from .config.registry import RegistryManager


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

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Инициализация менеджера конфигурации.

        Args:
            config_dir: Путь к директории с конфигурациями
        """
        self.config_dir = config_dir or Path("config")

        # Инициализация менеджеров
        self.settings = SettingsManager(self.config_dir / "settings.yaml")
        self.columns = ColumnsManager(self.config_dir / "columns.yaml")
        self.strategies = StrategyManager(self.config_dir / "delivery/strategies")
        self.registry = RegistryManager(
            self.config_dir / "delivery/strategies/registry.yaml"
        )

    def get_strategy_config(self, strategy_name: str) -> dict:
        """Получение полной конфигурации для стратегии.

        Args:
            strategy_name: Название стратегии
        """
        return {
            "settings": self.settings.get_config(),
            "columns": self.columns.get_strategy_columns(strategy_name),
            "strategy": self.strategies.get_strategy(strategy_name),
        }

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

    def get_registry_config(self) -> dict:
        """Получение конфигурации реестра стратегий.

        Returns:
            dict: Конфигурация реестра стратегий
        """
        return self.registry.get_config()
