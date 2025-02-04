"""Тесты для проверки работы с конфигурацией."""

import pytest

from utils.config import ConfigManager


@pytest.fixture
def config_manager() -> ConfigManager:
    """Фикстура для создания менеджера конфигурации."""
    return ConfigManager()


def test_config_structure(config_manager: ConfigManager) -> None:
    """Тест структуры конфигурации."""
    config = config_manager.config

    # Проверяем наличие основных секций
    assert "columns" in config
    assert "output" in config

    # Проверяем секцию columns
    columns = config["columns"]
    assert "delivery_method" in columns

    # Проверяем настройки delivery_method
    delivery_method = columns["delivery_method"]
    assert "source" in delivery_method
    assert "validation" in delivery_method
    assert "postal_keyword" in delivery_method["validation"]

    # Проверяем секцию output
    output = config["output"]
    assert "postal" in output
    assert "filename" in output["postal"]
