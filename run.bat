@echo off
REM Run script for Smart Traffic Monitoring System on Windows

echo ========================================
echo Starting Traffic Monitoring System
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Set Flask variables
set FLASK_APP=app.py
set FLASK_ENV=production

echo Starting Flask server...
echo.
echo ========================================
echo Access the application at:
echo http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m flask run --host=0.0.0.0 --port=5000

pause
