"""Модуль для обработки альтернативных способов доставки."""

import datetime
import logging
from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, NamedStyle, Side
from openpyxl.utils import get_column_letter
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
    def from_row(cls, row: pd.Series, config: Dict) -> Optional["PickupPointClient"]:
        """Создание клиента из строки данных."""
        try:
            receiver_type = str(row.get("Получатель заказа", "")).strip()
            logger.debug("Обработка получателя типа: %s", receiver_type)

            # Получаем конфигурацию для типа получателя
            receiver_config = None
            for r_type in config["receiver_types"].values():
                if r_type["type"] == receiver_type:
                    receiver_config = r_type
                    break

            if not receiver_config:
                logger.warning("Неизвестный тип получателя: %s", receiver_type)
                return None

            # Получаем имя и фамилию
            surname = str(
                row.get(receiver_config["name_fields"]["surname"], "")
            ).strip()
            name = str(row.get(receiver_config["name_fields"]["name"], "")).strip()
            logger.debug("Получены данные: фамилия='%s', имя='%s'", surname, name)

            if not surname or not name:
                logger.warning(
                    "Пропуск: нет имени для %s (фамилия='%s', имя='%s')",
                    receiver_type,
                    surname,
                    name,
                )
                return None

            # Получаем код пункта выдачи
            pickup_config = config["pickup_point"]
            pickup_raw = str(row.get(pickup_config["source_column"], "")).strip()
            logger.debug("Сырые данные пункта выдачи: %s", pickup_raw)

            try:
                pickup_parts = pickup_raw.split(pickup_config["split_by"])
                pickup_point = pickup_parts[pickup_config["position"]]
                logger.debug(
                    "Разбор пункта выдачи: части=%s, выбрано='%s'",
                    pickup_parts,
                    pickup_point,
                )
            except (IndexError, AttributeError) as e:
                logger.error("Ошибка разбора пункта выдачи: %s", str(e))
                return None

            if not pickup_point:
                logger.warning("Пропуск: нет центра выдачи в строке '%s'", pickup_raw)
                return None

            client = cls(
                full_name=f"{surname} {name}".title(),
                pickup_point=pickup_point,
                receiver_type=receiver_type,
            )
            logger.debug("Создан клиент: %s", client)
            return client

        except Exception as e:
            logger.exception("Ошибка создания клиента: %s", str(e))
            return None

    def __str__(self) -> str:
        """Строковое представление клиента."""
        return f"ФИО='{self.full_name}', ПВ='{self.pickup_point}', Тип='{self.receiver_type}'"


class PickupPointStrategy(DeliveryStrategy):
    """Стратегия обработки данных для пунктов выдачи."""

    SENDER_NAME = "Беренёвой Ольги"
    SENDER_PHONE = "+79159833971"

    def __init__(self, config_manager: ConfigManager) -> None:
        """Инициализация стратегии."""
        self.config_manager = config_manager
        self.config = config_manager.config["delivery_methods"]["types"]["Центр_Выдачи"]

    def _create_styles(self, workbook: Workbook) -> NamedStyle:
        """Создание стилей для бирок."""
        style = NamedStyle(name="birka")
        style.font = Font(name="Century", size=13, b=True)  # используем b вместо bold
        border = Side(style="thin", color="000000")
        style.border = Border(left=border, right=border, top=border, bottom=border)
        style.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )
        workbook.add_named_style(style)
        return style

    def _create_labels(
        self, data: pd.DataFrame, sheet: Worksheet, style: NamedStyle
    ) -> None:
        """Создание бирок на листе."""
        logger.info("Начало создания бирок для %d клиентов", len(data))

        row = 1
        col_map = {0: "A", 1: "C", 2: "E"}

        for idx, client in enumerate(data.itertuples(), 1):
            col = col_map[idx % 3]
            logger.debug(
                "Создание бирки #%d: позиция=%s%d, клиент=%s", idx, col, row, client.ФИО
            )

            # Добавляем данные и применяем стили
            cells = [
                (f"{col}{row}", client.ФИО),
                (f"{col}{row+1}", f"в ЦВ {client.Центр_Выдачи}"),
                (f"{col}{row+2}", "от Беренёвой Ольги"),
            ]

            for cell_ref, value in cells:
                cell = sheet[cell_ref]
                cell.value = value
                cell.style = style
                logger.debug("Ячейка %s: значение='%s'", cell_ref, value)

            # Переходим к следующей группе бирок
            if idx % 3 == 0:
                row += 4
                logger.debug("Переход на новую строку: %d", row)

        logger.info("Создание бирок завершено")

    def _format_worksheet(self, sheet: Worksheet) -> None:
        """Форматирование листа с бирками."""
        logger.debug("Начало форматирования листа")

        # Устанавливаем размеры основных колонок
        for col in ["A", "C", "E"]:
            sheet.column_dimensions[col].width = 30
            logger.debug("Установлена ширина колонки %s: 30", col)

        # Устанавливаем минимальную ширину промежуточных колонок
        for col in ["B", "D"]:
            sheet.column_dimensions[col].width = 0.17  # примерно 1 мм
            logger.debug("Установлена минимальная ширина колонки %s: 0.17", col)

        # Устанавливаем высоту строк
        for row in range(1, sheet.max_row + 1):
            height = 25 if row % 4 != 0 else 3
            sheet.row_dimensions[row].height = height
            logger.debug("Установлена высота строки %d: %d", row, height)

        logger.debug("Форматирование листа завершено")

    def _create_delivery_list(
        self, data: pd.DataFrame, sheet: Worksheet, style: NamedStyle
    ) -> None:
        """Создание списка доставки на листе.

        Args:
            data: DataFrame с данными
            sheet: Лист Excel
            style: Стиль для списка
        """
        logger.debug("Начало создания списка доставки")

        # Заголовок
        sheet["B1"].value = f"Заказы от {self.SENDER_NAME} {self.SENDER_PHONE}"
        sheet["B1"].style = style
        sheet["B2"].value = ""

        # Дата и количество
        today = datetime.date.today().strftime("%d.%m.%Y")
        sheet["B3"].value = today
        sheet["C3"].value = f"{len(data)} человек в списке"
        sheet["B3"].style = style
        sheet["C3"].style = style

        # Устанавливаем размеры колонок
        sheet.column_dimensions["A"].width = 5
        sheet.column_dimensions["B"].width = 30
        sheet.column_dimensions["C"].width = 30

        # Сортируем данные
        sorted_data = data.sort_values(["Центр_Выдачи", "ФИО"])
        border_bottom = Border(bottom=Side(style="thin"))

        current_center = None
        row_num = 4

        # Создаем список
        for _, row in sorted_data.iterrows():
            sheet[f"B{row_num}"].value = row["ФИО"]
            sheet[f"C{row_num}"].value = f"в ЦВ {row['Центр_Выдачи']}"

            sheet[f"B{row_num}"].style = style
            sheet[f"C{row_num}"].style = style

            new_center = str(row["Центр_Выдачи"])
            needs_border = current_center and current_center != new_center

            if needs_border:
                prev_row = row_num - 1
                sheet[f"B{prev_row}"].border = border_bottom
                sheet[f"C{prev_row}"].border = border_bottom

            current_center = new_center
            sheet.row_dimensions[row_num].height = 15
            row_num += 1

        # Добавляем границу последней строке
        if row_num > 4:
            last_row = row_num - 1
            sheet[f"B{last_row}"].border = border_bottom
            sheet[f"C{last_row}"].border = border_bottom

        logger.debug("Создание списка доставки завершено")

    def _get_sort_key(self, text: str) -> tuple:
        """Получение ключа для сортировки русских букв.

        Args:
            text: Текст для сортировки

        Returns:
            tuple: Кортеж чисел для сортировки
        """
        # Словарь для русских букв
        ru_alphabet = {
            "а": 1,
            "б": 2,
            "в": 3,
            "г": 4,
            "д": 5,
            "е": 6,
            "ё": 7,
            "ж": 8,
            "з": 9,
            "и": 10,
            "й": 11,
            "к": 12,
            "л": 13,
            "м": 14,
            "н": 15,
            "о": 16,
            "п": 17,
            "р": 18,
            "с": 19,
            "т": 20,
            "у": 21,
            "ф": 22,
            "х": 23,
            "ц": 24,
            "ч": 25,
            "ш": 26,
            "щ": 27,
            "ъ": 28,
            "ы": 29,
            "ь": 30,
            "э": 31,
            "ю": 32,
            "я": 33,
            " ": 0,  # пробел имеет наименьший приоритет
        }

        # Приводим к нижнему регистру и преобразуем каждую букву в числовой код
        # Для отсутствующих в словаре символов используем их коды + 1000
        # чтобы они шли после русских букв
        return tuple(ru_alphabet.get(c, ord(c) + 1000) for c in text.lower())

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка данных для пунктов выдачи."""
        try:
            if data.empty:
                return pd.DataFrame()

            logger.debug("Начало обработки данных пунктов выдачи")

            # Проверяем наличие всех нужных колонок
            required_columns = self.config["columns"]["required"]
            missing_columns = [
                col for col in required_columns if col not in data.columns
            ]
            if missing_columns:
                raise ValueError(f"Отсутствуют колонки: {', '.join(missing_columns)}")

            # Создаем список клиентов
            clients = []
            for _, row in data.iterrows():
                client = PickupPointClient.from_row(row, self.config)
                if client:
                    clients.append(client)

            # Сортируем клиентов по ФИО
            clients.sort(key=lambda x: x.full_name)
            logger.debug("Клиенты отсортированы по ФИО")

            # Создаем DataFrame
            result = pd.DataFrame(
                [
                    {
                        field["name"]: getattr(client, field["source"])
                        for field in self.config["columns"]["output"]
                    }
                    for client in clients
                ]
            )

            return result.drop_duplicates()

        except Exception as e:
            logger.exception("Ошибка при обработке данных: %s", str(e))
            raise

    def save(self, data: pd.DataFrame, output_path: str) -> None:
        """Сохранение данных в Excel файл.

        Args:
            data: DataFrame с данными
            output_path: путь для сохранения файла
        """
        # Сортируем данные по ФИО
        sorted_data = data.sort_values("ФИО").reset_index(drop=True)

        # Создаем новый Excel файл
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Бирки"

        # Получаем настройки стилей
        styles = self.config_manager.get_setting("excel_settings.styling", {})

        # Устанавливаем ширину промежуточных колонок сразу
        for col_letter in ["B", "D"]:
            sheet.column_dimensions[col_letter].width = 0.17

        # Заполняем данные
        row = 1
        col = 1
        for _, record in sorted_data.iterrows():
            # Добавляем бирку
            self._add_label(sheet, row, col, record, styles)

            # Переходим к следующей позиции
            col += 2
            if col > 5:  # Максимум 3 бирки в строке
                # Устанавливаем высоту промежутка между группами бирок
                sheet.row_dimensions[row + 3].height = 3
                col = 1
                row += 4

        # Если есть данные, устанавливаем высоту последнего промежутка
        if not sorted_data.empty:
            sheet.row_dimensions[row + 3].height = 3

        # Сохраняем файл
        wb.save(output_path)

    def _add_label(
        self, sheet, row: int, col: int, record: pd.Series, styles: dict
    ) -> None:
        """Добавление одной бирки на лист.

        Args:
            sheet: Лист Excel для добавления бирки
            row: Номер строки
            col: Номер колонки
            record: Строка данных
            styles: Настройки стилей
        """
        # Создаем стиль для бирки
        style = NamedStyle(name=f"birka_{row}_{col}")
        style.font = Font(
            name=styles.get("font_name", "Century"),
            size=13,  # Фиксированный размер шрифта
            bold=True,
        )
        border = Side(style="thin", color="000000")
        style.border = Border(left=border, right=border, top=border, bottom=border)
        style.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

        # Добавляем данные и применяем стили
        cells = [
            (row, record["ФИО"]),
            (row + 1, f"в ЦВ {record['Центр_Выдачи']}"),
            (row + 2, f"от {self.SENDER_NAME}"),
        ]

        for row_idx, value in cells:
            cell = sheet.cell(row=row_idx, column=col)
            cell.value = value
            cell.style = style

        # Устанавливаем ширину только для основных колонок
        if col % 2 != 0:  # только нечетные колонки (A, C, E)
            sheet.column_dimensions[get_column_letter(col)].width = styles.get(
                "column_width", 30
            )
