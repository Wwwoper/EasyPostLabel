"""Модуль для обработки почтовых отправлений."""

import pandas as pd

from processors.delivery_strategies.base import DeliveryStrategy
from utils.normalizers import PhoneNormalizer, PostcodeNormalizer


class PostalDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки почтовой доставки."""

    def __init__(self):
        """Инициализация стратегии."""
        self.phone_normalizer = PhoneNormalizer()
        self.postcode_normalizer = PostcodeNormalizer()

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о почтовой доставке."""
        if data.empty:
            return pd.DataFrame()

        processed_data = data.copy()

        # Нормализуем телефонные номера
        if "phone" in processed_data.columns:
            processed_data["phone"] = processed_data["phone"].apply(
                self.phone_normalizer.normalize
            )

        # Нормализуем почтовые индексы
        if "postal_index" in processed_data.columns:
            processed_data["postal_index"] = processed_data["postal_index"].apply(
                self.postcode_normalizer.normalize
            )

        return processed_data

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов."""
        try:
            if data.empty:
                return

            print("\nДанные для сохранения:")
            print(data[["postal_index", "full_name", "phone"]].head())

            postal_table_data = []
            headers = [
                "recipient_address",
                "recipient_name",
                "weight",
                "recipient_phone",
                "mail_type",
            ]

            postal_clients_dict = data[["postal_index", "full_name", "phone"]].to_dict(
                "records"
            )

            for client in postal_clients_dict:
                try:
                    # Проверяем и форматируем индекс
                    index = self.postcode_normalizer.normalize(
                        client.get("postal_index")
                    )
                    if not index:
                        print(
                            f"\nПропуск клиента: отсутствует индекс - {client.get('full_name')}"
                        )
                        continue

                    # Форматируем телефон
                    phone = self.phone_normalizer.normalize(client.get("phone"))
                    if not phone:
                        print(
                            f"\nПропуск клиента: некорректный телефон - {client.get('full_name')}"
                        )
                        continue

                    row = [
                        index,
                        client.get("full_name", ""),
                        "0",
                        phone,
                        "4",
                    ]
                    postal_table_data.append(row)
                except Exception as e:
                    print(
                        f"\nОшибка при обработке клиента {client.get('full_name')}: {str(e)}"
                    )
                    continue

            if not postal_table_data:
                raise ValueError("Нет данных для сохранения после валидации")

            df_postal = pd.DataFrame(postal_table_data, columns=headers)
            print("\nПодготовленные данные для сохранения:")
            print(df_postal)

            df_postal.to_excel(output_path, index=False)
            print(f"\nДанные сохранены в файл: {output_path}")
            print(f"Сохранено записей: {len(df_postal)}")

        except Exception as e:
            print(f"\nОшибка при сохранении данных: {str(e)}")
            raise
