<div align="center">
  <img src="defaults/recruiter.png" alt="Collock recruiter" width="260" style="border-radius: 16px;" />

  # 🎙 Collock

  **AI-powered mock interview practice — cinematic, immersive, brutally honest.**

  ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.33+-FF4B4B?logo=streamlit&logoColor=white)
  ![OpenRouter](https://img.shields.io/badge/OpenRouter-API-6366f1)

</div>

---

Collock drops you into a live mock interview with an AI recruiter. Configure your target role, pick a recruiter persona, choose a difficulty — and get grilled. Real feedback after every answer, a full session summary at the end.

## Features

- **3 recruiter personas** — Friendly Coach, Tough Realist, Technical Deep-Diver, each with a generated portrait
- **5 interview types** — General, Technical, Behavioral, Coding, Mixed
- **5 difficulty levels** — Intern → Staff, each calibrated to the right depth
- **4 OpenAI models** — from `gpt-5-nano` (fast & cheap) to `gpt-5.4-mini` (highest quality)
- **Per-answer feedback** — structured coaching after every response
- **Session summary** — AI-written performance review at the end
- **LLM debug panel** — live message stream, cost per call, prompt critique tool
- **Input sanitization** — prompt injection guard on all user inputs

## Stack

| Layer | Tech |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| LLM | [OpenRouter](https://openrouter.ai) (OpenAI-compatible) |
| Image gen | Google Gemini 2.5 Flash (via OpenRouter) |
| Styling | Custom CSS — dark cinematic glassmorphism theme |

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Create a .env file
echo "OPENROUTER_API_KEY=sk-or-..." > .env

# 3. Run
streamlit run collock.py
```

Get an API key at [openrouter.ai/keys](https://openrouter.ai/keys).

## Project structure

```
collock.py              # Main app (single-file Streamlit)
collock-styles.css      # Dark cinematic theme
defaults/
  collock_content.py    # Personas, question banks, prompts
  recruiter.png         # Default recruiter portrait
docs/
  backlog.md            # Feature backlog
  prompts.md            # Prompt engineering techniques
test/
  jailbreak_test.py     # Playwright security test suite
```

---

<div align="center">
  <sub>Built with Claude Code · Powered by OpenRouter</sub>
</div>
