### ✅ BASIC (Core Requirements)\

[x] Define interview prep scope (e.g. technical, behavioral, job-specific, etc.)\
[x] Choose tech stack (Streamlit or Next.js)\
[x] Set up project in VS Code / Cursor\
[x] Create OpenRouter API key\
[x] Select LLM model (gpt-5-mini / nano / full)\
[x] Build single-page app UI\
[x] Implement OpenRouter API call\
[x] Write at least 5 system prompts using different techniques:\
[x] 1. Zero-shot\
[x] 2. Few-shot\
[x] 3. Chain-of-thought\
[x] 4. Role-based persona injection\
[x] 5. Self-consistency / meta-instruction\
→ all 5 integrated in build_system_prompt() — see docs/prompts.md
[x] Write user prompt logic for interview prep\
[x] Tune at least one model parameter (temperature / top-p / etc.)\
[x] Add at least one security guard (e.g. input validation)\
→ sanitize_input() blocks prompt injection on name + role fields\
[x] Ensure app works end-to-end (user can practice interviews)

#### 🟢 EASY (Optional Improvements)\

To-do: \
[x] Add difficulty levels (easy / medium / hard questions)\
[x] Implement AI interviewer personas (strict / neutral / friendly)\
\
Nice to have:\
[ ] Generate interviewer evaluation guidelines\
[x] Get AI critique (usability, security, prompts)
→ "Critique this app" button in sidebar\
\
Extra:\
[ ] Improve prompts for specific domain (IT, finance, etc.)\
[ ] Add more security (input + system prompt validation)\
[ ] Add response modes (concise vs detailed)

### 🟡 MEDIUM (Advanced Features)

To-do:\
[x] Implement image generation feature\
[x] Read OpenRouter docs and implement 1 custom improvement\
[x] Deploy app online
→ https://collock.streamlit.app (Streamlit Community Cloud)\
[x] Add UI controls for model settings (temperature, top-p, etc.)\
[x] Show cost estimation per request (via OpenRouter pricing)\

Nice-to-have:\
[x] Allow user to select different LLMs
→ selectbox in LLM Settings expander (4 models)\
[x] Perform jailbreak testing on your app
→ test/jailbreak_test.py — 8/8 passed\
[x] Document jailbreak results in Excel
→ test/jailbreak_results.csv\

Extra:\
[ ] Implement 2 structured JSON outputs
[ ] Add job description input (RAG-style prep)

### 🔴 HARD (Stretch Goals)

To-do:\
[x] Convert app into full chatbot (multi-turn conversation)

Nice to have:\
[ ] Evaluate performance (LLM-as-a-judge or similar)

Extra:\
[ ] Deploy to cloud (AWS / Azure / Gemini)\
[ ] Use LangChain (chains or agents)\
[ ] Add vector database (avoid repeated outputs)\
[ ] Integrate open-source LLMs
