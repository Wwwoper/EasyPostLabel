"""Тесты для проверки граничных случаев и обработки ошибок."""

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def config_manager():
    """Фикстура для создания менеджера конфигурации."""
    return ConfigManager()


def test_missing_required_columns(config_manager):
    """Тест обработки данных с отсутствующими обязательными столбцами."""
    # DataFrame без обязательных столбцов
    df = pd.DataFrame({
        "Какой-то столбец": ["значение1", "значение2"]
    })
    
    processor = DeliveryProcessor(df, config_manager)
    processor.process()
    
    # Проверяем, что результаты пустые
    assert processor.postal_clients.empty
    assert processor.alternative_clients.empty


def test_invalid_data_types(config_manager):
    """Тест обработки данных с неправильными типами данных."""
    df = pd.DataFrame({
        "ФИО полностью": [123, 456],  # Числа вместо строк
        "Список": [True, False],  # Булевы значения вместо строк
        "Телефон": [123, 456],  # Числа вместо строк
        "только Индекс отделения для получения.": [123, 456]
    })
    
    processor = DeliveryProcessor(df, config_manager)
    processor.process()
    
    # Проверяем, что данные были обработаны корректно
    # True преобразуется в "True", что не содержит "Почта"
    assert len(processor.postal_clients) == 0
    assert len(processor.alternative_clients) == 2


def test_special_characters(config_manager):
    """Тест обработки данных со специальными символами."""
    df = pd.DataFrame({
        "ФИО полностью": ["Иванов!@#$%^&*()"],
        "Список": ["Почта России!!!"],
        "Телефон": ["!@#$%^&*()+79991234567"],
        "только Индекс отделения для получения.": ["!@#$%^&*()123456"]
    })
    
    processor = DeliveryProcessor(df, config_manager)
    processor.process()
    
    # Проверяем нормализацию телефона
    assert processor.postal_clients["Телефон"].iloc[0] == "79991234567"


def test_duplicate_data(config_manager):
    """Тест обработки дублирующихся данных."""
    df = pd.DataFrame({
        "ФИО полностью": ["Иванов И.И.", "Иванов И.И."],
        "Список": ["Почта России", "Почта России"],
        "Телефон": ["79991234567", "79991234567"],
        "только Индекс отделения для получения.": ["123456", "123456"]
    })
    
    processor = DeliveryProcessor(df, config_manager)
    processor.process()
    
    # Проверяем, что дубликаты обрабатываются как отдельные записи
    assert len(processor.postal_clients) == 2


def test_null_values(config_manager):
    """Тест обработки пустых значений."""
    df = pd.DataFrame({
        "ФИО полностью": [None, "Петров П.П."],
        "Список": ["Почта России", None],
        "Телефон": [None, "79991234567"],
        "только Индекс отделения для получения.": ["123456", None]
    })
    
    processor = DeliveryProcessor(df, config_manager)
    processor.process()
    
    # Проверяем обработку записей с пустыми значениями
    assert not processor.postal_clients.empty 