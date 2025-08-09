@echo off
echo 🤖 Starting Enhanced Robotic Gemini AI Chatbot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo 📝 Creating .env file from template...
    copy env_template.txt .env
    echo.
    echo ⚠️  Please edit the .env file and add your Gemini API key:
    echo    GEMINI_API_KEY=your_gemini_api_key_here
    echo    FLASK_SECRET_KEY=your-secret-key-here
    echo.
    echo 🔗 Get your API key from: https://makersuite.google.com/app/apikey
    echo.
    pause
)

REM Start the enhanced Flask application
echo 🚀 Starting Enhanced Flask Application...
echo 🌐 Open your browser and go to: http://localhost:5000
echo.
echo 💡 Features:
echo    - 🔐 User authentication (login/signup)
echo    - 🧠 Enhanced AI accuracy with context memory
echo    - 🎨 Futuristic robotic UI
echo    - 📊 Real-time context information
echo.
python app_flask.py

pause
