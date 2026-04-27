<div align="center">

# 🎙 Collock

**AI-powered mock interview practice — immersive, brutally honest.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.33+-FF4B4B?logo=streamlit&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-6366f1)

[![Live on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://collock.streamlit.app)

</div>

---

Collock drops you into a live mock interview with an AI recruiter. Configure your target role, pick a recruiter persona, choose a difficulty — and get grilled. Full session summary at the end.

## Features

- **3 recruiter personas** — Friendly Coach, Tough Realist, Technical Deep-Diver, each with a generated portrait
- **5 interview types** — General, Technical, Behavioral, Mixed
- **5 difficulty levels** — Intern → Staff, each calibrated to the right depth
- **4 OpenAI models** — from `gpt-5-nano` (fast & cheap) to `gpt-5.4-mini` (highest quality)
- **Per-answer feedback** — structured coaching after every response
- **Session summary** — AI-written performance review at the end
- **LLM debug panel** — live message stream, cost per call, prompt critique tool
- **Input sanitization** — prompt injection guard on all user inputs

## Stack

| Layer     | Tech                                                    |
| --------- | ------------------------------------------------------- |
| UI        | [Streamlit](https://streamlit.io)                       |
| LLM       | [OpenRouter](https://openrouter.ai) (OpenAI-compatible) |
| Image gen | Google Gemini 2.5 Flash (via OpenRouter)                |

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Create a .env file
echo "OPENROUTER_API_KEY=sk-or-..." > .env

# 3. Run
streamlit run collock.py
```

---

**Try it live →** [collock.streamlit.app](https://collock.streamlit.app) — deployed on Streamlit Community Cloud. No install required.
(this private repo was cloned to a [public one](https://github.com/francesco-grani/collock) in order to deploy on Streamlit)

---

## Security testing

Jailbreak testing was performed using a Playwright script that fires 9 known prompt injection attempts against a live session. **Result: 9/9 passed** — the model stayed in character on every attempt.

- Test script: [`test/jailbreak_test.py`](test/jailbreak_test.py)
- Results: [`test/jailbreak_results.csv`](test/jailbreak_results.csv)

---

<div align="center">
  <sub>Built with Claude Code · Powered by OpenRouter & Streamlit</sub>
</div>
