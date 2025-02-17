"""Менеджер стратегий доставки."""

from pathlib import Path
from typing import Dict, List

import yaml

from .base import BaseConfigManager


class StrategyManager(BaseConfigManager):
    """Менеджер стратегий доставки."""

    def __init__(self, config_path: Path) -> None:
        """Инициализация менеджера стратегий.

        Args:
            config_path: Путь к директории с конфигурациями стратегий
        """
        self.strategies_dir = config_path
        self.strategies: Dict = {}
        self.load_strategies()

    def load_strategies(self) -> None:
        """Загрузка всех стратегий."""
        registry_path = self.strategies_dir / "registry.yaml"
        with open(registry_path, "r", encoding="utf-8") as f:
            self.registry = yaml.safe_load(f) or {}

        for strategy in self.registry["enabled_strategies"]:
            strategy_path = self.strategies_dir / f"{strategy}.yaml"
            with open(strategy_path, "r", encoding="utf-8") as f:
                self.strategies[strategy] = yaml.safe_load(f) or {}

    def get_strategy(self, name: str) -> Dict:
        """Получение конфигурации стратегии.

        Args:
            name: Название стратегии
        """
        mapped_name = self.registry["strategy_mapping"].get(name, name)
        if mapped_name not in self.strategies:
            raise ValueError(f"Неизвестная стратегия: {name}")
        return self.strategies[mapped_name]

    def get_enabled_strategies(self) -> List[str]:
        """Получение списка включенных стратегий."""
        return self.registry["enabled_strategies"]
