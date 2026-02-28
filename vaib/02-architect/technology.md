# Technology Stack

## Runtime & Language
- Python: `3.10.x` (minimum `3.10+` per requirements)

## Structured Output Contract & Parsing
- Python stdlib `json` + `re`: canonical strict JSON parse + JSON block extraction from mixed text.
- Pydantic: `2.12.5` — final typed validation after normalization/coercion.
- OpenAI SDK: `2.24.0` — repair-pass call in JSON-only mode when strict parse fails twice.
- No mandatory JSON5 dependency by default: minimal JSON5-like fixes (trailing commas / single quotes) are implemented as controlled local sanitizer and executed only on fallback path.

## Core Application
- Gradio: `6.7.0` — web UI, streaming updates via generator `yield`.
- OpenAI SDK: `2.24.0` — OpenAI-compatible client with configurable `base_url`.
- Tavily Python SDK: `0.7.21` — fixed and only search provider.
- Pydantic: `2.12.5` — strict structured output models and validation.
- Python Dotenv: `1.2.1` — load environment variables from `.env`.

## Async & HTTP
- httpx: `0.28.1` — explicit transport layer for robust API calls/timeouts (if needed directly).

## Utilities
- tenacity: `9.1.4` — controlled retries for network/transient failures (non-concurrent).
- orjson: `3.11.7` — deterministic and fast JSON parsing/serialization.

## Quality & Standards
- pytest: `9.0.2` — **BLOCKED** — CVE-2025-71176 (DoS/Privilege Escalation via /tmp/pytest-of-{user}). **Alternative:** Use `pytest >= 9.1.0` when available, or set `PYTEST_DEBUG_TEMPROOT` to secure custom temp directory.
- ruff: `0.15.4` — lint/format checks.
- mypy: `1.19.1` — strict typing enforcement.
- radon: `6.0.1` — complexity checks from system rules.
- flake8: `7.3.0` — optional style gate (aligned with rules).
- wemake-python-styleguide: `1.6.0` — optional strict style profile.

## Persistence & Files
- Local config file: `config.json` (project root or dedicated config path).
- Generated artifacts: `outputs/lead_magnet_[YYYYMMDD_HHMMSS].md`.

## Pinning Policy
1. Use exact pinned versions above for reproducibility.
2. Do not upgrade dependencies inside implementation tasks without explicit architecture approval.
3. Any future upgrade requires separate change task with compatibility validation.
