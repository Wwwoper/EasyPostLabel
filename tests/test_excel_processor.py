"""Тесты для ExcelProcessor."""

from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest
from openpyxl import Workbook

from processors.excel_processor import ExcelProcessor
from utils.config import ConfigManager


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Создает тестовую конфигурацию."""
    return {
        "excel": {"sheet_index": 0, "header_row": 0},
        "columns": {
            "receiver_type": {
                "source": "Кто будет получать заказ",
                "column_index": 0,
            },
            "surname": {"source": "Фамилия", "column_index": 1},
            "name": {"source": "Имя", "column_index": 2},
            "delivery_method": {"source": "Список", "column_index": 3},
            "phone": {"source": "Телефон", "column_index": 4},
        },
        "receivers": {
            "type_field": "Кто будет получать заказ",
            "fields": {
                "Лично я": {"surname_field": "Фамилия", "name_field": "Имя"},
                "Другой человек": {"surname_field": "Фамилия", "name_field": "Имя"},
            },
        },
    }


@pytest.fixture
def config_manager(test_config: Dict[str, Any]) -> ConfigManager:
    """Создает менеджер конфигурации с тестовыми настройками."""
    manager = ConfigManager()
    manager.config = test_config
    return manager


@pytest.fixture
def sample_excel(tmp_path: Path) -> Path:
    """Создает тестовый Excel файл."""
    wb = Workbook()
    ws = wb.active

    headers = ["Кто будет получать заказ", "Фамилия", "Имя", "Список", "Телефон"]
    ws.append(headers)
    ws.append(["Лично я", "Иванов", "Иван", "Магнит", "79991234567"])
    ws.append(["Другой человек", "Петров", "Петр", "Почта России", "79992345678"])

    file_path = tmp_path / "test.xlsx"
    wb.save(file_path)
    return file_path


def test_excel_read(sample_excel: Path, config_manager: ConfigManager) -> None:
    """Тест чтения Excel файла."""
    processor = ExcelProcessor(sample_excel, config_manager)
    df = processor.read_data()

    assert not df.empty
    assert len(df) == 2
    assert list(df.columns) == [
        "Кто будет получать заказ",
        "Фамилия",
        "Имя",
        "Список",
        "Телефон",
    ]


def test_invalid_file(tmp_path: Path, config_manager: ConfigManager) -> None:
    """Тест обработки некорректного файла."""
    invalid_file = tmp_path / "invalid.xlsx"
    invalid_file.write_text("Not an Excel file")

    processor = ExcelProcessor(invalid_file, config_manager)
    with pytest.raises(ValueError):
        processor.read_data()


def test_missing_file(tmp_path: Path, config_manager: ConfigManager) -> None:
    """Тест обработки отсутствующего файла."""
    missing_file = tmp_path / "missing.xlsx"

    processor = ExcelProcessor(missing_file, config_manager)
    with pytest.raises(FileNotFoundError):
        processor.read_data()


def test_data_types(sample_excel: Path, config_manager: ConfigManager) -> None:
    """Тест обработки различных типов данных."""
    processor = ExcelProcessor(sample_excel, config_manager)
    df = processor.read_data()

    assert df["Телефон"].dtype == object
    assert df["Кто будет получать заказ"].dtype == object
    assert all(df.dtypes == object)


def test_process_data(sample_excel: Path, config_manager: ConfigManager) -> None:
    """Тест обработки данных."""
    processor = ExcelProcessor(sample_excel, config_manager)
    df = processor.read_data()
    result = processor.process_data(df)

    assert not result.empty
    assert len(result) == 2
    assert "ФИО" in result.columns
    assert result["ФИО"].iloc[0] == "Иванов Иван"
    assert result["ФИО"].iloc[1] == "Петров Петр"


def test_empty_data(config_manager: ConfigManager) -> None:
    """Тест обработки пустых данных."""
    processor = ExcelProcessor(Path("dummy.xlsx"), config_manager)
    result = processor.process_data(pd.DataFrame())
    assert result.empty
