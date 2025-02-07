"""Модуль нормализации данных."""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Pattern

import pandas as pd

from utils.config import ConfigManager
from utils.exceptions import ValidationError

logger = logging.getLogger(__name__)
config = ConfigManager()


@dataclass
class PhoneNormalizationConfig:
    """Конфигурация нормализации телефона."""
    country_code: str
    min_length: int
    max_length: int
    patterns: List[Pattern]

    @classmethod
    def from_config(cls) -> 'PhoneNormalizationConfig':
        """Создание конфигурации из настроек."""
        phone_config = config.get_setting("normalization.phone", {})
        return cls(
            country_code=phone_config.get("country_code", "7"),
            min_length=phone_config.get("min_length", 10),
            max_length=phone_config.get("max_length", 11),
            patterns=[re.compile(p) for p in phone_config.get("patterns", [])]
        )


class PhoneNormalizer:
    """Нормализатор телефонных номеров."""

    def __init__(self):
        self.config = PhoneNormalizationConfig.from_config()

    @staticmethod
    def _clean_phone(phone: str) -> str:
        """Очистка номера от всех не цифр."""
        return re.sub(r"\D", "", str(phone))

    def _validate_phone(self, phone: str) -> bool:
        """Проверка формата номера."""
        if not self.config.patterns:
            return True
        return any(pattern.match(phone) for pattern in self.config.patterns)

    def normalize(self, phone: Optional[str]) -> str:
        """Нормализация телефонного номера."""
        try:
            if not phone or pd.isna(phone):
                return ""

            # Очищаем номер
            digits = self._clean_phone(phone)
            if not digits:
                return ""

            # Проверяем длину
            if len(digits) < self.config.min_length or len(digits) > self.config.max_length:
                logger.warning("Некорректная длина номера: %s", phone)
                return ""

            # Нормализуем
            if len(digits) == 10:
                digits = f"{self.config.country_code}{digits}"
            elif digits.startswith("8"):
                digits = f"{self.config.country_code}{digits[1:]}"

            # Проверяем формат
            if not self._validate_phone(digits):
                logger.warning("Некорректный формат номера: %s", phone)
                return ""

            return digits

        except Exception as e:
            logger.exception("Ошибка нормализации номера: %s", str(e))
            return ""


@dataclass
class PostcodeNormalizationConfig:
    """Конфигурация нормализации индекса."""
    length: int
    validate_region: bool
    allowed_regions: List[str]

    @classmethod
    def from_config(cls) -> 'PostcodeNormalizationConfig':
        """Создание конфигурации из настроек."""
        postcode_config = config.get_setting("normalization.postcode", {})
        return cls(
            length=postcode_config.get("length", 6),
            validate_region=postcode_config.get("validate_region", False),
            allowed_regions=postcode_config.get("allowed_regions", [])
        )


class PostcodeNormalizer:
    """Нормализатор почтовых индексов."""

    def __init__(self):
        self.config = PostcodeNormalizationConfig.from_config()

    def normalize(self, postcode: Optional[str | int | float]) -> str:
        """Нормализация почтового индекса."""
        try:
            if pd.isna(postcode):
                return ""

            # Преобразуем в строку и очищаем
            postcode_str = str(postcode).strip()

            # Если это число с точкой, преобразуем в целое
            if isinstance(postcode, float):
                postcode_str = str(int(float(postcode_str)))

            # Удаляем все не цифры
            digits = re.sub(r"\D", "", postcode_str)

            # Проверяем длину
            if len(digits) != self.config.length:
                logger.warning("Некорректная длина индекса: %s", postcode)
                return ""

            # Проверяем регион
            if self.config.validate_region and self.config.allowed_regions:
                region_code = digits[:3]
                if region_code not in self.config.allowed_regions:
                    logger.warning("Недопустимый регион: %s", region_code)
                    return ""

            return digits

        except Exception as e:
            logger.exception("Ошибка нормализации индекса: %s", str(e))
            return ""
