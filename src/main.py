"""Основной модуль приложения."""

from pathlib import Path

from processors.delivery_processor import DeliveryProcessor
from processors.excel_processor import ExcelProcessor
from validators.data_validator import DataValidator


def process_client_data(input_file: Path) -> tuple[bool, str]:
    """Основная функция обработки клиентских данных.

    Args:
        input_file: путь к входному XLSX файлу

    Returns:
        tuple[bool, str]: (успех операции, сообщение о результате)
    """
    try:
        # Чтение файла
        excel_processor = ExcelProcessor(input_file)
        data = excel_processor.read_data()

        # Валидация данных
        validator = DataValidator()
        if not validator.validate(data):
            return False, validator.get_error_message()

        # Обработка данных о доставке
        delivery_processor = DeliveryProcessor(data)
        delivery_processor.process()

        # Сохранение результатов
        delivery_processor.save_results()

        return True, "Данные успешно обработаны"

    except Exception as e:
        return False, f"Ошибка обработки данных: {str(e)}"


def main():
    """Основная функция приложения."""
    # Пример использования
    input_file = Path("input.xlsx")
    success, message = process_client_data(input_file)
    print(message)


if __name__ == "__main__":
    main()
    main()
