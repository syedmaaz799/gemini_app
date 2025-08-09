import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import hashlib
import secrets
from datetime import datetime

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

# Enhanced system prompt for better accuracy and consistency
SYSTEM_PROMPT = """You are a helpful, accurate, and intelligent AI assistant. Your responses should be:

1. **Accurate and Relevant**: Always provide correct, up-to-date information
2. **Contextual**: Maintain awareness of the conversation history
3. **Helpful**: Offer practical, actionable advice
4. **Clear**: Use simple, understandable language
5. **Professional**: Maintain a professional yet friendly tone
6. **Safe**: Avoid harmful, unethical, or dangerous content

When responding:
- If you're unsure about something, say so rather than guessing
- Provide sources when possible for factual information
- Ask clarifying questions when needed
- Be concise but thorough
- Use markdown formatting for better readability

Remember: Your goal is to be genuinely helpful while maintaining high accuracy standards."""

def build_conversation_context(messages, system_prompt):
    """Build conversation context for better memory"""
    context = f"{system_prompt}\n\n"
    
    # Add recent conversation history (last 10 messages to avoid token limits)
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    for msg in recent_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content']}\n"
    
    return context

def validate_response(response_text):
    """Basic response validation"""
    if not response_text or len(response_text.strip()) < 2:
        return False, "Response too short"
    
    # Check for common error patterns
    error_patterns = [
        "I'm sorry, I cannot",
        "I'm unable to",
        "I don't have access to",
        "I cannot provide",
        "I'm not able to"
    ]
    
    for pattern in error_patterns:
        if pattern.lower() in response_text.lower():
            return False, f"Response contains error pattern: {pattern}"
    
    return True, "Valid response"

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
        "messages": [],
        "system_context": SYSTEM_PROMPT,
        "created_at": datetime.now().isoformat()
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
st.sidebar.title("💬 Enhanced Gemini Chatbot")

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

    # Main title with context info
    st.title(f"🗨️ Enhanced Gemini Chat: {chat_data['title']}")
    
    # Show context information
    if chat_data["messages"]:
        context_length = len(build_conversation_context(
            chat_data["messages"], 
            chat_data.get("system_context", SYSTEM_PROMPT)
        ))
        st.caption(f"📊 Context: {context_length} characters | Messages: {len(chat_data['messages'])}")

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

        # Get Gemini response with enhanced context
        try:
            with st.chat_message("assistant"):
                with st.spinner("🤖 Enhanced Gemini is thinking..."):
                    # Build conversation context
                    conversation_context = build_conversation_context(
                        chat_data["messages"],
                        chat_data.get("system_context", SYSTEM_PROMPT)
                    )
                    
                    # Create enhanced prompt with context
                    enhanced_prompt = f"{conversation_context}\n\nUser: {prompt}\nAssistant:"
                    
                    # Get response with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            response = model.generate_content(enhanced_prompt)
                            answer = response.text
                            
                            # Validate response
                            is_valid, validation_message = validate_response(answer)
                            
                            if not is_valid and attempt < max_retries - 1:
                                # Try again with a different approach
                                fallback_prompt = f"Please provide a helpful response to: {prompt}"
                                response = model.generate_content(fallback_prompt)
                                answer = response.text
                            
                            st.markdown(answer)
                            break
                            
                        except Exception as e:
                            if attempt == max_retries - 1:
                                st.error(f"❌ Failed to get response after {max_retries} attempts: {str(e)}")
                                answer = "I apologize, but I encountered an error. Please try again."
                                st.markdown(answer)
                            else:
                                continue

            # Only save if successful
            chat_data["messages"].append({"role": "assistant", "content": answer})
            
            # Show context info after response
            context_length = len(conversation_context)
            st.caption(f"📊 Context used: {context_length} characters")
            
        except Exception as e:
            st.error("❌ Enhanced Gemini failed to respond. Please try again.")
            chat_data["messages"].pop()  # Remove last user prompt on failure

        # Save chat after exchange
        save_chats()

else:
    st.title("💬 Enhanced Gemini Chatbot")
    st.write("Start a new chat from the sidebar to begin!")
    
    # Show features
    st.markdown("""
    ### 🚀 Enhanced Features:
    
    **🤖 Improved AI Accuracy:**
    - Enhanced system prompts for better responses
    - Response validation and retry logic
    - Context-aware conversations
    
    **🧠 Conversational Memory:**
    - Maintains conversation history
    - Context-aware responses
    - Smart context management
    
    **📊 Better User Experience:**
    - Real-time context information
    - Enhanced error handling
    - Improved response quality
    """)
