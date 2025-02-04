"""Тесты для проверки форматирования выходных данных."""

from pathlib import Path

import pandas as pd
import pytest

from processors.delivery_strategies.postal import PostalDeliveryStrategy


@pytest.fixture
def postal_strategy() -> PostalDeliveryStrategy:
    """Фикстура для создания стратегии."""
    return PostalDeliveryStrategy()


def test_output_columns_order(
    postal_strategy: PostalDeliveryStrategy,
    tmp_path: Path,
) -> None:
    """Тест порядка столбцов в выходном файле."""
    df = pd.DataFrame(
        {
            "ФИО полностью": ["Иванов И.И."],
            "Список": ["Почта России"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    output_path = str(tmp_path / "test_output.xlsx")
    postal_strategy.save(df, output_path)

    # Читаем сохраненный файл
    saved_df = pd.read_excel(output_path)

    # Проверяем порядок столбцов
    expected_columns = [
        "recipient_address",
        "recipient_name",
        "weight",
        "recipient_phone",
        "mail_type",
    ]
    assert list(saved_df.columns) == expected_columns


def test_output_data_types(
    postal_strategy: PostalDeliveryStrategy,
    tmp_path: Path,
) -> None:
    """Тест типов данных в выходном файле."""
    df = pd.DataFrame(
        {
            "ФИО полностью": ["Иванов И.И."],
            "Список": ["Почта России"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    output_path = str(tmp_path / "test_output.xlsx")
    postal_strategy.save(df, output_path)

    # Читаем сохраненный файл
    saved_df = pd.read_excel(output_path, dtype=str)

    # Проверяем типы данных
    row = saved_df.iloc[0]
    assert row["recipient_phone"].isdigit()
    assert row["weight"] == "0"
    assert row["mail_type"] == "4"
