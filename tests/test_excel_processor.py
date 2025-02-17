from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from processors.excel_processor import ExcelProcessor


@pytest.fixture
def config_manager():
    """Фикстура для создания ConfigManager с тестовой конфигурацией."""
    mock_config = Mock()

    # Настраиваем возвращаемые значения
    mock_config.settings.get_excel_settings.return_value = {
        "start_row": 1,
        "sheet_index": 0,
        "use_columns": True,
    }

    mock_config.columns.get_config.return_value = {
        "common_columns": {
            "delivery": {
                "method": {
                    "source": "Способ передачи",
                    "excel_column": "B",
                    "column_index": 2,
                }
            }
        },
        "postal_columns": {
            "client_name": {
                "source": "ФИО полностью",
                "excel_column": "K",
                "column_index": 11,
            },
            "postal_code": {
                "source": "Индекс отделения для получения.",
                "excel_column": "J",
                "column_index": 10,
            },
            "phone": {"source": "Телефон", "excel_column": "L", "column_index": 12},
        },
        "pickpoint_columns": {
            "receiver": {
                "type": {
                    "source": "Получатель заказа",
                    "excel_column": "C",
                    "column_index": 3,
                }
            },
            "self": {
                "surname": {
                    "source": "Фамилия",
                    "excel_column": "D",
                    "column_index": 4,
                },
                "name": {"source": "Имя", "excel_column": "E", "column_index": 5},
            },
            "other": {
                "surname": {
                    "source": "Фамилия получателя заказа",
                    "excel_column": "G",
                    "column_index": 7,
                },
                "name": {
                    "source": "Имя получателя заказа",
                    "excel_column": "H",
                    "column_index": 8,
                },
            },
            "delivery": {
                "method": {
                    "source": "Список",
                    "excel_column": "M",
                    "column_index": 13,
                    "first_word": True,
                }
            },
        },
    }

    return mock_config


@pytest.fixture
def sample_excel_data():
    """Фикстура с тестовыми данными Excel."""
    return [
        {  # Почта
            "B": "Почта",
            "K": "Михайлов Виктор",
            "J": "123456",
            "L": "79803471936",
        },
        {  # PickPoint - Лично я
            "B": "Центр_Выдачи",
            "C": "Лично я",
            "D": "Иванов",
            "E": "Иван",
            "M": "Глобус (среда и суббота)",
        },
        {  # PickPoint - Другой человек
            "B": "Центр_Выдачи",
            "C": "Другой человек",
            "G": "Петров",
            "H": "Петр",
            "M": "Бемби (передача вторник)",
        },
    ]


def test_read_data(config_manager):
    """Тест чтения данных из Excel файла."""
    with patch("processors.excel_processor.load_workbook") as mock_load_workbook:
        # Мокаем загрузку Excel файла
        mock_wb = Mock()
        mock_ws = Mock()
        mock_wb.worksheets = [mock_ws]
        mock_load_workbook.return_value = mock_wb

        # Создаем тестовые данные
        sample_data = [
            {  # Почта
                "B": "Почта",
                "K": "Михайлов Виктор",
                "J": "123456",
                "L": "79803471936",
            },
            {  # PickPoint - Лично я
                "B": "Центр_Выдачи",
                "C": "Лично я",
                "D": "Иванов",
                "E": "Иван",
                "M": "Глобус (среда и суббота)",
            },
            {  # PickPoint - Другой человек
                "B": "Центр_Выдачи",
                "C": "Другой человек",
                "G": "Петров",
                "H": "Петр",
                "M": "Бемби (передача вторник)",
            },
        ]

        # Создаем тестовые строки
        mock_rows = []
        for row_data in sample_data:
            mock_row = []
            for col in "ABCDEFGHIJKLM":
                mock_cell = Mock()
                mock_cell.value = row_data.get(col, "")
                mock_cell.data_type = "s"
                mock_cell.number_format = "General"
                mock_row.append(mock_cell)
            mock_rows.append(mock_row)

        mock_ws.iter_rows.return_value = mock_rows

        # Создаем процессор и читаем данные
        processor = ExcelProcessor(Path("test.xlsx"), config_manager)
        df = processor.read_data()

        # Проверяем результаты
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_data)

        # Проверяем данные для Почты
        postal_row = df[df["delivery.method"] == "Почта"].iloc[0]
        assert postal_row["postal.client_name"] == "Михайлов Виктор"
        assert postal_row["postal.postal_code"] == "123456"
        assert postal_row["postal.phone"] == "79803471936"

        # Проверяем данные для PickPoint - Лично я
        pickpoint_self = df[
            (df["delivery.method"] == "Центр_Выдачи")
            & (df["receiver.type"] == "Лично я")
        ].iloc[0]
        assert pickpoint_self["self.surname"] == "Иванов"
        assert pickpoint_self["self.name"] == "Иван"
        assert pickpoint_self["pickpoint.delivery.method"] == "Глобус"

        # Проверяем данные для PickPoint - Другой человек
        pickpoint_other = df[
            (df["delivery.method"] == "Центр_Выдачи")
            & (df["receiver.type"] == "Другой человек")
        ].iloc[0]
        assert pickpoint_other["other.surname"] == "Петров"
        assert pickpoint_other["other.name"] == "Петр"
        assert pickpoint_other["pickpoint.delivery.method"] == "Бемби"


def test_edge_cases(config_manager):
    """Тест граничных случаев."""
    with patch("processors.excel_processor.load_workbook") as mock_load_workbook:
        mock_wb = Mock()
        mock_ws = Mock()
        mock_wb.worksheets = [mock_ws]
        mock_load_workbook.return_value = mock_wb

        # Тестовые данные с граничными случаями
        sample_data = [
            {  # Пустые значения
                "B": "Почта",
                "K": "",  # Пустое ФИО
                "J": "",  # Пустой индекс
                "L": "",  # Пустой телефон
            },
            {  # Некорректные типы данных
                "B": "Центр_Выдачи",
                "C": 123,  # Число вместо строки
                "D": True,  # Boolean вместо строки
                "M": None,  # None вместо строки
            },
            {  # Спецсимволы и пробелы
                "B": " Почта ",  # Пробелы вокруг
                "K": "Иванов И.И.",  # Спецсимволы
                "J": " 123456 ",  # Пробелы в индексе
                "L": "+79001234567",  # Телефон с +
            },
        ]

        # Создаем тестовые строки
        mock_rows = []
        for row_data in sample_data:
            mock_row = []
            for col in "ABCDEFGHIJKLM":
                mock_cell = Mock()
                mock_cell.value = row_data.get(col, "")
                mock_cell.data_type = "s"
                mock_cell.number_format = "General"
                mock_row.append(mock_cell)
            mock_rows.append(mock_row)

        mock_ws.iter_rows.return_value = mock_rows

        # Создаем процессор и читаем данные
        processor = ExcelProcessor(Path("test.xlsx"), config_manager)
        df = processor.read_data()

        # Проверяем обработку пустых значений
        empty_row = df.iloc[0]
        assert empty_row["postal.client_name"] == ""
        assert empty_row["postal.postal_code"] == ""
        assert empty_row["postal.phone"] == ""

        # Проверяем преобразование типов
        type_row = df.iloc[1]
        assert isinstance(type_row["receiver.type"], str)
        assert isinstance(type_row["self.surname"], str)
        assert isinstance(type_row["pickpoint.delivery.method"], str)

        # Проверяем обработку спецсимволов
        special_row = df.iloc[2]
        assert special_row["delivery.method"].strip() == "Почта"
        assert special_row["postal.postal_code"].strip() == "123456"
        assert special_row["postal.phone"].replace("+", "") == "79001234567"


def test_data_validation(config_manager):
    """Тест чтения некорректных данных."""
    with patch("processors.excel_processor.load_workbook") as mock_load_workbook:
        # Мокаем загрузку Excel файла
        mock_wb = Mock()
        mock_ws = Mock()
        mock_wb.worksheets = [mock_ws]
        mock_load_workbook.return_value = mock_wb

        # Тестовые данные
        sample_data = [
            {  # Некорректные данные
                "B": "Почта",
                "K": "Иванов Иван",
                "J": "не индекс",
                "L": "не телефон",
            }
        ]

        # Создаем тестовые строки
        mock_rows = []
        for row_data in sample_data:
            mock_row = []
            for col in "ABCDEFGHIJKLM":
                mock_cell = Mock()
                mock_cell.value = row_data.get(col, "")
                mock_cell.data_type = "s"
                mock_cell.number_format = "General"
                mock_row.append(mock_cell)
            mock_rows.append(mock_row)

        mock_ws.iter_rows.return_value = mock_rows

        # Создаем процессор и читаем данные
        processor = ExcelProcessor(Path("test.xlsx"), config_manager)
        df = processor.read_data()

        # Проверяем, что данные просто читаются как есть
        row = df.iloc[0]
        assert row["postal.phone"] == "не телефон"  # Данные без валидации
        assert row["postal.postal_code"] == "не индекс"  # Данные без валидации
        assert row["postal.client_name"] == "Иванов Иван"  # ФИО как есть
        assert row["delivery.method"] == "Почта"  # Тип доставки как есть
