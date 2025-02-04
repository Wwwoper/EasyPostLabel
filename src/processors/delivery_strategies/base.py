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
        pass
    
    @abstractmethod
    def save(self, data: pd.DataFrame, output_dir: str):
        """Сохранение результатов обработки.
        
        Args:
            data: DataFrame с обработанными данными
            output_dir: Путь для сохранения результатов
        """
        pass 