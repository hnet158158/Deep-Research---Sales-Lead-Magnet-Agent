"""
Research Aggregator Module
Последовательно выполняет поиск по списку query и агрегирует контекст.
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field

from src.clients import TavilyClientWrapper

logger = logging.getLogger(__name__)


@dataclass
class ResearchItem:
    """Один элемент исследования."""
    query: str
    success: bool
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""


@dataclass
class ResearchAggregate:
    """Агрегированные результаты исследования."""
    items: List[ResearchItem] = field(default_factory=list)
    success_count: int = 0
    fail_count: int = 0


def run_sequential_search(
    queries: List[str],
    tavily_client: TavilyClientWrapper,
    max_results: int = 5
) -> ResearchAggregate:
    """
    Последовательно выполняет поиск по списку query.

    # START_CONTRACT_run_sequential_search
    # Input: queries (List[str]), tavily_client (TavilyClientWrapper), max_results (int)
    # Russian Intent: Выполнить последовательный поиск по всем запросам с политикой деградации
    # Output: ResearchAggregate - агрегированные результаты
    # END_CONTRACT_run_sequential_search
    """
    logger.debug("[Research][run_sequential_search] Belief: Начало последовательного поиска | Input: queries, max_results | Expected: ResearchAggregate")

    aggregate = ResearchAggregate()

    for i, query in enumerate(queries, 1):
        logger.info(f"[Research] Searching query {i}/{len(queries)}: {query}")

        response = tavily_client.search_once(query, max_results)

        if response and "results" in response:
            item = ResearchItem(
                query=query,
                success=True,
                results=response["results"]
            )
            aggregate.success_count += 1
            logger.info(f"[Research] Query {i} succeeded: {len(response['results'])} results")
        else:
            item = ResearchItem(
                query=query,
                success=False,
                error="Search failed or returned no results"
            )
            aggregate.fail_count += 1
            logger.warning(f"[Research] Query {i} failed")

        aggregate.items.append(item)

    logger.debug(f"[Research][run_sequential_search] Belief: Поиск завершен | Input: queries, max_results | Expected: ResearchAggregate, Success: {aggregate.success_count}, Failed: {aggregate.fail_count}")
    return aggregate


def merge_research_items(aggregate: ResearchAggregate) -> List[Dict[str, Any]]:
    """
    Объединяет все успешные результаты исследования.

    # START_CONTRACT_merge_research_items
    # Input: aggregate (ResearchAggregate)
    # Russian Intent: Объединить все успешные результаты в один список
    # Output: List[Dict[str, Any]] - объединенные результаты
    # END_CONTRACT_merge_research_items
    """
    logger.debug("[Research][merge_research_items] Belief: Объединение результатов | Input: aggregate | Expected: List[Dict]")

    merged = []
    for item in aggregate.items:
        if item.success:
            merged.extend(item.results)

    logger.debug(f"[Research][merge_research_items] Belief: Результаты объединены | Input: aggregate | Expected: List[Dict], Count: {len(merged)}")
    return merged


def format_research_context(results: List[Dict[str, Any]]) -> str:
    """
    Форматирует результаты исследования в контекст для LLM.

    # START_CONTRACT_format_research_context
    # Input: results (List[Dict[str, Any]])
    # Russian Intent: Отформатировать результаты поиска в текстовый контекст
    # Output: str - форматированный контекст
    # END_CONTRACT_format_research_context
    """
    logger.debug("[Research][format_research_context] Belief: Форматирование контекста | Input: results | Expected: str")

    if not results:
        return "No research data available."

    context_parts = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        content = result.get("content", "")
        raw_content = result.get("raw_content", "")

        part = f"Source {i}:\n"
        part += f"Title: {title}\n"
        part += f"URL: {url}\n"
        part += f"Content: {content}\n"
        if raw_content:
            part += f"Full Content: {raw_content[:500]}...\n"
        part += "\n"

        context_parts.append(part)

    context = "\n".join(context_parts)
    logger.debug(f"[Research][format_research_context] Belief: Контекст отформатирован | Input: results | Expected: str, Length: {len(context)}")
    return context


def check_search_failure(aggregate: ResearchAggregate) -> bool:
    """
    Проверяет, полностью ли провалился поиск.

    # START_CONTRACT_check_search_failure
    # Input: aggregate (ResearchAggregate)
    # Russian Intent: Проверить что все поисковые запросы провалились
    # Output: bool - True если все провалились
    # END_CONTRACT_check_search_failure
    """
    logger.debug("[Research][check_search_failure] Belief: Проверка полного провала поиска | Input: aggregate | Expected: bool")

    is_full_failure = aggregate.success_count == 0

    logger.debug(f"[Research][check_search_failure] Belief: Проверка завершена | Input: aggregate | Expected: bool, Result: {is_full_failure}")
    return is_full_failure
