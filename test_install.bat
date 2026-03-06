@echo off
REM Test script to verify Traffic Monitoring System installation

echo.
echo ================================================
echo Traffic Monitoring System - Installation Test
echo ================================================
echo.

setlocal enabledelayedexpansion

REM Test 1: Check if venv exists
echo [1/4] Checking virtual environment...
if exist venv (
    echo    ✓ Virtual environment found
) else (
    echo    ✗ Virtual environment NOT found
    echo    Run setup.bat first!
    pause
    exit /b 1
)

REM Test 2: Activate venv and check Python
echo [2/4] Checking Python and packages...
call venv\Scripts\activate.bat >nul 2>&1
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo    ✓ Python available
    for /f "tokens=*" %%i in ('pip list 2^>nul ^| find /c "flask"') do if %%i equ 0 (
        echo    ✗ Flask not installed
        echo    Run: pip install -r requirements.txt
        pause
        exit /b 1
    ) else (
        echo    ✓ Flask installed
    )
) else (
    echo    ✗ Python not found in venv
    pause
    exit /b 1
)

REM Test 3: Check required files
echo [3/4] Checking files...
set "missing=0"
if not exist app.py (
    echo    ✗ app.py missing
    set "missing=1"
)
if not exist detector.py (
    echo    ✗ detector.py missing
    set "missing=1"
)
if not exist templates\index.html (
    echo    ✗ templates/index.html missing
    set "missing=1"
)
if "!missing!" equ "0" (
    echo    ✓ All required files present
) else (
    pause
    exit /b 1
)

REM Test 4: Check data directories
echo [4/4] Checking data directories...
if exist data\jembatan_merah (
    echo    ✓ data directories exist
) else (
    echo    ! Creating data directories...
    mkdir data\jembatan_merah
    mkdir data\jl_djuanda
    mkdir data\stasiun_bogor
    echo    ✓ data directories created
)

echo.
echo ================================================
echo Installation verified successfully! ✓
echo ================================================
echo.
echo Next steps:
echo 1. Edit templates/maps.html and add Google Maps API key
echo 2. Run run.bat to start the application
echo 3. Access http://localhost:5000
echo.
pause
