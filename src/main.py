"""Основной модуль приложения для обработки данных о доставке."""

import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
sys.path.append(str(Path(__file__).parent / "src"))

# Все импорты после добавления пути
from processors.delivery_processor import DeliveryProcessor  # noqa: E402
from processors.excel_processor import ExcelProcessor  # noqa: E402
from utils.config import ConfigManager  # noqa: E402


def main() -> None:
    """Основная функция приложения."""
    try:
        # Инициализируем конфигурацию
        config = ConfigManager()

        # Создаем процессор Excel и читаем данные
        input_file = Path("files/input_file.xlsx")
        if not input_file.exists():
            print(f"Ошибка: Файл {input_file} не найден")
            sys.exit(1)

        excel_processor = ExcelProcessor(input_file, config)
        df = excel_processor.read_data()

        # Создаем процессор доставки
        delivery_processor = DeliveryProcessor(df, config)

        # Обрабатываем данные
        delivery_processor.process()

        # Сохраняем результаты
        delivery_processor.save_results()

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
