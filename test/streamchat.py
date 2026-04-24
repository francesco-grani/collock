import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

st.markdown('<style>' + open('streamchat-styles.css').read() + '</style>', unsafe_allow_html=True)


h = st.container(key="header")
with h:
    st.title("SmaLLM")
    st.write("A small language model that can answer your questions.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)



# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})



    # Send message to LLM
    response = client.chat.completions.create(
        model="openai/gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    response_message = response.choices[0].message.content

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_message)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_message})