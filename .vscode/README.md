# VS Code Settings Documentation

## 🔧 Настройки VS Code для Python разработки

### settings.json

#### Python настройки

- `python.defaultInterpreterPath` - путь к виртуальному окружению
- `python.analysis.extraPaths` - дополнительные пути для анализа кода
- `python.terminal.activateEnvironment` - автоактивация виртуального окружения

#### Форматирование

- `black-formatter.args` - настройки Black (длина строки 88 символов)
- `isort.args` - настройки isort (профиль black, длина строки 88)
- `editor.formatOnSave` - автоформатирование при сохранении

#### Линтинг

- `flake8.args` - настройки flake8:
  - max-line-length=88 - максимальная длина строки
  - extend-ignore=E203 - игнорирование конфликтов с black
  - docstring-convention=google - стиль документации Google

#### Типизация

- `mypy-type-checker.args`:
  - disallow-untyped-defs - запрет функций без типов
  - check-untyped-defs - проверка функций без типов
  - ignore-missing-imports - игнорирование отсутствующих типов в импортах

### launch.json

#### Конфигурация для pre-commit

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

Запуск:

- Через меню "Run and Debug" (⇧⌘D)
- Через клавишу F5
- Выбрав конфигурацию "Run pre-commit"

### tasks.json

#### Task для pre-commit

```json
{
    "label": "Run pre-commit",
    "type": "shell",
    "command": "pre-commit run --all-files",
    "group": {
        "kind": "build",
        "isDefault": true
    },
    "presentation": {
        "reveal": "always",
        "panel": "new"
    }
}
```

Запуск:

- Через Command Palette (⌘⇧P): "Tasks: Run Task" → "Run pre-commit"
- Через клавиатуру: ⌘⇧B (macOS) или Ctrl+Shift+B (Windows/Linux)
- Через меню: Terminal → Run Task → Run pre-commit

## ⚡️ Быстрые команды

### macOS

- ⌘⇧B - запуск pre-commit (default build task)
- ⌘⇧P - открытие Command Palette
- F5 - запуск через отладчик

### Windows/Linux

- Ctrl+Shift+B - запуск pre-commit (default build task)
- Ctrl+Shift+P - открытие Command Palette
- F5 - запуск через отладчик

## 🔍 Расширения VS Code

### Обязательные

- Python - основное расширение для Python
- Black Formatter - форматирование кода
- Flake8 - линтинг
- isort - сортировка импортов

### Рекомендуемые

- Python Docstring Generator - генерация документации
- Python Type Hint - подсказки типов
- GitLens - расширенная работа с Git
- Error Lens - подсветка ошибок в коде

## 🚀 Советы по использованию

1. **Автоформатирование**:
   - Код форматируется автоматически при сохранении
   - Используйте ⌘S (macOS) или Ctrl+S (Windows/Linux)

2. **Линтинг**:
   - Ошибки подсвечиваются в реальном времени
   - Полная проверка при запуске pre-commit

3. **Отладка**:
   - Используйте F5 для быстрого запуска pre-commit
   - Результаты отображаются в новой панели

4. **Command Palette**:
   - Быстрый доступ ко всем командам
   - Поиск по названию команды

## 🔄 Обновление настроек

1. При изменении настроек в `.vscode/*.json`:
   - Убедитесь, что файлы добавлены в Git
   - Обновите документацию при необходимости

2. При добавлении новых расширений:
   - Добавьте их в список рекомендуемых
   - Обновите соответствующие настройки

## 🐛 Решение проблем

### Распространенные проблемы

1. **Не работает форматирование**:
   - Проверьте установку Black
   - Убедитесь, что выбран правильный форматтер

2. **Ошибки линтинга**:
   - Проверьте настройки flake8
   - Убедитесь в совместимости версий

3. **Проблемы с pre-commit**:
   - Проверьте установку хуков
   - Обновите pre-commit до последней версии
