# =============================================================================
# Collock v1 — Cinematic Interview Experience
# =============================================================================

import os
import html as html_lib
from datetime import datetime
import json
import requests

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from collock_content import PERSONAS, QUESTION_BANKS, CODING_TASKS, fallback_question, get_img_prompt

load_dotenv()


# =============================================================================
# PAGE CONFIG & CONSTANTS
# =============================================================================

# The recruiter portrait used as the full-screen background.
# Sourced directly from the Stitch HTML export — may expire; replace freely.
RECRUITER_IMAGE_URL = (
    "https://lh3.googleusercontent.com/aida-public/"
    "AB6AXuAWpIDenUwWyzvNAKtMwOU4JM-2mklLEQq6g42Q-jQk_6tLcGlU_MBoXvGm"
    "UIvINPKC8J1cWb5prAqbSst3rls1VEISC0_B4QCqEvVcp_e34fPi2WNEIh0DrDyIw"
    "yz6CJGzc2oI3O5WWHlbDaEJTVxQ8z4X5jlHq-PZIHUFrK8hmgZyhbGnss2ZELoyU"
    "lMSBDiTU6Yn1O9dj38wMx3huThCfYUgOeUI4igMOypJIfRwiO1QUUb5kpdgWh2-Pk"
    "nsdpn8UMpIenXT58I"
)

# This must be the very first Streamlit call — sets the browser tab and layout.
# initial_sidebar_state="collapsed" hides the sidebar by default for a
# full-screen immersive feel. Users expand it via the arrow in the top-left.
st.set_page_config(
    page_title="Collock",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="auto",
)


# =============================================================================
# CSS — DARK CINEMATIC THEME
# =============================================================================
# This is a large block of CSS injected into the page via st.markdown().
# It does several things:
#   1. Imports fonts: Plus Jakarta Sans (headings), Inter (body), JetBrains Mono (code)
#   2. Hides Streamlit's default top bar, footer, and hamburger menu
#   3. Makes all Streamlit containers transparent so our background image shows
#   4. Styles sidebar, buttons, sliders, inputs, expanders to match the dark theme
#   5. Defines reusable glass panel classes (.adventure-glass, .hud-panel, .chip)
#      that we reference in the HTML blocks rendered below
#
# NOTE: this is a plain triple-quoted string (no "f" prefix), so CSS curly
# braces {} are fine here without escaping.

st.markdown('<style>' + open('collock-styles.css').read() + '</style>', unsafe_allow_html=True)



# =============================================================================
# BACKGROUND IMAGE — full-screen, fixed, darkened
# =============================================================================
# We inject a fixed <div> with z-index: -1 that sits behind all Streamlit
# content. It contains:
#   1. The recruiter portrait — darkened and faded at the bottom with a mask
#   2. A gradient overlay div (dark at bottom → transparent → semi-dark at top)
#
# Because this is an f-string, we reference RECRUITER_IMAGE_URL as {RECRUITER_IMAGE_URL}.
# The inline CSS uses style="..." format (no braces that would conflict with f-strings).

st.markdown(f"""
<div class="bg-wrapper">
    <img src="{st.session_state.get('recruiter_image_url', RECRUITER_IMAGE_URL)}" alt="Recruiter" class="bg-image" />
    <div class="bg-overlay"></div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALISATION
# =============================================================================
# Streamlit re-runs the script top-to-bottom on every user interaction.
# st.session_state persists values across those reruns.
# The pattern "if key not in st.session_state" ensures we only set the
# default value on the very first run — never on subsequent reruns.

if "started" not in st.session_state:
    st.session_state.started = False            # Is an interview currently active?

if "interview_ended" not in st.session_state:
    st.session_state.interview_ended = False    # Has the user clicked End Session?

if "question_index" not in st.session_state:
    st.session_state.question_index = 0         # How many questions have been asked

if "question_total" not in st.session_state:
    st.session_state.question_total = 10        # Total questions in a full session

if "start_time" not in st.session_state:
    st.session_state.start_time = None          # datetime when Start was clicked

if "end_time" not in st.session_state:
    st.session_state.end_time = None            # datetime when End was clicked
    # We record both so the summary can show the total session duration.
    # There is NO live timer in this version — only a duration in the summary.

if "interview_type" not in st.session_state:
    st.session_state.interview_type = "Mixed"

if "active_persona" not in st.session_state:
    st.session_state.active_persona = ""        # Locked at Start — used for the card label

if "active_role" not in st.session_state:
    st.session_state.active_role = ""

if "active_difficulty" not in st.session_state:
    st.session_state.active_difficulty = "Mid"

if "messages" not in st.session_state:
    # Full conversation history, kept for the LLM's context only — not shown in the UI
    st.session_state.messages = []

if "current_question" not in st.session_state:
    # Text displayed in the main dialogue card
    st.session_state.current_question = (
        "Open the sidebar on the left and configure your session, "
        "then click Start Interview to begin."
    )

if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None       # Coaching note shown in the tip box

if "session_summary" not in st.session_state:
    st.session_state.session_summary = None     # AI-written summary shown after End

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "top_p" not in st.session_state:
    st.session_state.top_p = 0.9

if "coding_task_index" not in st.session_state:
    st.session_state.coding_task_index = 0      # Cycles through CODING_TASKS

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []      # Messages rendered in the chat UI

if "recruiter_image_url" not in st.session_state:
    st.session_state.recruiter_image_url = RECRUITER_IMAGE_URL  # Default; replaced on persona change

if "prev_persona" not in st.session_state:
    st.session_state.prev_persona = None        # None = first load, skip generation

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "target_role" not in st.session_state:
    st.session_state.target_role = ""

if "persona" not in st.session_state:
    st.session_state.persona = list(PERSONAS.keys())[0]

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Mid"

if "session_ready" not in st.session_state:
    st.session_state.session_ready = False   # True once Start is clicked; never reverts on sidebar reruns

if "skip_img_generation" not in st.session_state:
    st.session_state.skip_img_generation = False

if "img_generated_for_persona" not in st.session_state:
    st.session_state.img_generated_for_persona = None

if "pending_llm_call" not in st.session_state:
    st.session_state.pending_llm_call = False

# Dedicated session state keys for dialog inputs — persists values across sidebar-triggered reruns
if "dlg_user_name" not in st.session_state:
    st.session_state.dlg_user_name = ""
if "dlg_target_role" not in st.session_state:
    st.session_state.dlg_target_role = ""
if "dlg_persona" not in st.session_state:
    st.session_state.dlg_persona = list(PERSONAS.keys())[0]
if "dlg_difficulty" not in st.session_state:
    st.session_state.dlg_difficulty = "Mid"

if "debug_panel_open" not in st.session_state:
    st.session_state.debug_panel_open = False

if "last_call_cost" not in st.session_state:
    st.session_state.last_call_cost = None

if "total_session_cost" not in st.session_state:
    st.session_state.total_session_cost = 0.0


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def add_message(role: str, text: str) -> None:
    """Append a message dict to the conversation history in session state."""
    st.session_state.messages.append({"role": role, "content": text})

def reset_chat():
    st.session_state.messages = []


def format_duration(start: datetime, end: datetime) -> str:
    """
    Return a human-readable duration string, e.g. '8 min 34 sec' or '45 sec'.
    Used in the session summary after the interview ends.
    """
    total_seconds = int((end - start).total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    if minutes > 0:
        return f"{minutes} min {seconds} sec"
    return f"{seconds} sec"


def render_debug_panel():
    with st.container(height=600):
        st.markdown('<div class="debug-panel-header">LLM Stream</div>', unsafe_allow_html=True)
        messages = st.session_state.get("messages", [])
        if not messages:
            st.caption("No messages yet. Start an interview.")
        else:
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                MAX_SYS = 300
                if role == "system":
                    display = content[:MAX_SYS] + f"\n[…{len(content) - MAX_SYS} chars]" if len(content) > MAX_SYS else content
                    badge = "🔧 system"
                elif role == "assistant":
                    display = content
                    badge = "🤖 assistant"
                else:
                    display = content
                    badge = "👤 user"
                st.markdown(
                    f'<div class="debug-msg debug-msg-{role}">'
                    f'<span class="debug-msg-role">{badge}</span>'
                    f'<pre class="debug-msg-content">{html_lib.escape(display)}</pre>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        st.divider()
        last = st.session_state.get("last_call_cost")
        total = st.session_state.get("total_session_cost", 0.0)
        c1, c2 = st.columns(2)
        c1.metric("Last call", f"${last:.5f}" if last is not None else "—")
        c2.metric("Session", f"${total:.5f}")


def parse_ai_response(text: str) -> tuple:
    """
    Split the LLM response into (feedback, question).

    The LLM is instructed (in the system prompt) to format post-answer responses as:

        FEEDBACK: [1-2 sentences of coaching]
        ---
        [The next interview question]

    If the separator "---" is found, we split on it and strip the "FEEDBACK:" prefix.
    If not found (e.g., the very first question), we return (None, full_text).

    Returns:
        (feedback_string or None, question_string)
    """
    if not text:
        return None, ""
    separator = "\n---\n"
    if separator in text:
        before, after = text.split(separator, 1)
        feedback = before.strip()
        # Strip the "FEEDBACK:" label if the LLM included it
        if feedback.upper().startswith("FEEDBACK:"):
            feedback = feedback[len("FEEDBACK:"):].strip()
        return feedback, after.strip()
    # No separator — the entire text is the question (first question of session)
    return None, text.strip()


def build_system_prompt(persona: str, role: str, difficulty: str, interview_type: str) -> str:
    """
    Build the hidden instruction string sent to the LLM with every API call.

    The system prompt shapes the LLM's personality, question style, and
    response formatting. It is never shown in the UI.
    """
    persona_description = PERSONAS.get(persona, PERSONAS["The Friendly Coach"])["description"]
    role_label = role.strip() if role.strip() else "an unspecified role"

    difficulty_note = {
        "Intern":  "Keep questions foundational. Focus on learning potential, not experience.",
        "Junior":  "Focus on practical basics, real project experience, and growth mindset.",
        "Mid":     "Balance breadth and depth. Expect solid foundations and ownership.",
        "Senior":  "Probe for leadership, architectural thinking, and deep domain expertise.",
        "Staff":   "Focus on system design, cross-team strategy, and organisational impact.",
    }.get(difficulty, "Calibrate to a mid-level candidate.")

    return (
        f"{persona_description}\n\n"
        f"You are conducting a mock job interview for: {role_label}.\n"
        f"Difficulty: {difficulty}. {difficulty_note}\n"
        f"Interview focus: {interview_type} questions.\n\n"
        "RESPONSE FORMAT — follow this exactly after the candidate answers:\n\n"
        "FEEDBACK: [1-2 sentences of specific, actionable coaching on their answer]\n"
        "---\n"
        "[Your next interview question — one question only, no preamble]\n\n"
        "For the opening question (no answer yet), just ask the question directly.\n\n"
        "Rules:\n"
        "- ONE question per response. Never list multiple.\n"
        "- Be concise. No long introductions or sign-offs.\n"
        "- Stay fully in character as the recruiter at all times.\n"
    )


def generate_recruiter_image(persona_name: str) -> str | None:
    """
    Call google/gemini-2.5-flash-image via OpenRouter to generate a recruiter portrait.
    Returns a URL or base64 data-URL string on success, None on any failure.
    """
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "google/gemini-2.5-flash-image",
            "messages": [
                {
                    "role": "user",
                    "content": get_img_prompt(persona_name)
                }
            ],
            "modalities": ["image", "text"]
        }
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # The generated image will be in the assistant message
        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images"):
                for image in message["images"]:
                    image_url = image["image_url"]["url"]  # Base64 data URL
                    print(f"Generated image: {image_url[:50]}...")
                    return image_url

    except Exception as e:
        print(f"Error generating recruiter image: {e}")
        return None


def get_ai_response(
    history: list,
    system_prompt: str,
    temp: float,
    top_p: float,
    interview_type: str = None,
) -> str:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
        messages = [{"role": "system", "content": system_prompt}] + history
        response = client.chat.completions.create(
            model="openai/gpt-5-nano",
            max_completion_tokens=800,
            reasoning_effort="low",
            messages=messages,
            temperature=temp,
            top_p=top_p,
        )
        content = response.choices[0].message.content

        try:
            call_cost = response.usage.model_extra.get("cost") if response.usage.model_extra else None
            if call_cost is not None:
                st.session_state.last_call_cost = float(call_cost)
                st.session_state.total_session_cost = (
                    st.session_state.get("total_session_cost", 0.0) + float(call_cost)
                )
            else:
                st.session_state.last_call_cost = None
        except Exception:
            st.session_state.last_call_cost = None
        print(f"Cost: {st.session_state.last_call_cost}")
        print(f"Reasoning: {response.choices[0].message.reasoning}")

        if content is None:
            # Log the full response to the terminal for debugging
            print("[DEBUG] get_ai_response: content is None")
            print(f"[DEBUG] finish_reason: {response.choices[0].finish_reason}")
            print(f"[DEBUG] full response: {response}")
            if interview_type:
                return fallback_question(interview_type)
            return "⚠ The model returned an empty response. Please try again."
        return content

    except Exception as error:
        err = str(error)
        if "401" in err or "authentication" in err.lower():
            return "API key error — check OPENROUTER_API_KEY in your .env file."
        if "429" in err or "rate limit" in err.lower():
            return "Rate limit reached. Please wait a moment and try again."
        if interview_type:
            return fallback_question(interview_type)
        return f"Connection error: {err}"


# =============================================================================
# SETUP DIALOG — shown at startup and after Reset
# =============================================================================

@st.dialog("Welcome to Collock 🎙", dismissible=False)
def setup_dialog():
    st.markdown(
        "Set up your interview session below, then hit **Start** — your AI recruiter is ready."
    )

    _persona_options = list(PERSONAS.keys())

    with st.form("setup_form"):
        st.text_input("Your name", placeholder="e.g. Alex", key="dlg_user_name")
        st.text_input(
            "Role you're applying for",
            placeholder="e.g. Senior Product Designer",
            key="dlg_target_role",
        )
        st.selectbox("Recruiter style", options=_persona_options, key="dlg_persona")
        st.select_slider(
            "Difficulty level",
            options=["Intern", "Junior", "Mid", "Senior", "Staff"],
            key="dlg_difficulty",
        )
        
        st.checkbox("Skip image generation", key="dlg_skip_img_generation")

        
        submitted = st.form_submit_button(
            "▶ Start Interview", type="primary", use_container_width=True
        )

    if submitted:
        if not st.session_state.dlg_user_name.strip():
            st.error("Please enter your name.")
        
        elif not st.session_state.dlg_target_role.strip():
            st.error("Please enter the role you're applying for.")
        else:
            st.session_state.user_name         = st.session_state.dlg_user_name
            st.session_state.target_role       = st.session_state.dlg_target_role
            st.session_state.persona           = st.session_state.dlg_persona
            st.session_state.difficulty        = st.session_state.dlg_difficulty
            st.session_state.skip_img_generation = st.session_state.dlg_skip_img_generation
            st.session_state.session_ready     = True
            st.session_state.pending_start     = True
            st.rerun()  # forces full app rerun — closes dialog, then pending_start handler fires

if not st.session_state.session_ready:
    setup_dialog()

# Convert pending_start → trigger_start in a separate quick rerun so the dialog
# is fully dismissed before any slow operation (image gen, LLM call) begins.
if st.session_state.get("pending_start"):
    del st.session_state["pending_start"]
    st.session_state.trigger_start = True
    st.rerun()


# =============================================================================
# SIDEBAR — CONFIGURATION & CONTROLS
# =============================================================================
# The sidebar is collapsed by default. Users open it with the arrow button
# in the top-left corner of the screen.

with st.sidebar:
    # Brand heading
    st.header("**Settings**")

    # ----- Interview settings form (changes only apply when Apply is clicked) -----
    _persona_options = list(PERSONAS.keys())
    _interview_type_options = ["Mixed", "General", "Technical", "Behavioral"]

    with st.form("sidebar_settings"):
        _form_target_role = st.text_input(
            "Target role",
            value=st.session_state.target_role,
            placeholder="e.g. Senior UX Designer",
        )
        _form_difficulty = st.select_slider(
            "Difficulty",
            options=["Intern", "Junior", "Mid", "Senior", "Staff"],
            value=st.session_state.difficulty,
        )
        _form_persona = st.selectbox(
            "Recruiter persona",
            options=_persona_options,
            index=_persona_options.index(st.session_state.persona),
        )
        _form_interview_type = st.selectbox(
            "Interview type",
            options=_interview_type_options,
            index=_interview_type_options.index(st.session_state.interview_type),
        )

        _form_skip_image = st.checkbox(
            "Skip image generation"
            )

        settings_applied = st.form_submit_button("Apply and reset", use_container_width=True)

    if settings_applied:
        st.session_state.target_role   = _form_target_role
        st.session_state.difficulty    = _form_difficulty
        st.session_state.persona       = _form_persona
        st.session_state.interview_type = _form_interview_type
        st.session_state.skip_img_generation = _form_skip_image
        reset_chat()

    st.divider()

    # ----- Session flow buttons (outside form — instant action) -----
    col_a, col_b = st.columns(2)
    with col_a:
        next_clicked = st.button(
            "→ Next Q",
            use_container_width=True,
            disabled=not st.session_state.started,
        )
    with col_b:
        end_clicked = st.button(
            "⏹ End",
            use_container_width=True,
            disabled=not st.session_state.started,
        )

    reset_clicked = st.button("↺ Reset", use_container_width=True)
    start_clicked = False  # Start is handled by the setup dialog only

    st.divider()

    # ----- Advanced LLM settings (collapsed) -----
    with st.expander("⚙ LLM Settings", expanded=False):
        st.caption("Adjust how the AI generates its responses.")
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.5,
            value=st.session_state.temperature,
            step=0.05,
            help="0 = deterministic. 1.5 = highly creative / unpredictable.",
        )
        st.session_state.top_p = st.slider(
            "Top-p",
            min_value=0.0, max_value=1.0,
            value=st.session_state.top_p,
            step=0.05,
            help="Limits token choices to the top-p probability mass.",
        )


# Use only committed (session-state) values from here on — form inputs are display-only
# until the sidebar "Apply settings" button is clicked.
persona       = st.session_state.persona
target_role   = st.session_state.target_role
difficulty    = st.session_state.difficulty
interview_type = st.session_state.interview_type


# =============================================================================
# PERSONA CHANGE — generate recruiter portrait when the user picks a new persona
# =============================================================================
# prev_persona is None only on the very first load (skip generation then).
# On every subsequent persona change, call Gemini image generation and rerun
# so the new portrait appears in the background before the interview starts.

if persona != st.session_state.prev_persona:
    st.session_state.persona = persona          # keep session state in sync so sidebar doesn't revert
    if st.session_state.prev_persona is not None and not st.session_state.skip_img_generation:
        with st.spinner("Generating recruiter portrait…"):
            new_url = generate_recruiter_image(persona)
        if new_url:
            st.session_state.recruiter_image_url = new_url
        st.session_state.img_generated_for_persona = persona
    st.session_state.prev_persona = persona
    st.rerun()


# =============================================================================
# BUTTON LOGIC
# =============================================================================

# Consume the one-shot flag written by the setup dialog's Start button.
start_from_modal = st.session_state.get("trigger_start", False)
if start_from_modal:
    del st.session_state["trigger_start"]

if start_clicked or start_from_modal:
    # Phase 1 — generate portrait if not already done for this persona
    if (
        not st.session_state.skip_img_generation
        and st.session_state.img_generated_for_persona != persona
    ):
        with st.spinner("Generating your recruiter portrait…"):
            new_url = generate_recruiter_image(persona)
        if new_url:
            st.session_state.recruiter_image_url = new_url
        st.session_state.img_generated_for_persona = persona

    prompt = build_system_prompt(persona, target_role, difficulty, interview_type)

    st.session_state.started = True
    st.session_state.interview_ended = False
    st.session_state.start_time = datetime.now()
    st.session_state.end_time = None
    st.session_state.question_index = 1
    st.session_state.interview_type = interview_type
    st.session_state.active_persona = persona
    st.session_state.active_role = target_role
    st.session_state.active_difficulty = difficulty
    st.session_state.last_feedback = None
    st.session_state.session_summary = None
    st.session_state.messages = []
    st.session_state.question_coding = False
    st.session_state.last_call_cost = None
    st.session_state.total_session_cost = 0.0

    opening_prompt = (
        f"Start a {difficulty.lower()} difficulty mock interview for "
        f"{target_role or 'an unspecified role'}. "
        f"First greet the candidate whose name is {st.session_state.user_name} and then ask your first interview question now."
    )
    add_message("user", opening_prompt)

    # Phase 2 — fetch the first question (always shows a spinner)
    with st.spinner("Your recruiter is getting ready…"):
        raw = get_ai_response(
            st.session_state.messages, prompt,
            st.session_state.temperature, st.session_state.top_p,
            interview_type=interview_type,
        )
    add_message("assistant", raw)
    _, question = parse_ai_response(raw)
    st.session_state.current_question = question
    st.session_state.display_messages = [{"role": "assistant", "content": question}]
    st.rerun()

if next_clicked and st.session_state.started:
    prompt = build_system_prompt(
        st.session_state.active_persona,
        st.session_state.active_role,
        st.session_state.active_difficulty,
        st.session_state.interview_type,
    )
    add_message("user", "Please ask the next question.")
    raw = get_ai_response(
        st.session_state.messages, prompt,
        st.session_state.temperature, st.session_state.top_p,
        interview_type=st.session_state.interview_type,
    )
    add_message("assistant", raw)
    feedback, question = parse_ai_response(raw)
    if feedback:
        st.session_state.last_feedback = feedback
    st.session_state.current_question = question
    st.session_state.display_messages.append({"role": "assistant", "content": question})
    st.session_state.question_index = min(
        st.session_state.question_index + 1,
        st.session_state.question_total,
    )
    st.rerun()

if end_clicked and st.session_state.started:
    st.session_state.started = False
    st.session_state.interview_ended = True
    st.session_state.end_time = datetime.now()      # Record end time for duration calc
    st.session_state.last_feedback = None
    st.session_state.current_question = "Session complete. See your summary below."

    # Ask the model for a session summary based on the full conversation
    prompt = build_system_prompt(
        st.session_state.active_persona,
        st.session_state.active_role,
        st.session_state.active_difficulty,
        st.session_state.interview_type,
    )
    summary_messages = st.session_state.messages + [{
        "role": "user",
        "content": (
            "The interview is now over. Write a brief session summary (3-5 sentences): "
            "overall impression, 2 strengths, 2 areas to improve. Be specific and constructive."
        ),
    }]
    st.session_state.session_summary = get_ai_response(
        summary_messages, prompt,
        st.session_state.temperature, st.session_state.top_p,
    )
    st.rerun()

if reset_clicked:
    st.session_state.started = False
    st.session_state.interview_ended = False
    st.session_state.question_index = 0
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.messages = []
    st.session_state.display_messages = []
    st.session_state.current_question = ""
    st.session_state.last_feedback = None
    st.session_state.session_summary = None
    st.session_state.coding_task_index = 0
    st.session_state.session_ready = False
    st.session_state.img_generated_for_persona = None
    st.session_state.last_call_cost = None
    st.session_state.total_session_cost = 0.0
    st.rerun()


# =============================================================================
# MAIN AREA — TOP HUD (brand pill + progress card)
# =============================================================================
# Rendered as raw HTML so we can match the exact style from the HTML export:
# a translucent brand pill on the left and a HUD progress card on the right.
# We use an f-string here so Python can inject the live progress values.
# Inline styles avoid CSS-brace conflicts with f-strings.

progress_pct = min(
    int(st.session_state.question_index / st.session_state.question_total * 100),
    100,
)

hud_col, panel_col = st.columns([3, 1])

with hud_col:
    st.markdown(f"""
<div class="hud-top-bar">
    <div class="hud-top-right">
        <div class="brand-pill">
            <span class="brand-pill-icon">🎙</span>
            <span class="brand-pill-name">Collock</span>
        </div>
        <div class="hud-panel progress-card">
            <div class="progress-header">
                <span class="progress-label">Progress</span>
                <span class="progress-count">{st.session_state.question_index} / {st.session_state.question_total}</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{progress_pct}%;"></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with panel_col:
    toggle_label = "✕ Close debug" if st.session_state.debug_panel_open else "🔍 LLM debug"
    if st.button(toggle_label, key="debug_toggle", use_container_width=True):
        st.session_state.debug_panel_open = not st.session_state.debug_panel_open
        st.rerun()
    if st.session_state.debug_panel_open:
        render_debug_panel()


# =============================================================================
# MAIN AREA — CHAT HISTORY
# =============================================================================
# Mirrors the streamchat.py pattern: loop over display_messages and render
# each with st.chat_message() so Streamlit handles role avatars and bubbles.
# display_messages holds only parsed, user-visible content — the raw API
# history (with hidden prompts and FEEDBACK: prefixes) stays in st.session_state.messages.

for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# If a user answer was just submitted, the user message is already visible above.
# Now run the LLM call with a spinner inside the next assistant bubble, then rerun
# to replace the spinner with the real answer.
if st.session_state.pending_llm_call:
    st.session_state.pending_llm_call = False
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            _prompt = build_system_prompt(
                st.session_state.active_persona,
                st.session_state.active_role,
                st.session_state.active_difficulty,
                st.session_state.interview_type,
            )
            _raw = get_ai_response(
                st.session_state.messages, _prompt,
                st.session_state.temperature, st.session_state.top_p,
                interview_type=st.session_state.interview_type,
            )
    add_message("assistant", _raw)
    _feedback, _question = parse_ai_response(_raw)
    if _feedback:
        st.session_state.last_feedback = _feedback
    st.session_state.current_question = _question
    st.session_state.display_messages.append({"role": "assistant", "content": _question})
    st.session_state.question_index = min(
        st.session_state.question_index + 1,
        st.session_state.question_total,
    )
    st.rerun()


# =============================================================================
# MAIN AREA — CODING TASK EXPANDER
# =============================================================================
# Only rendered during an active interview. Collapsed by default so it stays
# out of the way until the recruiter assigns a coding exercise.

if st.session_state.started and st.session_state.question_coding == True:
    task_idx = st.session_state.coding_task_index % len(CODING_TASKS)
    task = CODING_TASKS[task_idx]

    with st.expander(f"💻  Coding Task: {task['title']}", expanded=False):
        # Language and difficulty chips
        st.markdown(
            f"<span class='chip'>{task['language']}</span>"
            f"<span class='chip'>{task['difficulty']}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**Task:** {task['description']}")
        st.code(task["starter_code"], language="python")

        solution = st.text_area(
            "Your solution",
            height=140,
            placeholder="Write your Python code here…",
            key=f"solution_{task_idx}",   # Unique key prevents state collisions across tasks
        )
        if st.button("Submit solution", key=f"submit_{task_idx}", type="primary"):
            if solution.strip():
                code_msg = f"Here is my solution for '{task['title']}':\n```python\n{solution}\n```"
                add_message("user", code_msg)
                st.session_state.display_messages.append({"role": "user", "content": code_msg})
                prompt = build_system_prompt(
                    st.session_state.active_persona,
                    st.session_state.active_role,
                    st.session_state.active_difficulty,
                    st.session_state.interview_type,
                )
                raw = get_ai_response(
                    st.session_state.messages, prompt,
                    st.session_state.temperature, st.session_state.top_p,
                    interview_type=st.session_state.interview_type,
                )
                add_message("assistant", raw)
                feedback, question = parse_ai_response(raw)
                if feedback:
                    st.session_state.last_feedback = feedback
                st.session_state.current_question = question
                st.session_state.display_messages.append({"role": "assistant", "content": question})
                st.session_state.coding_task_index += 1
                st.rerun()
            else:
                st.warning("Write a solution before submitting.")


# =============================================================================
# MAIN AREA — SESSION SUMMARY
# =============================================================================
# Shown only after the user clicks End Session. Displays stats (questions
# answered, answers given, duration) and an AI-generated performance summary.

if st.session_state.interview_ended and st.session_state.session_summary:
    st.markdown("<br>", unsafe_allow_html=True)

    # Calculate session duration from the recorded start and end datetimes
    duration_str = "—"
    if st.session_state.start_time and st.session_state.end_time:
        duration_str = format_duration(
            st.session_state.start_time,
            st.session_state.end_time,
        )

    # Stats row using Streamlit metric widgets
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Questions", st.session_state.question_index)
    with m2:
        # Subtract 1 for the hidden opening "Start" prompt we injected
        user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
        st.metric("Answers given", max(0, user_turns - 1))
    with m3:
        st.metric("Duration", duration_str)

    # AI-written summary in a glass panel with an indigo tint
    safe_summary = html_lib.escape(st.session_state.session_summary)
    st.markdown(f"""
    <div class="adventure-glass summary-glass">
        <div class="summary-label">Session Summary</div>
        <p class="summary-text">{safe_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Click  ↺ Reset  in the sidebar to start a new session.")


# =============================================================================
# CHAT INPUT — answer submission, pinned to the bottom of the page
# =============================================================================
# st.chat_input is a special Streamlit widget that always renders at the very
# bottom of the viewport. It's disabled when no interview is running.
# When the user submits an answer:
#   1. Add it to the message history
#   2. Call the AI for feedback + next question
#   3. Parse the response into (feedback, question)
#   4. Update session state and trigger a page rerun

user_answer = st.chat_input(
    "Type your response…",
    disabled=not st.session_state.started,
)

if user_answer:
    st.session_state.display_messages.append({"role": "user", "content": user_answer})
    add_message("user", user_answer)
    st.session_state.pending_llm_call = True
    st.rerun()
