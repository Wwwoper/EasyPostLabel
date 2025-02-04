"""Тесты для проверки различных конфигураций."""

from pathlib import Path

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Фикстура с тестовыми данными."""
    return pd.DataFrame(
        {
            "Способ_доставки": ["Post", "Alternative"],
            "Customer_Name": ["Иванов И.И.", "Петров П.П."],
            "Phone": ["79991234567", "79992345678"],
            "PostCode": ["123456", None],
            "только Индекс отделения для получения.": ["123456", None],
            "ФИО полностью": ["Иванов И.И.", "Петров П.П."],
            "Телефон": ["79991234567", "79992345678"],
        }
    )


def test_custom_column_names(sample_data: pd.DataFrame) -> None:
    """Тест работы с нестандартными именами столбцов."""
    config = {
        "columns": {
            "delivery_method": {
                "source": "Способ_доставки",
                "validation": {"postal_keyword": "Post"},
            },
            "name": {"source": "Customer_Name"},
            "phone": {"source": "Phone"},
            "postcode": {"source": "PostCode"},
        },
        "output": {
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    manager = ConfigManager()
    manager.config = config

    processor = DeliveryProcessor(sample_data, manager)
    processor.process()

    assert len(processor.postal_clients) == 1
    assert len(processor.alternative_clients) == 1


def test_multiple_postal_keywords() -> None:
    """Тест обработки нескольких ключевых слов для почты."""
    config = {
        "columns": {
            "delivery_method": {
                "source": "Способ_доставки",
                "validation": {
                    "postal_keyword": "Post|Mail|Почта",  # Используем regex
                },
            }
        },
        "output": {
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    data = pd.DataFrame(
        {
            "Способ_доставки": ["Post Office", "Mail Service", "Почта России"],
            "ФИО полностью": ["Test1", "Test2", "Test3"],
            "Телефон": ["79991234567", "79992345678", "79993456789"],
            "только Индекс отделения для получения.": ["123456", "123457", "123458"],
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
                "source": "Способ_доставки",
                "validation": {"postal_keyword": "Post"},
            }
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
            "Способ_доставки": ["Post"],
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
                "source": "Способ_доставки",
                "validation": {"postal_keyword": "Почта"},
            }
        },
        "output": {
            "postal": {"filename": "postal.xlsx"},
            "alternative": {"filename": "alternative.xlsx"},
        },
    }

    data = pd.DataFrame(
        {
            "Способ_доставки": ["Почта России"],
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
