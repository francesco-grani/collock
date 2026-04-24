# Backlog Status & Next Steps

## What's actually done (vs. what's marked)

| Item                              | Backlog mark | Reality                                                           |
| --------------------------------- | ------------ | ----------------------------------------------------------------- |
| Difficulty levels                 | ✅           | Done — `select_slider` in sidebar                                 |
| AI interviewer personas           | `[ ]`        | **Done** — 3 personas in `defaults/collock_content.py`            |
| Image generation                  | `[ ]`        | **Done** — Gemini 2.5 Flash via OpenRouter                        |
| UI controls for model settings    | `[ ]`        | **Done** — temperature + top-p sliders in sidebar                 |
| Show cost estimation              | `[ ]`        | **Partial** — captured & shown in LLM debug panel, not in main UI |
| Multi-turn chatbot                | ✅           | Done                                                              |
| System prompt techniques (need 5) | `[ ]`        | **Partial** — only zero-shot + structured output                  |
| Security guard                    | `[ ]`        | **Minimal** — only empty-field checks; no prompt injection guard  |
| Deploy app online                 | `[ ]`        | Not done                                                          |
| LLM model selector                | `[ ]`        | Not done — hardcoded to `openai/gpt-5-nano`                       |

---

## Recommended next steps (in priority order)

### 1. System prompt techniques — BASIC requirement, highest priority

**Why**: The course requires 5 named techniques. Only zero-shot is currently used.

**How**: Expand `build_system_prompt()` in `collock.py` to weave in 4 more techniques. No new UI needed — they live inside the prompt string itself:

| Technique                           | Implementation                                                                                           |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Zero-shot                           | ✅ already done                                                                                          |
| Few-shot                            | Add 2–3 example Q&A pairs inside the system prompt for the chosen interview type                         |
| Chain-of-thought                    | Add "Think step by step before you ask your next question" instruction                                   |
| Role-based persona                  | Already partially there (persona description); make it more explicit with "You ARE a [persona]…" framing |
| Self-consistency / meta-instruction | Add "Before responding, verify your question matches the difficulty level and interview type"            |

Effort: ~1 hour, single file (`defaults/collock_content.py` + `collock.py`).

---

### 2. Security guard — BASIC requirement

**Why**: User-supplied name and role are interpolated directly into the system prompt — classic prompt injection risk.

**How**: Add a `sanitize_input(text)` helper that:

- Strips leading/trailing whitespace
- Rejects strings containing common injection patterns (e.g. `"Ignore previous instructions"`, `"You are now"`, `"###"`, `"[INST]"`)
- Caps length (e.g. 200 chars for name, 300 for role)
- Shows `st.error()` if rejected

Apply it to the name and role fields before they're interpolated into the prompt.

Effort: ~30 min, single file.

---

### 3. Deploy app online — MEDIUM requirement

**How**: Streamlit Cloud is the zero-config path — just connect the GitHub repo, set `OPENROUTER_API_KEY` as a secret, and it deploys automatically from `collock.py`. No Dockerfile needed.

Effort: ~20 min setup, no code changes.

---

## Files involved

- [collock.py](../collock.py) — security guard, prompt techniques
- [defaults/collock_content.py](../defaults/collock_content.py) — few-shot examples, CoT instructions
- [docs/backlog.md](backlog.md) — marks to update

---

## Nice-to-have plan

### N1 — EASY — Generate interviewer evaluation guidelines

**Version A (preferred):** The guidelines are authored upfront as a static base, not generated on the fly. Define a rubric per interview type (e.g. Technical → problem-solving, correctness, communication; Behavioral → STAR structure, specificity, self-awareness) stored in `defaults/collock_content.py`. The recruiter persona uses these guidelines at session start (injected into the system prompt) to score answers consistently. At end-of-session, the judge call references the same rubric explicitly.

**Version B (alternative):** After the session ends, make an extra LLM call that asks the model to reconstruct and output the scoring criteria it implicitly applied, as a markdown table (skill → score → comment). Display below the session summary card. No upfront rubric needed.

### N2 — EASY — Get AI critique (usability, security, prompts)

Have an LLM review the app's own system prompt and flag issues.
**How**: Add a one-off button in the LLM debug expander ("Critique this app") that sends the current `build_system_prompt()` output to the LLM with a meta-prompt asking for usability, security, and prompt quality feedback. Display the result in an expander.

### N3 — MEDIUM — Allow user to select different LLMs

Let users pick from a curated list of OpenRouter models.
**How**: Add a `st.selectbox` in the sidebar LLM settings expander with a short list (e.g. `gpt-5-nano`, `gpt-4.1-mini`, `claude-haiku-4-5`, `mistral-small`). Store in `st.session_state.model`. Pass it to `client.chat.completions.create()` instead of the hardcoded string.

### N4 — MEDIUM — Perform jailbreak testing + document results

**How**: Write a Playwright test script in `test/` that sends known injection prompts (e.g. "Ignore all previous instructions", "You are now DAN", `###SYSTEM:`) as user answers. Log the model's responses and export to CSV for documentation.

### N5 — HARD — Evaluate candidate performance (LLM-as-a-judge)

Score the **candidate's** answers on a rubric (ties into N1-A if rubric exists).
**How**: After `session_summary` is generated, make a second LLM call with a judge prompt that receives the full Q&A transcript and outputs a JSON score per answer (clarity, relevance, depth: 1–5). Display as metric widgets or a bar chart using `st.bar_chart()` in the summary section.

### N6 — HARD — Evaluate interviewer quality (LLM-as-a-judge, second scoring system)

Score the **LLM interviewer's** behaviour — were its questions fair, relevant, well-calibrated to difficulty, and free from bias or leading phrasing?
**How**: A separate judge call receives only the assistant messages (questions + feedback) from the session and scores them on criteria such as: relevance to the role, difficulty calibration, question clarity, absence of leading/biased phrasing, and quality of the feedback given. Output a score card displayed alongside the candidate score. This lets you compare recruiter quality across personas and models.
