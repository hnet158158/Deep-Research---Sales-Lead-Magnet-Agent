"""
Gradio Presentation & Streaming UX Module
Реализует UI и потоковую подачу прогресса.
"""

import logging
import os
from typing import Generator, Tuple, Optional

import gradio as gr
from dotenv import load_dotenv

from src.config import load_env_config, UiSettings, save_ui_settings, validate_ui_settings
from src.clients import LlmClient, TavilyClientWrapper
from src.orchestrator import GenerationOrchestrator
from src.errors import format_ui_error, stream_logs, StageError

logger = logging.getLogger(__name__)


def build_ui() -> gr.Blocks:
    """
    Строит Gradio UI.

    # START_CONTRACT_build_ui
    # Input: None
    # Russian Intent: Создать Gradio интерфейс с компонентами
    # Output: gr.Blocks - готовый интерфейс
    # END_CONTRACT_build_ui
    """
    logger.debug("[UI][build_ui] Belief: Построение Gradio UI | Input: None | Expected: gr.Blocks")

    with gr.Blocks(title="AI Lead Magnet Generator") as demo:
        gr.Markdown("# AI Lead Magnet Generator")

        with gr.Row():
            # Левая колонка: 1/3 ширины - ввод, настройки, логи
            with gr.Column(scale=1):
                topic_input = gr.Textbox(
                    label="Тема лид-магнита",
                    placeholder="Введите тему для генерации...",
                    lines=2
                )
                generate_btn = gr.Button("Сгенерировать", variant="primary", size="lg")

                with gr.Accordion("Настройки", open=True):
                    words_slider = gr.Slider(
                        minimum=100,
                        maximum=1000,
                        value=300,
                        step=50,
                        label="Слов на главу"
                    )
                    chapters_slider = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Количество глав"
                    )
                    temp_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.7,
                        step=0.1,
                        label="Креативность (Temperature)"
                    )
                    editor_temp_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.2,
                        step=0.1,
                        label="Креативность редакторов"
                    )
                    keep_links_checkbox = gr.Checkbox(
                        value=True,
                        label="Сохранять ссылки"
                    )
                    section_editors_checkbox = gr.Checkbox(
                        value=True,
                        label="Промежуточные редакторы глав"
                    )

                logs_output = gr.Textbox(
                    label="Логи выполнения",
                    lines=10,
                    interactive=False,
                    autoscroll=True
                )

            # Правая колонка: 2/3 ширины - только блок просмотра статьи
            with gr.Column(scale=2):
                markdown_output = gr.Markdown(label="Статья", elem_id="article-preview")

        generate_btn.click(
            fn=on_generate_click,
            inputs=[
                topic_input,
                words_slider,
                chapters_slider,
                temp_slider,
                editor_temp_slider,
                keep_links_checkbox,
                section_editors_checkbox
            ],
            outputs=[logs_output, markdown_output]
        )

    logger.debug("[UI][build_ui] Belief: Gradio UI построен | Input: None | Expected: gr.Blocks")
    return demo


def on_generate_click(
    topic: str,
    words_per_chapter: int,
    chapter_count: int,
    temperature: float,
    editor_temperature: float,
    keep_links: bool,
    enable_section_editors: bool
) -> Generator[Tuple[str, Optional[str]], None, None]:
    """
    Обработчик клика на кнопку генерации.

    # START_CONTRACT_on_generate_click
    # Input: topic, words_per_chapter, chapter_count, temperature, editor_temperature, keep_links, enable_section_editors
    # Russian Intent: Запустить генерацию и стримить прогресс в UI
    # Output: Generator - стрим обновлений (logs, markdown)
    # END_CONTRACT_on_generate_click
    """
    logger.debug(
        f"[UI][on_generate_click] Belief: Запуск генерации | "
        f"Input: topic={topic}, settings | Expected: Generator"
    )

    # Инициализация
    try:
        app_config = load_env_config()
        ui_settings = UiSettings(
            words_per_chapter=words_per_chapter,
            chapter_count=chapter_count,
            temperature=temperature,
            editor_temperature=editor_temperature,
            keep_links=keep_links,
            enable_section_editors=enable_section_editors
        )

        if not validate_ui_settings(ui_settings):
            yield ("❌ Invalid settings", None)
            return

        # Сохранение настроек
        save_ui_settings(ui_settings)

        # Инициализация клиентов
        llm_client = LlmClient(app_config)
        tavily_client = TavilyClientWrapper(app_config.tavily_api_key)

        # Оркестратор
        orchestrator = GenerationOrchestrator(
            app_config,
            ui_settings,
            llm_client,
            tavily_client
        )

        # Запуск pipeline (без file output в UI)
        for logs, markdown, _ in stream_logs(orchestrator.run_pipeline(topic)):
            yield (logs, markdown)

    except StageError as e:
        error_msg = format_ui_error(e)
        yield (error_msg, None)
    except ValueError as e:
        error_msg = f"❌ Configuration Error: {e}"
        yield (error_msg, None)
    except Exception as e:
        logger.error(f"[UI][on_generate_click] Unexpected error: {e}")
        error_msg = f"❌ Unexpected error: {type(e).__name__}"
        yield (error_msg, None)


def format_ui_state(
    logs: str,
    markdown: Optional[str],
    filepath: Optional[str]
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Форматирует состояние UI для вывода.

    # START_CONTRACT_format_ui_state
    # Input: logs, markdown, filepath
    # Russian Intent: Форматировать состояние UI для отображения
    # Output: Tuple[str, Optional[str], Optional[str]]
    # END_CONTRACT_format_ui_state
    """
    logger.debug(
        "[UI][format_ui_state] Belief: Форматирование состояния UI | "
        "Input: logs, markdown, filepath | Expected: Tuple"
    )

    return logs, markdown, filepath


def main():
    """
    Запуск Gradio приложения.

    # START_CONTRACT_main
    # Input: None
    # Russian Intent: Инициализировать окружение и запустить Gradio UI
    # Output: None (блокирующий запуск)
    # END_CONTRACT_main
    """
    # START_CONTRACT_main
    # Input: None
    # Russian Intent: Инициализировать окружение и запустить Gradio UI
    # Output: None (блокирующий запуск)
    # END_CONTRACT_main

    logger.debug(
        "[UI][main] Belief: Загрузка .env файла | "
        "Input: None | Expected: ENV переменные загружены"
    )

    load_dotenv()

    logger.debug("[UI][main] Belief: .env файл загружен | Input: None | Expected: ENV переменные доступны")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting AI Lead Magnet Generator...")

    # Гарантируем прямой loopback-доступ для внутреннего startup probe Gradio
    # (обход системного proxy для localhost/127.0.0.1).
    no_proxy_hosts = "localhost,127.0.0.1,::1"
    existing_no_proxy = os.environ.get("NO_PROXY", "")
    if existing_no_proxy:
        if "localhost" not in existing_no_proxy:
            os.environ["NO_PROXY"] = f"{existing_no_proxy},{no_proxy_hosts}"
    else:
        os.environ["NO_PROXY"] = no_proxy_hosts
    os.environ["no_proxy"] = os.environ["NO_PROXY"]

    demo = build_ui()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False
    )


if __name__ == "__main__":
    main()
