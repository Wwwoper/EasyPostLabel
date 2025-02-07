"""Модуль для обработки альтернативных способов доставки."""

import datetime
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Border, Font, NamedStyle, Side
from openpyxl.worksheet.worksheet import Worksheet

from processors.delivery_strategies.base import DeliveryStrategy
from utils.config import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class PickupPointClient:
    """Структура данных клиента пункта выдачи."""

    full_name: str
    pickup_point: str
    receiver_type: str

    @classmethod
    def from_row(cls, row: pd.Series) -> Optional["PickupPointClient"]:
        """Создание клиента из строки данных."""
        try:
            receiver_type = str(row.get("Получатель заказа", "")).strip()
            name_fields = {
                "Лично я": ("Фамилия", "Имя"),
                "Другой человек": (
                    "Фамилия получателя заказа",
                    "Имя получателя заказа",
                ),
            }

            fields = name_fields.get(receiver_type)
            if not fields:
                logger.warning("Неизвестный тип получателя: %s", receiver_type)
                return None

            surname = str(row.get(fields[0], "")).strip()
            name = str(row.get(fields[1], "")).strip()

            if not surname or not name:
                logger.warning("Пропуск: нет имени для %s", receiver_type)
                return None

            pickup_point = str(row.get("Список", "")).strip().split()[0]
            if not pickup_point:
                logger.warning("Пропуск: нет центра выдачи")
                return None

            return cls(
                full_name=f"{surname} {name}".title(),
                pickup_point=pickup_point,
                receiver_type=receiver_type,
            )

        except Exception as e:
            logger.error("Ошибка создания клиента: %s", str(e))
            return None


class PickupPointStrategy(DeliveryStrategy):
    """Стратегия обработки данных для пунктов выдачи."""

    SENDER_NAME = "Беренёвой Ольги"
    SENDER_PHONE = "+79159833971"

    def __init__(self, config_manager: ConfigManager) -> None:
        """Инициализация стратегии."""
        self.config_manager = config_manager

    def _create_styles(self, workbook: Workbook) -> Tuple[NamedStyle, NamedStyle]:
        """Создание стилей для Excel."""
        birka_style = NamedStyle(name="birka")
        birka_style.font = Font(name="Century", size=13)
        border = Side(style="thin", color="000000")
        birka_style.border = Border(
            left=border, top=border, right=border, bottom=border
        )

        list_style = NamedStyle(name="list")
        list_style.font = Font(name="Century", size=12)

        workbook.add_named_style(birka_style)
        workbook.add_named_style(list_style)

        return birka_style, list_style

    def _create_labels(self, data: pd.DataFrame, sheet: Worksheet) -> None:
        """Создание бирок на листе."""
        b = 1
        for idx, row in enumerate(data.itertuples(), 1):
            column = {0: "A", 1: "C", 2: "E"}[(idx - 1) % 3]

            for i, value in enumerate(
                [row.ФИО, f"в ЦВ {row.Центр_Выдачи}", f"от {self.SENDER_NAME}"]
            ):
                cell = f"{column}{b+i}"
                sheet[cell].value = value
                sheet[cell].style = "birka"

            if idx % 3 == 0:
                b += 4

        max_row = sheet.max_row
        for row in range(1, max_row + 1):
            sheet.row_dimensions[row].height = 25 if row % 4 != 0 else 3

    def _create_delivery_list(self, data: pd.DataFrame, sheet: Worksheet) -> None:
        """Создание списка доставки на листе."""
        sheet["B1"].value = f"Заказы от {self.SENDER_NAME} {self.SENDER_PHONE}"
        sheet["B1"].style = "list"
        sheet["B2"].value = ""

        today = datetime.date.today().strftime("%d.%m.%Y")
        sheet["B3"].value = today
        sheet["C3"].value = f"{len(data)} человек в списке"

        sorted_data = data.sort_values(["Центр_Выдачи", "ФИО"])
        border_bottom = Border(bottom=Side(style="thin"))

        current_center: str | None = None
        row_num = 4

        for _, row in sorted_data.iterrows():
            sheet[f"B{row_num}"].value = row["ФИО"]
            sheet[f"C{row_num}"].value = f"в ЦВ {row['Центр_Выдачи']}"

            sheet[f"B{row_num}"].style = "list"
            sheet[f"C{row_num}"].style = "list"

            new_center = str(row["Центр_Выдачи"])
            needs_border = current_center and current_center != new_center

            if needs_border:
                prev_row = row_num - 1
                sheet[f"B{prev_row}"].border = border_bottom
                sheet[f"C{prev_row}"].border = border_bottom

            current_center = new_center
            sheet.row_dimensions[row_num].height = 15
            row_num += 1

        if row_num > 4:
            last_row = row_num - 1
            sheet[f"B{last_row}"].border = border_bottom
            sheet[f"C{last_row}"].border = border_bottom

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных для пунктов выдачи."""
        try:
            if data.empty:
                return pd.DataFrame()

            logger.debug("Начало обработки данных пунктов выдачи")

            # Проверяем наличие всех нужных колонок
            required_columns = [
                "Получатель заказа",
                "Список",
                "Фамилия",
                "Имя",
                "Фамилия получателя заказа",
                "Имя получателя заказа",
            ]

            missing_columns = [
                col for col in required_columns if col not in data.columns
            ]
            if missing_columns:
                raise ValueError(f"Отсутствуют колонки: {', '.join(missing_columns)}")

            # Создаем список клиентов
            clients = []
            for _, row in data.iterrows():
                try:
                    receiver_type = str(row.get("Получатель заказа", "")).strip()

                    if receiver_type == "Лично я":
                        surname = str(row.get("Фамилия", "")).strip()
                        name = str(row.get("Имя", "")).strip()
                    else:  # Другой человек
                        surname = str(row.get("Фамилия получателя заказа", "")).strip()
                        name = str(row.get("Имя получателя заказа", "")).strip()

                    if not surname or not name:
                        logger.warning(
                            "Пропуск записи: отсутствует фамилия или имя для %s",
                            receiver_type,
                        )
                        continue

                    pickup_point = str(row.get("Список", "")).strip().split()[0]

                    clients.append(
                        PickupPointClient(
                            full_name=f"{surname} {name}".title(),
                            pickup_point=pickup_point,
                            receiver_type=receiver_type,
                        )
                    )
                except Exception as e:
                    logger.error("Ошибка обработки строки: %s", str(e))
                    continue

            # Создаем DataFrame
            result = pd.DataFrame(
                [
                    {
                        "ФИО": client.full_name,
                        "Центр_Выдачи": client.pickup_point,
                    }
                    for client in clients
                ]
            )

            result = result.drop_duplicates().sort_values(["Центр_Выдачи", "ФИО"])
            return result

        except Exception as e:
            logger.exception("Ошибка при обработке данных: %s", str(e))
            raise

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение результатов в файл."""
        if data.empty:
            logger.warning("Нет данных для сохранения")
            return

        try:
            wb = Workbook()
            self._create_styles(wb)

            labels_sheet = wb.active
            labels_sheet.title = "Бирки"
            delivery_sheet = wb.create_sheet("Список доставки")

            # Настройка размеров колонок
            labels_sheet.column_dimensions["A"].width = 30
            labels_sheet.column_dimensions["B"].width = 1
            labels_sheet.column_dimensions["C"].width = 30
            labels_sheet.column_dimensions["D"].width = 1
            labels_sheet.column_dimensions["E"].width = 30
            labels_sheet.column_dimensions["F"].width = 1

            delivery_sheet.column_dimensions["A"].width = 5
            delivery_sheet.column_dimensions["B"].width = 30
            delivery_sheet.column_dimensions["C"].width = 30

            self._create_labels(data, labels_sheet)
            self._create_delivery_list(data, delivery_sheet)

            wb.save(output_path)
            logger.info("Данные сохранены в файл: %s", output_path)
            logger.debug("Сохранено %d записей", len(data))

        except Exception as e:
            logger.exception("Ошибка при сохранении файла: %s", str(e))
            raise
