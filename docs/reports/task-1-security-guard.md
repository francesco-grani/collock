# Task 1 — Security Guard Report

## What was done
Added a `sanitize_input()` helper function and applied it to the name and role fields in the setup dialog.

## Implementation details

**New constant** `INJECTION_PATTERNS` — a list of lowercase strings that indicate a prompt injection attempt:
- `"ignore previous"`, `"ignore all"`, `"forget your"`, `"you are now"`
- `"###"`, `"[inst]"`, `"[system]"`, `"system:"`, `"disregard"`
- `"pretend you"`, `"act as if"`, `"new instructions"`

**New function** `sanitize_input(text, max_len) -> (str, str | None)`:
- Strips whitespace
- Rejects if over max length (name: 100 chars, role: 200 chars)
- Rejects if any injection pattern found (case-insensitive)
- Returns `(cleaned_text, error_message_or_None)`

**Dialog submit handler** now runs both fields through sanitize_input before accepting them. Errors are shown via `st.error()` and the dialog stays open.

## Checkpoint
Git commit: `feat: add input sanitization guard against prompt injection`
Rollback: `git revert 5061d92`
