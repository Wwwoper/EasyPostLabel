"""Менеджер конфигурации колонок."""

from collections import defaultdict
from typing import Any, Dict

from .base import BaseConfigManager


class ColumnsManager(BaseConfigManager):
    """Менеджер конфигурации колонок."""

    def validate_config(self) -> None:
        """Валидация конфигурации колонок."""
        if not isinstance(self.config, dict):
            raise ValueError("Неверный формат конфигурации колонок")

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = "") -> Dict[str, Dict]:
        """Преобразование вложенного словаря в плоский.

        Args:
            d: Вложенный словарь
            parent_key: Ключ родителя для формирования полного пути

        Returns:
            Dict: Плоский словарь с полными путями в качестве ключей
        """
        items: Dict[str, Dict] = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict) and not all(
                key in v for key in ["source", "excel_column"]
            ):
                items.update(self._flatten_dict(v, new_key))
            else:
                items[new_key] = v
        return items

    def get_strategy_columns(self, strategy: str) -> Dict:
        """Получение конфигурации колонок для стратегии.

        Args:
            strategy: Название стратегии (postal/pickpoint)

        Returns:
            Dict: Конфигурация колонок для стратегии
        """
        strategy_key = f"{strategy}_columns"
        strategy_columns = self.config.get(strategy_key, {})

        # Преобразуем вложенную структуру в плоскую
        flattened_columns = self._flatten_dict(strategy_columns)

        # Фильтруем только колонки с полной конфигурацией
        return {
            k: v
            for k, v in flattened_columns.items()
            if isinstance(v, dict) and "source" in v and "excel_column" in v
        }

    def get_column_config(self, strategy: str, column_name: str) -> Dict:
        """Получение конфигурации конкретной колонки.

        Args:
            strategy: Название стратегии
            column_name: Название колонки

        Returns:
            Dict: Конфигурация колонки
        """
        columns = self.get_strategy_columns(strategy)
        return columns.get(column_name, {})
