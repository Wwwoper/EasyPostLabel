"""Обработчик данных о способах доставки."""

import pandas as pd

from utils.config import ConfigManager
from utils.constants import DEFAULT_OUTPUT_DIR

from .delivery_strategies.alternative import AlternativeDeliveryStrategy
from .delivery_strategies.postal import PostalDeliveryStrategy


class DeliveryProcessor:
    """Обработчик данных о способах доставки."""

    def __init__(self, data: pd.DataFrame, config_manager: ConfigManager) -> None:
        """Инициализация обработчика данных о способах доставки.

        Args:
            data: DataFrame с исходными данными
            config_manager: Менеджер конфигурации
        """
        self.data = data
        self.config_manager = config_manager
        self.postal_strategy = PostalDeliveryStrategy()
        self.alternative_strategy = AlternativeDeliveryStrategy(config_manager)
        self.postal_clients = pd.DataFrame()
        self.alternative_clients = pd.DataFrame()

    def _validate_postal_data(self, data: pd.DataFrame) -> bool:
        """Проверка наличия необходимых полей для почтовой доставки.

        Args:
            data: DataFrame для проверки

        Returns:
            bool: True если все необходимые поля присутствуют
        """
        required_fields = [
            "Телефон",
            "ФИО полностью",
            "только Индекс отделения для получения.",
        ]
        return all(field in data.columns for field in required_fields)

    def process(self) -> None:
        """Обработка данных о способах доставки."""
        # Проверяем, что DataFrame не пустой
        if self.data.empty:
            print("\nПредупреждение: Нет данных для обработки")
            return

        # Получаем конфигурацию для поля delivery_method
        delivery_config = self.config_manager.config.get("columns", {}).get(
            "delivery_method", {}
        )
        delivery_column = delivery_config.get("source")
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

        # Обработка почтовых клиентов
        postal_data = self.data[postal_mask]
        if not postal_data.empty and self._validate_postal_data(postal_data):
            self.postal_clients = self.postal_strategy.process(postal_data)
        else:
            print("\nПредупреждение: Нет данных для почтовой доставки")

        # Обработка альтернативных клиентов
        alternative_data = self.data[~postal_mask]
        if not alternative_data.empty:
            # Копируем столбец delivery_column как "Список" для совместимости
            alternative_data = alternative_data.copy()
            alternative_data["Список"] = alternative_data[delivery_column]
            self.alternative_clients = self.alternative_strategy.process(
                alternative_data
            )

        # Отладочная информация
        print(f"\nНайдено почтовых клиентов: {len(self.postal_clients)}")
        print(f"Найдено альтернативных клиентов: {len(self.alternative_clients)}")

        if not self.postal_clients.empty:
            # Копируем столбец delivery_column как "Список" для отображения
            self.postal_clients = self.postal_clients.copy()
            self.postal_clients["Список"] = self.postal_clients[delivery_column]
            print("\nПримеры почтовых клиентов:")
            print(self.postal_clients[["ФИО полностью", "Список", "Телефон"]].head())

    def save_results(self) -> None:
        """Сохранение результатов в файлы.

        Raises:
            OSError: если директория для сохранения не существует или недоступна
        """
        # Проверяем существование директории перед сохранением
        if not DEFAULT_OUTPUT_DIR.exists():
            raise OSError(f"Директория {DEFAULT_OUTPUT_DIR} не существует")

        # Сохранение почтовых клиентов
        postal_config = self.config_manager.config.get("output", {}).get("postal", {})
        if not self.postal_clients.empty:
            output_path = DEFAULT_OUTPUT_DIR / postal_config["filename"]
            self.postal_strategy.save(self.postal_clients, str(output_path))

        # Сохранение альтернативных клиентов
        alt_config = self.config_manager.config.get("output", {}).get("alternative", {})
        if not self.alternative_clients.empty:
            output_path = DEFAULT_OUTPUT_DIR / alt_config["filename"]
            self.alternative_strategy.save(self.alternative_clients, str(output_path))
