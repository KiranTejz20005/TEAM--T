@echo off
echo 🚀 FinMDA-Bot Package Installation Script
echo ==========================================

echo.
echo 📋 Checking prerequisites...

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python is installed
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js is installed
)

echo.
echo 📦 Installing Backend Dependencies...
echo =====================================

cd backend
echo Installing Python packages...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
) else (
    echo ✅ Backend dependencies installed successfully
)

echo.
echo 📦 Installing Frontend Dependencies...
echo =====================================

cd ..\frontend
echo Installing Node.js packages...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    echo Try running: npm install -g npm@latest
    pause
    exit /b 1
) else (
    echo ✅ Frontend dependencies installed successfully
)

echo.
echo 🎉 Installation Complete!
echo ========================
echo.
echo 🚀 To start the application:
echo.
echo Terminal 1 (Backend):
echo   cd TEAM--T\backend
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo Terminal 2 (Frontend):
echo   cd TEAM--T\frontend
echo   npm start
echo.
echo 🌐 Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
