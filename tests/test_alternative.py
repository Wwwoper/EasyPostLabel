"""Тесты для альтернативной стратегии доставки."""

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest
from pandas import DataFrame
from tests.conftest import typed_fixture

from processors.delivery_strategies.alternative import AlternativeDeliveryStrategy
from utils.config import ConfigManager


@typed_fixture
def config_manager() -> ConfigManager:
    """Создает менеджер конфигурации."""
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
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }
    return config


@typed_fixture
def alternative_strategy(config_manager: ConfigManager) -> AlternativeDeliveryStrategy:
    """Создает экземпляр стратегии."""
    return AlternativeDeliveryStrategy(config_manager)


def test_data_processing(alternative_strategy: AlternativeDeliveryStrategy) -> None:
    """Тест обработки данных."""
    data = pd.DataFrame(
        {
            "Фамилия": ["Иванов", "Петров"],
            "Имя": ["Иван", "Петр"],
            "Список": ["Магнит", "Пятерочка"],
            "Кто будет получать заказ": ["Лично я", "Лично я"],
        }
    )

    result = alternative_strategy.process(data)
    assert len(result) == 2
    assert "ФИО" in result.columns
    assert "Центр_Выдачи" in result.columns


def test_save_output(
    alternative_strategy: AlternativeDeliveryStrategy, tmp_path: Path
) -> None:
    """Тест сохранения результатов."""
    data = pd.DataFrame(
        {
            "ФИО": ["Иванов Иван", "Петров Петр"],
            "Центр_Выдачи": ["Магнит", "Пятерочка"],
        }
    )

    output_path = tmp_path / "test_output.xlsx"
    alternative_strategy.save(data, str(output_path))
    assert output_path.exists()


def test_empty_data_handling(alternative_strategy: AlternativeDeliveryStrategy) -> None:
    """Тест обработки пустых данных."""
    empty_data = pd.DataFrame()
    result = alternative_strategy.process(empty_data)
    assert result.empty


def test_missing_columns_handling(
    alternative_strategy: AlternativeDeliveryStrategy,
) -> None:
    """Тест обработки данных с отсутствующими столбцами."""
    data = pd.DataFrame({"Неправильный столбец": ["Тест"]})
    result = alternative_strategy.process(data)
    assert result.empty


def test_special_characters_handling(
    alternative_strategy: AlternativeDeliveryStrategy,
) -> None:
    """Тест обработки специальных символов."""
    data = pd.DataFrame(
        {
            "Фамилия": ["Иванов-Петров", "О'Коннор"],
            "Имя": ["Иван", "Джон"],
            "Список": ["Магнит", "Пятерочка"],
            "Кто будет получать заказ": ["Лично я", "Лично я"],
        }
    )

    result = alternative_strategy.process(data)
    assert len(result) == 2
    assert all(isinstance(name, str) for name in result["ФИО"])
