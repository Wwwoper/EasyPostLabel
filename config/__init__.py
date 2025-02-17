"""Пакет с конфигурацией."""

from pathlib import Path
from typing import Any, Dict

import yaml


class ConfigManager:
    """Класс для загрузки и управления конфигурациями."""

    def __init__(self):
        """Инициализация конфигурационного менеджера."""
        self.config_dir = Path(__file__).parent
        self._config = {}

    def load_config(self) -> Dict[Any, Any]:
        """Загрузка всех конфигураций."""
        # Загрузка базовой конфигурации
        self._config.update(self._load_yaml("base.yaml"))

        # Загрузка маппинга столбцов
        self._config.update(self._load_yaml("columns.yaml"))

        # Загрузка конфигураций стратегий
        strategies_dir = self.config_dir / "delivery" / "strategies"

        # Сначала загружаем main.yaml
        main_config = self._load_yaml(strategies_dir / "main.yaml")
        self._config.update(main_config)

        # Затем загружаем стратегии
        for strategy in main_config.get("enabled_strategies", []):
            strategy_file = strategies_dir / f"{strategy}.yaml"
            if strategy_file.exists():
                self._config["delivery_strategies"].update(
                    self._load_yaml(strategy_file)["delivery_strategies"]
                )

        return self._config

    def _load_yaml(self, path: Path) -> Dict[Any, Any]:
        """Загрузка YAML файла."""
        with open(path) as f:
            return yaml.safe_load(f)


# Создаем экземпляр конфигурации
config = ConfigManager().load_config()
