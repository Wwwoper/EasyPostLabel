"""Модуль нормализации данных."""

import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Нормализация ФИО."""
    try:
        if not name:
            return ""
        # Удаляем лишние пробелы и приводим к единому регистру
        normalized = " ".join(name.strip().split())
        return normalized.title()
    except Exception as e:
        logger.exception("Ошибка при нормализации имени: %s", str(e))
        return name


class PhoneNormalizer:
    """Нормализатор телефонных номеров."""

    @staticmethod
    def normalize(phone: Optional[str]) -> str:
        """Нормализация телефонного номера в формат +7XXXXXXXXXX.

        Args:
            phone: Строка с номером телефона

        Returns:
            str: Нормализованный номер телефона или пустая строка
        """
        try:
            if not phone or pd.isna(phone):
                return ""

            # Удаляем все не цифры
            digits = re.sub(r"\D", "", str(phone))
            if not digits:
                return ""

            # Нормализуем номер
            if digits.startswith("8"):
                digits = "7" + digits[1:]
            elif len(digits) == 10 and digits.startswith("9"):
                digits = "7" + digits

            # Проверяем финальный формат
            if len(digits) == 11 and digits.startswith("7"):
                return f"{digits}"

            logger.warning("Некорректный формат номера: %s", phone)
            return ""

        except Exception as e:
            logger.exception("Ошибка при нормализации телефона: %s", str(e))
            return ""


class PostcodeNormalizer:
    """Нормализатор почтовых индексов."""

    @staticmethod
    def normalize(postcode: Optional[str]) -> str:
        """Нормализация почтового индекса в формат XXXXXX.

        Args:
            postcode: Строка с индексом

        Returns:
            str: Нормализованный индекс или пустая строка
        """
        try:
            if not postcode or pd.isna(postcode):
                return ""

            # Преобразуем в строку и очищаем
            postcode_str = str(postcode).strip()

            # Если это число с точкой, преобразуем в целое
            if isinstance(postcode, float):
                postcode_str = str(int(float(postcode_str)))

            # Удаляем все не цифры
            digits = re.sub(r"\D", "", postcode_str)

            # Проверяем длину
            if len(digits) == 6:
                return digits

            logger.warning("Некорректный формат индекса: %s", postcode)
            return ""

        except Exception as e:
            logger.exception("Ошибка при нормализации индекса: %s", str(e))
            return ""
