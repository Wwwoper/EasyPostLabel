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
        try:
            if self.data.empty:
                print("\nПредупреждение: Нет данных для обработки")
                return

            # Получаем конфигурацию для поля delivery_method
            delivery_config = self.config_manager.config.get("delivery_methods", {})
            type_column = delivery_config.get("type_column", {})
            delivery_column = type_column.get("source")

            if not delivery_column or delivery_column not in self.data.columns:
                raise ValueError(
                    f"Отсутствует столбец способа доставки: {delivery_column}"
                )

            # Преобразуем столбец в строковый тип
            self.data[delivery_column] = self.data[delivery_column].astype(str)

            # Получаем конфигурацию для почтовой доставки
            postal_config = delivery_config.get("types", {}).get("Почта", {})
            postal_fields = postal_config.get("required_fields", [])

            # Получаем маппинг полей для почты
            postal_field_mapping = {
                field["field"]: field["source"] for field in postal_fields
            }

            # Разделение клиентов по способу доставки
            postal_mask = self.data[delivery_column].str.contains(
                "Почта", case=False, na=False
            )

            # Обработка почтовых клиентов
            postal_data = self.data[postal_mask].copy()
            if not postal_data.empty:
                print("\nПочтовые данные до обработки:")
                print(
                    postal_data[
                        ["Индекс отделения для получения.", "ФИО полностью", "Телефон"]
                    ].head()
                )

                # Проверяем наличие необходимых колонок
                required_columns = [
                    postal_field_mapping["postal_index"],
                    postal_field_mapping["full_name"],
                    postal_field_mapping["phone"],
                ]

                missing_columns = [
                    col for col in required_columns if col not in postal_data.columns
                ]

                if missing_columns:
                    print(
                        f"\nОтсутствуют обязательные колонки для почты: {missing_columns}"
                    )
                else:
                    # Переименовываем колонки в соответствии с маппингом
                    column_mapping = {v: k for k, v in postal_field_mapping.items()}
                    postal_data = postal_data.rename(columns=column_mapping)

                    print("\nПочтовые данные после переименования:")
                    print(postal_data[["postal_index", "full_name", "phone"]].head())

                    self.postal_clients = self.postal_strategy.process(postal_data)

                    # Отладочная информация с новыми именами колонок
                    print(f"\nНайдено почтовых клиентов: {len(self.postal_clients)}")
                    print(
                        f"Найдено альтернативных клиентов: {len(self.alternative_clients)}"
                    )

                    if not self.postal_clients.empty:
                        print("\nПримеры почтовых клиентов:")
                        print(self.postal_clients[["full_name", "phone"]].head())
            else:
                print("\nНет данных для почтовой доставки")

            # Обработка альтернативных клиентов
            alternative_data = self.data[~postal_mask]
            if not alternative_data.empty:
                self.alternative_clients = self.alternative_strategy.process(
                    alternative_data
                )

        except Exception as e:
            print(f"Ошибка при обработке данных: {str(e)}")
            raise

    def save_results(self) -> None:
        """Сохранение результатов в файлы.

        Raises:
            OSError: если директория для сохранения не существует или недоступна
            ValueError: если отсутствует конфигурация вывода
        """
        try:
            # Проверяем существование директории
            if not DEFAULT_OUTPUT_DIR.exists():
                raise OSError(f"Директория {DEFAULT_OUTPUT_DIR} не существует")

            # Получаем конфигурацию шаблонов
            output_templates = self.config_manager.config.get("output", {}).get(
                "templates", {}
            )
            if not output_templates:
                raise ValueError("Отсутствует конфигурация шаблонов вывода")

            # Сохранение почтовых клиентов
            postal_template = output_templates.get("postal", {})
            if not self.postal_clients.empty:
                if "filename" not in postal_template:
                    raise ValueError("Не указано имя файла для почтовых клиентов")

                output_path = DEFAULT_OUTPUT_DIR / postal_template["filename"]
                print(f"\nСохранение почтовых клиентов в {output_path}")
                self.postal_strategy.save(self.postal_clients, str(output_path))

            # Сохранение альтернативных клиентов
            pickup_template = output_templates.get("pickup_point", {})
            if not self.alternative_clients.empty:
                if "filename" not in pickup_template:
                    raise ValueError("Не указано имя файла для альтернативных клиентов")

                output_path = DEFAULT_OUTPUT_DIR / pickup_template["filename"]
                print(f"Сохранение альтернативных клиентов в {output_path}")
                self.alternative_strategy.save(
                    self.alternative_clients, str(output_path)
                )

        except Exception as e:
            print(f"\nОшибка при сохранении результатов: {str(e)}")
            raise
