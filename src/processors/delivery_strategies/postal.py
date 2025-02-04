"""Модуль для обработки почтовых отправлений."""

import re

import pandas as pd

from processors.delivery_strategies.base import DeliveryStrategy


class PostalDeliveryStrategy(DeliveryStrategy):
    """Стратегия обработки почтовой доставки."""

    def _normalize_phone(self, phone: str) -> str:
        """Нормализация номера телефона в формат 79XXXXXXXXX.

        Args:
            phone: Строка с номером телефона

        Returns:
            str: Нормализованный номер телефона
        """
        # Проверяем на None и пустые значения
        if phone is None or pd.isna(phone):
            return ""

        # Проверяем тип и конвертируем в строку
        try:
            phone = str(phone)
        except (TypeError, ValueError):
            return ""

        # Удаляем все не цифры
        clean_phone = re.sub(r"\D", "", phone)

        # Нормализуем номер
        if clean_phone.startswith("8"):
            clean_phone = "7" + clean_phone[1:]
        elif len(clean_phone) == 10 and clean_phone.startswith("9"):
            clean_phone = "7" + clean_phone

        # Проверяем финальный формат и возвращаем результат
        return (
            clean_phone
            if len(clean_phone) == 11 and clean_phone.startswith("7")
            else ""
        )

    def _normalize_postcode(self, postcode: str) -> str:
        """Нормализация почтового индекса.

        Args:
            postcode: Строка с индексом

        Returns:
            str: Нормализованный индекс (6 цифр) или пустая строка
        """
        # Проверяем на None и пустые значения
        if postcode is None or pd.isna(postcode):
            return ""

        # Проверяем тип и конвертируем в строку
        try:
            postcode = str(postcode)
        except (TypeError, ValueError):
            return ""

        # Удаляем все не цифры и проверяем длину
        clean_postcode = re.sub(r"\D", "", postcode)
        return clean_postcode if len(clean_postcode) == 6 else ""

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных о почтовой доставке.

        Args:
            data: DataFrame с данными клиентов

        Returns:
            DataFrame: Обработанные данные почтовых клиентов
        """
        # Проверяем на пустой DataFrame
        if data.empty:
            return pd.DataFrame()

        # Создаем копию данных
        processed_data = data.copy()

        # Нормализуем телефонные номера
        if "Телефон" in processed_data.columns:
            processed_data["Телефон"] = processed_data["Телефон"].apply(
                self._normalize_phone
            )

        # Нормализуем почтовые индексы
        if "только Индекс отделения для получения." in processed_data.columns:
            processed_data["только Индекс отделения для получения."] = processed_data[
                "только Индекс отделения для получения."
            ].apply(self._normalize_postcode)

        return processed_data

    def save(self, data: pd.DataFrame, output_path: str) -> None:
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

        # Создаем DataFrame для сохранения
        df_postal = pd.DataFrame(postal_table_data, columns=headers)

        # Явно конвертируем столбец телефона в строку
        df_postal["recipient_phone"] = df_postal["recipient_phone"].astype(str)

        # Сохраняем в Excel
        df_postal.to_excel(output_path, index=False)
        print(f"\nДанные сохранены в файл: {output_path}")
