@echo off
echo Starting Robotic Gemini AI Chat...
echo.
echo Activating virtual environment...
call venv\Scripts\activate
echo.
echo Starting Flask application...
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app_flask.py
pause 