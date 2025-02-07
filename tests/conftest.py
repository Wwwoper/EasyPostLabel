"""Конфигурация тестов и общие фикстуры."""

import os
from pathlib import Path
import pytest
from utils.config import ConfigManager

@pytest.fixture(autouse=True)
def setup_test_env():
    """Автоматически устанавливает тестовое окружение для всех тестов."""
    os.environ["TESTING"] = "1"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture
def config():
    """Предоставляет тестовую конфигурацию."""
    test_config_path = Path(__file__).parent / "data" / "test_config.yaml"
    return ConfigManager(str(test_config_path))
