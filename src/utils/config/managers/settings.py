"""Менеджер глобальных настроек."""

from typing import Any, Dict

from .base import BaseConfigManager


class SettingsManager(BaseConfigManager):
    """Менеджер глобальных настроек."""

    def validate_config(self) -> None:
        """Валидация настроек."""
        required_sections = {"excel", "validation"}
        if not all(section in self.config for section in required_sections):
            raise ValueError("Отсутствуют обязательные секции в настройках")

    def get_excel_settings(self) -> Dict[str, Any]:
        """Получение настроек Excel."""
        return self.config.get("excel", {})

    def get_validation_settings(self) -> Dict[str, Any]:
        """Получение настроек валидации."""
        return self.config.get("validation", {})
