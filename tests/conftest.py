"""Общие фикстуры для тестов."""

from typing import Any, Callable, TypeVar

import pytest

T = TypeVar("T")


def typed_fixture(func: Callable[..., T]) -> Callable[..., T]:
    """Декоратор для создания типизированной фикстуры.

    Args:
        func: Функция-фикстура

    Returns:
        Callable: Декорированная фикстура
    """
    return pytest.fixture(func)
