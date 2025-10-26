@echo off
echo ========================================
echo  FinMDA-Bot - Quick Start Script
echo ========================================
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up backend...
cd backend

echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Step 3: Configuring environment...
if not exist .env (
    copy env.example .env
    echo.
    echo ========================================
    echo  IMPORTANT: Configure your API key!
    echo ========================================
    echo.
    echo 1. Get FREE Gemini API key from:
    echo    https://makersuite.google.com/app/apikey
    echo.
    echo 2. Edit backend\.env file
    echo 3. Replace "your_gemini_api_key_here" with your actual key
    echo.
    echo Press any key after you've added your API key...
    pause
)

echo.
echo Step 4: Initializing database...
python init_db.py

echo.
echo Step 5: Starting backend server...
echo Backend will run on: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python -m app.main

pause



