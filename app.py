import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# 🎨 PREMIUM CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
}

/* Chat area */
.chat-container {
    max-width: 700px;
    margin: auto;
    padding: 20px;
}

/* Title */
.title {
    text-align: center;
    font-size: 36px;
    font-weight: bold;
    color: white;
}

/* User bubble */
.user-msg {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    padding: 12px;
    border-radius: 16px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
    color: white;
    box-shadow: 0 4px 20px rgba(0,114,255,0.5);
}

/* Bot bubble */
.bot-msg {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 12px;
    border-radius: 16px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    margin-right: auto;
    color: white;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# 🧠 Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

# 📌 SIDEBAR (Chat History)
with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat"):
        if st.session_state.messages:
            st.session_state.history.append(st.session_state.messages)
        st.session_state.messages = []

    st.markdown("---")

    # Show past chats
    for i, chat in enumerate(st.session_state.history[::-1]):
        if st.button(f"Chat {len(st.session_state.history)-i}"):
            st.session_state.messages = chat

    st.markdown("---")
    st.write("⚙️ Features")
    st.write("✔ Reminders")
    st.write("✔ Calendar")
    st.write("✔ Memory")

# 🎯 MAIN UI
st.markdown('<div class="title">🤖 AI Assistant</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 💬 Input
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("🤖 Thinking..."):
        try:
            response = requests.get(API_URL, params={"q": user_input})
            result = response.json()
            bot_reply = result.get("response", "Error")

        except Exception as e:
            bot_reply = f"Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()