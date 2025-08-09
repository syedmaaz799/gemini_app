# 🤖 Enhanced Robotic Gemini AI Chatbot

A sophisticated Flask and Streamlit-based web interface for Google's Gemini AI chatbot with enhanced accuracy, conversational memory, and authentication system.

## 🚀 Key Features

### 🔐 Authentication System
- **Secure Login/Signup**: Complete user authentication with password hashing
- **User Profiles**: Personalized experience with user-specific chat history
- **Session Management**: Secure session handling with Flask sessions
- **Password Security**: Salted SHA-256 password hashing

### 🧠 Enhanced AI Accuracy
- **System Prompts**: Sophisticated system prompts for better response quality
- **Response Validation**: Automatic validation of AI responses
- **Retry Logic**: Intelligent retry mechanism for failed requests
- **Error Pattern Detection**: Identifies and handles common AI error patterns

### 💬 Conversational Memory
- **Context Management**: Maintains conversation history across sessions
- **Smart Context Building**: Intelligent context assembly for better responses
- **Memory Optimization**: Efficient memory usage with context limits
- **Persistent Storage**: Local JSON storage for chat history

### 🎨 Futuristic UI/UX
- **Robotic Theme**: Cyberpunk-inspired design with animated particles
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Feedback**: Live typing indicators and context information
- **Markdown Support**: Rich text formatting for AI responses

## 📁 Project Structure

```
Simple_Gemini - Copy/
├── app_flask.py          # Enhanced Flask application with authentication
├── app.py               # Enhanced Streamlit application
├── templates/
│   ├── login.html       # Login page with robotic theme
│   ├── signup.html      # Signup page with validation
│   ├── chat.html        # Enhanced chat interface
│   └── index.html       # Original chat interface
├── requirements.txt      # Python dependencies
├── env_template.txt     # Environment variables template
├── setup_env.py         # Environment setup script
├── start_app.bat        # Windows startup script
└── README.md           # This file
```

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Simple_Gemini-Copy
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file based on `env_template.txt`:
```bash
# Copy the template
cp env_template.txt .env

# Edit the .env file with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your-secret-key-here
```

### 4. Get Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

## 🚀 Running the Application

### Option 1: Flask Application (Recommended)
```bash
python app_flask.py
```
- **URL**: http://localhost:5000
- **Features**: Full authentication, user management, enhanced UI

### Option 2: Streamlit Application
```bash
streamlit run app.py
```
- **URL**: http://localhost:8501
- **Features**: Enhanced AI accuracy, conversational memory

## 🔧 Technical Improvements

### 1. Model Output Accuracy

**Problem**: Gemini AI occasionally delivers incorrect or irrelevant responses.

**Solution**: 
- **Enhanced System Prompts**: Comprehensive system prompts that guide the AI's behavior
- **Response Validation**: Automatic validation of AI responses to detect errors
- **Retry Logic**: Intelligent retry mechanism with fallback prompts
- **Error Pattern Detection**: Identifies common AI error patterns and handles them

```python
# Enhanced system prompt
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
```

### 2. Conversational Memory

**Problem**: The model doesn't retain information from earlier conversation turns.

**Solution**:
- **Context Building**: Intelligent assembly of conversation history
- **Memory Management**: Efficient handling of conversation context
- **Smart Truncation**: Keeps recent messages while avoiding token limits
- **Persistent Storage**: Local JSON storage for chat history

```python
def build_conversation_context(messages, system_prompt):
    """Build conversation context for better memory"""
    context = f"{system_prompt}\n\n"
    
    # Add recent conversation history (last 10 messages to avoid token limits)
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    for msg in recent_messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content']}\n"
    
    return context
```

### 3. Authentication System

**Problem**: No user management or security features.

**Solution**:
- **User Registration**: Secure signup with email validation
- **Password Security**: Salted SHA-256 hashing
- **Session Management**: Flask sessions for user state
- **User Isolation**: Each user has their own chat history

```python
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
```

### 4. Enhanced User Experience

**Features Added**:
- **Real-time Context Info**: Shows context length and message count
- **Typing Indicators**: Visual feedback during AI processing
- **Error Handling**: Graceful error handling with user-friendly messages
- **Responsive Design**: Works on all device sizes
- **Markdown Support**: Rich text formatting for AI responses

## 🔒 Security Features

- **Password Hashing**: Salted SHA-256 for secure password storage
- **Session Security**: Secure session management with Flask
- **Input Validation**: Server-side validation of all user inputs
- **CSRF Protection**: Built-in Flask CSRF protection
- **Secure Headers**: Proper security headers implementation

## 📊 Performance Optimizations

- **Context Optimization**: Smart truncation to avoid token limits
- **Caching**: Efficient chat history caching
- **Error Recovery**: Intelligent retry mechanisms
- **Memory Management**: Optimized context building

## 🎯 Usage Examples

### 1. Creating a New Account
1. Visit the application
2. Click "Sign up here"
3. Enter username, email, and password
4. Confirm password
5. Click "Create Account"

### 2. Starting a Conversation
1. Login to your account
2. Click "New Chat" or start typing
3. Type your message
4. The AI will respond with context-aware answers

### 3. Managing Chats
- **Rename**: Click the rename button in the sidebar
- **Delete**: Click the ❌ button next to any chat
- **Switch**: Click on any chat in the sidebar to switch

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for Flask app)
FLASK_SECRET_KEY=your-secret-key-here
```

### Customization
- **System Prompt**: Modify `SYSTEM_PROMPT` in the code
- **Context Length**: Adjust the message limit in `build_conversation_context()`
- **UI Theme**: Modify CSS in the HTML templates
- **Retry Logic**: Adjust `max_retries` in the response handling

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure your `.env` file contains the correct API key
   - Verify the API key is valid at Google AI Studio

2. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Ensure Python 3.7+ is installed

3. **Port Already in Use**
   - Change the port in the app configuration
   - Kill existing processes on the port

4. **Authentication Issues**
   - Clear browser cookies
   - Restart the application
   - Check the `users.json` file for corruption

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for the underlying AI model
- Flask and Streamlit communities for the web frameworks
- The open-source community for inspiration and tools

---

**🎉 Enjoy your enhanced robotic AI assistant! 🤖** 