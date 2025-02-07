"""Модуль для обработки альтернативных способов доставки."""

import logging
from dataclasses import dataclass

import pandas as pd

from processors.delivery_strategies.base import DeliveryStrategy
from utils.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class PickupPointClient:
    """Структура данных клиента пункта выдачи."""
    full_name: str
    pickup_point: str

    @classmethod
    def from_row(cls, row: pd.Series) -> "PickupPointClient":
        """Создание клиента из строки данных."""
        return cls(
            full_name=f"{row.surname} {row.name}",
            pickup_point=row.pickup_point
        )


class PickupPointStrategy(DeliveryStrategy):
    """Стратегия обработки данных для пунктов выдачи."""

    def __init__(self, config_manager: ConfigManager) -> None:
        """Инициализация стратегии."""
        logger.debug("Инициализация стратегии пунктов выдачи")
        self.config_manager = config_manager
        
        # Получаем конфигурацию полей
        self.required_fields = self.config_manager.get_required_fields("Центр_Выдачи")
        self.field_mapping = {
            field["field"]: field["source"] for field in self.required_fields
        }
        
        # Получаем стили
        template = self.config_manager.get_output_template("pickup_point")
        self.styles = template.get("styles", {})
        
        logger.debug("Маппинг полей: %s", self.field_mapping)
        logger.info("Стратегия пунктов выдачи инициализирована")

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных для пунктов выдачи."""
        try:
            logger.debug("Начало обработки данных пунктов выдачи")
            logger.debug("Входные данные:\n%s", data.to_string())

            # Проверяем наличие всех нужных колонок
            source_columns = list(self.field_mapping.values())
            missing_columns = [col for col in source_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Отсутствуют колонки: {', '.join(missing_columns)}")

            # Создаем промежуточный DataFrame
            result = pd.DataFrame()
            for field, source in self.field_mapping.items():
                result[field] = data[source]

            # Преобразуем данные в список клиентов
            clients = [PickupPointClient.from_row(row) for _, row in result.iterrows()]
            logger.debug("Создано клиентов: %d", len(clients))

            # Создаем итоговый DataFrame с нужными колонками
            result = pd.DataFrame([
                {
                    "client_name": client.full_name,
                    "delivery_method": client.pickup_point
                }
                for client in clients
            ])

            logger.debug("Результат обработки:\n%s", result.to_string())
            logger.info("Обработано записей центров выдачи: %d", len(result))

            return result

        except Exception as e:
            logger.exception("Ошибка при обработке данных: %s", str(e))
            raise

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов в файл."""
        if data.empty:
            logger.warning("Нет данных для сохранения")
            return

        try:
            logger.debug("Начало сохранения данных в %s", output_path)
            
            # Сохраняем в Excel
            data.to_excel(output_path, index=False)
            logger.info("Данные сохранены в файл: %s", output_path)
            logger.debug("Сохранено %d записей", len(data))

        except Exception as e:
            logger.exception("Ошибка при сохранении файла: %s", str(e))
            raise
