"""Тесты для основного модуля."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from main import main


@pytest.fixture
def mock_config_manager() -> Mock:
    """Создает мок для ConfigManager."""
    return Mock()


@pytest.fixture
def mock_excel_processor() -> Mock:
    """Создает мок для ExcelProcessor."""
    processor = Mock()
    return processor


@pytest.fixture
def mock_delivery_processor() -> Mock:
    """Создает мок для DeliveryProcessor."""
    return Mock()


def test_main_success(tmp_path: Path) -> None:
    """Тест успешного выполнения программы."""
    # Создаем тестовый файл
    input_file = tmp_path / "test.xlsx"
    input_file.write_text("test")

    # Создаем директорию для выходных файлов
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)

    with patch("sys.argv", ["main.py", str(input_file)]), patch(
        "pathlib.Path.exists", return_value=True
    ), patch("processors.excel_processor.ExcelProcessor.read_data"), patch(
        "processors.excel_processor.ExcelProcessor.process_data"
    ), patch(
        "processors.delivery_processor.DeliveryProcessor.process"
    ), patch(
        "processors.delivery_strategies.postal.PostalDeliveryStrategy.save"
    ), patch(
        "processors.delivery_strategies.alternative.AlternativeDeliveryStrategy.save"
    ):
        main()
        assert True  # Если дошли до этой точки, значит ошибок не было


def test_main_missing_file() -> None:
    """Тест обработки отсутствующего входного файла."""
    with patch("sys.argv", ["main.py", "nonexistent.xlsx"]), patch(
        "pathlib.Path.exists", return_value=False
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_processing_error(
    tmp_path: Path, mock_config_manager: Mock, mock_excel_processor: Mock
) -> None:
    """Тест обработки ошибок при обработке данных."""
    input_file = tmp_path / "input_file.xlsx"
    input_file.touch()

    mock_excel_processor.read_data.side_effect = ValueError("Test error")

    with patch("main.ConfigManager", return_value=mock_config_manager), patch(
        "main.ExcelProcessor", return_value=mock_excel_processor
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
