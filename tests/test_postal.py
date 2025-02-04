"""Тесты для стратегии обработки почтовых отправлений."""

from unittest.mock import patch

import pandas as pd
import pytest

from processors.delivery_strategies.postal import PostalDeliveryStrategy


@pytest.fixture
def postal_strategy():
    """Фикстура для создания стратегии."""
    return PostalDeliveryStrategy()


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными."""
    return pd.DataFrame(
        {
            "Телефон": [
                "89999002291",
                "+79203451508",
                "9203451508",
                "123",  # неверный формат
                None,  # пустое значение
            ],
            "ФИО полностью": ["Тест Тестов"] * 5,
            "только Индекс отделения для получения.": ["123456"] * 5,
        }
    )


def test_normalize_phone(postal_strategy):
    """Тест нормализации телефонных номеров."""
    assert postal_strategy._normalize_phone("89999002291") == "79999002291"
    assert postal_strategy._normalize_phone("+79203451508") == "79203451508"
    assert postal_strategy._normalize_phone("9203451508") == "79203451508"
    assert postal_strategy._normalize_phone("123") == ""
    assert postal_strategy._normalize_phone(None) == ""


def test_process_data(postal_strategy, sample_data):
    """Тест обработки данных."""
    result = postal_strategy.process(sample_data)

    # Проверяем, что все телефоны нормализованы
    expected_phones = [
        "79999002291",
        "79203451508",
        "79203451508",
        "",  # неверный формат
        "",  # было None
    ]

    assert list(result["Телефон"]) == expected_phones


def test_process_dataframe(postal_strategy, sample_data):
    """Тест обработки DataFrame с данными клиентов."""
    processed_df = postal_strategy.process(sample_data)

    # Проверяем, что DataFrame не пустой
    assert not processed_df.empty

    # Проверяем, что все телефоны нормализованы
    expected_phones = [
        "79999002291",
        "79203451508",
        "79203451508",
        "",  # неверный формат
        "",  # было None
    ]
    assert processed_df["Телефон"].tolist() == expected_phones


def test_save_empty_dataframe(postal_strategy, tmp_path):
    """Тест сохранения пустого DataFrame."""
    empty_df = pd.DataFrame()
    output_path = tmp_path / "empty_test.xlsx"

    # Проверяем, что метод не создает файл для пустого DataFrame
    postal_strategy.save(empty_df, output_path)
    assert not output_path.exists()


@patch("builtins.print")
def test_save_valid_dataframe(mock_print, postal_strategy, sample_data, tmp_path):
    """Тест сохранения валидного DataFrame."""
    output_path = tmp_path / "test_output.xlsx"

    # Сохраняем данные
    postal_strategy.save(sample_data, output_path)

    # Проверяем, что файл создан
    assert output_path.exists()

    # Читаем сохраненный файл
    saved_df = pd.read_excel(output_path)

    # Проверяем структуру сохраненных данных
    expected_columns = [
        "recipient_address",
        "recipient_name",
        "weight",
        "recipient_phone",
        "mail_type",
    ]
    assert all(col in saved_df.columns for col in expected_columns)

    # Проверяем количество строк
    assert len(saved_df) == len(sample_data)

    # Проверяем, что были вызваны print statements
    assert mock_print.call_count >= 2
