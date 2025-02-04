"""Обработчик Excel файлов."""

from pathlib import Path
from typing import Dict, List, Set, Tuple

import pandas as pd
from openpyxl import load_workbook

from utils.config import ConfigManager
from utils.utils import get_client_full_name


class ExcelProcessor:
    """Обработчик Excel файлов."""

    def __init__(self, file_path: Path, config_manager: ConfigManager):
        """Инициализация обработчика Excel файлов.

        Args:
            file_path: Путь к файлу
            config_manager: Менеджер конфигурации
        """
        self.file_path = file_path
        self.config_manager = config_manager
        self.df: pd.DataFrame | None = None

    def _get_cell_value(self, cell, col_config: dict) -> str:
        """Получение значения ячейки с учетом её типа."""
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
            x in value for x in ["-", ":", "."]
        ):
            if isinstance(value, (int, float)):
                return ""
        return value

    def read_data(self) -> pd.DataFrame:
        """Чтение данных из Excel файла.

        Returns:
            pd.DataFrame: данные из файла

        Raises:
            FileNotFoundError: если файл не найден
            ValueError: если формат файла некорректный
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")

        try:
            excel_config = self.config_manager.config.get("excel", {})
            columns_config = self.config_manager.config.get("columns", {})

            # Читаем данные через openpyxl
            wb = load_workbook(self.file_path, data_only=True)
            ws = wb.worksheets[excel_config.get("sheet_index", 0)]

            # Создаем словарь для данных
            data = []

            # Читаем данные начиная со строки start_row
            start_row = excel_config.get("start_row", 1)
            for row in ws.iter_rows(min_row=start_row):
                row_data = {}
                for _, col_config in columns_config.items():
                    # Получаем значение из нужной колонки (column_index начинается с 1)
                    cell = row[col_config["column_index"] - 1]

                    # Получаем значение в зависимости от типа ячейки
                    row_data[col_config["source"]] = self._get_cell_value(
                        cell, col_config
                    )

                data.append(row_data)

            # Создаем DataFrame из списка словарей
            self.df = pd.DataFrame(data)

            # Отладочная информация
            print("\nТипы данных столбцов:")
            print(self.df.dtypes)
            print("\nПервые несколько строк:")
            print(self.df.head())

            return self.df
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {str(e)}") from e

    def process_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Обработка данных из файла.

        Returns:
            Tuple[List[Dict], List[Dict]]: кортеж из двух списков -
            почтовые клиенты и остальные клиенты
        """
        if self.df is None:
            self.read_data()

        # Создаем множества для хранения уникальных записей
        postal_clients_set: Set[Tuple] = set()
        other_clients_set: Set[Tuple] = set()

        # Обрабатываем каждую строку
        for _, row in self.df.iterrows():
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

        return postal_clients, other_clients
