"""Генератор тестовых данных."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Константы для генерации
PICKUP_POINTS = [
    "Бемби (передача вторник и пятница)",
    (
        "Атмосфера (вторник и четверг, пр-т Машиностроителей д.9 "
        "ТРЦ Аврора 2 этаж., выдача 60 руб)"
    ),
    "Глобус (среда и суббота, Ленинградский пр-т, д. 54)",
    "Радуга (понедельник и четверг, ул. Труфанова, д. 19)",
    "Солнышко (вторник и пятница, ул. Свободы, д. 46)",
]

SURNAMES = [
    "Иванов",
    "Петров",
    "Сидоров",
    "Смирнов",
    "Кузнецов",
    "Попов",
    "Васильев",
    "Соколов",
    "Михайлов",
    "Новиков",
    "Федоров",
    "Морозов",
    "Волков",
    "Алексеев",
    "Лебедев",
    "Семенов",
    "Егоров",
    "Павлов",
    "Козлов",
    "Степанов",
]

NAMES = [
    "Иван",
    "Петр",
    "Сергей",
    "Андрей",
    "Дмитрий",
    "Алексей",
    "Максим",
    "Михаил",
    "Николай",
    "Александр",
    "Владимир",
    "Евгений",
    "Павел",
    "Василий",
    "Виктор",
    "Игорь",
    "Денис",
    "Артем",
    "Антон",
    "Олег",
]

POSTAL_CODES = [
    "150000",
    "150001",
    "150002",
    "150003",
    "150004",
    "150005",
    "150006",
    "150007",
    "150008",
    "150009",
    "150010",
    "150011",
    "150012",
    "150013",
    "150014",
    "150015",
    "150016",
    "150017",
    "150018",
    "150019",
]


def generate_phone():
    """Генерация случайного номера телефона."""
    return f"+7980{random.randint(1000000, 9999999)}"


def generate_timestamp():
    """Генерация случайной отметки времени."""
    base = datetime.now()
    delta = timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
    return (base - delta).strftime("%d.%m.%Y %H:%M:%S")


def generate_data():
    """Генерация тестовых данных."""
    data = []
    for _ in range(100):
        delivery_type = random.choice(["Почта", "Центр_Выдачи"])
        row = {
            "Отметка времени": generate_timestamp(),
            "Способ передачи": delivery_type,
            "Получатель заказа": "",
            "Фамилия": "",
            "Имя": "",
            "Ваша Фамилия": "",
            "Ваше Имя": "",
            "Фамилия получателя заказа": "",
            "Имя получателя заказа": "",
            "Индекс отделения для получения.": "",
            "ФИО полностью": "",
            "Телефон": "",
            "Список": "",
        }

        if delivery_type == "Почта":
            row["ФИО полностью"] = f"{random.choice(SURNAMES)} {random.choice(NAMES)}"
            row["Телефон"] = generate_phone()
            row["Индекс отделения для получения."] = random.choice(POSTAL_CODES)
        else:
            receiver_type = random.choice(["Лично я", "Другой человек"])
            row["Получатель заказа"] = receiver_type
            row["Список"] = random.choice(PICKUP_POINTS)

            if receiver_type == "Лично я":
                row["Фамилия"] = random.choice(SURNAMES)
                row["Имя"] = random.choice(NAMES)
            else:
                row["Ваша Фамилия"] = random.choice(SURNAMES)
                row["Ваше Имя"] = random.choice(NAMES)
                row["Фамилия получателя заказа"] = random.choice(SURNAMES)
                row["Имя получателя заказа"] = random.choice(NAMES)

        data.append(row)
    return data


def save_csv(filename="new_file.csv"):
    """Сохранение данных в CSV файл."""
    data = generate_data()
    fieldnames = [
        "Отметка времени",
        "Способ передачи",
        "Получатель заказа",
        "Фамилия",
        "Имя",
        "Ваша Фамилия",
        "Ваше Имя",
        "Фамилия получателя заказа",
        "Имя получателя заказа",
        "Индекс отделения для получения.",
        "ФИО полностью",
        "Телефон",
        "Список",
    ]

    # Создаем директорию files если её нет
    files_dir = Path("files")
    files_dir.mkdir(exist_ok=True)

    # Сохраняем файл
    file_path = files_dir / filename
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        print(f"Файл сохранен: {file_path}")


if __name__ == "__main__":
    save_csv()
