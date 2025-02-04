"""Интеграционные тесты для альтернативной доставки."""

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def input_data():
    """Фикстура с входными данными."""
    return pd.DataFrame(
        {
            "Кто будет получать заказ": ["Лично я", "Другой человек", "Лично я"],
            "Фамилия": ["иванов", "Сидоров", "КУЗНЕЦОВ"],
            "Имя": ["иван", None, "ПЕТР"],
            "Фамилия получателя заказа": [None, "Петров", None],
            "Имя получателя заказа": [None, "Иван", None],
            "Список": ["Магнит Доставка", "Пятерочка Центр", "Магнит Север"],
        }
    )


def test_end_to_end_processing(input_data, tmp_path):
    """Тест полного цикла обработки данных."""
    # Инициализация
    config = ConfigManager()
    config.config["output"]["alternative"]["filename"] = "test_labels.xlsx"

    # Создаем процессор
    processor = DeliveryProcessor(input_data, config)

    # Подменяем путь сохранения
    import processors.delivery_processor as dp

    original_dir = dp.DEFAULT_OUTPUT_DIR
    dp.DEFAULT_OUTPUT_DIR = tmp_path

    try:
        # Обработка данных
        processor.process()
        processor.save_results()

        # Проверяем результаты
        output_path = tmp_path / "test_labels.xlsx"
        assert output_path.exists()

        # Проверяем содержимое файла
        result_df = pd.read_excel(
            output_path,
            sheet_name="Список доставки",
            skiprows=3,  # Пропускаем заголовок и пустую строку
            usecols=[1, 2]  # Читаем только столбцы с ФИО и центром выдачи
        )
        assert len(result_df) > 0

        # Проверяем форматирование данных
        # Проверяем, что каждое слово в имени начинается с заглавной буквы
        for name in result_df.iloc[:, 0]:
            if pd.isna(name):  # Пропускаем пустые значения
                continue
            parts = str(name).split()
            assert all(part[0].isupper() and part[1:].islower() for part in parts), \
                f"Неправильный формат имени: {name}"

        # Проверяем формат центра выдачи
        for center in result_df.iloc[:, 1]:
            if pd.isna(center):  # Пропускаем пустые значения
                continue
            center_str = str(center)
            assert center_str.startswith("в ЦВ"), \
                f"Центр выдачи должен начинаться с 'в ЦВ': {center_str}"
            center_name = center_str.split()[-1]
            assert center_name[0].isupper() and center_name[1:].islower(), \
                f"Название центра должно быть с заглавной буквы: {center_name}"

    finally:
        dp.DEFAULT_OUTPUT_DIR = original_dir


def test_duplicate_handling(input_data, tmp_path):
    """Тест обработки дубликатов."""
    # Добавляем дубликат
    duplicate_data = pd.concat([input_data, input_data.iloc[[0]]])

    config = ConfigManager()
    processor = DeliveryProcessor(duplicate_data, config)
    processor.process()

    # Проверяем, что дубликаты обработаны корректно
    assert len(processor.alternative_clients) == len(
        processor.alternative_clients["ФИО"].unique()
    )


def test_sorting_order(input_data, tmp_path):
    """Тест порядка сортировки в выходном файле."""
    config = ConfigManager()
    config.config["output"]["alternative"]["filename"] = "test_sort.xlsx"

    processor = DeliveryProcessor(input_data, config)

    # Подменяем путь сохранения
    import processors.delivery_processor as dp

    original_dir = dp.DEFAULT_OUTPUT_DIR
    dp.DEFAULT_OUTPUT_DIR = tmp_path

    try:
        processor.process()
        processor.save_results()

        # Проверяем сортировку в файле
        result_df = pd.read_excel(
            tmp_path / "test_sort.xlsx",
            sheet_name="Список доставки",
            skiprows=3,  # Пропускаем заголовок и пустую строку
            names=["ФИО", "Центр_Выдачи"],  # Задаем имена столбцов
        )

        # Проверяем, что данные отсортированы сначала по центру выдачи, потом по ФИО
        sorted_df = result_df.sort_values(["Центр_Выдачи", "ФИО"])
        pd.testing.assert_frame_equal(result_df, sorted_df)

    finally:
        dp.DEFAULT_OUTPUT_DIR = original_dir


def test_name_formatting(input_data):
    """Тест форматирования имен."""
    config = ConfigManager()
    processor = DeliveryProcessor(input_data, config)
    processor.process()

    # Проверяем правильность форматирования имен
    for name in processor.alternative_clients["ФИО"]:
        parts = name.split()
        assert len(parts) == 2  # Должны быть только фамилия и имя
        assert all(part.istitle() for part in parts)  # Каждое слово с заглавной
