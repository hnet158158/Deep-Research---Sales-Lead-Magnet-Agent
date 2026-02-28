"""
Error Policy & Observability Module
Централизует правила отказоустойчивости и логирование.
"""

import logging
from typing import Optional, Generator, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class StageError(Exception):
    """Ошибка на определенной стадии pipeline."""

    def __init__(self, stage: str, message: str, recoverable: bool = False):
        self.stage = stage
        self.message = message
        self.recoverable = recoverable
        super().__init__(f"[{stage}] {message}")


class PipelineError(Exception):
    """Критическая ошибка pipeline."""


class PipelineStage(Enum):
    """Стадии pipeline."""
    QUERY_BUILDER = "Генератор запросов"
    SEARCH = "Поиск"
    STRUCTURE_PLANNER = "Планировщик структуры"
    CHAPTER_WRITER = "Писатель глав"
    FINAL_EDITOR = "Финальный редактор"
    ASSEMBLY = "Сборка"


def emit_log(stage: str, message: str) -> str:
    """
    Публикует user-readable лог начала стадии.

    # START_CONTRACT_emit_log
    # Input: stage (str), message (str)
    # Russian Intent: Публикация лога стадии для UI
    # Output: str - форматированное сообщение
    # END_CONTRACT_emit_log
    """
    logger.debug(f"[Errors][emit_log] Belief: Публикация лога | Input: stage={stage}, message | Expected: str")

    log_message = f"📍 {stage}: {message}"
    logger.info(log_message)

    return log_message


def emit_belief_log(module: str, function: str, intent: str, input_args: str, expected: str) -> None:
    """
    Публикует debug-лог с шаблоном [Belief].

    # START_CONTRACT_emit_belief_log
    # Input: module, function, intent, input_args, expected
    # Russian Intent: Публикация debug-лога с шаблоном [Belief]
    # Output: None
    # END_CONTRACT_emit_belief_log
    """
    log_message = f"[{module}][{function}] Belief: {intent} | Input: {input_args} | Expected: {expected}"
    logger.debug(log_message)


def handle_stage_failure(
    stage: str,
    error: Exception,
    recoverable: bool = False
) -> StageError:
    """
    Обрабатывает ошибку стадии.

    # START_CONTRACT_handle_stage_failure
    # Input: stage (str), error (Exception), recoverable (bool)
    # Russian Intent: Обработать ошибку стадии и вернуть контролируемое исключение
    # Output: StageError
    # END_CONTRACT_handle_stage_failure
    """
    logger.debug(f"[Errors][handle_stage_failure] Belief: Обработка ошибки стадии | Input: stage={stage}, error, recoverable | Expected: StageError")

    error_type = type(error).__name__
    error_msg = str(error)

    # Удаляем потенциальные секреты
    safe_msg = error_msg
    for keyword in ["api_key", "token", "password", "secret"]:
        if keyword in safe_msg.lower():
            safe_msg = safe_msg[:safe_msg.lower().find(keyword)] + "[REDACTED]"

    stage_error = StageError(stage, f"{error_type}: {safe_msg}", recoverable)

    logger.error(f"[Errors][handle_stage_failure] Stage error: {stage_error}")
    return stage_error


def format_ui_error(stage_error: StageError) -> str:
    """
    Форматирует ошибку для UI.

    # START_CONTRACT_format_ui_error
    # Input: stage_error (StageError)
    # Russian Intent: Форматировать ошибку для отображения в UI
    # Output: str - форматированное сообщение
    # END_CONTRACT_format_ui_error
    """
    logger.debug("[Errors][format_ui_error] Belief: Форматирование ошибки для UI | Input: stage_error | Expected: str")

    if stage_error.recoverable:
        icon = "⚠️"
        status = "Восстанавливаемая ошибка"
    else:
        icon = "❌"
        status = "Критическая ошибка"

    message = f"{icon} {status} на стадии {stage_error.stage}\n{stage_error.message}"

    logger.debug("[Errors][format_ui_error] Belief: Ошибка отформатирована | Input: stage_error | Expected: str")
    return message


def stream_logs(
    generator: Generator[Tuple[str, Optional[str], Optional[str]], None, None]
) -> Generator[Tuple[str, Optional[str], Optional[str]], None, None]:
    """
    Обертка для стриминга логов с накоплением и обработкой ошибок.

    # START_CONTRACT_stream_logs
    # Input: generator (Generator)
    # Russian Intent: Обернуть генератор для безопасного накопительного стриминга логов
    # Output: Generator
    # END_CONTRACT_stream_logs
    """
    logger.debug("[Errors][stream_logs] Belief: Начало накопительного стриминга логов | Input: generator | Expected: Generator")

    accumulated_logs = ""
    accumulated_markdown = None
    accumulated_filepath = None

    try:
        for logs, markdown, filepath in generator:
            # Накапливаем логи
            if logs:
                if accumulated_logs:
                    accumulated_logs += "\n" + logs
                else:
                    accumulated_logs = logs

            # Обновляем markdown и filepath (они не накапливаются)
            if markdown is not None:
                accumulated_markdown = markdown
            if filepath is not None:
                accumulated_filepath = filepath

            # Yield накопленное состояние
            yield (accumulated_logs, accumulated_markdown, accumulated_filepath)
    except Exception as e:
        logger.error(f"[Errors][stream_logs] Error during streaming: {e}")
        error_msg = f"❌ Unexpected error: {type(e).__name__}"
        if accumulated_logs:
            error_msg = accumulated_logs + "\n" + error_msg
        yield (error_msg, None, None)
