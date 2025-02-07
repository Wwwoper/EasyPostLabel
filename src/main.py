"""Основной модуль приложения для обработки данных о доставке."""

from pathlib import Path

from processors.delivery_processor import DeliveryProcessor
from processors.excel_processor import ExcelProcessor
from utils.config import ConfigManager
from utils.exceptions import handle_exception
from utils.logger import setup_logger

# Настраиваем логирование
logger = setup_logger(__name__, level="development")


def setup_environment() -> tuple[Path, ConfigManager]:
    """Настройка окружения приложения.

    Returns:
        tuple: (путь к входному файлу, менеджер конфигурации)

    Raises:
        FileNotFoundError: если входной файл не найден
    """
    input_file = Path("files/new_file.xlsx")
    if not input_file.exists():
        raise FileNotFoundError(f"Файл не найден: {input_file}")

    config = ConfigManager()
    logger.info("Окружение настроено успешно")
    return input_file, config


def process_delivery_data(input_file: Path, config: ConfigManager) -> bool:
    """Обработка данных о доставке.

    Args:
        input_file: Путь к входному файлу
        config: Менеджер конфигурации

    Returns:
        bool: Успешность обработки
    """
    try:
        logger.info("Начало обработки файла: %s", input_file)

        # Читаем данные
        excel_processor = ExcelProcessor(input_file, config)
        df = excel_processor.read_data()

        if df.empty:
            logger.warning("Нет данных для обработки")
            return False

        # Обрабатываем данные
        processor = DeliveryProcessor(df, config)
        result = processor.process()

        if not result.success:
            logger.error("Ошибка обработки: %s", result.error)
            return False

        # Сохраняем результаты
        if processor.save_results():
            logger.info("Статистика обработки: %s", result.stats)
            return True

        return False

    except Exception as e:
        logger.exception("Ошибка обработки: %s", str(e))
        return False


def main() -> None:
    """Основная функция приложения."""
    try:
        # Инициализация
        input_file, config = setup_environment()

        # Обработка
        if process_delivery_data(input_file, config):
            logger.info("Программа завершена успешно")
        else:
            logger.error("Программа завершена с ошибками")

    except Exception as e:
        error_msg = handle_exception(e)
        logger.error("Критическая ошибка: %s", error_msg)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
