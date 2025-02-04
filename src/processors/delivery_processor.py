"""Обработчик данных о способах доставки."""

import pandas as pd

from utils.config import ConfigManager
from utils.constants import DEFAULT_OUTPUT_DIR

from .delivery_strategies.alternative import AlternativeDeliveryStrategy
from .delivery_strategies.postal import PostalDeliveryStrategy


class DeliveryProcessor:
    """Обработчик данных о способах доставки."""

    def __init__(self, data: pd.DataFrame, config_manager: ConfigManager):
        """Инициализация обработчика данных о способах доставки."""
        self.data = data
        self.config_manager = config_manager
        self.postal_strategy = PostalDeliveryStrategy()
        self.alternative_strategy = AlternativeDeliveryStrategy()
        self.postal_clients = pd.DataFrame()
        self.alternative_clients = pd.DataFrame()

    def process(self):
        """Обработка данных о способах доставки."""
        # Проверяем, что DataFrame не пустой
        if self.data.empty:
            print("\nПредупреждение: Нет данных для обработки")
            return

        # Получаем конфигурацию для поля delivery_method
        delivery_config = self.config_manager.config.get("columns", {}).get(
            "delivery_method", {}
        )
        delivery_column = delivery_config.get("source")  # "Список"
        postal_keyword = delivery_config.get("validation", {}).get(
            "postal_keyword", "Почта"
        )

        # Проверяем наличие необходимого столбца
        if delivery_column not in self.data.columns:
            print(f"\nОшибка: Отсутствует столбец {delivery_column!r}")
            return

        # Преобразуем столбец в строковый тип
        self.data[delivery_column] = self.data[delivery_column].astype(str)

        # Разделение клиентов по способу доставки
        postal_mask = self.data[delivery_column].str.contains(
            postal_keyword, case=False, na=False
        )

        # Обработка каждой группы своей стратегией
        self.postal_clients = self.postal_strategy.process(self.data[postal_mask])
        self.alternative_clients = self.alternative_strategy.process(
            self.data[~postal_mask]
        )

        # Отладочная информация
        print(f"\nНайдено почтовых клиентов: {len(self.postal_clients)}")
        print(f"Найдено альтернативных клиентов: {len(self.alternative_clients)}")

        if not self.postal_clients.empty:
            print("\nПримеры почтовых клиентов:")
            print(self.postal_clients[["ФИО полностью", "Список", "Телефон"]].head())

    def save_results(self):
        """Сохранение результатов в файлы."""
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)

        # Сохранение почтовых клиентов
        postal_config = self.config_manager.config.get("output", {}).get("postal", {})
        if not self.postal_clients.empty:
            output_path = DEFAULT_OUTPUT_DIR / postal_config["filename"]
            self.postal_strategy.save(self.postal_clients, output_path)
