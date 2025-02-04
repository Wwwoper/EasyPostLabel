"""Тесты для утилит."""

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from utils.config import ConfigManager
from utils.utils import get_client_full_name, process_dataframe, read_excel_file


@pytest.fixture
def sample_data() -> Dict[str, str]:
    """Фикстура с тестовыми данными клиента."""
    return {
        "Кто будет получать заказ": "Лично я",
        "Фамилия": "Иванов",
        "Имя": "Иван",
        "Фамилия получателя заказа": None,
        "Имя получателя заказа": None
    }


def test_get_client_full_name(sample_data: Dict[str, str]) -> None:
    """Тест получения полного имени клиента."""
    result = get_client_full_name(sample_data, "Кто будет получать заказ")
    assert result == "Иванов Иван"


def test_get_client_full_name_other(sample_data: Dict[str, str]) -> None:
    """Тест получения имени другого получателя."""
    sample_data.update({
        "Кто будет получать заказ": "Другой человек",
        "Фамилия получателя заказа": "Петров",
        "Имя получателя заказа": "Петр"
    })
    result = get_client_full_name(sample_data, "Кто будет получать заказ")
    assert result == "Петров Петр"


def test_invalid_receiver_type(sample_data: Dict[str, str]) -> None:
    """Тест обработки некорректного типа получателя."""
    sample_data["Кто будет получать заказ"] = "Неизвестный тип"
    with pytest.raises(ValueError):
        get_client_full_name(sample_data, "Кто будет получать заказ")


def test_read_excel_file(tmp_path: Path) -> None:
    """Тест чтения Excel файла."""
    # Создаем тестовый файл
    df = pd.DataFrame({
        "Test": ["data"]
    })
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    
    config = ConfigManager()
    result = read_excel_file(str(file_path), config)
    assert not result.empty


def test_process_dataframe() -> None:
    """Тест обработки DataFrame."""
    df = pd.DataFrame({
        "Кто будет получать заказ": ["Лично я"],  # Это значение должно соответствовать ReceiverType.SELF.value
        "Фамилия": ["Иванов"],
        "Имя": ["Иван"],
        "Список": ["Магнит"],
        "Телефон": ["79991234567"]
    })
    
    config = ConfigManager()
    config.config = {
        "columns": {
            "receiver_type": {
                "source": "Кто будет получать заказ"
            }
        },
        "receivers": {
            "fields": {
                "Лично я": {
                    "surname_field": "Фамилия",
                    "name_field": "Имя"
                }
            }
        }
    }
    
    result = process_dataframe(df, config)
    assert "ФИО клиента" in result.columns
    assert result["ФИО клиента"].iloc[0] == "Иванов Иван" 