"""Базовый класс для стратегий обработки доставки."""

from abc import ABC, abstractmethod

import pandas as pd


class DeliveryStrategy(ABC):
    """Базовый класс для стратегий обработки доставки."""

    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о доставке.

        Args:
            data: DataFrame с данными клиентов

        Returns:
            DataFrame: Обработанные данные
        """

    @abstractmethod
    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов обработки.

        Args:
            data: DataFrame с обработанными данными
            output_path: Путь для сохранения результатов
        """
