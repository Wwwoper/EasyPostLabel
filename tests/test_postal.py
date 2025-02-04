"""Тесты для проверки почтовой доставки."""

import pandas as pd
import pytest

from processors.delivery_strategies.postal import PostalDeliveryStrategy


@pytest.fixture
def postal_strategy() -> PostalDeliveryStrategy:
    """Фикстура для создания стратегии."""
    return PostalDeliveryStrategy()


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Фикстура с тестовыми данными."""
    return pd.DataFrame(
        {
            "ФИО полностью": ["Иванов И.И."],
            "Список": ["Почта России"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )


def test_phone_normalization(postal_strategy: PostalDeliveryStrategy) -> None:
    """Тест нормализации телефонных номеров."""
    # Тестовые номера
    test_phones = [
        "+7 (999) 123-45-67",  # Форматированный номер
        "8(999)1234567",  # Номер с 8
        "89991234567",  # Номер с 8 без форматирования
        "9991234567",  # Номер без 7/8
    ]

    # Проверяем каждый номер
    for phone in test_phones:
        normalized = postal_strategy._normalize_phone(phone)
        assert len(normalized) == 11
        assert normalized.startswith("7")
        assert normalized.isdigit()


def test_postcode_normalization(postal_strategy: PostalDeliveryStrategy) -> None:
    """Тест нормализации почтовых индексов."""
    # Тестовые индексы
    test_postcodes = [
        " 123456 ",  # Пробелы
        "123 456",  # Разделитель
        "12345",  # Короткий индекс
        "1234567",  # Длинный индекс
    ]

    # Проверяем каждый индекс
    for postcode in test_postcodes:
        normalized = postal_strategy._normalize_postcode(postcode)
        if normalized:  # Если индекс валидный
            assert len(normalized) == 6
            assert normalized.isdigit()


def test_data_processing(
    postal_strategy: PostalDeliveryStrategy,
    sample_data: pd.DataFrame,
) -> None:
    """Тест обработки данных."""
    processed_data = postal_strategy.process(sample_data)

    # Проверяем, что данные не пустые
    assert not processed_data.empty

    # Проверяем нормализацию телефонов
    assert all(
        phone.startswith("7") and len(phone) == 11
        for phone in processed_data["Телефон"]
    )

    # Проверяем нормализацию индексов
    assert all(
        len(str(postcode)) == 6 and str(postcode).isdigit()
        for postcode in processed_data["только Индекс отделения для получения."]
    )


def test_empty_data_handling(postal_strategy: PostalDeliveryStrategy) -> None:
    """Тест обработки пустых данных."""
    empty_df = pd.DataFrame()
    processed_data = postal_strategy.process(empty_df)
    assert processed_data.empty


def test_invalid_data_handling(postal_strategy: PostalDeliveryStrategy) -> None:
    """Тест обработки некорректных данных."""
    invalid_data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест"],
            "Список": ["Почта России"],
            "Телефон": ["не номер"],
            "только Индекс отделения для получения.": ["не индекс"],
        }
    )

    processed_data = postal_strategy.process(invalid_data)
    assert processed_data["Телефон"].iloc[0] == ""
    assert processed_data["только Индекс отделения для получения."].iloc[0] == ""
