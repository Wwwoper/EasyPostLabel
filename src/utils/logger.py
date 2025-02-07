"""Модуль настройки логирования."""

import logging
import sys
from pathlib import Path
from typing import Optional

# Форматы логов
CONSOLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DEBUG_CONSOLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Уровни логирования для разных окружений
LOG_LEVELS = {
    "development": logging.DEBUG,
    "production": logging.INFO,
}


def setup_logger(
    name: str,
    level: str = "development",
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Настройка логгера.

    Args:
        name: Имя логгера
        level: Уровень логирования ('development' или 'production')
        log_file: Путь к файлу логов

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level, logging.INFO))

    # Очищаем существующие обработчики
    logger.handlers.clear()

    # Настраиваем вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    
    # В режиме разработки используем более подробный формат
    if level == "development":
        console_handler.setFormatter(logging.Formatter(DEBUG_CONSOLE_FORMAT))
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
        console_handler.setLevel(logging.INFO)
    
    logger.addHandler(console_handler)

    # Настраиваем вывод в файл, если указан
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
        # В файл всегда пишем подробные логи
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger 