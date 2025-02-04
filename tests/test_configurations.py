"""Тесты для различных конфигураций."""

from pathlib import Path
from typing import Dict

import pandas as pd
from pandas import DataFrame

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


def test_multiple_postal_keywords() -> None:
    """Тест обработки нескольких ключевых слов для почты."""
    config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {
                    "postal_keyword": "Post|Mail|Почта",
                },
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    data = pd.DataFrame(
        {
            "Список": ["Post Office", "Mail Service", "Почта России"],
            "ФИО полностью": ["Test1", "Test2", "Test3"],
            "Телефон": ["79991234567", "79992345678", "79993456789"],
            "только Индекс отделения для получения.": ["123456"] * 3,
        }
    )

    manager = ConfigManager()
    manager.config = config

    processor = DeliveryProcessor(data, manager)
    processor.process()

    assert len(processor.postal_clients) == 3


def test_custom_output_format(tmp_path: Path) -> None:
    """Тест пользовательского формата вывода."""
    config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Post"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "postal": {
                "filename": "postal.xlsx",
                "format": {
                    "date_format": "%Y-%m-%d",
                    "phone_format": "+7(###)###-##-##",
                },
            },
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    data = pd.DataFrame(
        {
            "Список": ["Post"],
            "ФИО полностью": ["Test User"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    manager = ConfigManager()
    manager.config = config

    processor = DeliveryProcessor(data, manager)
    processor.process()

    assert len(processor.postal_clients) == 1


def test_unicode_configuration() -> None:
    """Тест конфигурации с Unicode символами."""
    config = {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта"},
            },
            "phone": {"source": "Телефон"},
            "name": {"source": "ФИО полностью"},
        },
        "output": {
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    data = pd.DataFrame(
        {
            "Список": ["Почта России"],
            "ФИО полностью": ["Иванов Иван Иванович"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    manager = ConfigManager()
    manager.config = config

    processor = DeliveryProcessor(data, manager)
    processor.process()

    assert len(processor.postal_clients) == 1
