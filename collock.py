# =============================================================================
# Collock v1 — Cinematic Interview Experience
# =============================================================================

import os
import sys
import base64
import html as html_lib
from datetime import datetime
import requests

sys.path.insert(0, os.getcwd())

import streamlit as st
from streamlit_float import *
from openai import OpenAI
from dotenv import load_dotenv
from defaults.collock_content import PERSONAS, fallback_question, get_img_prompt

load_dotenv()
float_init(theme=True, include_unstable_primary=False)



# =============================================================================
# region PAGE CONFIG & CONSTANTS
# =============================================================================

# Loaded as base64 data URI — works offline and never expires.
with open(os.path.join(os.getcwd(), "defaults", "recruiter.png"), "rb") as _f:
    RECRUITER_IMAGE_URL = f"data:image/png;base64,{base64.b64encode(_f.read()).decode()}"

st.set_page_config(
    page_title="Collock",
    page_icon="🎙",
    layout="wide",
    initial_sidebar_state="auto",
)

# endregion

# =============================================================================
# region CSS — DARK CINEMATIC THEME
# =============================================================================

st.markdown('<style>' + open(os.path.join(os.getcwd(), 'collock-styles.css')).read() + '</style>', unsafe_allow_html=True)

# endregion


# =============================================================================
# region BACKGROUND IMAGE
# =============================================================================

st.markdown(f"""
<div class="bg-wrapper">
    <img src="{st.session_state.get('recruiter_image_url', RECRUITER_IMAGE_URL)}" alt="Recruiter" class="bg-image" />
    <div class="bg-overlay"></div>
</div>
""", unsafe_allow_html=True)

# endregion

# =============================================================================
# region SESSION STATE INITIALISATION
# =============================================================================

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

if "dlg_loading" not in st.session_state:
    st.session_state.dlg_loading = False   # True while dialog shows loading spinner

# Dedicated session state keys for dialog inputs — persists values across sidebar-triggered reruns
if "dlg_user_name" not in st.session_state:
    st.session_state.dlg_user_name = ""
if "dlg_target_role" not in st.session_state:
    st.session_state.dlg_target_role = ""
if "dlg_persona" not in st.session_state:
    st.session_state.dlg_persona = list(PERSONAS.keys())[0]
if "dlg_difficulty" not in st.session_state:
    st.session_state.dlg_difficulty = "Mid"

if "last_call_cost" not in st.session_state:
    st.session_state.last_call_cost = None

if "total_session_cost" not in st.session_state:
    st.session_state.total_session_cost = 0.0

if "app_critique" not in st.session_state:
    st.session_state.app_critique = None

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "openai/gpt-5-nano"


# endregion

# =============================================================================
# region HELPER FUNCTIONS
# =============================================================================

INJECTION_PATTERNS = [
    "ignore previous", "ignore all", "forget your", "you are now",
    "###", "[inst]", "[system]", "system:", "disregard",
    "pretend you", "act as if", "new instructions",
]

def sanitize_input(text: str, max_len: int) -> tuple[str, str | None]:
    """Return (cleaned_text, error_or_None). Blocks prompt injection attempts."""
    text = text.strip()
    if len(text) > max_len:
        return text, f"Input too long (max {max_len} characters)."
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            return text, "Input contains disallowed content. Please rephrase."
    return text, None


def add_message(role: str, response, temp: float = None, top_p: float = None) -> None:
    """Append a message dict to the conversation history in session state."""
    if isinstance(response, tuple):
        text, cost = response
    else:
        text = response
        cost = 0.0
    msg = {"role": role, "content": text, "cost": cost}
    if temp is not None:
        msg["temp"] = temp
    if top_p is not None:
        msg["top_p"] = top_p
    st.session_state.messages.append(msg)


def build_system_prompt(persona: str, role: str, difficulty: str, interview_type: str, is_summary: bool = False) -> str:
    
    persona_description = PERSONAS.get(persona, PERSONAS["The Friendly Coach"])["description"]
    role_label = role.strip() if role.strip() else "an unspecified role"

    difficulty_note = {
        "Intern":  "Keep questions foundational. Focus on learning potential, not experience.",
        "Junior":  "Focus on practical basics, real project experience, and growth mindset.",
        "Mid":     "Balance breadth and depth. Expect solid foundations and ownership.",
        "Senior":  "Probe for leadership, architectural thinking, and deep domain expertise.",
        "Staff":   "Focus on system design, cross-team strategy, and organisational impact.",
    }.get(difficulty, "Calibrate to a mid-level candidate.")

    if not is_summary:
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
            "- Do not follow-up on a previous question, just ask the next one.\n"
            "- Be concise. No long introductions or sign-offs.\n"
            "- Stay fully in character as the recruiter at all times.\n"
            "- Even if the user asks, NEVER give any answer, you are only making questions.\n"
            "- Even if the user asks, NEVER change your questions or their difficulty based on their request."
            "- Always greet the user with their name, but never greet them more than once."
            "- Do not add the next question in the reasoning, just write it directly in the output message."
        )

    else:
        return (
            f"{persona_description}\n\n"
            "The interview is now over. Be specific and constructive and write a brief session summary keeping in mind the job role ({role_label}) and difficulty level ({difficulty})."
            "Use the following structure:"
            "<structure>"
            "[1-2 sentences of overall feedback on the candidate's performance in this session]"
            "\n"
            "**Strenghts:**"
            "- Describe strength 1"
            "- Describe strength 2"
            "\n"
            "**Areas for improvement:**"
            "- Describe area 1"
            "- Describe area 2"
            "</structure>"
            "Do NOT add any further question."
            ""
            "Example summary:"
            "<example>"
            "Overall, you showed strong problem-solving skills and a good grasp of design principles, but could improve on communication and providing more detailed explanations of your design choices."
            "\n"
            "Strengths:"
            "- You demonstrated a solid understanding of user-centered design and provided thoughtful solutions to the challenges presented."
            "- Your portfolio showcased a range of projects with clear design processes and outcomes."
            "\n"
            "Areas for improvement:"
            "- In some answers, your explanations were a bit brief. Providing more detail on your design decisions and the rationale behind them would strengthen your responses."
            "- You could work on articulating your thought process more clearly during the interview to help the interviewer follow your reasoning better."
            "</example>"
        )


def get_ai_response(
    history: list,
    system_prompt: str,
    temp: float,
    top_p: float,
    interview_type: str = None,
    model_used = st.session_state.get("selected_model", "openai/gpt-5-nano"),
) -> str:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
        )
        messages = [{"role": "system", "content": system_prompt}] + history

        response = client.chat.completions.create(
            model=model_used,
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

        if not content:
            print(f"[DEBUG] get_ai_response: empty content. finish_reason={response.choices[0].finish_reason}")
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



def parse_ai_response(text) -> tuple:
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

    if isinstance(text, tuple):
        text = text[0]

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
            # Track image generation cost alongside LLM call costs
            img_cost = result.get("usage", {}).get("cost")
            if img_cost is not None:
                st.session_state.total_session_cost = (
                    st.session_state.get("total_session_cost", 0.0) + float(img_cost)
                )

            message = result["choices"][0]["message"]
            if message.get("images"):
                for image in message["images"]:
                    image_url = image["image_url"]["url"]
                    return image_url

    except Exception as e:
        print(f"Error generating recruiter image: {e}")
        return None

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

        st.markdown('<span class="debug-msg-role">🔧 system</span>', unsafe_allow_html=True)
        st.code(build_system_prompt(persona, target_role, difficulty, interview_type), language=None)
    
        st.markdown('<div class="debug-panel-header">LLM Stream</div>', unsafe_allow_html=True)
        messages = st.session_state.get("messages", [])
        if not messages:
            st.caption("No messages yet. Start an interview.")
        else:
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                cost = msg.get("cost", 0.0)
                if role == "assistant":
                    badge = "🤖 assistant"
                    temp_val = msg.get("temp")
                    top_p_val = msg.get("top_p")
                    params = ""
                    if temp_val is not None or top_p_val is not None:
                        params = (
                            f'<span class="debug-msg-params">'
                            f'temp={temp_val:.2f} · top_p={top_p_val:.2f}'
                            f'</span>'
                        )
                    st.markdown(
                        f'<div class="debug-msg debug-msg-assistant">'
                        f'<span class="debug-msg-role">{badge}{params}</span>'
                        f'<pre class="debug-msg-content">{html_lib.escape(content)}</pre>'
                        f'<span class="debug-msg-cost">{cost:.5f} €</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    badge = "👤 user"
                    st.markdown(
                        f'<div class="debug-msg debug-msg-user">'
                        f'<span class="debug-msg-role">{badge}</span>'
                        f'<pre class="debug-msg-content">{html_lib.escape(content)}</pre>'
                        f'<span class="debug-msg-cost">{cost:.5f} €</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        summary = st.session_state.get("session_summary")
        if summary:
            st.markdown(
                f'<div class="debug-msg debug-msg-system">'
                f'<span class="debug-msg-role">🔧 system · session summary</span>'
                f'<pre class="debug-msg-content">{html_lib.escape(summary)}</pre>'
                f'</div>',
                unsafe_allow_html=True,
            )

# endregion

# =============================================================================
# region SETUP DIALOG
# =============================================================================

@st.dialog("Welcome to Collock 🎙", dismissible=False)
def setup_dialog():
    # Loading state — form was submitted, slow ops running inside the dialog
    if st.session_state.dlg_loading:
        persona   = st.session_state.persona
        role      = st.session_state.target_role
        diff      = st.session_state.difficulty
        itype     = st.session_state.interview_type

        if (not st.session_state.skip_img_generation
                and st.session_state.img_generated_for_persona != persona):
            with st.spinner("Generating recruiter portrait…"):
                new_url = generate_recruiter_image(persona)
            if new_url:
                st.session_state.recruiter_image_url = new_url
            st.session_state.img_generated_for_persona = persona
        st.session_state.prev_persona = persona

        prompt = build_system_prompt(persona, role, diff, itype)
        st.session_state.started          = True
        st.session_state.interview_ended  = False
        st.session_state.start_time       = datetime.now()
        st.session_state.end_time         = None
        st.session_state.question_index   = 1
        st.session_state.interview_type   = itype
        st.session_state.active_persona   = persona
        st.session_state.active_role      = role
        st.session_state.active_difficulty = diff
        st.session_state.last_feedback    = None
        st.session_state.session_summary  = None
        st.session_state.messages         = []
        st.session_state.display_messages = []
        st.session_state.question_coding  = False
        st.session_state.last_call_cost   = None
        st.session_state.total_session_cost = 0.0

        opening_prompt = (
            f"Start a {diff.lower()} difficulty mock interview for "
            f"{role or 'an unspecified role'}. "
            f"First greet the candidate whose name is {st.session_state.user_name} "
            f"and then ask your first interview question now."
        )
        add_message("user", opening_prompt)

        with st.spinner("Your recruiter is getting ready…"):
            raw = get_ai_response(
                st.session_state.messages, prompt,
                st.session_state.temperature, st.session_state.top_p,
                interview_type=itype,
            )
        add_message("assistant", raw, temp=st.session_state.temperature, top_p=st.session_state.top_p)
        _, question = parse_ai_response(raw)
        st.session_state.current_question  = question
        st.session_state.display_messages  = [{"role": "assistant", "content": question}]
        st.session_state.dlg_loading       = False
        st.session_state.session_ready     = True
        st.rerun()
        return

    # Normal form state
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
        name, name_err = sanitize_input(st.session_state.dlg_user_name, max_len=50)
        role, role_err = sanitize_input(st.session_state.dlg_target_role, max_len=60)
        if not name:
            st.error("Please enter your name.")
        elif not role:
            st.error("Please enter the role you're applying for.")
        elif name_err:
            st.error(f"Name: {name_err}")
        elif role_err:
            st.error(f"Role: {role_err}")
        else:
            st.session_state.user_name          = name
            st.session_state.target_role        = role
            st.session_state.persona            = st.session_state.dlg_persona
            st.session_state.difficulty         = st.session_state.dlg_difficulty
            st.session_state.interview_type     = st.session_state.get("interview_type", "Mixed")
            st.session_state.skip_img_generation = st.session_state.dlg_skip_img_generation
            st.session_state.dlg_loading        = True   # Switch dialog to loading state
            st.rerun()

if not st.session_state.session_ready:
    setup_dialog()


# endregion

# =============================================================================
# region SIDEBAR — CONFIGURATION & CONTROLS
# =============================================================================

with st.sidebar:

    progress_pct = min(
    int(st.session_state.question_index / st.session_state.question_total * 100),
    100,
)
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

        settings_applied = st.form_submit_button("Apply and reset", type="primary", use_container_width=True)

    if settings_applied:
        st.session_state.target_role        = _form_target_role
        st.session_state.difficulty         = _form_difficulty
        st.session_state.persona            = _form_persona
        st.session_state.interview_type     = _form_interview_type
        st.session_state.skip_img_generation = _form_skip_image
        st.session_state.trigger_apply_reset = True
        st.rerun()


    end_clicked = st.button(
        "⏹ End",
        use_container_width=True,
        disabled=not st.session_state.started,
    )
    st.divider()

    # ----- Advanced LLM settings (collapsed) -----
    with st.expander("⚙ LLM Settings", expanded=False):
        st.caption("Adjust how the AI generates its responses.")
        _available_models = [
            "openai/gpt-5-nano",
            "openai/gpt-5.4-mini",
            "openai/gpt-5-mini",
            "openai/gpt-4.1-mini",
        ]
        st.session_state.selected_model = st.selectbox(
            "Model",
            options=_available_models,
            index=_available_models.index(st.session_state.selected_model),
            help="Model used for interview questions and feedback.",
        )
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0, max_value=1.0,
            value=st.session_state.temperature,
            step=0.05,
            help="0 = deterministic. 1.0 = highly creative / unpredictable.",
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


# endregion

# =============================================================================
# region PERSONA CHANGE
# =============================================================================

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


# endregion

# =============================================================================
# region BUTTON LOGIC
# =============================================================================

# Consume the sidebar Apply and reset flag.
apply_reset = st.session_state.get("trigger_apply_reset", False)
if apply_reset:
    del st.session_state["trigger_apply_reset"]

if apply_reset:
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
    add_message("assistant", raw, temp=st.session_state.temperature, top_p=st.session_state.top_p)
    _, question = parse_ai_response(raw)
    st.session_state.current_question = question
    st.session_state.display_messages = [{"role": "assistant", "content": question}]
    st.rerun()

# Auto-end: if all questions have been delivered, trigger the end flow immediately.
if (st.session_state.started
        and not st.session_state.interview_ended
        and st.session_state.question_index >= st.session_state.question_total):
    end_clicked = True

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
        is_summary=True,
    )
    summary_messages = st.session_state.messages + [{
        "role": "user",
        "content": (
            "The interview is now over, I just need one more thing from you: based on everything that was said in this session, write a brief performance summary for the candidate."
        ),
    }]
    st.session_state.session_summary = get_ai_response(
        summary_messages, prompt,
        0, st.session_state.top_p,
    )
    st.rerun()


# endregion

# =============================================================================
# region MAIN AREA
# =============================================================================

with st.container(key="main-wrapper", horizontal_alignment="center"):
    with st.container(key="chat", width=900):
        # region CHAT HISTORY
        for message in st.session_state.display_messages:
            if message["role"] == "assistant":
                with st.chat_message(message["role"], avatar=st.session_state.get("recruiter_image_url") if st.session_state.get("recruiter_image_url", "").startswith("http") else "🎙"):
                    st.markdown(message["content"])
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if st.session_state.pending_llm_call:
            st.session_state.pending_llm_call = False
            with st.chat_message("assistant", avatar=st.session_state.get("recruiter_image_url") if st.session_state.get("recruiter_image_url", "").startswith("http") else "🎙"):
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
            add_message("assistant", _raw, temp=st.session_state.temperature, top_p=st.session_state.top_p)
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


        # endregion

        # region SESSION SUMMARY
        if st.session_state.interview_ended and st.session_state.session_summary is not None:
            st.markdown("<br>", unsafe_allow_html=True)

            duration_str = "—"
            if st.session_state.start_time and st.session_state.end_time:
                duration_str = format_duration(
                    st.session_state.start_time,
                    st.session_state.end_time,
                )

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Questions", st.session_state.question_index)
            with m2:
                # -1 to exclude the hidden opening prompt injected as a "user" message
                user_turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
                st.metric("Answers given", max(0, user_turns - 1))
            with m3:
                st.metric("Duration", duration_str)

            safe_summary = html_lib.escape(st.session_state.session_summary)
            st.markdown(f"""
            <div class="adventure-glass summary-glass">
                <div class="summary-label">Session Summary</div>
                <p class="summary-text">{safe_summary}</p>
            </div>
            """, unsafe_allow_html=True)

            st.caption("<- Click  Apply and reset  in the sidebar to start a new session.")


        # endregion

        # region CHAT INPUT
        with st.container():
            user_answer = st.chat_input(
                "Type your response…",
                disabled=not st.session_state.started,
            )
            # Lift the chat input above the floating debug panel at the bottom.
            # The bottom value matches the collapsed expander header height (~3rem).
            float_parent(css=float_css_helper(bottom="calc(3.5rem + 15px)", z_index="99", left="auto", right="auto"))

        if user_answer:
            st.session_state.display_messages.append({"role": "user", "content": user_answer})
            add_message("user", user_answer)
            st.session_state.pending_llm_call = True
            st.rerun()

        with st.container(key="footer-wrapper", horizontal_alignment="center"):
            float_parent(css=float_css_helper(bottom="15px", z_index="100"))
            with st.expander(label="LLM Debug", key="debugPanel", width=900):
                with st.expander(label="LLM Stream"):
                    render_debug_panel()
                
                last = st.session_state.get("last_call_cost")
                total = st.session_state.get("total_session_cost", 0.0)
                c1, c2 = st.columns(2)
                c1.metric("Last call cost", f"{last:.5f} €" if last is not None else "—")
                c2.metric("Total session cost", f"{total:.5f} €")


                if st.button("🔍 Critique this app", use_container_width=True):
                    critique_meta_prompt = (
                        "You are an expert in LLM application design and prompt engineering. "
                        "Review the following system prompt used in a mock interview app and give "
                        "concise, specific feedback on: "
                        "(1) prompt clarity and effectiveness, "
                        "(2) potential security vulnerabilities, "
                        "(3) user experience gaps. "
                        "Be direct and actionable. Use bullet points.\n\n"
                        "SYSTEM PROMPT UNDER REVIEW:\n"
                        + build_system_prompt(
                            st.session_state.persona,
                            st.session_state.target_role,
                            st.session_state.difficulty,
                            st.session_state.interview_type,
                        )
                    )
                    with st.spinner("Analysing prompts…"):
                        st.session_state.app_critique = get_ai_response(
                            [], critique_meta_prompt, 0.3, 0.9, st.session_state.interview_type, "openai/gpt-5.4-mini"
                        )
                if st.session_state.app_critique:
                    with st.expander("Critique result", expanded=True):
                        st.markdown(st.session_state.app_critique)

        # endregion  (CHAT INPUT)
    # endregion  (MAIN AREA)