"""
Markdown Assembly & Export Module
Сшивает документ и сохраняет в файл с timestamp.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def assemble_document_sections(
    title: str,
    subtitle: str,
    introduction: str,
    chapters: List[str],
    conclusions: str
) -> str:
    """
    Сшивает документ в фиксированном порядке.

    # START_CONTRACT_assemble_document_sections
    # Input: title, subtitle, introduction, chapters (List[str]), conclusions
    # Russian Intent: Собрать все секции документа в единый Markdown
    # Output: str - собранный документ
    # END_CONTRACT_assemble_document_sections
    """
    logger.debug("[Export][assemble_document_sections] Belief: Сборка документа | Input: title, subtitle, introduction, chapters, conclusions | Expected: str")

    parts = []

    parts.append(f"# {title}\n")
    parts.append(f"## {subtitle}\n")
    parts.append(f"{introduction}\n")

    for i, chapter in enumerate(chapters, 1):
        parts.append(f"## Chapter {i}\n")
        parts.append(f"{chapter}\n")

    parts.append("## Conclusion\n")
    parts.append(f"{conclusions}\n")

    document = "\n".join(parts)
    logger.debug("[Export][assemble_document_sections] Belief: Документ собран | Input: title, subtitle, introduction, chapters, conclusions | Expected: str")
    return document


def ensure_outputs_dir(outputs_dir: str = "outputs") -> Path:
    """
    Проверяет/создает директорию outputs.

    # START_CONTRACT_ensure_outputs_dir
    # Input: outputs_dir (str)
    # Russian Intent: Убедиться что директория для вывода существует
    # Output: Path - путь к директории
    # END_CONTRACT_ensure_outputs_dir
    """
    logger.debug("[Export][ensure_outputs_dir] Belief: Проверка директории outputs | Input: outputs_dir | Expected: Path")

    path = Path(outputs_dir)
    path.mkdir(parents=True, exist_ok=True)

    logger.debug(f"[Export][ensure_outputs_dir] Belief: Директория готова | Input: outputs_dir | Expected: Path, Result: {path}")
    return path


def build_output_filename(prefix: str = "lead_magnet") -> str:
    """
    Генерирует имя файла с timestamp.

    # START_CONTRACT_build_output_filename
    # Input: prefix (str)
    # Russian Intent: Сгенерировать имя файла с временной меткой
    # Output: str - имя файла
    # END_CONTRACT_build_output_filename
    """
    logger.debug("[Export][build_output_filename] Belief: Генерация имени файла | Input: prefix | Expected: str")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.md"

    logger.debug(f"[Export][build_output_filename] Belief: Имя файла сгенерировано | Input: prefix | Expected: str, Result: {filename}")
    return filename


def save_markdown_file(content: str, filepath: Path) -> Path:
    """
    Сохраняет Markdown файл.

    # START_CONTRACT_save_markdown_file
    # Input: content (str), filepath (Path)
    # Russian Intent: Сохранить содержимое в файл
    # Output: Path - путь к сохраненному файлу
    # END_CONTRACT_save_markdown_file
    """
    logger.debug("[Export][save_markdown_file] Belief: Сохранение файла | Input: content, filepath | Expected: Path")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.debug(f"[Export][save_markdown_file] Belief: Файл сохранен | Input: content, filepath | Expected: Path, Result: {filepath}")
    return filepath


def export_lead_magnet(
    title: str,
    subtitle: str,
    introduction: str,
    chapters: List[str],
    conclusions: str,
    outputs_dir: str = "outputs"
) -> str:
    """
    Полный цикл экспорта лид-магнита.

    # START_CONTRACT_export_lead_magnet
    # Input: title, subtitle, introduction, chapters, conclusions, outputs_dir
    # Russian Intent: Собрать и сохранить лид-магнит в файл
    # Output: str - путь к сохраненному файлу
    # END_CONTRACT_export_lead_magnet
    """
    logger.debug("[Export][export_lead_magnet] Belief: Экспорт лид-магнита | Input: title, subtitle, introduction, chapters, conclusions, outputs_dir | Expected: str")

    document = assemble_document_sections(title, subtitle, introduction, chapters, conclusions)
    dir_path = ensure_outputs_dir(outputs_dir)
    filename = build_output_filename()
    filepath = dir_path / filename

    save_markdown_file(document, filepath)

    logger.debug(f"[Export][export_lead_magnet] Belief: Лид-магнит экспортирован | Input: title, subtitle, introduction, chapters, conclusions, outputs_dir | Expected: str, Result: {filepath}")
    return str(filepath)
