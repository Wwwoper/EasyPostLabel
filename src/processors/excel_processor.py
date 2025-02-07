"""Обработчик Excel файлов."""

from pathlib import Path
from typing import Any, Set, Tuple, List, Optional

import pandas as pd
from openpyxl import load_workbook
from openpyxl.cell import Cell
import logging
from dataclasses import dataclass

from utils.config import ConfigManager
from utils.utils import get_client_full_name

logger = logging.getLogger(__name__)


@dataclass
class PostalClient:
    """Данные почтового клиента."""
    name: str
    delivery: str
    address: int
    phone: int

@dataclass
class PickupClient:
    """Данные клиента центра выдачи."""
    name: str
    delivery: str

class ExcelProcessor:
    """Обработчик Excel файлов."""

    def __init__(self, file_path: Path, config_manager: ConfigManager) -> None:
        """Инициализация обработчика Excel файлов.

        Args:
            file_path: Путь к файлу
            config_manager: Менеджер конфигурации
        """
        self.file_path = file_path
        self.config_manager = config_manager
        self.df: pd.DataFrame | None = None

    def _get_cell_value(self, cell: Cell, col_config: dict[str, Any]) -> str:
        """Получение значения ячейки с учетом её типа.

        Args:
            cell: Ячейка Excel
            col_config: Конфигурация столбца

        Returns:
            str: Значение ячейки в виде строки
        """
        value = cell.value

        if cell.data_type == "n" and value is not None:
            value = str(int(value))
        elif hasattr(cell, "number_format") and "General" not in cell.number_format:
            try:
                value = cell.internal_value
            except Exception:
                pass

            value = str(value).strip() if value is not None else ""

        # Специальная обработка для поля "Кто будет получать заказ"
        if col_config["source"] == "Кто будет получать заказ" and any(
            x in str(value) for x in ["-", ":", "."]
        ):
            if isinstance(value, (int, float)):
                return ""
        return str(value) if value is not None else ""

    def read_data(self) -> pd.DataFrame:
        """Чтение данных из Excel файла."""
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"Файл не найден: {self.file_path}")

            if self.file_path.stat().st_size == 0:
                raise ValueError("Файл пуст")

            logger.debug("Чтение файла: %s", self.file_path)

            # Получаем конфигурацию
            excel_config = self.config_manager.config.get("excel", {})
            required_columns = self._get_required_columns()

            # Читаем данные
            df = pd.read_excel(
                self.file_path,
                sheet_name=excel_config.get("sheet_index", 0),
                header=excel_config.get("header_row", 0),
            )

            if df.empty:
                raise ValueError("DataFrame пустой после чтения")

            # Проверяем колонки
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Отсутствуют колонки: {missing_columns}")

            return df

        except Exception as e:
            logger.exception("Ошибка чтения файла: %s", str(e))
            raise

    def _get_required_columns(self) -> list[str]:
        """Получение списка необходимых колонок."""
        delivery_config = self.config_manager.config.get("delivery_methods", {})
        
        columns = []
        # Добавляем колонку типа доставки
        type_column = delivery_config.get("type_column", {})
        if type_column:
            columns.append(type_column["source"])

        # Добавляем колонки для каждого типа доставки
        for type_config in delivery_config.get("types", {}).values():
            fields = type_config.get("required_fields", {})
            if isinstance(fields, list):
                columns.extend(f["source"] for f in fields)
            elif isinstance(fields, dict):
                for field_list in fields.values():
                    if isinstance(field_list, list):
                        columns.extend(f["source"] for f in field_list)

        return list(set(columns))  # Убираем дубликаты

    def _create_postal_client(self, row: pd.Series) -> Optional[PostalClient]:
        """Создание почтового клиента из строки данных."""
        try:
            return PostalClient(
                name=get_client_full_name(row, self.config_manager),
                delivery=row["Список"],
                address=int(float(row["только Индекс отделения для получения."])),
                phone=int(float(row["Телефон"]))
            )
        except Exception as e:
            logger.error("Ошибка создания почтового клиента: %s", str(e))
            return None

    def _create_pickup_client(self, row: pd.Series) -> Optional[PickupClient]:
        """Создание клиента центра выдачи из строки данных."""
        try:
            return PickupClient(
                name=get_client_full_name(row, self.config_manager),
                delivery=row["Список"].split()[0]
            )
        except Exception as e:
            logger.error("Ошибка создания клиента центра выдачи: %s", str(e))
            return None

    def process_data(self, df: pd.DataFrame | None) -> pd.DataFrame:
        """Обработка данных из Excel файла."""
        if df is None or df.empty:
            return pd.DataFrame()

        postal_clients: List[PostalClient] = []
        pickup_clients: List[PickupClient] = []

        for _, row in df.iterrows():
            if "Почта" in row["Список"]:
                if client := self._create_postal_client(row):
                    postal_clients.append(client)
            else:
                if client := self._create_pickup_client(row):
                    pickup_clients.append(client)

        # Создаем DataFrame из обработанных данных
        result_data = []
        
        # Добавляем почтовых клиентов
        result_data.extend([
            {
                "ФИО": client.name,
                "Способ доставки": client.delivery,
                "Адрес": client.address,
                "Телефон": client.phone
            }
            for client in postal_clients
        ])

        # Добавляем клиентов центров выдачи
        result_data.extend([
            {
                "ФИО": client.name,
                "Способ доставки": client.delivery
            }
            for client in pickup_clients
        ])

        return pd.DataFrame(result_data).drop_duplicates()
