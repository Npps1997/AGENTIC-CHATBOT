import streamlit as st
import requests

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI Chatbot Agents")
st.write("Create and interact with your AI agents!")

# --- UI Inputs ---
system_prompt = st.text_area("Define your AI Agent:", height=70, placeholder="Type your system prompt here...")
MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "meta-llama/llama-4-scout-17b-16e-instruct"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]
provider = st.radio("Select Provider:", ("Groq", "OpenAI"))
selected_model = st.selectbox("Select Model:", MODEL_NAMES_GROQ if provider=="Groq" else MODEL_NAMES_OPENAI)
allow_web_search = st.checkbox("Allow Web Search")

# --- Session state setup ---
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# --- Display existing chat history ---
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- New user input ---
user_input = st.chat_input("Type your message...")

if user_input:
    # 1. Instantly display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state["message_history"].append({"role": "user", "content": user_input})

    # 2. Compose backend payload & fetch AI reply
    API_URL = "http://backend:9999/chat"
    payload = {
        "model_name": selected_model,
        "model_provider": provider,
        "system_prompt": system_prompt,
        "messages": st.session_state["message_history"],
        "allow_search": allow_web_search
    }
    with st.spinner("AI is thinking..."):
        response = requests.post(API_URL, json=payload)
        ai_reply = (
            response.json().get("response", "Sorry, no response from agent.")
            if response.status_code == 200
            else f"Error: {response.status_code} {response.text}"
        )

    # 3. Instantly display AI reply and append to history
    with st.chat_message("assistant"):
        st.markdown(ai_reply)
    st.session_state["message_history"].append({"role": "assistant", "content": ai_reply})

# --- Optional: Reset chat button ---
if st.button("Reset Chat"):
    st.session_state["message_history"] = []
    st.rerun()
