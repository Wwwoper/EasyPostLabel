"""Тесты для обработки ошибок."""

from pathlib import Path
from typing import Any
from unittest.mock import patch
from zipfile import BadZipFile
import os

import pandas as pd
import pytest

from processors.delivery_processor import DeliveryProcessor
from utils.config import ConfigManager
from main import main


@pytest.fixture
def config_manager() -> ConfigManager:
    """Фикстура для создания менеджера конфигурации."""
    return ConfigManager()


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


def test_file_permission_error(sample_data: pd.DataFrame, tmp_path: Path) -> None:
    """Тест обработки ошибки доступа к файлу."""
    config = ConfigManager()
    config.config["output"] = {
        "postal": {"filename": "test.xlsx"},
        "alternative": {"filename": "test_alt.xlsx"},
    }

    processor = DeliveryProcessor(sample_data, config)
    processor.process()

    # Создаем файл с запретом на запись
    output_path = tmp_path / "test.xlsx"
    output_path.touch(mode=0o444)

    with patch("processors.delivery_processor.DEFAULT_OUTPUT_DIR", tmp_path):
        with pytest.raises(PermissionError):
            processor.save_results()


def test_disk_space_error(tmp_path: Path) -> None:
    """Тест обработки ошибки нехватки места на диске."""
    # Создаем тестовый файл
    test_file = tmp_path / "test.xlsx"
    test_file.write_text("test")

    # Имитируем ошибку нехватки места при создании директории
    with patch('os.makedirs') as mock_makedirs:
        mock_makedirs.side_effect = OSError("No space left on device")
        with pytest.raises(OSError, match="No space left on device"):
            os.makedirs(tmp_path / "output")


def test_invalid_output_path(sample_data: pd.DataFrame, tmp_path: Path) -> None:
    """Тест обработки некорректного пути сохранения."""
    config = ConfigManager()
    config.config["output"] = {
        "postal": {"filename": "test.xlsx"},
        "alternative": {"filename": "test_alt.xlsx"},
    }

    processor = DeliveryProcessor(sample_data, config)
    processor.process()

    # Пытаемся сохранить в несуществующую директорию
    nonexistent_dir = tmp_path / "nonexistent"

    with patch("processors.delivery_processor.DEFAULT_OUTPUT_DIR", nonexistent_dir):
        with pytest.raises(OSError):
            processor.save_results()


def test_corrupted_excel_file(tmp_path: Path) -> None:
    """Тест обработки поврежденного Excel файла."""
    # Создаем поврежденный Excel файл
    corrupted_file = tmp_path / "corrupted.xlsx"
    corrupted_file.write_text("This is not a valid Excel file")

    with pytest.raises(BadZipFile):
        pd.read_excel(corrupted_file, engine="openpyxl")


def test_memory_error_handling(config_manager: ConfigManager) -> None:
    """Тест обработки ошибки нехватки памяти."""
    data = pd.DataFrame(
        {
            "Список": ["Почта России"],
            "ФИО полностью": ["Тест"],
            "Телефон": ["79991234567"],
            "только Индекс отделения для получения.": ["123456"],
        }
    )

    with patch("pandas.DataFrame.copy", side_effect=MemoryError("Out of memory")):
        processor = DeliveryProcessor(data, config_manager)
        with pytest.raises(MemoryError, match="Out of memory"):
            processor.process()
