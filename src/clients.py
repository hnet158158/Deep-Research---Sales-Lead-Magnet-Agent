"""
Provider Clients Module
Единый интерфейс к OpenAI-compatible LLM и Tavily Search.
"""

import logging
from typing import Optional
from openai import OpenAI
from tavily import TavilyClient

from src.config import AppConfig

logger = logging.getLogger(__name__)


class LlmClient:
    """Клиент для OpenAI-compatible LLM."""

    def __init__(self, config: AppConfig):
        """
        Инициализация LLM клиента.

        # START_CONTRACT_LlmClient_init
        # Input: config (AppConfig)
        # Russian Intent: Инициализировать клиент LLM с настройками из конфигурации
        # Output: None
        # END_CONTRACT_LlmClient_init
        """
        logger.debug("[Clients][LlmClient_init] Belief: Инициализация LLM клиента | Input: config | Expected: Клиент готов")

        self.client = OpenAI(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url
        )
        self.model = config.llm_model
        self.reasoning_budget = config.llm_reasoning_budget

        logger.debug("[Clients][LlmClient_init] Belief: LLM клиент инициализирован | Input: config | Expected: Клиент готов")

    def _build_reasoning_kwargs(self) -> dict:
        """
        Возвращает provider-specific аргументы для контроля бюджета размышлений.

        # START_CONTRACT__build_reasoning_kwargs
        # Input: None
        # Russian Intent: Сформировать kwargs для моделей, поддерживающих бюджет размышлений
        # Output: dict
        # END_CONTRACT__build_reasoning_kwargs
        """
        logger.debug("[Clients][_build_reasoning_kwargs] Belief: Формирование reasoning kwargs | Input: model, reasoning_budget | Expected: dict")

        if self.reasoning_budget <= 0:
            return {}

        is_gemini_model = "gemini" in self.model.lower()
        if not is_gemini_model:
            return {}

        kwargs = {"extra_body": {"thinking_budget": self.reasoning_budget}}
        logger.debug("[Clients][_build_reasoning_kwargs] Belief: Thinking budget передан через extra_body только для Gemini | Input: model, reasoning_budget | Expected: dict")
        return kwargs

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Генерирует JSON ответ от LLM.

        # START_CONTRACT_generate_json
        # Input: system_prompt (str), user_prompt (str), temperature (float)
        # Russian Intent: Получить JSON ответ от LLM для структурированных данных
        # Output: str - raw JSON строка
        # END_CONTRACT_generate_json
        """
        logger.debug("[Clients][generate_json] Belief: Генерация JSON от LLM | Input: system_prompt, user_prompt, temperature | Expected: str")

        try:
            reasoning_kwargs = self._build_reasoning_kwargs()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
                **reasoning_kwargs
            )
            result = response.choices[0].message.content
            logger.debug("[Clients][generate_json] Belief: JSON получен успешно | Input: system_prompt, user_prompt, temperature | Expected: str")
            return result
        except Exception as e:
            logger.error(f"[Clients][generate_json] LLM error: {e}")
            raise

    def generate_markdown(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Генерирует Markdown текст от LLM.

        # START_CONTRACT_generate_markdown
        # Input: system_prompt (str), user_prompt (str), temperature (float)
        # Russian Intent: Получить Markdown текст от LLM
        # Output: str - Markdown текст
        # END_CONTRACT_generate_markdown
        """
        logger.debug("[Clients][generate_markdown] Belief: Генерация Markdown от LLM | Input: system_prompt, user_prompt, temperature | Expected: str")

        try:
            reasoning_kwargs = self._build_reasoning_kwargs()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                **reasoning_kwargs
            )
            result = response.choices[0].message.content
            logger.debug("[Clients][generate_markdown] Belief: Markdown получен успешно | Input: system_prompt, user_prompt, temperature | Expected: str")
            return result
        except Exception as e:
            logger.error(f"[Clients][generate_markdown] LLM error: {e}")
            raise

    def repair_json_once(self, broken_json: str) -> str:
        """
        Выполняет один repair-pass через LLM для исправления сломанного JSON.

        # START_CONTRACT_repair_json_once
        # Input: broken_json (str) - сломанный JSON
        # Russian Intent: Исправить сломанный JSON через LLM в JSON-only режиме
        # Output: str - исправленный JSON
        # END_CONTRACT_repair_json_once
        """
        logger.debug("[Clients][repair_json_once] Belief: Repair-pass для JSON | Input: broken_json | Expected: str")

        repair_system_prompt = """Роль: Специалист по ремонту JSON
Ваша задача - исправить следующий сломанный JSON и вернуть ТОЛЬКО валидный JSON.

Инструкции:
1. Проанализируйте структуру сломанного JSON.
2. Исправьте синтаксические ошибки (отсутствующие кавычки, висящие запятые и т.д.).
3. Верните ТОЛЬКО исправленный JSON, без объяснений или markdown-ограничителей.
4. НЕ изменяйте данные, только исправляйте синтаксис.

"""

        repair_user_prompt = f"""Сломанный JSON:
{broken_json}

Верните исправленный JSON сейчас."""

        try:
            reasoning_kwargs = self._build_reasoning_kwargs()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": repair_system_prompt},
                    {"role": "user", "content": repair_user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                **reasoning_kwargs
            )
            result = response.choices[0].message.content
            logger.debug("[Clients][repair_json_once] Belief: JSON отремонтирован | Input: broken_json | Expected: str")
            return result
        except Exception as e:
            logger.error(f"[Clients][repair_json_once] Repair failed: {e}")
            raise


class TavilyClientWrapper:
    """Обертка для Tavily Search."""

    def __init__(self, api_key: str):
        """
        Инициализация Tavily клиента.

        # START_CONTRACT_TavilyClientWrapper_init
        # Input: api_key (str)
        # Russian Intent: Инициализировать клиент Tavily Search
        # Output: None
        # END_CONTRACT_TavilyClientWrapper_init
        """
        logger.debug("[Clients][TavilyClientWrapper_init] Belief: Инициализация Tavily клиента | Input: api_key | Expected: Клиент готов")

        self.client = TavilyClient(api_key=api_key)

        logger.debug("[Clients][TavilyClientWrapper_init] Belief: Tavily клиент инициализирован | Input: api_key | Expected: Клиент готов")

    def search_once(self, query: str, max_results: int = 5) -> Optional[dict]:
        """
        Выполняет один поисковый запрос.

        # START_CONTRACT_search_once
        # Input: query (str), max_results (int)
        # Russian Intent: Выполнить поиск по запросу через Tavily
        # Output: dict - результаты поиска или None при ошибке
        # END_CONTRACT_search_once
        """
        logger.debug(f"[Clients][search_once] Belief: Поиск по запросу | Input: query={query}, max_results | Expected: dict")

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_raw_content=True
            )
            logger.debug(f"[Clients][search_once] Belief: Поиск успешен | Input: query={query}, max_results | Expected: dict")
            return response
        except Exception as e:
            logger.error(f"[Clients][search_once] Search failed for query '{query}': {e}")
            return None


def safe_log_error(error: Exception, context: str) -> str:
    """
    Безопасно логирует ошибку без утечки секретов.

    # START_CONTRACT_safe_log_error
    # Input: error (Exception), context (str)
    # Russian Intent: Логировать ошибку без раскрытия чувствительных данных
    # Output: str - безопасное сообщение об ошибке
    # END_CONTRACT_safe_log_error
    """
    logger.debug("[Clients][safe_log_error] Belief: Безопасное логирование ошибки | Input: error, context | Expected: str")

    error_type = type(error).__name__
    error_msg = str(error)

    # Удаляем потенциальные секреты из сообщения
    safe_msg = error_msg
    for keyword in ["api_key", "token", "password", "secret"]:
        if keyword in safe_msg.lower():
            safe_msg = safe_msg[:safe_msg.lower().find(keyword)] + "[REDACTED]"

    result = f"{context}: {error_type} - {safe_msg}"
    logger.warning(f"[Clients][safe_log_error] {result}")
    return result
