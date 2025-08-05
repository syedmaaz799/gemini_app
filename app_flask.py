from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")  # Change this in production

# File path for saving chat history
CHAT_FILE = "saved_chats.json"

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please create a .env file with your API key.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

def load_chats():
    """Load saved chats from file"""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    """Save chats to file"""
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f)

def create_new_chat():
    """Create a new chat"""
    chats = load_chats()
    chat_id = str(uuid.uuid4())
    chats[chat_id] = {
        "title": f"Chat {len(chats) + 1}",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    save_chats(chats)
    return chat_id

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    """Get all chats"""
    chats = load_chats()
    return jsonify(chats)

@app.route('/api/chats', methods=['POST'])
def create_chat():
    """Create a new chat"""
    chat_id = create_new_chat()
    return jsonify({"chat_id": chat_id})

@app.route('/api/chats/<chat_id>')
def get_chat(chat_id):
    """Get specific chat"""
    chats = load_chats()
    if chat_id in chats:
        return jsonify(chats[chat_id])
    return jsonify({"error": "Chat not found"}), 404

@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
def add_message(chat_id):
    """Add a message to a chat"""
    chats = load_chats()
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404
    
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Add user message
    chats[chat_id]["messages"].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get Gemini response
    try:
        response = model.generate_content(user_message)
        assistant_message = response.text
        
        # Add assistant message
        chats[chat_id]["messages"].append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        save_chats(chats)
        
        return jsonify({
            "user_message": user_message,
            "assistant_message": assistant_message
        })
        
    except Exception as e:
        # Remove user message on failure
        chats[chat_id]["messages"].pop()
        save_chats(chats)
        return jsonify({"error": "Failed to get response from Gemini"}), 500

@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
def update_chat_title(chat_id):
    """Update chat title"""
    chats = load_chats()
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404
    
    data = request.get_json()
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({"error": "Title cannot be empty"}), 400
    
    chats[chat_id]["title"] = new_title
    save_chats(chats)
    
    return jsonify({"title": new_title})

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat"""
    chats = load_chats()
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404
    
    del chats[chat_id]
    save_chats(chats)
    
    return jsonify({"message": "Chat deleted successfully"})

@app.route('/api/chats/<chat_id>/messages/<int:message_index>', methods=['DELETE'])
def delete_message(chat_id, message_index):
    """Delete a specific message"""
    chats = load_chats()
    if chat_id not in chats:
        return jsonify({"error": "Chat not found"}), 404
    
    if message_index >= len(chats[chat_id]["messages"]):
        return jsonify({"error": "Message not found"}), 404
    
    # Remove the message and all subsequent messages
    chats[chat_id]["messages"] = chats[chat_id]["messages"][:message_index]
    save_chats(chats)
    
    return jsonify({"message": "Message deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 