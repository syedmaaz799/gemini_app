import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File path for saving chat history
CHAT_FILE = "saved_chats.json"

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("❌ GEMINI_API_KEY not found in environment variables. Please create a .env file with your API key.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-pro")

# Load saved chats on session start
if "all_chats" not in st.session_state:
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            st.session_state["all_chats"] = json.load(f)
    else:
        st.session_state["all_chats"] = {}

if "active_chat" not in st.session_state:
    st.session_state["active_chat"] = None

# Save chats to file
def save_chats():
    with open(CHAT_FILE, "w") as f:
        json.dump(st.session_state["all_chats"], f)

# Create new chat
def start_new_chat():
    chat_id = str(len(st.session_state["all_chats"]) + 1)
    st.session_state["all_chats"][chat_id] = {
        "title": f"Chat {chat_id}",
        "messages": []
    }
    st.session_state["active_chat"] = chat_id
    save_chats()

# Delete selected chat
def delete_chat(chat_id):
    if chat_id in st.session_state["all_chats"]:
        del st.session_state["all_chats"][chat_id]
        st.session_state["active_chat"] = None
        save_chats()
        st.experimental_rerun()

# Sidebar UI
st.sidebar.title("💬 Gemini Chatbot")

# New chat button
st.sidebar.button("➕ New Chat", on_click=start_new_chat)

# List existing chats with delete buttons
for chat_id, chat in st.session_state["all_chats"].items():
    col1, col2 = st.sidebar.columns([5, 1])
    if col1.button(chat["title"], key=f"chat_{chat_id}"):
        st.session_state["active_chat"] = chat_id
    if col2.button("❌", key=f"delete_{chat_id}", help="Delete this chat"):
        delete_chat(chat_id)

# If a chat is active
if st.session_state["active_chat"]:
    chat_id = st.session_state["active_chat"]
    chat_data = st.session_state["all_chats"][chat_id]

    # Rename chat
    with st.sidebar.expander(f"✏️ Rename '{chat_data['title']}'"):
        new_title = st.text_input(
            "Rename chat",
            value=chat_data["title"],
            key=f"rename_{chat_id}"
        )
        if new_title and new_title != chat_data["title"]:
            chat_data["title"] = new_title
            save_chats()

    # Main title
    st.title(f"🗨️ Gemini Chat: {chat_data['title']}")

    # Show message history with delete buttons
    for i, msg in enumerate(chat_data["messages"]):
        col1, col2 = st.columns([10, 1])
        with col1:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        with col2:
            if st.button("🗑️", key=f"delete_msg_{i}", help="Delete this message"):
                chat_data["messages"].pop(i)
                save_chats()
                st.experimental_rerun()

    # Chat input box
    prompt = st.chat_input("Type a message...")
    if prompt:
        # Add user message
        chat_data["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get Gemini response
        try:
            with st.chat_message("assistant"):
                with st.spinner("Gemini is thinking..."):
                    response = model.generate_content(prompt)
                    answer = response.text
                    st.markdown(answer)

            # Only save if successful
            chat_data["messages"].append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("❌ Gemini failed to respond. Please try again.")
            chat_data["messages"].pop()  # Remove last user prompt on failure

        # Save chat after exchange
        save_chats()

else:
    st.title("💬 Gemini Chatbot")
    st.write("Start a new chat from the sidebar to begin!")
