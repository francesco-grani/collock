# Task 4 — LLM Model Selector Report

## What was done
Added a model dropdown in the LLM Settings expander. The selected model is now used for all API calls instead of a hardcoded string.

## Implementation details

**New session state key:** `selected_model = "openai/gpt-5-nano"` — default preserved.

**UI:** `st.selectbox("Model", ...)` added at the top of the LLM Settings expander, above the temperature slider. Available models:
- `openai/gpt-5-nano` (default — cheapest)
- `openai/gpt-4.1-mini`
- `anthropic/claude-haiku-4-5`
- `mistralai/mistral-small`

**API call:** `get_ai_response()` now uses `st.session_state.get("selected_model", "openai/gpt-5-nano")` instead of a hardcoded string. The `.get()` with fallback ensures the app doesn't crash if session state is missing (e.g. first load race condition).

## Checkpoint
Git commit: `feat: add LLM model selector in sidebar (N3)`
Rollback: `git revert 0ae20c9`
