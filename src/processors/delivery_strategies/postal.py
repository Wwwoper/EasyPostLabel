"""Модуль для обработки почтовых отправлений."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd

from utils.config import ConfigManager
from utils.normalizers import PhoneNormalizer, PostcodeNormalizer
from processors.delivery_strategies.base import DeliveryStrategy

logger = logging.getLogger(__name__)


@dataclass
class PostalClient:
    """Структура данных почтового клиента."""
    postal_index: str
    full_name: str
    phone: str

    @classmethod
    def from_row(cls, row: pd.Series, config: Dict, normalizers: Dict) -> Optional["PostalClient"]:
        """Создание клиента из строки данных."""
        try:
            # Получаем и нормализуем индекс
            index_raw = row.get(config["postal"]["fields"]["index"]["source"])
            postal_index = normalizers["postcode"].normalize(index_raw)
            if not postal_index:
                logger.warning("Пропуск: нет индекса - %s", row.get(config["postal"]["fields"]["name"]["source"]))
                return None

            # Получаем и нормализуем телефон
            phone_raw = row.get(config["postal"]["fields"]["phone"]["source"])
            phone = normalizers["phone"].normalize(phone_raw)
            if not phone:
                logger.warning("Пропуск: нет телефона - %s", row.get(config["postal"]["fields"]["name"]["source"]))
                return None

            # Получаем ФИО
            full_name = str(row.get(config["postal"]["fields"]["name"]["source"], "")).strip()
            if not full_name:
                logger.warning("Пропуск: нет ФИО")
                return None

            return cls(
                postal_index=postal_index,
                full_name=full_name,
                phone=phone
            )

        except Exception as e:
            logger.error("Ошибка создания клиента: %s", str(e))
            return None


class PostalDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки почтовой доставки."""

    def __init__(self, config_manager: ConfigManager):
        """Инициализация стратегии."""
        self.config = config_manager.config["delivery_methods"]["types"]["Почта"]
        self.normalizers = {
            "phone": PhoneNormalizer(),
            "postcode": PostcodeNormalizer()
        }

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о почтовой доставке."""
        try:
            if data.empty:
                return pd.DataFrame()

            logger.debug("Начало обработки почтовых данных")

            # Проверяем наличие всех нужных колонок
            required_columns = self.config["columns"]["required"]
            missing_columns = [
                col for col in required_columns if col not in data.columns
            ]
            if missing_columns:
                raise ValueError(f"Отсутствуют колонки: {', '.join(missing_columns)}")

            # Создаем список клиентов
            clients = []
            for _, row in data.iterrows():
                client = PostalClient.from_row(row, self.config, self.normalizers)
                if client:
                    clients.append(client)

            # Создаем DataFrame
            result = pd.DataFrame(
                [
                    {
                        field["name"]: (
                            getattr(client, field["source"])
                            if "source" in field
                            else field["default"]
                        )
                        for field in self.config["columns"]["output"]
                    }
                    for client in clients
                ]
            )

            return result.drop_duplicates()

        except Exception as e:
            logger.exception("Ошибка при обработке данных: %s", str(e))
            raise

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов."""
        if data.empty:
            return

        try:
            # Используем конфигурацию для сохранения
            output_fields = self.config["columns"]["output"]
            
            # Сохраняем данные
            data.to_excel(output_path, index=False)
            logger.info("Сохранено %d записей в %s", len(data), output_path)

        except Exception as e:
            logger.exception("Ошибка при сохранении: %s", str(e))
            raise
