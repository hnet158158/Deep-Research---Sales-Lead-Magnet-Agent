# Requirements — AI Lead Magnet Generator (Gradio App)

## 1) Reality Check
Status: **PASS**.

No architectural nonsense or impossible constraints detected.

---

## 2) Intent Formalization (AAG)
- **Actor (Who):** Content marketer / business user working in web UI.
- **Action (What):** Provide topic, run research-driven generation pipeline, receive polished lead magnet in Markdown + downloadable file.
- **Goal (Why):** Produce high-quality, source-backed lead magnet quickly with transparent execution logs.

---

## 3) Scope
Build a Gradio application that generates a complete lead magnet from a user topic via Tavily research + OpenAI-compatible LLM pipeline.

In scope:
- Gradio UI with input, settings, live logs, markdown output, and file download.
- Async Python backend.
- OpenAI SDK with configurable `base_url`.
- Tavily as the fixed search provider.
- Persistent local settings storage.
- Markdown export to `outputs/lead_magnet_[YYYYMMDD_HHMMSS].md`.

Out of scope:
- Brave Search integration.
- Multi-provider routing for search.
- Parallel LLM chapter generation.

---

## 4) Hard Constraints (Must Not Be Violated)
1. **LLM calls are strictly sequential (FIFO).**
   - No concurrent LLM requests.
   - No `asyncio.gather` for LLM generation.
2. **Tavily is the only search provider.**
3. **Final stylist/editor step is always enabled.**
4. **UI must stream progress updates via `yield` to avoid perceived freeze.**
5. **Structured outputs are required for planner steps** (query list + structure JSON).

---

## 5) Configuration

### 5.1 Environment Variables (`.env`)
Required:
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `TAVILY_API_KEY`

### 5.2 UI Settings (Persistent)
A Gradio side panel/tab named **Settings** must include:
- **Words per chapter**: slider `[100..1000]`, default `300`.
- **Chapter count**: slider `[1..10]`, default `5`.
- **Temperature (Creativity)**: slider `[0.0..1.0]`, default `0.7`.

Persistence:
- Save locally to file (e.g., `config.json` or `settings.yaml`).
- Load on app startup.

---

## 6) UI Requirements (Gradio)
1. **Header**: `AI Lead Magnet Generator`.
2. **Input block**:
   - Topic textbox (`Тема лид-магнита`).
   - Button (`Сгенерировать`).
3. **Execution logs**:
   - Non-interactive text log component (`gr.Textbox(interactive=False)` or equivalent stream target).
   - Logs updated during run via `yield`.
4. **Output block**:
   - Markdown preview of final document.
   - File download component pointing to generated `.md` file.

---

## 7) Functional Pipeline
Trigger: click **Сгенерировать**.

### Step 1 — Query Builder (LLM)
Input: topic, `query_count`.
Output: strict JSON array of exactly `query_count` strings.

System prompt:
```text
Role: Search Query Refiner Agent
You refine a user's topic into highly targeted search queries for deep research.

Goal: Provide {query_count} well-crafted, distinct search queries based on the user's stated topic. These queries must be geared towards doing deep research on the subject.

Instructions:
1. Analyze User Input: Identify the exact concepts or keywords in the user's topic. Do NOT introduce tangential themes.
2. Generate Queries: Create exactly {query_count} unique search queries. Each query should include the main keywords and minor variations to preserve a narrow focus.
3. Output Format: Return a strict JSON array of strings containing the queries.

User Topic: "{topic}"
```

### Step 2 — Search (Tavily, Sequential)
Input: query list.
Behavior:
- Execute Tavily requests one by one.
- For each failed request, log error and continue.
- Abort pipeline only if **all** queries fail.
Output: aggregated research context (facts, quotes, URLs/source references).

### Step 3 — Structure Planner (LLM)
Input: research context + chapter count.
Output: strict JSON object:
- `title`
- `subtitle`
- `introduction`
- `conclusions`
- `chapters[]` with `title`, `prompt`

System prompt:
```text
Role: Research Leader and Project Planner
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
```

### Step 4 — Chapter Writer (LLM, Strict Sequential)
Input: planned chapters, research context, per-chapter word limit, temperature.
Behavior:
- Iterate chapters in `for` loop.
- One LLM request at a time (FIFO).
- Log progress: `Пишу главу i/N...`.
Output: ordered array of chapter markdown texts.

System prompt:
```text
Role: Research Assistant Writer
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
```

### Step 5 — Assembly + Final Editor + Export
Behavior:
1. Assemble draft markdown in order:
   `Title -> Subtitle -> Introduction -> Chapters -> Conclusion`.
2. Run mandatory final stylist/editor LLM pass.
3. Render final markdown in UI.
4. Save file to `outputs/lead_magnet_[YYYYMMDD_HHMMSS].md`.
5. Ensure `outputs/` exists; create automatically if missing.

Final editor system prompt:
```text
Role: Expert Editor
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
{assembled_draft_text}
```

---

## 8) Fault Tolerance Rules
1. **Search partial failure policy:**
   - `1..(N-1)` failed queries => continue with partial context.
   - `N` failed queries => stop and return recoverable error in UI.
2. **LLM failure policy:**
   - Log exact failed stage/chapter in UI logs.
   - Stop pipeline and surface explicit message.
3. **Validation failures (structured output parse):**
   - Treat as hard error for that stage.
   - Log parse issue and fail fast.

---

## 9) Non-Functional Requirements
1. **Responsiveness:** user must see ongoing progress in log stream during execution.
2. **Deterministic orchestration:** execution order is predictable and reproducible due to FIFO LLM queue.
3. **Security:** keys only from environment variables; no secrets in code/logs.
4. **Compatibility:** Python `3.10+`.

---

## 10) Acceptance Criteria
1. App starts with persisted settings loaded from local config file.
2. User can set topic + parameters and run generation from Gradio UI.
3. Logs are streamed throughout all stages (`yield` updates visible).
4. Query Builder returns exactly configured query count in strict JSON array.
5. Tavily requests are processed sequentially with graceful degradation policy.
6. Structure Planner returns valid JSON with required schema and exact chapter count.
7. Chapter generation is strictly sequential (no LLM concurrency).
8. Final editor pass always runs.
9. Final markdown is shown in UI and downloadable as file.
10. File is saved under `outputs/lead_magnet_[YYYYMMDD_HHMMSS].md` and directory auto-created.

---

## 11) Implementation Notes for Coder
- Use OpenAI-compatible client with `base_url` override.
- Implement explicit Pydantic (or equivalent) models for Step 1 and Step 3 outputs.
- Separate orchestrator, provider clients, prompt templates, and I/O utilities.
- Keep logs user-readable and stage-specific.

---

> **NEXT STEP:** Vaib2 Architect
> **COMMAND:** Switch to @vaib2-architect and say "Create Development Plan"
> **STATUS:** READY
