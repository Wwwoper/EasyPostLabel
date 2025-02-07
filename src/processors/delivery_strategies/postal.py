"""Модуль для обработки почтовых отправлений."""

import pandas as pd
from typing import Optional

from processors.delivery_strategies.base import DeliveryStrategy
from utils.normalizers import PhoneNormalizer, PostcodeNormalizer
import logging

logger = logging.getLogger(__name__)


class PostalDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки почтовой доставки."""

    HEADERS = [
        "recipient_address",
        "recipient_name",
        "weight",
        "recipient_phone",
        "mail_type",
    ]

    COLUMN_MAPPING = {
        "Телефон": "phone",
        "ФИО полностью": "full_name",
        "Индекс отделения для получения.": "postal_index"
    }

    def __init__(self):
        """Инициализация стратегии."""
        self.phone_normalizer = PhoneNormalizer()
        self.postcode_normalizer = PostcodeNormalizer()

    def _create_postal_row(self, client: dict) -> Optional[list]:
        """Создание строки для почтовой таблицы."""
        try:
            index = self.postcode_normalizer.normalize(client.get("postal_index"))
            if not index:
                logger.warning("Пропуск: нет индекса - %s", client.get("full_name"))
                return None

            phone = self.phone_normalizer.normalize(client.get("phone"))
            if not phone:
                logger.warning("Пропуск: нет телефона - %s", client.get("full_name"))
                return None

            return [
                index,
                client.get("full_name", ""),
                "0",
                phone,
                "4",
            ]
        except Exception as e:
            logger.error("Ошибка создания строки: %s", str(e))
            return None

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о почтовой доставке."""
        if data.empty:
            return pd.DataFrame()

        try:
            # Сначала переименовываем колонки
            processed_data = data.rename(columns=self.COLUMN_MAPPING)

            # Затем нормализуем данные
            processed_data["phone"] = processed_data["phone"].apply(
                self.phone_normalizer.normalize
            )
            processed_data["postal_index"] = processed_data["postal_index"].apply(
                self.postcode_normalizer.normalize
            )

            # Удаляем строки с пустыми значениями
            processed_data = processed_data.dropna(
                subset=["phone", "postal_index", "full_name"]
            )

            return processed_data

        except Exception as e:
            logger.exception("Ошибка обработки данных: %s", str(e))
            return pd.DataFrame()

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов."""
        if data.empty:
            return

        try:
            clients = data[["postal_index", "full_name", "phone"]].to_dict("records")
            postal_rows = [row for client in clients if (row := self._create_postal_row(client))]

            if not postal_rows:
                raise ValueError("Нет данных для сохранения после валидации")

            df_postal = pd.DataFrame(postal_rows, columns=self.HEADERS)
            df_postal.to_excel(output_path, index=False)
            logger.info("Сохранено %d записей в %s", len(df_postal), output_path)

        except Exception as e:
            logger.exception("Ошибка при сохранении: %s", str(e))
            raise
