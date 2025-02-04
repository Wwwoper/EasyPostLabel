"""Модуль для обработки почтовых отправлений."""

import re

import pandas as pd
from tabulate import tabulate

from processors.delivery_strategies.base import DeliveryStrategy


class PostalDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки почтовой доставки."""

    def _normalize_phone(self, phone: str) -> str:
        """Нормализация номера телефона в формат 79XXXXXXXXX.

        Args:
            phone: Строка с номером телефона

        Returns:
            str: Нормализованный номер телефона

        Examples:
            >>> _normalize_phone("89999002291")
            "79999002291"
            >>> _normalize_phone("+79203451508")
            "79203451508"
            >>> _normalize_phone("9203451508")
            "79203451508"
        """
        if not isinstance(phone, str):
            return ""

        # Удаляем все не цифры
        phone = re.sub(r"\D", "", phone)

        # Если номер начинается с 8, заменяем на 7
        if phone.startswith("8"):
            phone = "7" + phone[1:]

        # Если номер начинается с 9 и длина 10 цифр, добавляем 7 в начало
        elif len(phone) == 10 and phone.startswith("9"):
            phone = "7" + phone

        # Проверяем корректность номера (11 цифр, начинается с 7)
        if len(phone) == 11 and phone.startswith("7"):
            return phone

        return ""

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о почтовой доставке.

        Args:
            data: DataFrame с данными клиентов

        Returns:
            DataFrame: Обработанные данные почтовых клиентов
        """
        # Создаем копию данных
        processed_data = data.copy()

        # Нормализуем телефонные номера
        processed_data["Телефон"] = processed_data["Телефон"].apply(
            self._normalize_phone
        )

        return processed_data

    def save(self, data: pd.DataFrame, output_path: str):
        """Сохранение результатов в формате для почты.

        Args:
            data: DataFrame с данными клиентов
            output_path: Путь для сохранения файла
        """
        if data.empty:
            return

        # Создаем данные для таблицы почтовых клиентов
        postal_table_data = []
        headers = [
            "recipient_address",
            "recipient_name",
            "weight",
            "recipient_phone",
            "mail_type",
        ]

        # Преобразуем DataFrame в список словарей для удобства
        postal_clients_dict = data.to_dict("records")

        for client in postal_clients_dict:
            row = [
                client["только Индекс отделения для получения."],  # recipient_address
                client["ФИО полностью"],  # recipient_name
                "0",  # weight
                str(client["Телефон"]),  # recipient_phone как строка
                "4",  # mail_type
            ]
            postal_table_data.append(row)

        # Выводим таблицу в консоль
        print("\nТаблица для почтовой рассылки:")
        print(tabulate(postal_table_data, headers=headers, tablefmt="grid"))

        # Создаем DataFrame для сохранения
        df_postal = pd.DataFrame(postal_table_data, columns=headers)

        # Явно конвертируем столбец телефона в строку
        df_postal["recipient_phone"] = df_postal["recipient_phone"].astype(str)

        # Сохраняем в Excel
        df_postal.to_excel(output_path, index=False)
        print(f"\nДанные сохранены в файл: {output_path}")
