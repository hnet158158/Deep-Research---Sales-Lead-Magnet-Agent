# AI Lead Magnet Generator

Gradio приложение для генерации лид-магнитов с использованием Tavily Search и OpenAI-compatible LLM.

## Особенности

- **Исследование через Tavily**: Автоматический поиск релевантной информации по теме
- **Структурированная генерация**: 5-шаговый pipeline для создания качественного контента
- **Настройки UI**: Сохранение пользовательских предпочтений между запусками
- **Потоковые логи**: Отслеживание прогресса в реальном времени
- **Экспорт в Markdown**: Автоматическое сохранение с timestamp

## Требования

- Python 3.10+
- API ключ для OpenAI-compatible LLM
- API ключ для Tavily Search

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd "Deep Research - Sales Lead Magnet Agent"
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
```

Отредактируйте `.env` файл с вашими API ключами:
```
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
TAVILY_API_KEY=tvly-your_tavily_api_key_here
```

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: http://127.0.0.1:7860

## Архитектура

### Модули

- **config.py**: Загрузка ENV-переменных и управление настройками UI
- **schemas.py**: Промпты и JSON-схемы для LLM
- **clients.py**: Клиенты для LLM и Tavily Search
- **research.py**: Агрегатор результатов поиска
- **orchestrator.py**: Оркестратор полного pipeline
- **export.py**: Сборка и экспорт документа
- **errors.py**: Обработка ошибок и логирование
- **ui.py**: Gradio интерфейс

### Pipeline генерации

1. **Query Builder**: Генерация поисковых запросов на основе темы
2. **Search**: Последовательный поиск через Tavily
3. **Structure Planner**: Планирование структуры документа
4. **Chapter Writer**: Написание глав (по одной за раз)
5. **Assembly + Editor**: Сборка и финальная редакция

## Настройки UI

- **Слов на главу**: 100-1000 (по умолчанию: 300)
- **Количество глав**: 1-10 (по умолчанию: 5)
- **Креативность (Temperature)**: 0.0-1.0 (по умолчанию: 0.7)

## Выходные файлы

Генерируемые файлы сохраняются в директорию `outputs/` с именем формата:
```
lead_magnet_YYYYMMDD_HHMMSS.md
```

## Лицензия

MIT License
