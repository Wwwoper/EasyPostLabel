"""Валидатор входных данных."""

import re
from typing import Any, Dict

import pandas as pd

from utils.config import ConfigManager


class DataValidator:
    """Валидатор входных данных."""

    def __init__(self, config_manager: ConfigManager):
        """Инициализация валидатора.

        Args:
            config_manager: Менеджер конфигурации
        """
        self.config_manager = config_manager
        self.error_message = ""

    def validate(self, data: pd.DataFrame) -> bool:
        """Валидация входных данных на основе конфигурации.

        Args:
            data: DataFrame с данными для проверки

        Returns:
            bool: результат валидации
        """
        # Проверка наличия обязательных колонок
        required_columns = self.config_manager.get_required_columns()
        column_mapping = self.config_manager.get_column_mapping()

        for column in required_columns:
            source_column = column_mapping.get(column)
            if source_column not in data.columns:
                self.error_message = (
                    f"Отсутствует обязательный столбец: {source_column}"
                )
                return False

        # Валидация данных по правилам
        for column in required_columns:
            source_column = column_mapping.get(column)
            rules = self.config_manager.get_validation_rules(column)

            if not self._validate_column(data[source_column], rules):
                return False

        return True

    def _validate_column(self, series: pd.Series, rules: Dict[str, Any]) -> bool:
        """Валидация столбца по правилам."""
        if rules.get("min_length"):
            if (series.str.len() < rules["min_length"]).any():
                self.error_message = (
                    f"Значение короче минимальной длины ({rules['min_length']})"
                )
                return False

        if rules.get("max_length"):
            if (series.str.len() > rules["max_length"]).any():
                self.error_message = (
                    f"Значение длиннее максимальной длины ({rules['max_length']})"
                )
                return False

        if rules.get("pattern"):
            pattern = re.compile(rules["pattern"])
            if not series.str.match(pattern).all():
                self.error_message = "Значение не соответствует формату"
                return False

        if rules.get("allowed_values"):
            if not series.isin(rules["allowed_values"]).all():
                self.error_message = (
                    f"Недопустимое значение. Разрешены: {rules['allowed_values']}"
                )
                return False

        return True

    def get_error_message(self) -> str:
        """Получение сообщения об ошибке."""
        return self.error_message

    @staticmethod
    def validate_input_data(df):
        """Проверяет входные данные на корректность"""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Входные данные должны быть DataFrame")

        if df.empty:
            raise ValueError("DataFrame не должен быть пустым")

        required_columns = ["column1", "column2"]  # Укажите необходимые колонки
        missing_columns = set(required_columns) - set(df.columns)

        if missing_columns:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")

        return True
