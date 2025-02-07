"""Обработчик данных о способах доставки."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from utils.config import ConfigManager
from utils.paths import DEFAULT_OUTPUT_DIR
from utils.exceptions import ProcessingError
from .delivery_strategies.pickup_point import PickupPointStrategy
from .delivery_strategies.postal import PostalDeliveryStrategy

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Результаты обработки данных."""
    postal_clients: pd.DataFrame
    pickup_clients: pd.DataFrame
    success: bool
    error: Optional[str] = None
    stats: Dict[str, int] = None

    def __post_init__(self):
        """Инициализация статистики."""
        if self.stats is None:
            self.stats = {
                "total": 0,
                "postal": 0,
                "pickup": 0,
                "errors": 0
            }


class DeliveryProcessor:
    """Обработчик данных о способах доставки."""

    def __init__(self, data: pd.DataFrame, config_manager: ConfigManager) -> None:
        """Инициализация обработчика."""
        self.data = data
        self.config_manager = config_manager
        self.postal_strategy = PostalDeliveryStrategy(config_manager)
        self.pickup_strategy = PickupPointStrategy(config_manager)
        self.result = ProcessingResult(
            postal_clients=pd.DataFrame(),
            pickup_clients=pd.DataFrame(),
            success=False
        )

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

    def _validate_delivery_column(self) -> Tuple[bool, Optional[str]]:
        """Проверка столбца способа доставки."""
        try:
            delivery_config = self.config_manager.config.get("delivery_methods", {})
            type_column = delivery_config.get("type_column", {})
            delivery_column = type_column.get("source")

            if not delivery_column or delivery_column not in self.data.columns:
                return False, f"Отсутствует столбец способа доставки: {delivery_column}"

            self.data[delivery_column] = self.data[delivery_column].astype(str)
            return True, None

        except Exception as e:
            return False, str(e)

    def _split_clients(self, delivery_column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Разделение клиентов по способу доставки."""
        postal_mask = self.data[delivery_column].str.contains("Почта", case=False, na=False)
        return self.data[postal_mask].copy(), self.data[~postal_mask].copy()

    def _process_postal_clients(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка почтовых клиентов."""
        try:
            if data.empty:
                return pd.DataFrame()

            logger.info("Начало обработки почтовых клиентов")
            result = self.postal_strategy.process(data)
            
            if not result.empty:
                self.result.stats["postal"] = len(result)
                logger.info("Обработано почтовых клиентов: %d", len(result))
            
            return result

        except Exception as e:
            self.result.stats["errors"] += 1
            logger.exception("Ошибка обработки почтовых клиентов: %s", str(e))
            raise ProcessingError("Ошибка обработки почтовых клиентов") from e

    def _process_pickup_clients(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка клиентов центров выдачи."""
        try:
            if data.empty:
                return pd.DataFrame()

            logger.info("Начало обработки клиентов центров выдачи")
            result = self.pickup_strategy.process(data)
            
            if not result.empty:
                self.result.stats["pickup"] = len(result)
                logger.info("Обработано клиентов центров выдачи: %d", len(result))
            
            return result

        except Exception as e:
            self.result.stats["errors"] += 1
            logger.exception("Ошибка обработки клиентов центров выдачи: %s", str(e))
            raise ProcessingError("Ошибка обработки клиентов центров выдачи") from e

    def process(self) -> ProcessingResult:
        """Обработка данных о способах доставки."""
        try:
            if self.data.empty:
                raise ProcessingError("Нет данных для обработки")

            # Проверяем столбец доставки
            valid, error = self._validate_delivery_column()
            if not valid:
                raise ProcessingError(error or "Ошибка валидации столбца доставки")

            # Разделяем и обрабатываем клиентов
            postal_data, pickup_data = self._split_clients(
                self.config_manager.config["delivery_methods"]["type_column"]["source"]
            )

            # Обрабатываем данные
            self.result.postal_clients = self._process_postal_clients(postal_data)
            self.result.pickup_clients = self._process_pickup_clients(pickup_data)

            # Обновляем статистику
            self.result.stats["total"] = len(self.data)
            self.result.success = True

            logger.info("Обработка завершена успешно. Статистика: %s", self.result.stats)
            return self.result

        except Exception as e:
            self.result.error = str(e)
            logger.exception("Ошибка обработки данных: %s", str(e))
            return self.result

    def save_results(self) -> bool:
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

            # Сохраняем результаты
            if not self.result.postal_clients.empty:
                output_path = DEFAULT_OUTPUT_DIR / output_templates["postal"]["filename"]
                self.postal_strategy.save(self.result.postal_clients, str(output_path))
                logger.info("Сохранены почтовые клиенты: %s", output_path)

            if not self.result.pickup_clients.empty:
                output_path = DEFAULT_OUTPUT_DIR / output_templates["pickup_point"]["filename"]
                self.pickup_strategy.save(self.result.pickup_clients, str(output_path))
                logger.info("Сохранены клиенты центров выдачи: %s", output_path)

            return True

        except Exception as e:
            logger.exception("Ошибка сохранения результатов: %s", str(e))
            return False
