"""Обработчик Excel файлов."""

from pathlib import Path
from typing import Any, Set, Tuple

import pandas as pd
from openpyxl import load_workbook
from openpyxl.cell import Cell

from utils.config import ConfigManager
from utils.utils import get_client_full_name


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
        """Чтение данных из Excel файла.

        Returns:
            pd.DataFrame: данные из файла

        Raises:
            FileNotFoundError: если файл не найден
            ValueError: если формат файла некорректный
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"Файл не найден: {self.file_path}")

            # Проверяем, что файл не пустой
            if self.file_path.stat().st_size == 0:
                raise ValueError("Файл пуст")

            # Логируем путь к файлу для отладки
            print(f"\nЧтение файла: {self.file_path}")

            excel_config = self.config_manager.config.get("excel", {})
            delivery_config = self.config_manager.config.get("delivery_methods", {})

            if not delivery_config:
                raise ValueError("Отсутствует конфигурация методов доставки")

            # Собираем все необходимые колонки из конфигурации
            required_columns = []
            column_mapping = {}

            # Добавляем колонку типа доставки
            type_column = delivery_config.get("type_column", {})
            if type_column:
                required_columns.append(type_column["source"])
                column_mapping[type_column["source"]] = type_column["column_index"]

            # Собираем колонки для каждого типа доставки
            for delivery_type, type_config in delivery_config.get("types", {}).items():
                required_fields = type_config.get("required_fields", {})

                # Если required_fields это список
                if isinstance(required_fields, list):
                    for field in required_fields:
                        required_columns.append(field["source"])
                        column_mapping[field["source"]] = field["column_index"]

                # Если required_fields это словарь
                elif isinstance(required_fields, dict):
                    # Обрабатываем общие поля
                    common_fields = required_fields.get("common", [])
                    for field in common_fields:
                        required_columns.append(field["source"])
                        column_mapping[field["source"]] = field["column_index"]

                    # Обрабатываем поля для разных типов получателей
                    for receiver_type, fields in required_fields.items():
                        if receiver_type != "common" and isinstance(fields, list):
                            for field in fields:
                                required_columns.append(field["source"])
                                column_mapping[field["source"]] = field["column_index"]

            print("\nНеобходимые колонки:", required_columns)
            print("Маппинг колонок:", column_mapping)

            # Читаем данные через pandas
            df = pd.read_excel(
                self.file_path,
                sheet_name=excel_config.get("sheet_index", 0),
                header=excel_config.get("header_row", 0),
            )

            print("\nДоступные столбцы в файле:", df.columns.tolist())

            if df.empty:
                raise ValueError("DataFrame пустой после чтения")

            # Проверяем наличие необходимых столбцов
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Отсутствуют обязательные столбцы: {missing_columns}")

            return df

        except Exception as e:
            print(f"\nОшибка при чтении файла: {str(e)}")
            raise

    def process_data(self, df: pd.DataFrame | None) -> pd.DataFrame:
        """Обработка данных из Excel файла."""
        if df is None or df.empty:
            return pd.DataFrame()

        # Создаем множества для хранения уникальных записей
        postal_clients_set: Set[Tuple] = set()
        other_clients_set: Set[Tuple] = set()

        # Обрабатываем каждую строку
        for _, row in df.iterrows():
            client_name = get_client_full_name(row, self.config_manager)
            delivery_value = row["Список"]

            # Определяем способ доставки
            delivery = (
                delivery_value
                if "Почта" in delivery_value
                else delivery_value.split()[0]
            )

            if "Почта" in delivery_value:
                # Преобразуем адрес и телефон в целые числа
                postal_address = int(
                    float(row["только Индекс отделения для получения."])
                )
                phone = int(float(row["Телефон"]))

                # Создаем кортеж для уникальной идентификации записи
                postal_record = (client_name, delivery, postal_address, phone)
                postal_clients_set.add(postal_record)
            else:
                # Создаем кортеж для уникальной идентификации записи
                other_record = (client_name, delivery)
                other_clients_set.add(other_record)

        # Преобразуем множества обратно в списки словарей
        postal_clients = [
            {
                "ФИО": record[0],
                "Способ доставки": record[1],
                "Адрес": record[2],
                "Телефон": record[3],
            }
            for record in postal_clients_set
        ]

        other_clients = [
            {"ФИО": record[0], "Способ доставки": record[1]}
            for record in other_clients_set
        ]

        return pd.DataFrame(postal_clients + other_clients)
