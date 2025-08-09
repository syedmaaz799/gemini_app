from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import google.generativeai as genai
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
import hashlib
import secrets
from functools import wraps
import traceback
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-here")

# ===============================
# Database (SQLAlchemy configurable)
# ===============================

# Prefer a full DATABASE_URL if provided (e.g., from Render dashboard)
DATABASE_URL = os.getenv("DATABASE_URL")

# Backwards compatibility: if legacy MySQL env vars are provided, construct URL
if not DATABASE_URL:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")
    if db_user and db_password and db_host and db_name:
        DATABASE_URL = (
            f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        )

# Safe default for platforms without a DB (e.g., Render free web service): SQLite in /tmp
if not DATABASE_URL:
    DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:////tmp/gemini_app.db")

# Create engine with appropriate options
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String(36), primary_key=True)  # UUID4 string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    system_context = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String(36), ForeignKey("chats.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db_session():
    return SessionLocal()

# Ensure tables exist when running under a WSGI server like Gunicorn (Render)
@app.before_request
def _ensure_db_initialized():
    if not getattr(app, "_db_initialized", False):
        init_db()
        app._db_initialized = True

@app.teardown_appcontext
def _remove_db_session(exception=None):
    # Ensure scoped_session is removed per request/app context
    try:
        SessionLocal.remove()
    except Exception:
        pass


def generate_chat_title(from_text: str) -> str:
    """Generate a compact chat title based on the user's first message.
    Keeps it short and readable without calling the model.
    """
    if not from_text:
        return "New Chat"
    text = (from_text or "").strip().replace("\n", " ")
    # Remove excessive spaces
    while "  " in text:
        text = text.replace("  ", " ")
    # Trim to first sentence-ish
    sentence_end = max(text.find("?"), text.find("."), text.find("!"))
    if sentence_end != -1:
        candidate = text[: sentence_end + 1]
    else:
        candidate = text
    # Limit by words/length
    words = candidate.split()
    candidate = " ".join(words[:8])  # at most 8 words
    if len(candidate) > 45:
        candidate = candidate[:45].rstrip() + "…"
    return candidate

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please create a .env file with your API key.")

genai.configure(api_key=api_key)
# Use a widely available default model to avoid 404/permission errors
model = genai.GenerativeModel("models/gemini-2.5-flash")

# System prompt for better accuracy and image handling
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

Additionally, the user may upload images. When an image is provided, describe what you see and analyze it, referencing specific visual details. If the prompt includes both text and an image, integrate both in your answer."""

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_by_username(db, username: str):
    return db.query(User).filter_by(username=username).first()

def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode())
    return salt + hash_obj.hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    salt = hashed_password[:32]
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode())
    return hashed_password[32:] == hash_obj.hexdigest()

def serialize_chat(chat: Chat):
    return {
        "title": chat.title,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in sorted(chat.messages, key=lambda x: (x.timestamp, x.id))
        ],
        "created_at": chat.created_at.isoformat(),
        "system_context": chat.system_context or SYSTEM_PROMPT,
    }

def create_new_chat(db, user: User):
    """Create a new chat for a user"""
    chat_id = str(uuid.uuid4())
    count = db.query(Chat).filter_by(user_id=user.id).count()
    chat = Chat(id=chat_id, user_id=user.id, title=f"Chat {count + 1}", system_context=SYSTEM_PROMPT)
    db.add(chat)
    db.commit()
    return chat_id

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

@app.route('/')
def index():
    """Main page - redirect to login or chat"""
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db_session()
        user = get_user_by_username(db, username)
        if user and verify_password(password, user.password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_data'] = {"email": user.email, "created_at": user.created_at.isoformat()}
            return redirect(url_for('chat'))
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        db = get_db_session()
        if get_user_by_username(db, username):
            flash('Username already exists', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        else:
            user = User(username=username, email=email, password=hash_password(password))
            db.add(user)
            db.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    """Chat interface"""
    return render_template('chat.html')

@app.route('/api/chats')
@login_required
def get_chats():
    """Get all chats for current user"""
    db = get_db_session()
    chat_rows = (
        db.query(Chat)
        .filter_by(user_id=session['user_id'])
        .order_by(Chat.created_at.asc())
        .all()
    )
    result = {c.id: serialize_chat(c) for c in chat_rows}
    return jsonify(result)

@app.route('/api/chats', methods=['POST'])
@login_required
def create_chat():
    """Create a new chat"""
    db = get_db_session()
    user = db.query(User).get(session['user_id'])
    chat_id = create_new_chat(db, user)
    return jsonify({"chat_id": chat_id})

@app.route('/api/chats/<chat_id>')
@login_required
def get_chat(chat_id):
    """Get specific chat"""
    db = get_db_session()
    chat = db.query(Chat).filter_by(id=chat_id, user_id=session['user_id']).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    return jsonify(serialize_chat(chat))

@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
@login_required
def add_message(chat_id):
    """Add a message to a chat with enhanced context management"""
    db = get_db_session()
    chat = db.query(Chat).filter_by(id=chat_id, user_id=session['user_id']).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404

    # Accept form-data with optional image or JSON body
    user_message = ''
    uploaded_image_bytes = None
    if request.content_type and 'multipart/form-data' in request.content_type:
        user_message = (request.form.get('message') or '').strip()
        file = request.files.get('image')
        if file and file.filename:
            uploaded_image_bytes = file.read()
    else:
        data = request.get_json(silent=True) or {}
        user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Add user message
    db.add(Message(chat_id=chat.id, role="user", content=user_message))
    db.commit()

    # Build conversation context from DB
    msgs = (
        db.query(Message)
        .filter_by(chat_id=chat.id)
        .order_by(Message.timestamp.asc(), Message.id.asc())
        .all()
    )
    messages_for_context = [{"role": m.role, "content": m.content} for m in msgs]
    conversation_context = build_conversation_context(
        messages_for_context, chat.system_context or SYSTEM_PROMPT
    )
    
    # Create enhanced prompt with context
    enhanced_prompt = f"{conversation_context}\n\nUser: {user_message}\nAssistant:"
    
    # Get Gemini response with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Build request for text or image+text
            if uploaded_image_bytes:
                # Send a multimodal request
                gemini_parts = [
                    {"text": enhanced_prompt},
                    {"inline_data": {"mime_type": "image/*", "data": uploaded_image_bytes}}
                ]
                response = model.generate_content(gemini_parts)
            else:
                response = model.generate_content(enhanced_prompt)
            assistant_message = response.text
            
            # Validate response
            is_valid, validation_message = validate_response(assistant_message)
            
            if not is_valid and attempt < max_retries - 1:
                # Try again with a different approach
                fallback_prompt = f"Please provide a helpful response to: {user_message}"
                response = model.generate_content(fallback_prompt)
                assistant_message = response.text
            
            # Add assistant message
            db.add(Message(chat_id=chat.id, role="assistant", content=assistant_message))
            db.commit()

            # Auto-title: if this is the first user message and default title is used
            user_count = (
                db.query(Message)
                .filter_by(chat_id=chat.id, role="user")
                .count()
            )
            new_title = None
            if user_count == 1 and chat.title.lower().startswith("chat"):
                new_title = generate_chat_title(user_message)
                if new_title:
                    chat.title = new_title
                    db.commit()
            
            payload = {
                "user_message": user_message,
                "assistant_message": assistant_message,
                "context_length": len(conversation_context),
            }
            if new_title:
                payload["title"] = new_title
            return jsonify(payload)
            
        except Exception as e:
            if attempt == max_retries - 1:
                # Remove last user message if we failed
                last_user_msg = (
                    db.query(Message)
                    .filter_by(chat_id=chat.id, role="user")
                    .order_by(Message.timestamp.desc(), Message.id.desc())
                    .first()
                )
                if last_user_msg:
                    db.delete(last_user_msg)
                    db.commit()
                traceback.print_exc()
                return jsonify({"error": f"Failed to get response from Gemini: {str(e)}"}), 500
    
    return jsonify({"error": "Failed to get response after multiple attempts"}), 500

@app.route('/api/chats/<chat_id>/title', methods=['PUT'])
@login_required
def update_chat_title(chat_id):
    """Update chat title"""
    db = get_db_session()
    chat = db.query(Chat).filter_by(id=chat_id, user_id=session['user_id']).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    data = request.get_json()
    new_title = data.get('title', '').strip()
    if not new_title:
        return jsonify({"error": "Title cannot be empty"}), 400
    chat.title = new_title
    db.commit()
    return jsonify({"title": new_title})

@app.route('/api/chats/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete a chat"""
    db = get_db_session()
    chat = db.query(Chat).filter_by(id=chat_id, user_id=session['user_id']).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    db.delete(chat)
    db.commit()
    return jsonify({"message": "Chat deleted successfully"})

@app.route('/api/chats/<chat_id>/messages/<int:message_index>', methods=['DELETE'])
@login_required
def delete_message(chat_id, message_index):
    """Delete a specific message"""
    db = get_db_session()
    chat = db.query(Chat).filter_by(id=chat_id, user_id=session['user_id']).first()
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
    messages = (
        db.query(Message)
        .filter_by(chat_id=chat.id)
        .order_by(Message.timestamp.asc(), Message.id.asc())
        .all()
    )
    if message_index >= len(messages):
        return jsonify({"error": "Message not found"}), 404
    for m in messages[message_index:]:
        db.delete(m)
    db.commit()
    return jsonify({"message": "Message deleted successfully"})

@app.route('/api/profile')
@login_required
def get_profile():
    """Get user profile"""
    db = get_db_session()
    user = db.query(User).get(session['user_id'])
    return jsonify({
        'username': user.username,
        'email': user.email or '',
        'created_at': user.created_at.isoformat() if user.created_at else ''
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)