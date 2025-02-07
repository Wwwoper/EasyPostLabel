"""Модуль настройки логирования."""

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Форматы логов
CONSOLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DEBUG_CONSOLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FILE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"

# Уровни логирования
LOG_LEVELS = {
    "development": logging.DEBUG,
    "production": logging.INFO,
    "test": logging.DEBUG
}

# Настройки ротации
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

def get_log_path() -> Path:
    """Получение пути к файлу лога."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    return log_dir / f"app_{date_str}.log"

def create_console_handler(level: str) -> logging.Handler:
    """Создание обработчика для консоли."""
    console_handler = logging.StreamHandler(sys.stdout)
    
    # В режиме разработки используем подробный формат
    if level == "development":
        console_handler.setFormatter(logging.Formatter(DEBUG_CONSOLE_FORMAT))
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
        console_handler.setLevel(logging.INFO)
    
    return console_handler

def create_file_handler(log_file: Path) -> logging.Handler:
    """Создание обработчика для файла."""
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(FILE_FORMAT))
    file_handler.setLevel(logging.DEBUG)
    return file_handler

def setup_logger(
    name: str,
    level: str = "development",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Настройка логгера.

    Args:
        name: Имя логгера
        level: Уровень логирования ('development', 'production', 'test')
        log_file: Путь к файлу логов

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level, logging.INFO))

    # Очищаем существующие обработчики
    logger.handlers.clear()

    # Добавляем обработчик консоли
    logger.addHandler(create_console_handler(level))

    # Добавляем обработчик файла
    if log_file is None:
        log_file = get_log_path()
    logger.addHandler(create_file_handler(log_file))

    return logger 