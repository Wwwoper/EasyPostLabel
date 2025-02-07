"""Тесты для стратегии обработки пунктов выдачи."""

import os
from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook

from processors.delivery_strategies.pickup_point import PickupPointStrategy
from utils.config import ConfigManager


@pytest.fixture(autouse=True)
def setup_test_env():
    """Фикстура для настройки тестового окружения."""
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)


@pytest.fixture
def config():
    """Фикстура для получения тестовой конфигурации."""
    test_config_path = Path(__file__).parent / "data" / "test_config.yaml"
    return ConfigManager(str(test_config_path))


@pytest.fixture
def pickup_strategy(config):
    """Фикстура стратегии обработки пунктов выдачи."""
    return PickupPointStrategy(config)


@pytest.fixture
def test_data():
    """Фикстура тестовых данных."""
    return pd.DataFrame(
        {
            "ФИО": [
                "Алексеев Иван",
                "Борисов Петр",
                "Васильев Сергей",
                "Григорьев Андрей",
                "Дмитриев Павел",
            ],
            "Центр_Выдачи": ["Бемби", "Атмосфера", "Глобус", "Радуга", "Солнышко"],
        }
    )


def test_label_positions(pickup_strategy, test_data, tmp_path):
    """Тест правильности размещения бирок на листе."""
    # Создаем тестовый файл
    output_path = tmp_path / "test_labels.xlsx"
    pickup_strategy.save(test_data, str(output_path))

    # Проверяем созданный файл
    wb = load_workbook(output_path)
    sheet = wb["Бирки"]

    # Проверяем первую строку (3 бирки)
    # Первая бирка
    assert sheet["A1"].value == "Алексеев Иван"
    assert sheet["A2"].value == "в ЦВ Бемби"
    assert sheet["A3"].value == f"от {pickup_strategy.SENDER_NAME}"

    # Вторая бирка
    assert sheet["C1"].value == "Борисов Петр"
    assert sheet["C2"].value == "в ЦВ Атмосфера"
    assert sheet["C3"].value == f"от {pickup_strategy.SENDER_NAME}"

    # Третья бирка
    assert sheet["E1"].value == "Васильев Сергей"
    assert sheet["E2"].value == "в ЦВ Глобус"
    assert sheet["E3"].value == f"от {pickup_strategy.SENDER_NAME}"

    # Проверяем вторую строку (2 бирки)
    assert sheet["A5"].value == "Григорьев Андрей"
    assert sheet["A6"].value == "в ЦВ Радуга"
    assert sheet["A7"].value == f"от {pickup_strategy.SENDER_NAME}"

    assert sheet["C5"].value == "Дмитриев Павел"
    assert sheet["C6"].value == "в ЦВ Солнышко"
    assert sheet["C7"].value == f"от {pickup_strategy.SENDER_NAME}"

    # Проверяем промежуточные колонки
    assert sheet.column_dimensions["B"].width == 0.17
    assert sheet.column_dimensions["D"].width == 0.17

    # Проверяем высоту строк
    assert sheet.row_dimensions[4].height == 3  # промежуток между группами бирок


def test_label_sorting(pickup_strategy, tmp_path):
    """Тест сортировки бирок по алфавиту."""
    # Создаем неотсортированные данные
    unsorted_data = pd.DataFrame(
        {
            "ФИО": [
                "Васильев Сергей",
                "Алексеев Иван",
                "Дмитриев Павел",
                "Борисов Петр",
                "Григорьев Андрей",
            ],
            "Центр_Выдачи": ["Глобус", "Бемби", "Солнышко", "Атмосфера", "Радуга"],
        }
    )

    # Сохраняем и проверяем
    output_path = tmp_path / "test_sorted_labels.xlsx"
    pickup_strategy.save(unsorted_data, str(output_path))

    wb = load_workbook(output_path)
    sheet = wb["Бирки"]

    # Проверяем что ФИО идут в алфавитном порядке
    expected_order = [
        "Алексеев Иван",
        "Борисов Петр",
        "Васильев Сергей",
        "Григорьев Андрей",
        "Дмитриев Павел",
    ]

    # Проверяем первую строку
    assert sheet["A1"].value == expected_order[0]
    assert sheet["C1"].value == expected_order[1]
    assert sheet["E1"].value == expected_order[2]

    # Проверяем вторую строку
    assert sheet["A5"].value == expected_order[3]
    assert sheet["C5"].value == expected_order[4]


def test_label_style(pickup_strategy, test_data, tmp_path):
    """Тест стилей бирок."""
    output_path = tmp_path / "test_style_labels.xlsx"
    pickup_strategy.save(test_data, str(output_path))

    wb = load_workbook(output_path)
    sheet = wb["Бирки"]

    # Проверяем стиль первой бирки
    cell = sheet["A1"]
    assert cell.font.name == "Century"
    assert cell.font.size == 13
    assert cell.font.bold is True
    assert cell.alignment.horizontal == "center"
    assert cell.alignment.vertical == "center"
    assert cell.alignment.wrap_text is True
    assert cell.border.left.style == "thin"
    assert cell.border.right.style == "thin"
    assert cell.border.top.style == "thin"
    assert cell.border.bottom.style == "thin"


def test_pickup_strategy(pickup_strategy):
    # Ваш тестовый код
    pass
