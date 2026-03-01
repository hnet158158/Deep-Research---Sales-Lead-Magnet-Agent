import json
import re
from pathlib import Path

import pytest

from src.config import AppConfig, UiSettings, load_env_config, load_ui_settings, save_ui_settings, validate_ui_settings
from src.research import (
    ResearchAggregate,
    ResearchItem,
    run_sequential_search,
    merge_research_items,
    format_research_context,
    check_search_failure,
)
from src.schemas import (
    QueryListModel,
    LeadMagnetStructureModel,
    parse_query_output,
    parse_structure_output,
)
from src.export import (
    assemble_document_sections,
    ensure_outputs_dir,
    build_output_filename,
    save_markdown_file,
    export_lead_magnet,
)
from src.errors import StageError, emit_log, handle_stage_failure, format_ui_error, stream_logs
from src.clients import safe_log_error


class FakeTavilyWrapper:
    def __init__(self, responses):
        self._responses = responses
        self._idx = 0

    def search_once(self, query, max_results=5):
        if self._idx >= len(self._responses):
            return None
        r = self._responses[self._idx]
        self._idx += 1
        return r


def test_ui_settings_clamps_boundaries_adversarial():
    settings = UiSettings(words_per_chapter=10, chapter_count=999, temperature=-3.5)
    assert settings.words_per_chapter == 100
    assert settings.chapter_count == 10
    assert settings.temperature == 0.0


def test_validate_ui_settings_true_false_cases():
    assert validate_ui_settings(UiSettings(300, 5, 0.7)) is True
    assert validate_ui_settings(UiSettings(100, 1, 0.0)) is True


def test_ui_settings_keep_links_default_and_roundtrip(tmp_path):
    assert UiSettings().keep_links is True

    cfg = tmp_path / "config_keep_links.json"
    save_ui_settings(UiSettings(300, 5, 0.7, keep_links=False), str(cfg))
    loaded = load_ui_settings(str(cfg))
    assert loaded.keep_links is False


def test_ui_settings_editor_temperature_default_and_clamp():
    assert UiSettings().editor_temperature == 0.2

    low = UiSettings(editor_temperature=-1.0)
    high = UiSettings(editor_temperature=9.0)

    assert low.editor_temperature == 0.0
    assert high.editor_temperature == 1.0


def test_load_env_config_success(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "k1")
    monkeypatch.setenv("LLM_BASE_URL", "https://x")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setenv("TAVILY_API_KEY", "k2")

    cfg = load_env_config()
    assert isinstance(cfg, AppConfig)
    assert cfg.llm_api_key == "k1"


def test_load_env_config_missing_vars(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    with pytest.raises(ValueError) as e:
        load_env_config()
    assert "Missing required ENV variables" in str(e.value)


def test_load_and_save_ui_settings_roundtrip(tmp_path):
    cfg = tmp_path / "config.json"
    s = UiSettings(words_per_chapter=450, chapter_count=4, temperature=0.3)
    save_ui_settings(s, str(cfg))

    loaded = load_ui_settings(str(cfg))
    assert loaded.words_per_chapter == 450
    assert loaded.chapter_count == 4
    assert loaded.temperature == 0.3


def test_load_ui_settings_invalid_json_fallback(tmp_path):
    cfg = tmp_path / "broken.json"
    cfg.write_text("{bad json", encoding="utf-8")
    loaded = load_ui_settings(str(cfg))
    assert isinstance(loaded, UiSettings)
    assert loaded.words_per_chapter == 300


def test_run_sequential_search_mixed_results():
    responses = [
        {"results": [{"title": "ok1"}]},
        None,
        {"results": [{"title": "ok2"}, {"title": "ok3"}]},
    ]
    wrapper = FakeTavilyWrapper(responses)
    agg = run_sequential_search(["q1", "q2", "q3"], wrapper, max_results=5)

    assert agg.success_count == 2
    assert agg.fail_count == 1
    assert len(agg.items) == 3
    assert agg.items[1].success is False


def test_run_sequential_search_all_failures():
    wrapper = FakeTavilyWrapper([None, None])
    agg = run_sequential_search(["a", "b"], wrapper)
    assert check_search_failure(agg) is True
    assert agg.success_count == 0
    assert agg.fail_count == 2


def test_merge_research_items_only_success_items():
    agg = ResearchAggregate(
        items=[
            ResearchItem(query="q1", success=True, results=[{"id": 1}]),
            ResearchItem(query="q2", success=False, results=[{"id": 2}], error="x"),
            ResearchItem(query="q3", success=True, results=[{"id": 3}, {"id": 4}]),
        ],
        success_count=2,
        fail_count=1,
    )
    merged = merge_research_items(agg)
    assert merged == [{"id": 1}, {"id": 3}, {"id": 4}]


def test_format_research_context_empty_and_full():
    assert format_research_context([]) == "No research data available."

    long_raw = "x" * 800
    out = format_research_context([
        {
            "title": "T",
            "url": "https://e",
            "content": "C",
            "raw_content": long_raw,
        }
    ])
    assert "Source 1:" in out
    assert "Title: T" in out
    assert "URL: https://e" in out
    assert "Full Content:" in out


def test_parse_query_output_valid_and_invalid_cases():
    raw_ok = json.dumps({"queries": ["a", "b", "c"]})
    model = parse_query_output(raw_ok, expected_count=3)
    assert isinstance(model, QueryListModel)

    with pytest.raises(ValueError):
        parse_query_output("not-json", expected_count=3)

    with pytest.raises(ValueError):
        parse_query_output(json.dumps({"queries": ["a", "b"]}), expected_count=3)

    with pytest.raises(ValueError):
        parse_query_output(json.dumps({"queries": ["a", " ", "c"]}), expected_count=3)


def test_parse_structure_output_valid_and_invalid_cases(sample_structure):
    raw_ok = sample_structure.model_dump_json()
    model = parse_structure_output(raw_ok, expected_chapters=5)
    assert isinstance(model, LeadMagnetStructureModel)
    assert len(model.chapters) == 5

    with pytest.raises(ValueError):
        parse_structure_output("{", expected_chapters=5)

    raw_bad_count = sample_structure.model_dump()
    raw_bad_count["chapters"] = raw_bad_count["chapters"][:2]
    with pytest.raises(ValueError):
        parse_structure_output(json.dumps(raw_bad_count), expected_chapters=5)


def test_assemble_document_sections_contract():
    doc = assemble_document_sections(
        title="Title",
        subtitle="Sub",
        introduction="Intro",
        chapters=["Ch1 text", "Ch2 text"],
        conclusions="Final",
    )
    assert "# Title" in doc
    assert "## Sub" in doc
    assert "## Chapter 1" in doc and "## Chapter 2" in doc
    assert "## Conclusion" in doc


def test_export_helpers_and_export_full_cycle(tmp_path, monkeypatch):
    out_dir = tmp_path / "out"
    ensured = ensure_outputs_dir(str(out_dir))
    assert ensured.exists() and ensured.is_dir()

    fname = build_output_filename("pref")
    assert re.match(r"^pref_\d{8}_\d{6}\.md$", fname)

    path = out_dir / "x.md"
    saved = save_markdown_file("hello", path)
    assert saved == path
    assert path.read_text(encoding="utf-8") == "hello"

    monkeypatch.setattr("src.export.build_output_filename", lambda prefix="lead_magnet": "fixed.md")
    exported_path = export_lead_magnet(
        title="T",
        subtitle="S",
        introduction="I",
        chapters=["C1"],
        conclusions="K",
        outputs_dir=str(out_dir),
    )
    assert exported_path.endswith("fixed.md")
    assert Path(exported_path).exists()


def test_emit_and_format_error_and_redaction():
    msg = emit_log("Search", "started")
    assert msg.startswith("📍 Search: started")

    e = handle_stage_failure("Search", Exception("bad api_key=SECRET"), recoverable=True)
    assert isinstance(e, StageError)
    assert e.recoverable is True
    assert "[REDACTED]" in e.message

    ui = format_ui_error(e)
    assert "⚠️ Восстанавливаемая ошибка" in ui

    e2 = handle_stage_failure("StageX", RuntimeError("boom"), recoverable=False)
    ui2 = format_ui_error(e2)
    assert "❌ Критическая ошибка" in ui2


def test_stream_logs_success_and_exception_path():
    def gen_ok():
        yield ("a", None, None)
        yield ("b", "md", "file")

    assert list(stream_logs(gen_ok())) == [("a", None, None), ("a\nb", "md", "file")]

    def gen_fail():
        yield ("start", None, None)
        raise RuntimeError("x")

    out = list(stream_logs(gen_fail()))
    assert out[0] == ("start", None, None)
    assert "start" in out[-1][0]
    assert "❌ Unexpected error" in out[-1][0]


def test_safe_log_error_redacts_keywords():
    msg = safe_log_error(Exception("token=abc123 and password=xyz"), "ctx")
    assert "ctx: Exception -" in msg
    assert "[REDACTED]" in msg
