"""
Configuration & Settings Module
Загружает ENV-переменные и управляет пользовательскими настройками UI.
"""

import os
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Конфигурация приложения из ENV-переменных."""
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    tavily_api_key: str
    llm_max_output_tokens: int = 12000


@dataclass
class UiSettings:
    """Настройки UI пользователя."""
    words_per_chapter: int = 300
    chapter_count: int = 5
    temperature: float = 0.7

    # START_CONTRACT_UiSettings
    # Input: words_per_chapter (int), chapter_count (int), temperature (float)
    # Russian Intent: Хранить настройки UI с валидацией диапазонов
    # Output: Валидный объект UiSettings
    # END_CONTRACT_UiSettings

    def __post_init__(self):
        """Валидация настроек после инициализации."""
        self.words_per_chapter = max(100, min(1000, self.words_per_chapter))
        self.chapter_count = max(1, min(10, self.chapter_count))
        self.temperature = max(0.0, min(1.0, self.temperature))


def load_env_config() -> AppConfig:
    """
    Загружает обязательные ENV-переменные.

    # START_CONTRACT_load_env_config
    # Input: None
    # Russian Intent: Загрузить и провалидировать обязательные ENV-переменные
    # Output: Валидный AppConfig или исключение
    # END_CONTRACT_load_env_config
    """
    logger.debug("[Config][load_env_config] Belief: Загрузка ENV-конфигурации | Input: None | Expected: Валидный AppConfig")

    llm_api_key = os.getenv("LLM_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL")
    llm_model = os.getenv("LLM_MODEL")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    llm_max_output_tokens_raw = os.getenv("LLM_MAX_OUTPUT_TOKENS", "12000")

    missing = []
    if not llm_api_key:
        missing.append("LLM_API_KEY")
    if not llm_base_url:
        missing.append("LLM_BASE_URL")
    if not llm_model:
        missing.append("LLM_MODEL")
    if not tavily_api_key:
        missing.append("TAVILY_API_KEY")

    if missing:
        raise ValueError(f"Missing required ENV variables: {', '.join(missing)}")

    try:
        llm_max_output_tokens = int(llm_max_output_tokens_raw)
    except ValueError as e:
        raise ValueError("LLM_MAX_OUTPUT_TOKENS must be an integer") from e

    if llm_max_output_tokens < 500:
        raise ValueError("LLM_MAX_OUTPUT_TOKENS must be >= 500")

    config = AppConfig(
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        llm_model=llm_model,
        tavily_api_key=tavily_api_key,
        llm_max_output_tokens=llm_max_output_tokens
    )

    logger.debug("[Config][load_env_config] Belief: ENV-конфигурация загружена успешно | Input: None | Expected: Валидный AppConfig")
    return config


def load_ui_settings(config_path: str = "config.json") -> UiSettings:
    """
    Загружает настройки UI из файла или возвращает значения по умолчанию.

    # START_CONTRACT_load_ui_settings
    # Input: config_path (str) - путь к файлу настроек
    # Russian Intent: Загрузить настройки UI из файла или использовать дефолты
    # Output: Валидный UiSettings
    # END_CONTRACT_load_ui_settings
    """
    logger.debug("[Config][load_ui_settings] Belief: Загрузка UI-настроек | Input: config_path | Expected: Валидный UiSettings")

    path = Path(config_path)
    if not path.exists():
        logger.debug("[Config][load_ui_settings] Belief: Файл настроек не найден, используем дефолты | Input: config_path | Expected: Валидный UiSettings")
        return UiSettings()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        settings = UiSettings(**data)
        logger.debug("[Config][load_ui_settings] Belief: UI-настройки загружены из файла | Input: config_path | Expected: Валидный UiSettings")
        return settings
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"[Config][load_ui_settings] Failed to load settings: {e}, using defaults")
        return UiSettings()


def save_ui_settings(settings: UiSettings, config_path: str = "config.json") -> None:
    """
    Сохраняет настройки UI в файл.

    # START_CONTRACT_save_ui_settings
    # Input: settings (UiSettings), config_path (str)
    # Russian Intent: Сохранить настройки UI в файл JSON
    # Output: None
    # END_CONTRACT_save_ui_settings
    """
    logger.debug("[Config][save_ui_settings] Belief: Сохранение UI-настроек | Input: settings, config_path | Expected: Файл сохранен")

    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, indent=2, ensure_ascii=False)

    logger.debug("[Config][save_ui_settings] Belief: UI-настройки сохранены успешно | Input: settings, config_path | Expected: Файл сохранен")


def validate_ui_settings(settings: UiSettings) -> bool:
    """
    Валидирует настройки UI.

    # START_CONTRACT_validate_ui_settings
    # Input: settings (UiSettings)
    # Russian Intent: Проверить что настройки UI в допустимых диапазонах
    # Output: bool - True если валидно
    # END_CONTRACT_validate_ui_settings
    """
    logger.debug("[Config][validate_ui_settings] Belief: Валидация UI-настроек | Input: settings | Expected: bool")

    is_valid = (
        100 <= settings.words_per_chapter <= 1000 and
        1 <= settings.chapter_count <= 10 and
        0.0 <= settings.temperature <= 1.0
    )

    logger.debug(f"[Config][validate_ui_settings] Belief: Валидация завершена | Input: settings | Expected: bool, Result: {is_valid}")
    return is_valid
