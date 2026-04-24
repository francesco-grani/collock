# CLAUDE.md

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root (already gitignored):
```
OPENROUTER_API_KEY=sk-or-...
```
Get a key at https://openrouter.ai/keys

## Running the apps

```bash
# Original version — sidebar config + chat bubble UI
streamlit run Collock-stitch.py

# Cinematic rewrite — glassmorphism card + full-screen portrait background
streamlit run collock.py

# Standalone minimal chat demo
streamlit run streamchat.py
```

## Architecture

**Collock** is an AI-powered mock interview app. Users configure a session (target role, difficulty, persona, interview type) and the app conducts a live interview via an LLM.

All LLM calls go through [OpenRouter](https://openrouter.ai) using the OpenAI-compatible SDK:
```python
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)
```

This is a **single-file Streamlit app** — no routes, no separate components. Only the CSS styles are separate in a "collock-styles.css" file.

### Streamlit execution model

Streamlit re-runs the entire script top-to-bottom on every user interaction. `st.session_state` is the only way to persist values across reruns. The pattern used throughout:
```python
if "key" not in st.session_state:
    st.session_state.key = default_value
```

### AI response format

The LLM is instructed (via system prompt) to format post-answer responses as:
```
FEEDBACK: [1-2 sentences of coaching]
---
[Next interview question]
```

`parse_ai_response()` splits on `\n---\n` to separate feedback from the next question. If no separator is found (opening question), the entire text is treated as the question.

### System prompt construction

`build_system_prompt(persona, role, difficulty, interview_type)` assembles the hidden instruction string from:
- **PERSONAS** dict — shapes recruiter tone (Friendly Coach / Tough Realist / Technical Deep-Diver)
- **difficulty** — maps level (Intern → Staff) to a calibration note
- **interview_type** — General / Technical / Behavioral / Mixed / Coding

### Fallback question banks

`QUESTION_BANKS` and `CODING_TASKS` are static lists used when the API call fails, so the app never crashes silently.

### CSS injection pattern

Both apps inject large CSS blocks via `st.markdown(..., unsafe_allow_html=True)` to override Streamlit's default styling. `collock.py` additionally renders full layout sections as raw HTML strings (dialogue card, HUD panel, session summary) inserted with `st.markdown(..., unsafe_allow_html=True)`. User-supplied text passed into these HTML strings must be escaped with `html.escape()` to prevent XSS.

### Playwright UI testing

Always enable tracing when running Playwright scripts. Use this boilerplate:

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()

    # ... test actions ...

    context.tracing.stop(path="/tmp/collock_trace.zip")
    browser.close()
```

Open the trace with:
```bash
.venv/bin/playwright show-trace /tmp/collock_trace.zip
```
Or drag the zip onto https://trace.playwright.dev

### `interface/` folder

Contains the Stitch design tool artifacts:
- `stitch-prompt.md` — the design brief sent to the Stitch UI generator
- `stitch-result.html` — the HTML prototype output that `collock.py` faithfully reimplements in Streamlit
