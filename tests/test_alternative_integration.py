"""Интеграционные тесты для альтернативной стратегии доставки."""

from pathlib import Path

import pandas as pd
from pandas import DataFrame
from tests.conftest import typed_fixture

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@typed_fixture
def input_data() -> DataFrame:
    """Создает тестовые данные."""
    return pd.DataFrame(
        {
            "Фамилия": ["Иванов"],
            "Имя": ["Иван"],
            "Список": ["Магнит"],
            "Кто будет получать заказ": ["Лично я"],
            "Телефон": ["79991234567"],
        }
    )


def test_end_to_end_processing(input_data: DataFrame, tmp_path: Path) -> None:
    """Тест полного цикла обработки данных."""
    # Инициализация
    config = ConfigManager()
    config.config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта России"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "alternative": {"filename": str(tmp_path / "test_labels.xlsx")},
            "postal": {"filename": str(tmp_path / "postal_labels.xlsx")},
        },
    }

    # Создаем процессор
    processor = DeliveryProcessor(input_data, config)
    processor.process()

    assert not processor.alternative_clients.empty
    assert len(processor.alternative_clients) == 1


def test_duplicate_handling(input_data: DataFrame) -> None:
    """Тест обработки дубликатов."""
    # Добавляем дубликат
    duplicate_data = pd.concat([input_data, input_data.iloc[[0]]])

    config = ConfigManager()
    config.config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта России"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "alternative": {"filename": "test_labels.xlsx"},
            "postal": {"filename": "postal_labels.xlsx"},
        },
    }

    processor = DeliveryProcessor(duplicate_data, config)
    processor.process()

    # Проверяем, что дубликаты обработаны
    assert len(processor.alternative_clients) == 1


def test_sorting_order(input_data: DataFrame, tmp_path: Path) -> None:
    """Тест порядка сортировки в выходном файле."""
    config = ConfigManager()
    config.config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта России"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "alternative": {"filename": str(tmp_path / "test_sort.xlsx")},
            "postal": {"filename": str(tmp_path / "postal_labels.xlsx")},
        },
    }

    processor = DeliveryProcessor(input_data, config)
    processor.process()

    assert not processor.alternative_clients.empty
    assert processor.alternative_clients["ФИО"].is_monotonic_increasing


def test_name_formatting(input_data: DataFrame) -> None:
    """Тест форматирования имен."""
    config = ConfigManager()
    config.config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта России"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "alternative": {"filename": "test_labels.xlsx"},
            "postal": {"filename": "postal_labels.xlsx"},
        },
    }

    processor = DeliveryProcessor(input_data, config)
    processor.process()

    assert not processor.alternative_clients.empty
    assert all(name.istitle() for name in processor.alternative_clients["ФИО"])
