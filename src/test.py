"""Тестовый скрипт для проверки конфигурации."""

import sys
from pathlib import Path

from processors.delivery_processor import DeliveryProcessor
from processors.excel_processor import ExcelProcessor
from utils import ConfigManager
from utils.constants import DeliveryType

config = ConfigManager()
strategy_config = config.get_strategy_config(DeliveryType.POSTAL.value)

print(strategy_config)

input_file = Path("files/file_new_form.xlsx")
if not input_file.exists():
    print(f"Ошибка: Файл {input_file} не найден")
    sys.exit(1)

# print(input_file)
excel_processor = ExcelProcessor(input_file, config)
df = excel_processor.read_data()
print(df)
delivery_processor = DeliveryProcessor(df, config)
print(delivery_processor)
# # Обрабатываем данные
# out = delivery_processor.process()
# print(out)
# # Сохраняем результаты
# delivery_processor.save_results()
