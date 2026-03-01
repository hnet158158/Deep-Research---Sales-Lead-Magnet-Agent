"""
Lead Magnet Orchestrator Module
Управляет полным конвейером генерации (FIFO Pipeline).
"""

import logging
from typing import Generator, Tuple, Optional

from src.config import AppConfig, UiSettings
from src.clients import LlmClient, TavilyClientWrapper
from src.schemas import (
    build_query_prompt,
    parse_query_output,
    build_structure_prompt,
    parse_structure_output,
    build_chapter_writer_prompt,
    build_final_editor_prompt,
    build_section_editor_prompt
)
from src.research import (
    run_sequential_search,
    merge_research_items,
    format_research_context,
    check_search_failure
)
from src.export import export_lead_magnet
from src.errors import (
    emit_log,
    handle_stage_failure,
    PipelineStage,
    StageError
)

logger = logging.getLogger(__name__)


class GenerationOrchestrator:
    """Оркестратор генерации лид-магнита."""

    def __init__(
        self,
        app_config: AppConfig,
        ui_settings: UiSettings,
        llm_client: LlmClient,
        tavily_client: TavilyClientWrapper
    ):
        """
        Инициализация оркестратора.

        # START_CONTRACT_GenerationOrchestrator_init
        # Input: app_config, ui_settings, llm_client, tavily_client
        # Russian Intent: Инициализировать оркестратор с клиентами и настройками
        # Output: None
        # END_CONTRACT_GenerationOrchestrator_init
        """
        logger.debug("[Orchestrator][init] Belief: Инициализация оркестратора | Input: app_config, ui_settings | Expected: Оркестратор готов")

        self.app_config = app_config
        self.ui_settings = ui_settings
        self.llm_client = llm_client
        self.tavily_client = tavily_client

        logger.debug("[Orchestrator][init] Belief: Оркестратор инициализирован | Input: app_config, ui_settings | Expected: Оркестратор готов")

    def run_pipeline(self, topic: str) -> Generator[Tuple[str, Optional[str], Optional[str]], None, None]:
        """
        Запускает полный pipeline генерации.

        # START_CONTRACT_run_pipeline
        # Input: topic (str)
        # Russian Intent: Запустить полный pipeline генерации лид-магнита
        # Output: Generator - стрим логов, markdown, filepath
        # END_CONTRACT_run_pipeline
        """
        logger.debug(f"[Orchestrator][run_pipeline] Belief: Запуск pipeline | Input: topic={topic} | Expected: Generator")

        try:
            # Stage 1: Query Builder
            yield from self._run_query_builder(topic)

            # Stage 2: Search
            research_context = yield from self._run_search()

            # Stage 3: Structure Planner
            structure = yield from self._run_structure_planner(research_context)

            # Stage 4: Chapter Writer
            chapters = yield from self._run_chapter_writer(structure, research_context)

            # Stage 5: Assembly + Final Editor
            yield from self._run_assembly_and_editor(structure, chapters)

            logger.debug("[Orchestrator][run_pipeline] Belief: Pipeline завершен успешно | Input: topic | Expected: Generator")

        except StageError as e:
            logger.error(f"[Orchestrator][run_pipeline] Stage error: {e}")
            raise
        except Exception as e:
            logger.error(f"[Orchestrator][run_pipeline] Unexpected error: {e}")
            raise handle_stage_failure("Pipeline", e, recoverable=False)

    def _count_words(self, text: str) -> int:
        """
        Возвращает количество слов в тексте.

        # START_CONTRACT__count_words
        # Input: text (str)
        # Russian Intent: Подсчитать слова для контроля длины секции
        # Output: int
        # END_CONTRACT__count_words
        """
        logger.debug("[Orchestrator][_count_words] Belief: Подсчет слов | Input: text | Expected: int")
        words = [token for token in text.replace("\n", " ").split(" ") if token.strip()]
        return len(words)

    def _build_word_range(self, source_text: str, tolerance: float = 0.15) -> Tuple[int, int]:
        """
        Строит допустимый диапазон длины для секции.

        # START_CONTRACT__build_word_range
        # Input: source_text (str), tolerance (float)
        # Russian Intent: Вычислить нижнюю и верхнюю границы длины секции
        # Output: Tuple[int, int]
        # END_CONTRACT__build_word_range
        """
        logger.debug("[Orchestrator][_build_word_range] Belief: Расчет диапазона длины | Input: source_text, tolerance | Expected: Tuple[int, int]")
        base_count = max(1, self._count_words(source_text))
        min_words = max(1, int(base_count * (1 - tolerance)))
        max_words = max(min_words, int(base_count * (1 + tolerance)))
        return min_words, max_words

    def _edit_section_with_length_guard(self, section_name: str, section_markdown: str) -> str:
        """
        Редактирует одну секцию с проверкой диапазона длины.

        # START_CONTRACT__edit_section_with_length_guard
        # Input: section_name (str), section_markdown (str)
        # Russian Intent: Отредактировать секцию, сохранив близкий объем текста
        # Output: str
        # END_CONTRACT__edit_section_with_length_guard
        """
        logger.debug("[Orchestrator][_edit_section_with_length_guard] Belief: Секционное редактирование | Input: section_name, section_markdown | Expected: str")
        min_words, max_words = self._build_word_range(section_markdown)
        prompt = build_section_editor_prompt(
            section_name,
            section_markdown,
            min_words,
            max_words,
            keep_links=self.ui_settings.keep_links
        )
        edited = self.llm_client.generate_markdown(
            prompt,
            temperature=self.ui_settings.editor_temperature
        )
        edited_count = self._count_words(edited)
        if min_words <= edited_count <= max_words:
            logger.debug("[Orchestrator][_edit_section_with_length_guard] Belief: Секция прошла контроль длины | Input: section_name, min_words, max_words | Expected: str")
            return edited

        logger.debug("[Orchestrator][_edit_section_with_length_guard] Belief: Повторная попытка редактирования секции | Input: section_name, min_words, max_words | Expected: str")
        retry_prompt = build_section_editor_prompt(
            section_name,
            section_markdown,
            min_words,
            max_words,
            keep_links=self.ui_settings.keep_links
        )
        retried = self.llm_client.generate_markdown(
            retry_prompt,
            temperature=self.ui_settings.editor_temperature
        )
        retried_count = self._count_words(retried)
        if min_words <= retried_count <= max_words:
            logger.debug("[Orchestrator][_edit_section_with_length_guard] Belief: Повторная попытка успешна | Input: section_name, min_words, max_words | Expected: str")
            return retried

        logger.debug("[Orchestrator][_edit_section_with_length_guard] Belief: Возврат исходной секции после двух неуспешных попыток | Input: section_name, min_words, max_words | Expected: str")
        return section_markdown

    def _run_query_builder(self, topic: str) -> Generator[Tuple[str, Optional[str], Optional[str]], None, None]:
        """Stage 1: Query Builder."""
        stage = PipelineStage.QUERY_BUILDER.value
        yield (emit_log(stage, "Генерация поисковых запросов..."), None, None)

        try:
            prompt = build_query_prompt(topic, query_count=5)
            raw_output = self.llm_client.generate_json(prompt, temperature=0.3)
            query_model = parse_query_output(raw_output, expected_count=5, llm_client=self.llm_client)

            logger.debug(f"[Orchestrator][_run_query_builder] Belief: Запросы сгенерированы | Input: topic | Expected: List[str], Count: {len(query_model.queries)}")

            self._queries = query_model.queries
            yield (emit_log(stage, f"Сгенерировано {len(query_model.queries)} поисковых запросов"), None, None)

        except Exception as e:
            raise handle_stage_failure(stage, e, recoverable=False)

    def _run_search(self) -> Generator[Tuple[str, Optional[str], Optional[str]], None, str]:
        """Stage 2: Search."""
        stage = PipelineStage.SEARCH.value
        yield (emit_log(stage, "Поиск исследовательских данных..."), None, None)

        try:
            aggregate = run_sequential_search(self._queries, self.tavily_client)

            if check_search_failure(aggregate):
                error_msg = f"Все {len(self._queries)} поисковых запросов не удались"
                yield (emit_log(stage, error_msg), None, None)
                raise handle_stage_failure(stage, Exception(error_msg), recoverable=True)

            merged = merge_research_items(aggregate)
            research_context = format_research_context(merged)

            logger.debug(f"[Orchestrator][_run_search] Belief: Поиск завершен | Input: queries | Expected: str, Sources: {len(merged)}")

            yield (emit_log(stage, f"Найдено {len(merged)} исследовательских источников"), None, None)
            return research_context

        except StageError:
            raise
        except Exception as e:
            raise handle_stage_failure(stage, e, recoverable=True)

    def _run_structure_planner(self, research_context: str) -> Generator[Tuple[str, Optional[str], Optional[str]], None, dict]:
        """Stage 3: Structure Planner."""
        stage = PipelineStage.STRUCTURE_PLANNER.value
        yield (emit_log(stage, "Планирование структуры документа..."), None, None)

        try:
            prompt = build_structure_prompt(research_context, self.ui_settings.chapter_count)
            raw_output = self.llm_client.generate_json(prompt, temperature=0.5)
            structure = parse_structure_output(raw_output, expected_chapters=self.ui_settings.chapter_count, llm_client=self.llm_client)

            logger.debug(f"[Orchestrator][_run_structure_planner] Belief: Структура спланирована | Input: research_context | Expected: dict, Chapters: {len(structure.chapters)}")

            yield (emit_log(stage, f"Запланировано {len(structure.chapters)} глав"), None, None)
            return structure

        except Exception as e:
            raise handle_stage_failure(stage, e, recoverable=False)

    def _run_chapter_writer(self, structure: dict, research_context: str) -> Generator[Tuple[str, Optional[str], Optional[str]], None, list]:
        """Stage 4: Chapter Writer."""
        stage = PipelineStage.CHAPTER_WRITER.value
        chapters = []

        for i, chapter_plan in enumerate(structure.chapters, 1):
            yield (emit_log(stage, f"Написание главы {i}/{len(structure.chapters)}..."), None, None)

            try:
                prompt = build_chapter_writer_prompt(
                    main_title=structure.title,
                    chapter_title=chapter_plan.title,
                    chapter_prompt=chapter_plan.prompt,
                    research_context=research_context,
                    word_limit=self.ui_settings.words_per_chapter,
                    keep_links=self.ui_settings.keep_links
                )
                chapter_text = self.llm_client.generate_markdown(prompt, temperature=self.ui_settings.temperature)
                chapters.append(chapter_text)

                logger.debug(f"[Orchestrator][_run_chapter_writer] Belief: Глава написана | Input: chapter_title={chapter_plan.title} | Expected: str")

            except Exception as e:
                raise handle_stage_failure(f"{stage} (Глава {i})", e, recoverable=False)

        yield (emit_log(stage, f"Все {len(chapters)} глав написаны"), None, None)
        return chapters

    def _run_assembly_and_editor(self, structure: dict, chapters: list) -> Generator[Tuple[str, Optional[str], Optional[str]], None, str]:
        """Stage 5: Assembly + Final Editor."""
        stage = PipelineStage.ASSEMBLY.value
        yield (emit_log(stage, "Сборка документа..."), None, None)

        try:
            yield (emit_log(stage, "Редактирование введения с контролем длины..."), None, None)
            edited_intro = self._edit_section_with_length_guard("Introduction", structure.introduction)

            edited_chapters = []
            for i, chapter_text in enumerate(chapters, 1):
                yield (emit_log(stage, f"Редактирование главы {i}/{len(chapters)} с контролем длины..."), None, None)
                edited_chapter = self._edit_section_with_length_guard(f"Chapter {i}", chapter_text)
                edited_chapters.append(edited_chapter)

            yield (emit_log(stage, "Редактирование заключения с контролем длины..."), None, None)
            edited_conclusions = self._edit_section_with_length_guard("Conclusion", structure.conclusions)

            # Assembly
            draft = export_lead_magnet(
                title=structure.title,
                subtitle=structure.subtitle,
                introduction=edited_intro,
                chapters=edited_chapters,
                conclusions=edited_conclusions
            )

            yield (emit_log(stage, "Запуск легкого финального редактора..."), None, None)

            # Final Editor - читаем содержимое файла вместо пути
            from pathlib import Path
            draft_path = Path(draft)
            if draft_path.exists():
                with open(draft_path, "r", encoding="utf-8") as f:
                    draft_content = f.read()
            else:
                draft_content = draft  # Если файл не существует, используем как есть

            editor_prompt = build_final_editor_prompt(
                draft_content,
                keep_links=self.ui_settings.keep_links
            )
            final_markdown = self.llm_client.generate_markdown(
                editor_prompt,
                temperature=self.ui_settings.editor_temperature
            )

            # Save final version
            from src.export import save_markdown_file, ensure_outputs_dir, build_output_filename
            dir_path = ensure_outputs_dir()
            filename = build_output_filename()
            filepath = dir_path / filename
            save_markdown_file(final_markdown, filepath)

            logger.debug(f"[Orchestrator][_run_assembly_and_editor] Belief: Документ собран и отредактирован | Input: structure, chapters | Expected: str, Filepath: {filepath}")

            yield (emit_log(stage, f"Документ сохранен в {filepath}"), final_markdown, str(filepath))

            return str(filepath)

        except Exception as e:
            raise handle_stage_failure(stage, e, recoverable=False)
