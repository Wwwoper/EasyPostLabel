"""Скрипт для создания тестовых данных."""

import pandas as pd
from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Данные для почтовых отправлений
postal_data = pd.DataFrame({
    "Список": ["Почта", "Почта"],
    "ФИО полностью": ["Иванов Иван", "Петров Петр"],
    "Телефон": ["79001234567", "79009876543"],
    "только Индекс отделения для получения.": ["150035", "150030"]
})
postal_data.to_excel(TEST_DATA_DIR / "test_postal.xlsx", index=False)

# Данные для пунктов выдачи
pickup_data = pd.DataFrame({
    "Список": ["Бемби", "Бемби"],
    "Кто будет получать заказ": ["Лично я", "Лично я"],
    "Фамилия": ["Сидоров", "Козлов"],
    "Имя": ["Сидор", "Иван"]
})
pickup_data.to_excel(TEST_DATA_DIR / "test_pickup.xlsx", index=False)

# Смешанные данные
mixed_data = pd.DataFrame({
    "Список": ["Почта", "Бемби"],
    "ФИО полностью": ["Иванов Иван", None],
    "Телефон": ["79001234567", None],
    "только Индекс отделения для получения.": ["150035", None],
    "Кто будет получать заказ": [None, "Лично я"],
    "Фамилия": [None, "Сидоров"],
    "Имя": [None, "Сидор"]
})
mixed_data.to_excel(TEST_DATA_DIR / "test_mixed.xlsx", index=False) 