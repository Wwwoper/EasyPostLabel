"""Тесты для проверки форматирования данных."""

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def config_manager() -> ConfigManager:
    """Фикстура для создания менеджера конфигурации."""
    return ConfigManager()


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

    # Проверяем, что все номера приведены к формату 79XXXXXXXXX
    for phone in processor.postal_clients["Телефон"]:
        assert len(phone) == 11
        assert phone.startswith("7")
        assert phone.isdigit()


def test_address_formatting(config_manager: ConfigManager) -> None:
    """Тест форматирования адресов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест"] * 3,
            "Список": ["Почта России"] * 3,
            "Телефон": ["79991234567"] * 3,
            "только Индекс отделения для получения.": [
                " 123456 ",  # Пробелы
                "123 456",  # Разделитель
                "12345",  # Короткий индекс (некорректный)
            ],
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем формат индекса
    for address in processor.postal_clients["только Индекс отделения для получения."]:
        if address:  # Проверяем только непустые индексы
            assert len(str(address)) == 6
            assert str(address).isdigit()


def test_name_case_formatting(config_manager: ConfigManager) -> None:
    """Тест форматирования регистра имен."""
    data = pd.DataFrame(
        {
            "Кто будет получать заказ": ["Лично я"] * 3,
            "Фамилия": ["ИВАНОВ", "иванов", "Иванов"],
            "Имя": ["ИВАН", "иван", "Иван"],
            "Список": ["Магнит"] * 3,
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем, что все имена начинаются с заглавной буквы
    for name in processor.alternative_clients["ФИО"]:
        parts = name.split()
        assert all(part.istitle() for part in parts)
        assert not any(part.isupper() for part in parts)
        assert not any(part.islower() for part in parts)


def test_special_characters_handling(config_manager: ConfigManager) -> None:
    """Тест обработки специальных символов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": [
                "Иванов-Петров И.И.",
                "О'Коннор Джон",
                "Мюллер Ганс",
            ],
            "Список": ["Почта России"] * 3,
            "Телефон": ["79991234567"] * 3,
            "только Индекс отделения для получения.": ["123456"] * 3,
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем сохранение специальных символов в именах
    names = processor.postal_clients["ФИО полностью"].tolist()
    assert "Иванов-Петров" in names[0]
    assert "О'Коннор" in names[1]
    assert "Мюллер" in names[2]
