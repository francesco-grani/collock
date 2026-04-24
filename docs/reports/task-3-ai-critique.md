# Task 3 — AI Critique Button Report

## What was done
Added a "Critique this app" button in the sidebar that sends the current system prompt to the LLM for self-review.

## Implementation details

**New session state key:** `app_critique = None` — stores the last critique text across reruns.

**Button location:** Sidebar, below the LLM Settings expander, after a divider.

**Behaviour:** On click, builds the current system prompt using the live sidebar settings (persona, role, difficulty, interview type), wraps it in a meta-prompt asking for feedback on clarity, security, and UX, then calls `get_ai_response()` at temperature 0.3 for more focused output. Result stored in `st.session_state.app_critique` and displayed in an expander.

**Also added:** `.claude/settings.json` with 3 read-only permission rules from the `/fewer-permission-prompts` skill analysis.

## Checkpoint
Git commit: `feat: add AI self-critique button in sidebar (N2)`
Rollback: `git revert a6cb149`
