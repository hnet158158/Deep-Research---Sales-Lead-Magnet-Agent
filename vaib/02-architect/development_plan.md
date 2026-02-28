# Development Plan

## Module: Configuration & Settings
- **Contract**: Загружает обязательные ENV-переменные (`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`, `TAVILY_API_KEY`), управляет пользовательскими настройками UI (words per chapter, chapter count, temperature), обеспечивает сохранение/загрузку `config.json` между перезапусками.
- **Negative Constraints**:
  - MUST NOT хранить секреты в `config.json`, логах, markdown-выводе.
  - MUST NOT запускать pipeline при отсутствии обязательных ENV.
  - MUST NOT принимать значения вне диапазонов: words `[100..1000]`, chapters `[1..10]`, temperature `[0.0..1.0]`.
- **Map**: `AppConfig`, `UiSettings`, `load_env_config()`, `load_ui_settings()`, `save_ui_settings()`, `validate_ui_settings()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  PRE:
  - Файл `.env` существует или переменные доступны в окружении процесса.
  - Для UI доступен путь чтения/записи локального файла настроек.

  STEP 1: Вызвать `load_env_config()` и прочитать обязательные ключи.
  STEP 2: Провалидировать, что каждый обязательный ключ непустой.
  STEP 3: Если ENV некорректен — сформировать контролируемую ошибку конфигурации и остановить инициализацию app.
  STEP 4: Вызвать `load_ui_settings()`; если файл отсутствует — вернуть значения по умолчанию.
  STEP 5: Вызвать `validate_ui_settings()` с жесткими границами.
  STEP 6: При изменении пользователем настроек — повторно валидировать и вызвать `save_ui_settings()`.

  POST:
  - Доступен валидный `AppConfig` и валидный `UiSettings`.
  - Настройки UI устойчиво сохраняются между запусками.
  ************************
- **Mental Test**: "Passed: при первом запуске без `config.json` подставляются дефолты; после изменения настроек и перезапуска значения восстановлены, секреты не сохранены в локальном settings-файле."

## Module: Prompt & Structured Schema Layer
- **Contract**: Инкапсулирует системные промпты и строгие JSON-схемы для Step 1 (Query Builder) и Step 3 (Structure Planner), выполняет tolerant parsing-layer (normalization → shape coercion → strict validation) и гарантирует канонический контракт для клиента.
- **Negative Constraints**:
  - MUST NOT принимать невалидный JSON или частично валидную структуру как успешный результат.
  - MUST NOT обходить канонический формат Query-этапа (`{"queries": [...]}`).
  - MUST NOT выполнять JSON5-like правки как default path — только fallback при strict parse fail.
  - MUST NOT молча исправлять ответ LLM без явной валидации и логирования.
  - MUST NOT допускать несоответствие количества глав `chapter_count`.
- **Map**: `QueryListModel`, `LeadMagnetStructureModel`, `ChapterPlanModel`, `normalize_raw_json()`, `extract_first_json_block()`, `coerce_query_shape()`, `build_query_prompt()`, `build_structure_prompt()`, `parse_query_output()`, `parse_structure_output()`, `validate_query_count()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  PRE:
  - Входные параметры (`topic`, `query_count`, `chapter_count`, `research_context`) валидны.
  - Ответ LLM представлен строкой.

  STEP 1: Сформировать системный промпт для соответствующей стадии.
  STEP 2: Для Query-этапа зафиксировать единый канон в промпте: вернуть объект `{"queries": ["...", ...]}` (не массив верхнего уровня).
  STEP 3: Принять raw-строку от LLM без мутаций и запустить strict parse (`json.loads(raw)`).
  STEP 4: Если strict parse fail, выполнить `normalize_raw_json()`:
          - trim пробелов;
          - удалить markdown-fences (` ```json ... ``` ` и ` ``` ... ``` `);
          - извлечь первый валидный JSON-блок (`{...}` или `[...]`) через `extract_first_json_block()`.
  STEP 5: Повторить strict parse на нормализованной строке.
  STEP 6: Если parse снова fail, выполнить один fallback sanitizer-pass (минимальные JSON5-like правки: хвостовые запятые/одинарные кавычки), затем parse.
  STEP 7: Если parse снова fail, выполнить ровно один repair-pass через LLM в JSON-only режиме и повторить parse.
  STEP 8: Если после repair-pass parse fail, вернуть детальную parse error с sample raw и hard-stop стадии.
  STEP 9: Для Query-этапа выполнить `coerce_query_shape()`:
          - принять `[...]`;
          - принять `{"queries": [...]}`;
          - принять похожие ключи (`query`, `search_queries`, `items`) и смаппить в `queries`.
  STEP 10: Канонизировать Query-результат строго в объект `{"queries": [...]}`.
  STEP 11: Вызвать Pydantic-валидацию целевой модели.
  STEP 12: Проверить инварианты (`len(queries)==query_count`, `len(chapters)==chapter_count`, отсутствие пустых query-строк).
  STEP 13: При нарушении любого шага вернуть typed validation error с указанием стадии и инварианта.

  POST:
  - На Query-выходе всегда строго канонический объект `{"queries": [...]}`.
  - На выходе строго типизированный объект схемы.
  - Любая структурная ошибка приводит к fail-fast.
  ************************
- **Mental Test**: "Passed: если LLM вернул fenced массив внутри поясняющего текста, слой нормализации извлекает JSON, `coerce_query_shape()` приводит к `{"queries": [...]}`, затем count проходит строгую проверку."

## Module: Provider Clients (LLM + Tavily)
- **Contract**: Предоставляет единый интерфейс к OpenAI-compatible LLM (с `base_url`) и Tavily Search, включая таймауты, обработку сетевых исключений и stage-oriented logging.
- **Negative Constraints**:
  - MUST NOT выполнять параллельные LLM-запросы.
  - MUST NOT переключаться на другой search provider кроме Tavily.
  - MUST NOT расходовать более одного дополнительного LLM-вызова на repair-pass для одного parse-сбоя.
  - MUST NOT логировать API-ключи, полный auth payload или персональные секреты.
  - MUST NOT проглатывать исключения без trace-логирования.
- **Map**: `LlmClient`, `TavilyClient`, `generate_json()`, `generate_markdown()`, `repair_json_once()`, `search_once()`, `safe_log_error()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  STEP 1: Инициализировать `LlmClient` из `AppConfig` с заданным `base_url` и `model`.
  STEP 2: Инициализировать `TavilyClient` из `TAVILY_API_KEY`.
  STEP 3: Для Query-stage и repair-stage использовать единый `response_format={"type":"json_object"}` для синхронизации контракта клиента и промпта.
  STEP 4: Для каждого внешнего вызова обернуть выполнение в try/except и писать stage-specific logs.
  STEP 5: Возвращать либо валидный результат, либо контролируемое исключение уровня домена.
  ************************
- **Mental Test**: "Passed: при parse-fail repair-pass вызывается ровно один раз в JSON-only режиме; при повторном fail клиент возвращает контролируемую ошибку без утечки raw секрета."

## Module: Research Aggregator (Sequential Tavily Search)
- **Contract**: Последовательно выполняет поиск по списку query, агрегирует контекст (факты/цитаты/URL), реализует политику деградации: продолжить при частичных отказах и остановиться только если отказали все запросы.
- **Negative Constraints**:
  - MUST NOT запускать параллельный поиск через `asyncio.gather`.
  - MUST NOT падать при частичном отказе (`1..N-1`).
  - MUST NOT продолжать pipeline если `N` из `N` запросов завершились ошибкой.
- **Map**: `ResearchItem`, `ResearchAggregate`, `run_sequential_search()`, `merge_research_items()`, `format_research_context()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  PRE:
  - На вход подан непустой список query.
  - Tavily client и лог-стрим доступны.

  STEP 1: Инициализировать `success_count=0`, `fail_count=0`, `items=[]`.
  STEP 2: Для каждого `query` по порядку вызвать `search_once(query)`.
  STEP 3: Если ответ успешный — нормализовать структуру, добавить в `items`, `success_count += 1`.
  STEP 4: Если ошибка — записать лог "search failed for query_i", `fail_count += 1`, перейти к следующему query.
  STEP 5: После цикла проверить `success_count`.
  STEP 6: Если `success_count == 0` — вернуть recoverable error для UI и завершить pipeline.
  STEP 7: Иначе вызвать `merge_research_items()` и `format_research_context()`.

  POST:
  - При `success_count>0` возвращается агрегированный контекст.
  - При `success_count==0` возвращается контролируемая ошибка стадии Search.
  ************************
- **Mental Test**: "Passed: из 5 запросов 2 упали, 3 успешны — pipeline продолжился и использовал частичный контекст; при 5/5 failures генерация остановилась с recoverable UI error."

## Module: Lead Magnet Orchestrator (FIFO Pipeline)
- **Contract**: Управляет полным конвейером генерации строго по шагам 1→5, обеспечивает детерминированный FIFO-порядок LLM вызовов, stage logging и fail-fast на критических стадиях.
- **Negative Constraints**:
  - MUST NOT выполнять LLM-вызовы конкурентно или вне заданного порядка.
  - MUST NOT пропускать обязательный финальный editor step.
  - MUST NOT скрывать причину падения этапа от UI-логов.
- **Map**: `GenerationOrchestrator`, `run_pipeline()`, `run_query_builder()`, `run_structure_planner()`, `run_chapter_writer_fifo()`, `run_final_editor()`, `assemble_markdown()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  PRE:
  - Валидные `topic`, `UiSettings`, `AppConfig`.
  - Инициализированы клиенты LLM/Tavily и schema-layer.

  STEP 1: Лог "Stage 1: Query Builder" и выполнить `run_query_builder()`.
  STEP 2: Провалидировать строгий JSON-массив запросов.
  STEP 3: Лог "Stage 2: Search" и выполнить `run_sequential_search()`.
  STEP 4: Если Search вернул full failure — отдать recoverable error в UI, STOP.
  STEP 5: Лог "Stage 3: Structure Planner" и выполнить `run_structure_planner()` + strict schema validation.
  STEP 6: Лог "Stage 4: Chapter Writer" и для каждой главы в `for i in 1..N`:
          - лог `Пишу главу i/N...`
          - один LLM-запрос на главу
          - append результата в `chapter_texts`.
  STEP 7: Лог "Stage 5: Assembly" и выполнить `assemble_markdown()`.
  STEP 8: Обязательно выполнить `run_final_editor()` над собранным draft.
  STEP 9: Вернуть финальный markdown + путь экспортируемого файла.

  POST:
  - Все LLM-стадии выполнены строго последовательно.
  - Финальный текст прошел editor-pass и готов к экспорту.
  ************************
- **Mental Test**: "Passed: при 5 главах LLM вызван ровно 1 (queries) + 1 (planner) + 5 (chapters) + 1 (editor) раз в фиксированном порядке без параллелизма."

## Module: Gradio Presentation & Streaming UX
- **Contract**: Реализует UI (header, topic input, settings panel, logs, markdown preview, download) и потоковую подачу прогресса через `yield` на протяжении всего pipeline.
- **Negative Constraints**:
  - MUST NOT блокировать UI без промежуточных log updates.
  - MUST NOT использовать интерактивный редактор вместо read-only execution logs.
  - MUST NOT завершать генерацию без ссылки на downloadable file при успехе.
- **Map**: `build_ui()`, `on_generate_click()`, `stream_generation()`, `format_ui_state()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  STEP 1: Сконструировать Gradio layout по требованиям (header/input/settings/logs/output/download).
  STEP 2: Привязать кнопку `Сгенерировать` к генератору `stream_generation()`.
  STEP 3: На каждой стадии оркестратора делать `yield` с обновленным логом и текущим состоянием markdown/file.
  STEP 4: На ошибке отдавать понятный текст в логи и безопасное состояние output.
  STEP 5: На успехе показать polished markdown и активировать download-компонент.
  ************************
- **Mental Test**: "Passed: пользователь видит последовательные статусы Stage 1..5 в реальном времени, а после завершения — предпросмотр и кнопку скачивания файла."

## Module: Markdown Assembly & Export
- **Contract**: Сшивает документ в фиксированном порядке (`Title -> Subtitle -> Introduction -> Chapters -> Conclusion`), создает `outputs/` при отсутствии и сохраняет файл с timestamp-именем.
- **Negative Constraints**:
  - MUST NOT менять порядок секций документа.
  - MUST NOT падать из-за отсутствующей директории `outputs/`.
  - MUST NOT сохранять файл без временной метки в имени.
- **Map**: `assemble_document_sections()`, `ensure_outputs_dir()`, `build_output_filename()`, `save_markdown_file()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  STEP 1: Принять структурные части документа и массив глав в исходном порядке.
  STEP 2: Сформировать единый markdown-черновик строго по контрактному шаблону секций.
  STEP 3: Проверить/создать директорию `outputs/`.
  STEP 4: Сгенерировать имя `lead_magnet_[YYYYMMDD_HHMMSS].md`.
  STEP 5: Записать файл и вернуть абсолютный/относительный путь для UI download.
  ************************
- **Mental Test**: "Passed: при отсутствии папки `outputs/` она создается автоматически, файл сохраняется с timestamp и доступен для скачивания в UI."

## Module: Error Policy & Observability
- **Contract**: Централизует правила отказоустойчивости, stage-level диагностику и user-readable логи в соответствии с fault tolerance и требованиями прозрачности.
- **Negative Constraints**:
  - MUST NOT маскировать тип ошибки (search partial/full failure, LLM stage failure, parse failure).
  - MUST NOT терять информацию о том, на каком подшаге упал parsing-layer (strict/normalize/sanitizer/repair).
  - MUST NOT подавлять stack trace в технических логах.
  - MUST NOT раскрывать чувствительные данные в пользовательском log stream.
- **Map**: `PipelineError`, `StageError`, `ParseStageError`, `emit_log()`, `emit_belief_log()`, `handle_stage_failure()`, `build_parse_error_sample()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  STEP 1: На входе каждой стадии публиковать user-readable лог начала.
  STEP 2: Для внутренних debug-сообщений применять шаблон `[Belief]` из правил.
  STEP 3: При исключении классифицировать ошибку по типу стадии.
  STEP 4: Применить policy:
          - Search partial failure -> continue.
          - Search full failure -> recoverable stop.
          - LLM failure -> hard stop.
          - Parse failure после `strict -> normalize -> sanitizer -> repair` -> hard stop с детализированной диагностикой.
  STEP 5: В parse error включить ограниченный sample raw (без секретов и без полного дампа).
  STEP 6: Вернуть в UI явное сообщение о стадии, причине и статусе завершения.
  ************************
- **Mental Test**: "Passed: при полном parse-fail в Query-stage лог содержит последовательность неуспешных шагов parsing-layer и безопасный sample raw; pipeline завершается предсказуемо без тихих сбоев."

## Module: Contract Tests (Any-Format Structured Output)
- **Contract**: Определяет контрактные тесты для tolerant parsing-layer в `tests/test_contracts.py`, проверяет прием разных форм входа и строгие инварианты канонической модели.
- **Negative Constraints**:
  - MUST NOT ограничиваться одним happy-path JSON-объектом.
  - MUST NOT пропускать кейсы с fenced JSON и JSON внутри поясняющего текста.
  - MUST NOT считать валидным результат с неправильным `count` или пустыми query-строками.
- **Map**: `test_parse_query_from_array()`, `test_parse_query_from_object()`, `test_parse_query_from_fenced_json()`, `test_parse_query_from_embedded_json_text()`, `test_parse_query_invalid_count()`, `test_parse_query_empty_strings_rejected()`.
- **Internal Logic**:
  *** ALGORITHM DESIGN ***
  PRE:
  - Доступны функции `normalize_raw_json()`, `parse_query_output()`, `coerce_query_shape()` и модель `QueryListModel`.

  STEP 1: Проверить, что чистый массив строк корректно коэрсится в `{"queries": [...]}`.
  STEP 2: Проверить, что чистый объект `{"queries": [...]}` проходит без изменений.
  STEP 3: Проверить, что fenced JSON корректно очищается нормализатором.
  STEP 4: Проверить, что JSON внутри поясняющего текста корректно извлекается как первый валидный блок.
  STEP 5: Проверить, что неверный count приводит к typed validation error.
  STEP 6: Проверить, что пустые строки в queries отклоняются строгой моделью/инвариантом.

  POST:
  - Контракт "принимать любой формат" подтвержден тестами на normalization + coercion + strict validation.
  - Невалидные варианты отвергаются детерминированно.
  ************************
- **Mental Test**: "Passed: все допустимые формы raw-output приводятся к одному канону `{"queries": [...]}`, а нарушения count/empty строк стабильно падают на валидации."

## Delivery Contract for Vaib4 Coder
- Python `3.10+`, strict typing, без конкурентных LLM-вызовов.
- Четкое разделение слоев: UI / orchestrator / provider clients / prompts+schemas / io utils.
- `# START_CONTRACT` якорь сохраняется внутри функций реализации.
- Логирование с обязательным `[Belief]` шаблоном для debug-ветки.
- Любые изменения зависимостей вне утвержденного стека запрещены без отдельной задачи.

> **NEXT STEP:** Vaib3 Spec
> **COMMAND:** Switch to @vaib3-spec and say "Verify Technology Stack"
> **STATUS:** READY
