"""Конфигурация для pytest."""

import sys
from pathlib import Path

# Добавляем путь к src в PYTHONPATH
sys.path.append(str(Path(__file__).parent / "src"))
