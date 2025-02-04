"""Альтернативная стратегия доставки."""

import pandas as pd

from .base import DeliveryStrategy


class AlternativeDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки альтернативной доставки."""

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных об альтернативной доставке."""
        # Логика обработки альтернативных клиентов
        return data

    def save(self, data: pd.DataFrame, output_dir: str):
        """Сохранение результатов в формате для альтернативной доставки."""
        # Логика сохранения в labels.xlsx
        pass  # Логика сохранения в labels.xlsx
