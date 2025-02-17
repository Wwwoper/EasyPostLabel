"""Менеджер конфигурации."""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from .managers import ColumnsManager, SettingsManager, StrategyManager


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

    def get_registry_config(self) -> Dict[str, Any]:
        """Получение конфигурации реестра стратегий.

        Returns:
            Dict[str, Any]: Конфигурация реестра с enabled_strategies и strategy_mapping
        """
        return {
            "enabled_strategies": self.strategies.get_enabled_strategies(),
            "strategy_mapping": self.strategies.registry.get("strategy_mapping", {}),
        }

    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
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
        strategy = self.strategies.get_strategy("pickpoint")
        return strategy["receivers"]["type"]["source"]

    def get_receiver_fields(self, receiver_type: str) -> Dict[str, str]:
        """Получение полей для определенного типа получателя."""
        strategy = self.strategies.get_strategy("pickpoint")
        fields = strategy["receivers"]["fields"].get(receiver_type, {})
        return {str(k): str(v) for k, v in fields.items()}


__all__ = ["ConfigManager", "ReceiverType"]
