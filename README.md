# 🤖 Robotic Gemini AI Chat

A modern, animated Flask-based web interface for Google's Gemini AI chatbot with a futuristic robotic theme.

## ✨ Features

- 🤖 **Robotic Theme**: Futuristic design with animated particles and glowing effects
- 💬 **Chat Management**: Create, delete, and manage multiple chat sessions
- 🎨 **Animated Interface**: Smooth animations and visual effects
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 💾 **Persistent Storage**: Chat history is saved locally
- ⚡ **Real-time Chat**: Instant responses from Gemini AI
- 🎯 **Modern UI**: Clean, intuitive interface with robotic aesthetics

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Google Gemini API key

### Installation

1. **Clone or download the project files**

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your Gemini API key:**
   
   **Option 1: Using Environment Variables (Recommended)**
   
   Run the setup script:
   ```bash
   python setup_env.py
   ```
   
   Or manually create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```
   
   **Option 2: Direct Configuration**
   
   Edit `app_flask.py` and replace the API key:
   ```python
   genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
   ```

6. **Run the application:**
   ```bash
   python app_flask.py
   ```

7. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## 🎨 Features Overview

### Visual Design
- **Matrix-style color scheme**: Green text on dark background
- **Animated particles**: Floating background elements
- **Glowing effects**: Pulsing borders and shadows
- **Smooth transitions**: Hover effects and animations
- **Typing indicators**: Visual feedback during AI responses

### Functionality
- **Multiple chats**: Create and manage separate conversation threads
- **Chat history**: All conversations are automatically saved
- **Delete chats**: Remove unwanted conversations
- **Real-time responses**: Instant AI responses with typing indicators
- **Responsive layout**: Adapts to different screen sizes

## 📁 Project Structure

```
Simple_Gemini - Copy/
├── app_flask.py          # Main Flask application
├── requirements.txt      # Python dependencies
├── saved_chats.json     # Chat history storage
├── templates/
│   └── index.html       # Main HTML template
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables (Recommended)

The application now uses environment variables for better security by default:

1. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

2. The application automatically loads these variables. If you prefer to hardcode the API key, you can modify the code directly in the application files.

### Customization

You can customize the appearance by modifying the CSS in `templates/index.html`:

- **Colors**: Change the `#00ff41` green color to any other color
- **Animations**: Modify the CSS animations for different effects
- **Layout**: Adjust the grid layout and spacing
- **Fonts**: Change the font family from 'Courier New' to other monospace fonts

## 🛠️ API Endpoints

The Flask app provides the following REST API endpoints:

- `GET /api/chats` - Get all chats
- `POST /api/chats` - Create a new chat
- `GET /api/chats/<chat_id>` - Get specific chat
- `POST /api/chats/<chat_id>/messages` - Add message to chat
- `PUT /api/chats/<chat_id>/title` - Update chat title
- `DELETE /api/chats/<chat_id>` - Delete chat
- `DELETE /api/chats/<chat_id>/messages/<index>` - Delete specific message

## 🔒 Security Notes

- Change the default secret key in production
- Use environment variables for API keys
- Consider adding rate limiting for production use
- Implement proper session management for multi-user environments

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is valid and has proper permissions
2. **Port Already in Use**: Change the port in `app_flask.py` or kill the process using port 5000
3. **Import Errors**: Make sure all dependencies are installed in your virtual environment
4. **Chat History Not Loading**: Check if `saved_chats.json` has proper read/write permissions

### Debug Mode

For development, the app runs in debug mode by default. For production, set:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## 📱 Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for the powerful language model
- Flask framework for the web framework
- The open-source community for inspiration and tools

---

**Enjoy chatting with your robotic AI assistant! 🤖✨** 