# Skeptic Report (Simulated PRODUCTION Audit)

## Audit Context
- Requested mode: **"as if PRODUCTION"** (user override).
- Actual `CURRENT_MODE` in rules: `PROTOTYPE`.
- Applied policy baseline: Section 9 from `vaib/rules.md` as requested.

## Deadlock Check
- Rejection history for this module: **0 known prior skeptic rejections** (no prior skeptic artifacts found in repository).
- Escalation threshold (`>2`) reached: **No**.

## Findings (Sins / Technical Debt)

1. **Fragility: hardcoded runtime port in UI launch**
   - Location: `src/ui.py` (`demo.launch(... server_port=7861 ...)`)
   - Why it is debt: deployment/runtime behavior is pinned in code instead of config/env; brittle for shared environments and clashes with docs.

2. **Fragility: documentation/runtime mismatch**
   - Runtime says port `7861`, docs claim `7860`.
   - Location: `src/ui.py` and `README.md`.
   - Why it is debt: operational confusion; onboarding and smoke checks become unreliable.

3. **Fragility: critical generation knobs hardcoded in orchestrator**
   - Location: `src/orchestrator.py` (`query_count=5`, query parse expects 5, final-editor temperature `0.3`).
   - Why it is debt: behavior is frozen at code-level; cannot tune safely without code edits.

4. **Over-Engineering: duplicated tolerant JSON parsing pipelines for two schema flows**
   - Location: `src/schemas.py` in `parse_query_output` and `parse_structure_output`.
   - Why it is debt: nearly identical multi-step recovery logic (normalize/extract/repair) maintained in parallel, increasing change surface and regression risk.

## Debt Score
- Total sins: **4**
- Debt Score: **4**

## Certification Verdict
- **REJECTED** (Debt Score > 0)
- Rejection type: **CODE**

> **NEXT STEP:** Vaib4 Coder
> **COMMAND:** Switch to @vaib4-coder and say "Refactor Code per skeptic_report.md"
> **STATUS:** REJECTED (CODE)
