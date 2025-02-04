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
    processor.read_data.return_value = Mock()
    return processor


@pytest.fixture
def mock_delivery_processor() -> Mock:
    """Создает мок для DeliveryProcessor."""
    return Mock()


def test_main_success(
    tmp_path: Path,
    mock_config_manager: Mock,
    mock_excel_processor: Mock,
    mock_delivery_processor: Mock
) -> None:
    """Тест успешного выполнения основного процесса."""
    input_file = tmp_path / "input_file.xlsx"
    input_file.touch()
    
    with patch("main.ConfigManager", return_value=mock_config_manager), \
         patch("main.ExcelProcessor", return_value=mock_excel_processor), \
         patch("main.DeliveryProcessor", return_value=mock_delivery_processor):
        
        sys.argv = ["main.py"]
        main()
        
        mock_excel_processor.read_data.assert_called_once()
        mock_delivery_processor.process.assert_called_once()
        mock_delivery_processor.save_results.assert_called_once()


def test_main_missing_file() -> None:
    """Тест обработки отсутствующего входного файла."""
    with patch('sys.argv', ['main.py', 'nonexistent.xlsx']), \
         patch('pathlib.Path.exists', return_value=False):  # Имитируем отсутствие файла
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_processing_error(
    tmp_path: Path,
    mock_config_manager: Mock,
    mock_excel_processor: Mock
) -> None:
    """Тест обработки ошибок при обработке данных."""
    input_file = tmp_path / "input_file.xlsx"
    input_file.touch()
    
    mock_excel_processor.read_data.side_effect = ValueError("Test error")
    
    with patch("main.ConfigManager", return_value=mock_config_manager), \
         patch("main.ExcelProcessor", return_value=mock_excel_processor):
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1 