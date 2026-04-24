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