"""
Конфигурация pytest для тестов.
Общие fixtures для всех тестовых модулей.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.config import AppConfig, UiSettings
from src.clients import LlmClient, TavilyClientWrapper
from src.schemas import QueryListModel, LeadMagnetStructureModel, ChapterPlanModel


@pytest.fixture
def mock_env_vars():
    """Мок ENV переменных для тестов."""
    return {
        "LLM_API_KEY": "test_llm_key",
        "LLM_BASE_URL": "https://test.openai.com/v1",
        "LLM_MODEL": "gpt-4",
        "TAVILY_API_KEY": "test_tavily_key"
    }


@pytest.fixture
def app_config(mock_env_vars):
    """Fixture для AppConfig."""
    return AppConfig(
        llm_api_key=mock_env_vars["LLM_API_KEY"],
        llm_base_url=mock_env_vars["LLM_BASE_URL"],
        llm_model=mock_env_vars["LLM_MODEL"],
        tavily_api_key=mock_env_vars["TAVILY_API_KEY"]
    )


@pytest.fixture
def ui_settings():
    """Fixture для UiSettings с дефолтными значениями."""
    return UiSettings(
        words_per_chapter=300,
        chapter_count=5,
        temperature=0.7
    )


@pytest.fixture
def mock_openai_client():
    """Мок для OpenAI клиента."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "test response"
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_tavily_client():
    """Мок для Tavily клиента."""
    mock_client = MagicMock()
    mock_response = {
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "Test content 1",
                "raw_content": "Full test content 1"
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "Test content 2",
                "raw_content": "Full test content 2"
            }
        ]
    }
    mock_client.search.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_query_list():
    """Пример списка запросов."""
    return QueryListModel(queries=[
        "test query 1",
        "test query 2",
        "test query 3",
        "test query 4",
        "test query 5"
    ])


@pytest.fixture
def sample_structure():
    """Пример структуры лид-магнита."""
    return LeadMagnetStructureModel(
        title="Test Lead Magnet",
        subtitle="A Test Subtitle",
        introduction="This is a test introduction.",
        conclusions="This is a test conclusion.",
        chapters=[
            ChapterPlanModel(title="Chapter 1", prompt="Write about topic 1"),
            ChapterPlanModel(title="Chapter 2", prompt="Write about topic 2"),
            ChapterPlanModel(title="Chapter 3", prompt="Write about topic 3"),
            ChapterPlanModel(title="Chapter 4", prompt="Write about topic 4"),
            ChapterPlanModel(title="Chapter 5", prompt="Write about topic 5")
        ]
    )


@pytest.fixture
def sample_research_results():
    """Пример результатов поиска."""
    return [
        {
            "title": "Test Result 1",
            "url": "https://example.com/1",
            "content": "Test content 1",
            "raw_content": "Full test content 1"
        },
        {
            "title": "Test Result 2",
            "url": "https://example.com/2",
            "content": "Test content 2",
            "raw_content": "Full test content 2"
        }
    ]


@pytest.fixture
def temp_outputs_dir(tmp_path):
    """Временная директория для outputs."""
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    return outputs_dir


@pytest.fixture
def mock_logger():
    """Мок для logger."""
    return MagicMock()
