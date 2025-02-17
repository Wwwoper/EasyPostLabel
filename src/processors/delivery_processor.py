"""Обработчик данных о способах доставки."""

from typing import Dict, List, Optional

import pandas as pd

from utils.config import ConfigManager
from utils.constants import DEFAULT_OUTPUT_DIR


class DeliveryProcessor:
    """Обработчик данных о способах доставки."""

    def __init__(self, data: pd.DataFrame, config_manager: ConfigManager) -> None:
        self.data = data
        self.config_manager = config_manager
        self.delivery_data: Dict[str, pd.DataFrame] = {}

    def validate_required_fields(
        self, df: pd.DataFrame, required_fields: List[str]
    ) -> pd.DataFrame:
        """Проверка наличия и заполненности обязательных полей."""
        if not required_fields:
            return df

        # Проверяем наличие всех обязательных полей
        for field in required_fields:
            if field not in df.columns:
                print(f"Предупреждение: Поле {field} не найдено в данных")
                return pd.DataFrame()

        # Фильтруем строки с пустыми значениями в обязательных полях
        mask = pd.Series(True, index=df.index)
        for field in required_fields:
            mask &= df[field].notna() & (df[field] != "")

        return df[mask]

    def filter_data(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """Фильтрация данных по стратегии."""
        if df is None or df.empty:
            return pd.DataFrame()

        try:
            # Получаем конфигурацию стратегии
            strategy_config = self.config_manager.get_strategy_config(strategy)
            strategy_settings = strategy_config["strategy"]["delivery_strategies"][
                strategy
            ]

            print(f"\nОбработка стратегии {strategy}:")
            print(f"Исходное количество строк: {len(df)}")

            # Фильтрация по способу доставки
            if "validation" in strategy_settings:
                validation_rules = strategy_settings["validation"]
                if "delivery_method" in validation_rules:
                    delivery_rule = validation_rules["delivery_method"]
                    if "contains" in delivery_rule:
                        delivery_value = delivery_rule["contains"]
                        df = df[
                            df["delivery.method"].str.contains(
                                delivery_value, na=False, case=False
                            )
                        ]
                        print(
                            f"После фильтрации по delivery.method='{delivery_value}': {len(df)} строк"
                        )

            # Проверка обязательных полей
            required_fields = strategy_settings.get("required_fields", [])
            df = self.validate_required_fields(df, required_fields)
            print(f"После проверки обязательных полей: {len(df)} строк")

            return df

        except Exception as e:
            print(f"Ошибка при фильтрации данных для стратегии {strategy}: {str(e)}")
            return pd.DataFrame()

    def process(self) -> None:
        """Обработка данных о способах доставки."""
        if self.data.empty:
            print("\nПредупреждение: Нет данных для обработки")
            return

        # Получаем список активных стратегий из реестра
        registry_config = self.config_manager.get_registry_config()
        enabled_strategies = registry_config.get("enabled_strategies", [])
        strategy_mapping = registry_config.get("strategy_mapping", {})

        print(f"\nАктивные стратегии: {enabled_strategies}")

        # Обрабатываем каждую активную стратегию
        for strategy_name in enabled_strategies:
            try:
                # Получаем актуальное имя стратегии из маппинга
                actual_strategy = strategy_mapping.get(strategy_name, strategy_name)

                # Фильтруем данные для текущей стратегии
                filtered_data = self.filter_data(self.data, actual_strategy)

                # Сохраняем результат в словарь
                self.delivery_data[actual_strategy] = filtered_data

                # Отладочная информация
                print(f"\nНайдено клиентов для {actual_strategy}: {len(filtered_data)}")

            except Exception as e:
                print(f"Ошибка обработки стратегии {strategy_name}: {str(e)}")
                continue

    def get_processed_data(self, strategy: str) -> Optional[pd.DataFrame]:
        """Получение обработанных данных для стратегии."""
        return self.delivery_data.get(strategy)

    def save_results(self) -> None:
        """Сохранение результатов в файлы."""
        if not DEFAULT_OUTPUT_DIR.exists():
            raise OSError(f"Директория {DEFAULT_OUTPUT_DIR} не существует")

        # Сохраняем результаты для каждой стратегии
        for strategy_name, data in self.delivery_data.items():
            if not data.empty:
                output_path = DEFAULT_OUTPUT_DIR / f"{strategy_name}_clients.xlsx"
                data.to_excel(str(output_path), index=False)
                print(f"Сохранены данные для {strategy_name}: {len(data)} записей")
