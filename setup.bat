@echo off
REM Setup script for Smart Traffic Monitoring System on Windows

echo ========================================
echo Smart Traffic Monitoring System Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Creating data directories...
if not exist data mkdir data
if not exist data\jembatan_merah mkdir data\jembatan_merah
if not exist data\jl_djuanda mkdir data\jl_djuanda
if not exist data\stasiun_bogor mkdir data\stasiun_bogor

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit templates\maps.html and add your Google Maps API key
echo 2. Run: flask run
echo 3. Open http://localhost:5000 in your browser
echo.
pause
