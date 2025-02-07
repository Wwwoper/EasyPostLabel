"""Основной модуль приложения для обработки данных о доставке."""

import logging
import sys
from pathlib import Path

import pandas as pd

# Добавляем путь к src в PYTHONPATH
sys.path.append(str(Path(__file__).parent / "src"))

# Все импорты после добавления пути
from processors.delivery_processor import DeliveryProcessor  # noqa: E402
from processors.excel_processor import ExcelProcessor  # noqa: E402
from utils.config import ConfigManager  # noqa: E402


def validate_dataframe(df):
    """Проверяет DataFrame на наличие данных и колонок.

    Args:
        df (pd.DataFrame): DataFrame для проверки

    Raises:
        ValueError: Если DataFrame пустой или не содержит колонок
    """
    if df.empty or len(df.columns) == 0:
        raise ValueError(
            "DataFrame пустой или не содержит колонок. Проверьте входные данные."
        )


def load_data(file_path):
    """Загружает данные из файла в DataFrame.

    Args:
        file_path (str или Path): Путь к файлу с данными

    Returns:
        pd.DataFrame: Загруженные данные

    Raises:
        Exception: При ошибке загрузки или валидации данных
    """
    try:
        if str(file_path).endswith(".csv"):
            df = pd.read_csv(file_path)
        elif str(file_path).endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(
                "Неподдерживаемый формат файла. Используйте .csv или .xlsx"
            )

        validate_dataframe(df)
        return df
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {str(e)}")
        raise


def main() -> None:
    """Основная функция приложения."""
    try:
        # Инициализируем конфигурацию
        config = ConfigManager()

        # Создаем процессор Excel и читаем данные
        input_file = Path("files/new_file.xlsx")

        # Выводим абсолютный путь для отладки
        abs_path = input_file.absolute()
        print(f"\nПуть к файлу: {abs_path}")
        print(f"Файл существует: {input_file.exists()}")

        if not input_file.exists():
            raise FileNotFoundError(f"Файл {input_file} не найден")

        excel_processor = ExcelProcessor(input_file, config)
        df = excel_processor.read_data()

        if df.empty:
            print("\nПредупреждение: DataFrame пустой")
            return

        # Создаем процессор доставки
        delivery_processor = DeliveryProcessor(df, config)

        # Обрабатываем данные
        delivery_processor.process()

        # Сохраняем результаты
        delivery_processor.save_results()

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
