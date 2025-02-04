"""Интеграционные тесты для проверки работы всех компонентов."""

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def config():
    """Фикстура для создания тестовой конфигурации."""
    return {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта"},
            }
        },
        "output": {"postal": {"filename": "postal_test.xlsx"}},
    }


@pytest.fixture
def config_manager(config, monkeypatch):
    """Фикстура для создания менеджера конфигурации."""
    manager = ConfigManager()
    monkeypatch.setattr(manager, "config", config)
    return manager


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными клиентов."""
    return pd.DataFrame(
        {
            "ФИО полностью": [
                "Иванов Иван Иванович",
                "Петров Петр Петрович",
                "Сидоров Сидор Сидорович",
            ],
            "Список": ["Почта России", "Курьер", "Почта России"],
            "Телефон": ["89991234567", "+79992345678", "9993456789"],
            "только Индекс отделения для получения.": ["123456", "654321", "789012"],
        }
    )


def test_delivery_processor_initialization(config_manager, sample_data):
    """Тест инициализации процессора доставки."""
    processor = DeliveryProcessor(sample_data, config_manager)
    assert processor.data is not None
    assert processor.config_manager is not None
    assert processor.postal_clients.empty
    assert processor.alternative_clients.empty


def test_delivery_processor_process(config_manager, sample_data):
    """Тест процесса обработки данных."""
    processor = DeliveryProcessor(sample_data, config_manager)
    processor.process()

    # Проверяем разделение клиентов
    assert len(processor.postal_clients) == 2  # Два клиента с Почтой России
    assert len(processor.alternative_clients) == 1  # Один клиент с Курьером

    # Проверяем нормализацию телефонов для почтовых клиентов
    postal_phones = processor.postal_clients["Телефон"].tolist()
    assert postal_phones == ["79991234567", "79993456789"]


def test_delivery_processor_save(config_manager, sample_data, tmp_path):
    """Тест сохранения результатов."""
    # Подменяем путь сохранения на временную директорию
    config_manager.config["output"]["postal"]["filename"] = "test_output.xlsx"
    output_path = tmp_path / config_manager.config["output"]["postal"]["filename"]

    processor = DeliveryProcessor(sample_data, config_manager)
    processor.process()

    # Подменяем DEFAULT_OUTPUT_DIR на временную директорию
    import processors.delivery_processor as dp

    original_dir = dp.DEFAULT_OUTPUT_DIR
    dp.DEFAULT_OUTPUT_DIR = tmp_path

    try:
        processor.save_results()

        # Проверяем, что файл создан
        assert output_path.exists()

        # Читаем сохраненный файл с явным указанием типа данных для телефона
        saved_df = pd.read_excel(output_path, dtype={"recipient_phone": str})

        # Проверяем структуру данных
        expected_columns = [
            "recipient_address",
            "recipient_name",
            "weight",
            "recipient_phone",
            "mail_type",
        ]
        assert all(col in saved_df.columns for col in expected_columns)

        # Проверяем количество записей
        assert len(saved_df) == 2  # Должно быть два почтовых клиента

        # Проверяем форматирование телефонов
        phones = saved_df["recipient_phone"].astype(str)
        assert all(str(phone).startswith("7") for phone in phones)
        assert all(len(str(phone)) == 11 for phone in phones)

    finally:
        # Восстанавливаем оригинальный путь
        dp.DEFAULT_OUTPUT_DIR = original_dir


def test_empty_data_processing(config_manager):
    """Тест обработки пустых данных."""
    empty_df = pd.DataFrame()
    processor = DeliveryProcessor(empty_df, config_manager)
    processor.process()

    assert processor.postal_clients.empty
    assert processor.alternative_clients.empty


def test_invalid_phone_numbers(config_manager):
    """Тест обработки некорректных номеров телефонов."""
    invalid_data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест Тестов"],
            "Список": ["Почта России"],
            "Телефон": ["123"],  # Некорректный номер
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    processor = DeliveryProcessor(invalid_data, config_manager)
    processor.process()

    # Проверяем, что некорректный номер заменен на пустую строку
    assert processor.postal_clients["Телефон"].iloc[0] == ""
