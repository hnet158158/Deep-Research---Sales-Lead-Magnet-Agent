"""
Prompt & Structured Schema Layer
Инкапсулирует системные промпты и JSON-схемы для LLM.
"""

import json
import logging
import re
from typing import List
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class QueryListModel(BaseModel):
    """Модель для списка поисковых запросов."""
    queries: List[str] = Field(..., min_length=1)

    # START_CONTRACT_QueryListModel
    # Input: queries (List[str])
    # Russian Intent: Валидировать список поисковых запросов от LLM
    # Output: Валидный QueryListModel
    # END_CONTRACT_QueryListModel

    @field_validator("queries")
    @classmethod
    def validate_queries(cls, v: List[str]) -> List[str]:
        """Проверяет что список не пустой и все строки непустые."""
        if not v:
            raise ValueError("Queries list cannot be empty")
        if any(not q.strip() for q in v):
            raise ValueError("All queries must be non-empty strings")
        return v


class ChapterPlanModel(BaseModel):
    """Модель для плана главы."""
    title: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)


class LeadMagnetStructureModel(BaseModel):
    """Модель для структуры лид-магнита."""
    title: str = Field(..., min_length=1)
    subtitle: str = Field(..., min_length=1)
    introduction: str = Field(..., min_length=1)
    conclusions: str = Field(..., min_length=1)
    chapters: List[ChapterPlanModel] = Field(..., min_length=1)

    # START_CONTRACT_LeadMagnetStructureModel
    # Input: title, subtitle, introduction, conclusions, chapters
    # Russian Intent: Валидировать структуру лид-магнита от LLM
    # Output: Валидный LeadMagnetStructureModel
    # END_CONTRACT_LeadMagnetStructureModel

    @field_validator("chapters")
    @classmethod
    def validate_chapters(cls, v: List[ChapterPlanModel]) -> List[ChapterPlanModel]:
        """Проверяет что список глав не пустой."""
        if not v:
            raise ValueError("Chapters list cannot be empty")
        return v


def build_query_prompt(topic: str, query_count: int) -> str:
    """
    Формирует системный промпт для Query Builder.

    # START_CONTRACT_build_query_prompt
    # Input: topic (str), query_count (int)
    # Russian Intent: Сформировать промпт для генерации поисковых запросов
    # Output: str - системный промпт
    # END_CONTRACT_build_query_prompt
    """
    logger.debug("[Schemas][build_query_prompt] Belief: Формирование промпта Query Builder | Input: topic, query_count | Expected: str")

    prompt = f"""Role: Search Query Refiner Agent
You refine a user's topic into highly targeted search queries for deep research.

Goal: Provide {query_count} well-crafted, distinct search queries based on the user's stated topic. These queries must be geared towards doing deep research on the subject.

Instructions:
1. Analyze User Input: Identify the exact concepts or keywords in the user's topic. Do NOT introduce tangential themes.
2. Generate Queries: Create exactly {query_count} unique search queries. Each query should include the main keywords and minor variations to preserve a narrow focus.
3. Output Format: Return a strict JSON array of strings containing the queries.

User Topic: "{topic}"
"""
    return prompt


def build_structure_prompt(research_context: str, chapter_count: int) -> str:
    """
    Формирует системный промпт для Structure Planner.

    # START_CONTRACT_build_structure_prompt
    # Input: research_context (str), chapter_count (int)
    # Russian Intent: Сформировать промпт для планирования структуры лид-магнита
    # Output: str - системный промпт
    # END_CONTRACT_build_structure_prompt
    """
    logger.debug("[Schemas][build_structure_prompt] Belief: Формирование промпта Structure Planner | Input: research_context, chapter_count | Expected: str")

    prompt = f"""Role: Research Leader and Project Planner
Your task is to create a comprehensive, research-backed table of contents for a Lead Magnet based on the provided research context.

Instructions:
1. Read the research context carefully.
2. Create a logical structure consisting of exactly {chapter_count} chapters.
3. Generate a JSON object with the following schema:
   - "title": Title of the Lead Magnet
   - "subtitle": Subtitle
   - "introduction": A short introduction (approx 100 words)
   - "conclusions": A short conclusion (approx 100 words)
   - "chapters": An array of objects, where each object has:
     - "title": Chapter title
     - "prompt": Exhaustive, step-by-step instructions for the writer on what to cover in this chapter based on the research. Include data points to mention.

Research Context:
{research_context}
"""
    return prompt


def build_chapter_writer_prompt(
    main_title: str,
    chapter_title: str,
    chapter_prompt: str,
    research_context: str,
    word_limit: int
) -> str:
    """
    Формирует промпт для написания главы.

    # START_CONTRACT_build_chapter_writer_prompt
    # Input: main_title, chapter_title, chapter_prompt, research_context, word_limit
    # Russian Intent: Сформировать промпт для написания отдельной главы
    # Output: str - промпт для LLM
    # END_CONTRACT_build_chapter_writer_prompt
    """
    logger.debug("[Schemas][build_chapter_writer_prompt] Belief: Формирование промпта Chapter Writer | Input: main_title, chapter_title, chapter_prompt, research_context, word_limit | Expected: str")

    prompt = f"""Role: Research Assistant Writer
Your task is to write a single chapter for a Lead Magnet.

Guidelines:
- Write strictly in Markdown format.
- Length: Approximately {word_limit} words.
- Tone: Educational, informative, and actionable. Provide step-by-step guidance where applicable.
- Do NOT include the main article introduction or conclusion. Just write the chapter content.
- Use the provided research context to back up your claims. Include inline citations in Markdown format like [Source Name](URL) when referencing facts from the research.

Lead Magnet Title: "{main_title}"
Current Chapter Title: "{chapter_title}"
Chapter Instructions: "{chapter_prompt}"

Research Context available to you:
{research_context}
"""
    return prompt


def build_final_editor_prompt(assembled_draft: str) -> str:
    """
    Формирует промпт для финального редактирования.

    # START_CONTRACT_build_final_editor_prompt
    # Input: assembled_draft (str)
    # Russian Intent: Сформировать промпт для финальной полировки текста
    # Output: str - промпт для LLM
    # END_CONTRACT_build_final_editor_prompt
    """
    logger.debug("[Schemas][build_final_editor_prompt] Belief: Формирование промпта Final Editor | Input: assembled_draft | Expected: str")

    prompt = f"""Role: Expert Editor
You are refining and polishing content to ensure it meets the highest quality standards.

Instructions:
- Carefully read the entire assembled Lead Magnet.
- Check for grammar, spelling, and punctuation.
- Ensure consistency in tone, style, and voice throughout the piece. Make it sound authentic, formal but casual (avoid robotic or "cringe" AI phrasing).
- Improve sentence structure and flow.
- Ensure proper Markdown formatting (Headers, Lists, Bold text).
- Add placeholders like [Add image here of X] where visual context would be helpful.
- Return the final polished text in pure Markdown.

Draft Content:
{assembled_draft}
"""
    return prompt


def normalize_raw_json(raw: str) -> str:
    """
    Нормализует raw JSON строку (удаляет markdown fences, trim пробелы).

    # START_CONTRACT_normalize_raw_json
    # Input: raw (str) - сырой JSON от LLM
    # Russian Intent: Очистить JSON от markdown fences и лишних пробелов
    # Output: str - нормализованная JSON строка
    # END_CONTRACT_normalize_raw_json
    """
    logger.debug("[Schemas][normalize_raw_json] Belief: Нормализация JSON | Input: raw | Expected: str")

    # Trim пробелов
    normalized = raw.strip()

    # Удаляем markdown fences: ```json ... ``` и ``` ... ```
    patterns = [
        r'```json\s*',  # Начало ```json
        r'```\s*',      # Конец ```
        r'^\s*```',     # Начало ``` в начале
        r'```\s*$',     # Конец ``` в конце
    ]

    for pattern in patterns:
        normalized = re.sub(pattern, '', normalized, flags=re.MULTILINE)

    # Trim снова после удаления fences
    normalized = normalized.strip()

    logger.debug("[Schemas][normalize_raw_json] Belief: JSON нормализован | Input: raw | Expected: str")
    return normalized


def extract_first_json_block(raw: str) -> str:
    """
    Извлекает первый валидный JSON блок ({...} или [...]) из строки.

    # START_CONTRACT_extract_first_json_block
    # Input: raw (str) - строка с потенциально несколькими JSON блоками
    # Russian Intent: Извлечь первый валидный JSON блок из строки
    # Output: str - первый JSON блок
    # END_CONTRACT_extract_first_json_block
    """
    logger.debug("[Schemas][extract_first_json_block] Belief: Извлечение первого JSON блока | Input: raw | Expected: str")

    # Ищем первый {...} блок
    obj_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
    if obj_match:
        logger.debug("[Schemas][extract_first_json_block] Belief: Найден объектный JSON блок | Input: raw | Expected: str")
        return obj_match.group(0)

    # Ищем первый [...] блок
    arr_match = re.search(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', raw, re.DOTALL)
    if arr_match:
        logger.debug("[Schemas][extract_first_json_block] Belief: Найден массивный JSON блок | Input: raw | Expected: str")
        return arr_match.group(0)

    logger.debug("[Schemas][extract_first_json_block] Belief: JSON блок не найден | Input: raw | Expected: str")
    return raw


def coerce_query_shape(data: dict) -> dict:
    """
    Приводит различные форматы к каноническому {"queries": [...]}.

    # START_CONTRACT_coerce_query_shape
    # Input: data (dict) - распарсенные данные
    # Russian Intent: Привести данные к каноническому формату {"queries": [...]}
    # Output: dict - канонический формат
    # END_CONTRACT_coerce_query_shape
    """
    logger.debug("[Schemas][coerce_query_shape] Belief: Коэрсия формата запросов | Input: data | Expected: dict")

    # Если уже в каноническом формате
    if "queries" in data and isinstance(data["queries"], list):
        logger.debug("[Schemas][coerce_query_shape] Belief: Уже в каноническом формате | Input: data | Expected: dict")
        return {"queries": data["queries"]}

    # Проверяем похожие ключи
    possible_keys = ["query", "search_queries", "items", "results"]
    for key in possible_keys:
        if key in data and isinstance(data[key], list):
            logger.debug(f"[Schemas][coerce_query_shape] Belief: Найден ключ {key}, маппинг в queries | Input: data | Expected: dict")
            return {"queries": data[key]}

    # Если это просто список значений без ключа
    values = [v for v in data.values() if isinstance(v, list)]
    if values:
        logger.debug("[Schemas][coerce_query_shape] Belief: Использован первый список значений | Input: data | Expected: dict")
        return {"queries": values[0]}

    logger.debug("[Schemas][coerce_query_shape] Belief: Не удалось коэрсировать формат | Input: data | Expected: dict")
    return data


def validate_query_count(model: QueryListModel, expected_count: int) -> None:
    """
    Валидирует количество запросов.

    # START_CONTRACT_validate_query_count
    # Input: model (QueryListModel), expected_count (int)
    # Russian Intent: Проверить что количество запросов соответствует ожидаемому
    # Output: None или исключение ValueError
    # END_CONTRACT_validate_query_count
    """
    logger.debug("[Schemas][validate_query_count] Belief: Валидация количества запросов | Input: model, expected_count | Expected: None")

    if len(model.queries) != expected_count:
        error = f"Expected {expected_count} queries, got {len(model.queries)}"
        logger.debug(f"[Schemas][validate_query_count] Belief: Валидация не пройдена | Input: model, expected_count | Expected: None, Error: {error}")
        raise ValueError(error)

    logger.debug("[Schemas][validate_query_count] Belief: Валидация пройдена | Input: model, expected_count | Expected: None")


def parse_query_output(raw_output: str, expected_count: int, llm_client=None) -> QueryListModel:
    """
    Парсит и валидирует вывод Query Builder с tolerant parsing-layer.

    # START_CONTRACT_parse_query_output
    # Input: raw_output (str), expected_count (int), llm_client (optional)
    # Russian Intent: Распарсить JSON вывод LLM с tolerant parsing и валидировать количество запросов
    # Output: QueryListModel или исключение
    # END_CONTRACT_parse_query_output
    """
    logger.debug("[Schemas][parse_query_output] Belief: Парсинг вывода Query Builder | Input: raw_output, expected_count | Expected: QueryListModel")

    # STEP 3: Strict parse
    try:
        data = json.loads(raw_output)
        logger.debug("[Schemas][parse_query_output] Belief: Strict parse успешен | Input: raw_output | Expected: dict")
    except json.JSONDecodeError:
        # STEP 4: Normalize
        normalized = normalize_raw_json(raw_output)
        logger.debug("[Schemas][parse_query_output] Belief: JSON нормализован | Input: raw_output | Expected: str")

        # STEP 5: Retry strict parse
        try:
            data = json.loads(normalized)
            logger.debug("[Schemas][parse_query_output] Belief: Parse после нормализации успешен | Input: normalized | Expected: dict")
        except json.JSONDecodeError:
            # STEP 6: Extract first JSON block
            extracted = extract_first_json_block(normalized)
            logger.debug("[Schemas][parse_query_output] Belief: Извлечен первый JSON блок | Input: normalized | Expected: str")

            try:
                data = json.loads(extracted)
                logger.debug("[Schemas][parse_query_output] Belief: Parse после извлечения успешен | Input: extracted | Expected: dict")
            except json.JSONDecodeError:
                # STEP 7: Repair-pass через LLM (если доступен)
                if llm_client:
                    logger.debug("[Schemas][parse_query_output] Belief: Попытка repair-pass через LLM | Input: extracted | Expected: str")
                    try:
                        repaired = llm_client.repair_json_once(extracted)
                        data = json.loads(repaired)
                        logger.debug("[Schemas][parse_query_output] Belief: Repair-pass успешен | Input: extracted | Expected: dict")
                    except Exception as e:
                        # STEP 8: Fail with detailed error
                        error_msg = f"Failed to parse JSON after normalization, extraction and repair: {e}"
                        logger.error(f"[Schemas][parse_query_output] {error_msg}")
                        raise ValueError(error_msg)
                else:
                    # STEP 8: Fail with detailed error (без repair-pass)
                    error_msg = "Failed to parse JSON after normalization and extraction (no llm_client for repair)"
                    logger.error(f"[Schemas][parse_query_output] {error_msg}")
                    raise ValueError(error_msg)

    # STEP 9: Coerce query shape
    if isinstance(data, list):
        data = {"queries": data}
    elif isinstance(data, dict):
        data = coerce_query_shape(data)

    # STEP 11: Pydantic validation
    model = QueryListModel(**data)

    # STEP 12: Validate count
    validate_query_count(model, expected_count)

    logger.debug("[Schemas][parse_query_output] Belief: Парсинг успешен | Input: raw_output, expected_count | Expected: QueryListModel")
    return model


def parse_structure_output(raw_output: str, expected_chapters: int, llm_client=None) -> LeadMagnetStructureModel:
    """
    Парсит и валидирует вывод Structure Planner с tolerant parsing-layer.

    # START_CONTRACT_parse_structure_output
    # Input: raw_output (str), expected_chapters (int), llm_client (optional)
    # Russian Intent: Распарсить JSON вывод LLM с tolerant parsing и валидировать количество глав
    # Output: LeadMagnetStructureModel или исключение
    # END_CONTRACT_parse_structure_output
    """
    logger.debug("[Schemas][parse_structure_output] Belief: Парсинг вывода Structure Planner | Input: raw_output, expected_chapters | Expected: LeadMagnetStructureModel")

    # STEP 3: Strict parse
    try:
        data = json.loads(raw_output)
        logger.debug("[Schemas][parse_structure_output] Belief: Strict parse успешен | Input: raw_output | Expected: dict")
    except json.JSONDecodeError:
        # STEP 4: Normalize
        normalized = normalize_raw_json(raw_output)
        logger.debug("[Schemas][parse_structure_output] Belief: JSON нормализован | Input: raw_output | Expected: str")

        # STEP 5: Retry strict parse
        try:
            data = json.loads(normalized)
            logger.debug("[Schemas][parse_structure_output] Belief: Parse после нормализации успешен | Input: normalized | Expected: dict")
        except json.JSONDecodeError:
            # STEP 6: Extract first JSON block
            extracted = extract_first_json_block(normalized)
            logger.debug("[Schemas][parse_structure_output] Belief: Извлечен первый JSON блок | Input: normalized | Expected: str")

            try:
                data = json.loads(extracted)
                logger.debug("[Schemas][parse_structure_output] Belief: Parse после извлечения успешен | Input: extracted | Expected: dict")
            except json.JSONDecodeError:
                # STEP 7: Repair-pass через LLM (если доступен)
                if llm_client:
                    logger.debug("[Schemas][parse_structure_output] Belief: Попытка repair-pass через LLM | Input: extracted | Expected: str")
                    try:
                        repaired = llm_client.repair_json_once(extracted)
                        data = json.loads(repaired)
                        logger.debug("[Schemas][parse_structure_output] Belief: Repair-pass успешен | Input: extracted | Expected: dict")
                    except Exception as e:
                        # STEP 8: Fail with detailed error
                        error_msg = f"Failed to parse JSON after normalization, extraction and repair: {e}"
                        logger.error(f"[Schemas][parse_structure_output] {error_msg}")
                        raise ValueError(error_msg)
                else:
                    # STEP 8: Fail with detailed error (без repair-pass)
                    error_msg = "Failed to parse JSON after normalization and extraction (no llm_client for repair)"
                    logger.error(f"[Schemas][parse_structure_output] {error_msg}")
                    raise ValueError(error_msg)

    # STEP 11: Pydantic validation
    model = LeadMagnetStructureModel(**data)

    # STEP 12: Validate chapters count
    if len(model.chapters) != expected_chapters:
        error = f"Expected {expected_chapters} chapters, got {len(model.chapters)}"
        logger.debug(f"[Schemas][parse_structure_output] Belief: Валидация не пройдена | Input: model, expected_chapters | Expected: None, Error: {error}")
        raise ValueError(error)

    logger.debug("[Schemas][parse_structure_output] Belief: Парсинг успешен | Input: raw_output, expected_chapters | Expected: LeadMagnetStructureModel")
    return model
