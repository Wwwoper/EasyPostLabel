# Python Project Template

Шаблон настроек для Python проектов с полной конфигурацией линтеров, форматтеров и процессов разработки.

## 🛠 Структура проекта

```
.
├── config/                    # Конфигурационные файлы
│   ├── __init__.py
│   └── config.yaml           # Основной конфиг
├── src/                      # Исходный код
│   ├── __init__.py
│   ├── main.py              # Точка входа
│   ├── processors/          # Процессоры данных
│   ├── utils/               # Утилиты
│   └── validators/          # Валидаторы
├── tests/                    # Тесты
├── .gitignore               # Игнорируемые файлы
├── LICENSE                  # Лицензия
├── mypy.ini                # Конфигурация mypy
├── pytest.ini              # Конфигурация pytest
├── README.md               # Документация проекта
└── requirements.txt        # Зависимости проекта
```

## ⚙️ Настройка окружения

### Предварительные требования

- Python 3.11+
- Git
- VS Code (рекомендуется)

### Установка

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd <project-name>
```

2. Создайте виртуальное окружение:

```bash
python -m venv .venv
```

3. Активация виртуального окружения:

VS Code автоматически активирует виртуальное окружение благодаря настройке `python.terminal.activateEnvironment: true` в `settings.json`.

Если вы используете другой редактор или терминал, активируйте вручную:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

4. Установите зависимости:

```bash
pip install -r requirements.txt
```

5. Настройте pre-commit хуки:

```bash
pre-commit install
```

6. Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Используйте python-dotenv для загрузки переменных

```bash
pip install python-dotenv
```

7. **Важно!** Раскомментируйте секцию `.vscode` в `.gitignore` перед первым коммитом:

```gitignore
# VS Code
.vscode/*
```

Это необходимо для исключения настроек VS Code из рабочего репозитория.

## 🔧 Инструменты разработки

### Форматирование и линтинг

- **Black** (v25.1.0) - форматтер кода
- **isort** (v6.0.0) - сортировка импортов
- **flake8** (v7.1.1) - линтер
  - flake8-docstrings (v1.7.0)
  - flake8-bugbear (v24.2.6)
  - flake8-comprehensions (v3.14.0)
- **mypy** (v1.14.1) - статический анализатор типов
- **bandit** (v1.7.6) - анализатор безопасности
- **pre-commit** (v4.1.0) - управление хуками
- **pytest** (v8.0.2) - тестирование

### Дополнительные зависимости проекта

- **pandas** (>=1.3.0) - обработка данных
- **openpyxl** (>=3.0.0) - работа с Excel
- **pyyaml** (>=5.4.0) - работа с YAML конфигурацией

### VS Code расширения

- Python
- Black Formatter
- Flake8
- isort

### VS Code настройки

#### settings.json

VS Code автоматически настроен для Python разработки через `settings.json`:

- Форматирование при сохранении (Black)
- Сортировка импортов (isort)
- Линтинг (flake8)
- Проверка типов (mypy)
- Автоактивация виртуального окружения

#### launch.json и tasks.json

Настроены быстрые команды для запуска pre-commit:

1. **Через Command Palette (⌘⇧P или Ctrl+Shift+P)**:
   - Введите "Tasks: Run Task"
   - Выберите "Run pre-commit"

2. **Через клавиатуру**:
   - macOS: `⌘⇧B` (default build task)
   - Windows/Linux: `Ctrl+Shift+B`

3. **Через отладчик (F5)**:

```json
   {
       "name": "Run pre-commit",
       "type": "python",
       "request": "launch",
       "module": "pre_commit",
       "args": ["run", "--all-files"],
       "justMyCode": false
   }
```

4. **Через tasks.json**:

```json
   {
       "label": "Run pre-commit",
       "type": "shell",
       "command": "pre-commit run --all-files",
       "group": {
           "kind": "build",
           "isDefault": true
       }
   }
```

Подробная документация по настройкам VS Code доступна в [.vscode/README.md](.vscode/README.md)

## 🚀 Процесс разработки

### Проверка кода

```bash
# Запуск всех pre-commit хуков
pre-commit run --all-files

# Форматирование кода
black .

# Сортировка импортов
isort .

# Проверка типов
mypy .

# Линтинг
flake8

# Запуск тестов
pytest
```

### Создание Pull Request

1. Создайте ветку для изменений
2. Внесите изменения
3. Убедитесь, что все проверки пройдены
4. Создайте Pull Request используя шаблон из docs/PR.md

## 📝 Соглашения о коде

- Длина строки: 88 символов
- Документация: Google style docstrings
- Типизация: обязательна для всех функций
- Сортировка импортов: согласно конфигурации isort
- Тесты: обязательны для нового функционала
- Комментарии: на русском языке для улучшения понимания

## 🤝 Участие в разработке

1. Fork репозитория
2. Создайте ветку для изменений
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).
