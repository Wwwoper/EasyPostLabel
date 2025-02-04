"""Модуль для обработки Excel файлов."""

from pathlib import Path

import pandas as pd

from utils.config import ConfigManager
from utils.utils import get_client_full_name


class ExcelProcessor:
    """Класс для обработки Excel файлов."""

    def __init__(self, file_path: Path, config_manager: ConfigManager) -> None:
        """Инициализация процессора.

        Args:
            file_path: Путь к файлу Excel
            config_manager: Менеджер конфигурации
        """
        self.file_path = file_path
        self.config_manager = config_manager

    def read_data(self) -> pd.DataFrame:
        """Чтение данных из Excel файла.

        Returns:
            pd.DataFrame: Прочитанные данные

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл не может быть прочитан
        """
        try:
            # Читаем Excel файл, используя первую строку как заголовки
            # и преобразуем все столбцы в строки
            df = pd.read_excel(
                self.file_path,
                sheet_name=self.config_manager.config["excel"]["sheet_index"],
                header=self.config_manager.config["excel"]["header_row"],
                dtype=str,  # Все столбцы читаем как строки
            )

            # Выводим информацию о прочитанных данных
            print("\nТипы данных столбцов:")
            print(df.dtypes)
            print("\nПервые несколько строк:")
            print(df)

            return df

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {str(e)}")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных.

        Args:
            df: DataFrame с данными

        Returns:
            pd.DataFrame: Обработанные данные
        """
        if df.empty:
            return df

        try:
            # Получаем имя поля для определения типа получателя
            receiver_type_field = self.config_manager.get_receiver_type_field()

            # Обрабатываем каждую строку
            result = []
            for _, row in df.iterrows():
                row_dict = row.to_dict()
                # Добавляем поля для получателя заказа, если их нет
                if "Фамилия получателя заказа" not in row_dict:
                    row_dict["Фамилия получателя заказа"] = row_dict["Фамилия"]
                if "Имя получателя заказа" not in row_dict:
                    row_dict["Имя получателя заказа"] = row_dict["Имя"]

                # Создаем словарь с данными клиента
                client_data = {
                    "ФИО": get_client_full_name(row_dict, receiver_type_field),
                    "Телефон": row_dict["Телефон"],
                    "Способ доставки": row_dict["Список"],
                }
                result.append(client_data)

            return pd.DataFrame(result)

        except Exception as e:
            raise ValueError(f"Ошибка обработки данных: {str(e)}")
