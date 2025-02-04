"""Утилиты для обработки данных."""

from typing import Any

import pandas as pd

from .config import ConfigManager, ReceiverType


def get_client_full_name(row: dict[str, Any], receiver_type_field: str) -> str:
    """Получение полного имени клиента.

    Args:
        row: Словарь с данными клиента
        receiver_type_field: Поле для определения типа получателя

    Returns:
        str: Полное имя клиента
    """
    # Проверяем, что тип получателя валидный
    if receiver_type_field not in [rt.value for rt in ReceiverType]:
        raise ValueError(f"Неизвестный тип получателя: {receiver_type_field}")

    config = ConfigManager()
    fields = config.get_receiver_fields(receiver_type_field)

    surname = row[fields["surname_field"]].strip()
    name = row[fields["name_field"]].strip()

    return f"{surname} {name}"


def read_excel_file(file_path: str, config: ConfigManager) -> pd.DataFrame:
    """Чтение Excel файла с учетом конфигурации.

    Args:
        file_path: путь к Excel файлу
        config: экземпляр ConfigManager с настройками

    Returns:
        DataFrame с данными из Excel
    """
    excel_config = config.get_excel_config()
    sheet_index = excel_config.get("sheet_index", 0)

    # Читаем Excel файл с явным указанием строки заголовков
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_index,
        header=0,  # Первая строка - заголовки
    )

    print("\nВсе столбцы в файле:", df.columns.tolist())
    print("\nПервые несколько строк данных:")
    print(df.head())

    # Получаем маппинг исходных названий столбцов
    column_mapping = config.get_column_mapping()
    print("\nОжидаемые столбцы из конфигурации:", list(column_mapping.values()))

    # Проверяем, есть ли нужные столбцы в файле
    missing_columns = set(column_mapping.values()) - set(df.columns)
    if missing_columns:
        print("\nОтсутствующие столбцы:", missing_columns)

    return df


def process_dataframe(df: pd.DataFrame, config: ConfigManager) -> pd.DataFrame:
    """Обработка DataFrame с добавлением ФИО клиента.

    Args:
        df: pandas DataFrame с данными заказов
        config: экземпляр ConfigManager с настройками

    Returns:
        DataFrame с добавленным столбцом ФИО клиента
    """
    df["ФИО клиента"] = df.apply(
        lambda row: get_client_full_name(row, config.get_receiver_type_field()), axis=1
    )
    return df


def process_excel_file(input_file: str, config: ConfigManager) -> pd.DataFrame:
    """Полная обработка Excel файла.

    Args:
        input_file: путь к входному Excel файлу
        config: экземпляр ConfigManager с настройками

    Returns:
        DataFrame с обработанными данными
    """
    # Читаем Excel файл
    df = read_excel_file(input_file, config)

    # Обрабатываем данные
    df = process_dataframe(df, config)

    return df
