"""Интеграционные тесты для проверки работы всех компонентов."""

from pathlib import Path

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager


@pytest.fixture
def config() -> dict[str, dict]:
    """Фикстура для создания тестовой конфигурации."""
    return {
        "columns": {
            "delivery_method": {
                "source": "Список",
                "validation": {"postal_keyword": "Почта"},
            }
        },
        "output": {
            "postal": {"filename": "postal_test.xlsx"},
            "alternative": {"filename": "alternative_test.xlsx"},
        },
    }


@pytest.fixture
def config_manager(config: dict, monkeypatch: pytest.MonkeyPatch) -> ConfigManager:
    """Фикстура для создания менеджера конфигурации."""
    manager = ConfigManager()
    monkeypatch.setattr(manager, "config", config)
    return manager


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Фикстура с тестовыми данными клиентов."""
    return pd.DataFrame(
        {
            "ФИО полностью": [
                "Иванов Иван Иванович",
                "Петров Петр Петрович",
                "Сидоров Сидор Сидорович",
            ],
            "Список": ["Почта России", "Магнит Центр", "Почта России"],
            "Телефон": ["79991234567", "79992345678", "79993456789"],
            "только Индекс отделения для получения.": ["123456", None, "789012"],
            "Кто будет получать заказ": ["Лично я", "Лично я", "Лично я"],
            "Фамилия": ["Иванов", "Петров", "Сидоров"],
            "Имя": ["Иван", "Петр", "Сидор"],
        }
    )


def test_delivery_processor_initialization(
    config_manager: ConfigManager, sample_data: pd.DataFrame
) -> None:
    """Тест инициализации процессора доставки."""
    processor = DeliveryProcessor(sample_data, config_manager)
    assert processor is not None
    assert processor.data is not None
    assert processor.config_manager is not None
    assert processor.postal_clients.empty
    assert processor.alternative_clients.empty


def test_delivery_processor_process(
    config_manager: ConfigManager, sample_data: pd.DataFrame
) -> None:
    """Тест процесса обработки данных."""
    processor = DeliveryProcessor(sample_data, config_manager)
    processor.process()

    # Проверяем разделение клиентов
    assert len(processor.postal_clients) == 2  # Два клиента с Почтой России
    assert len(processor.alternative_clients) == 1  # Один клиент с Магнитом

    # Проверяем нормализацию телефонов для почтовых клиентов
    postal_phones = processor.postal_clients["Телефон"].tolist()
    assert postal_phones == ["79991234567", "79993456789"]


def test_delivery_processor_save(
    config_manager: ConfigManager, sample_data: pd.DataFrame, tmp_path: Path
) -> None:
    """Тест сохранения результатов."""
    # Подменяем пути сохранения на временную директорию
    config_manager.config["output"]["postal"]["filename"] = "test_postal.xlsx"
    config_manager.config["output"]["alternative"]["filename"] = "test_alternative.xlsx"

    processor = DeliveryProcessor(sample_data, config_manager)
    processor.process()

    # Подменяем DEFAULT_OUTPUT_DIR на временную директорию
    import processors.delivery_processor as dp

    original_dir = dp.DEFAULT_OUTPUT_DIR
    dp.DEFAULT_OUTPUT_DIR = tmp_path

    try:
        processor.save_results()

        # Проверяем, что файлы созданы
        postal_path = tmp_path / "test_postal.xlsx"
        alternative_path = tmp_path / "test_alternative.xlsx"
        assert postal_path.exists()
        assert alternative_path.exists()

        # Проверяем содержимое файла почтовой доставки
        postal_df = pd.read_excel(postal_path, dtype={"recipient_phone": str})
        assert len(postal_df) == 2
        assert all(
            col in postal_df.columns
            for col in [
                "recipient_address",
                "recipient_name",
                "weight",
                "recipient_phone",
                "mail_type",
            ]
        )

        # Проверяем содержимое файла альтернативной доставки
        alternative_df = pd.read_excel(
            alternative_path,
            sheet_name="Список доставки",
            skiprows=3,  # Пропускаем заголовок и пустую строку
            header=None,  # Не используем первую строку как заголовки
            usecols=[1, 2],  # Читаем только столбцы B и C
        )
        assert len(alternative_df) == 1  # Один альтернативный клиент

        # Проверяем формат данных
        name = alternative_df.iloc[0, 0]  # Первая строка, первый столбец (ФИО)
        center = alternative_df.iloc[0, 1]  # Первая строка, второй столбец (Центр)

        assert "Петров Петр" in str(name)  # Проверяем имя
        assert "в ЦВ" in str(center)  # Проверяем центр выдачи

    finally:
        # Восстанавливаем оригинальный путь
        dp.DEFAULT_OUTPUT_DIR = original_dir


def test_empty_data_processing(config_manager: ConfigManager) -> None:
    """Тест обработки пустых данных."""
    empty_df = pd.DataFrame()
    processor = DeliveryProcessor(empty_df, config_manager)
    processor.process()

    assert processor.postal_clients.empty
    assert processor.alternative_clients.empty


def test_invalid_phone_numbers(config_manager: ConfigManager) -> None:
    """Тест обработки некорректных номеров телефонов."""
    data = pd.DataFrame(
        {
            "ФИО полностью": ["Тест Тестов"],
            "Список": ["Почта России"],
            "Телефон": ["неправильный номер"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    processor = DeliveryProcessor(data, config_manager)
    processor.process()

    # Проверяем, что некорректный номер был обработан
    assert processor.postal_clients["Телефон"].iloc[0] == ""
