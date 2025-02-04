"""Тесты для форматирования данных."""

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest
from pandas import DataFrame
from tests.conftest import typed_fixture

from processors.delivery_processor import DeliveryProcessor
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


def test_phone_number_formatting(config_manager: ConfigManager) -> None:
    """Тест форматирования номеров телефонов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест"] * 4,
            "Список": ["Почта России"] * 4,
            "Телефон": [
                "+7 (999) 123-45-67",
                "8(999)1234567",
                "89991234567",
                "9991234567",
            ],
            "только Индекс отделения для получения.": ["123456"] * 4,
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем форматирование телефонов
    assert not processor.postal_clients.empty
    assert all(len(str(phone)) == 11 for phone in processor.postal_clients["Телефон"])


def test_address_formatting(config_manager: ConfigManager) -> None:
    """Тест форматирования адресов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест"] * 3,
            "Список": ["Почта России"] * 3,
            "Телефон": ["79991234567"] * 3,
            "только Индекс отделения для получения.": [
                " 123456 ",
                "123 456",
                "12345",
            ],
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем форматирование индексов
    assert not processor.postal_clients.empty


def test_name_case_formatting(config_manager: ConfigManager) -> None:
    """Тест форматирования регистра имен."""
    data = pd.DataFrame(
        {
            "Фамилия": ["ИВАНОВ", "иванов", "Иванов"],
            "Имя": ["ИВАН", "иван", "Иван"],
            "Список": ["Магнит"] * 3,
            "Кто будет получать заказ": ["Лично я"] * 3,
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем форматирование имен
    assert not processor.alternative_clients.empty
    assert all(name.istitle() for name in processor.alternative_clients["ФИО"])


def test_special_characters_handling(config_manager: ConfigManager) -> None:
    """Тест обработки специальных символов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": ["Иванов-Петров И.И.", "О'Коннор Джон"],
            "Список": ["Почта России", "Почта России"],
            "Телефон": ["79991234567", "79992345678"],
            "только Индекс отделения для получения.": ["123456", "123456"],
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем обработку специальных символов
    assert not processor.postal_clients.empty
