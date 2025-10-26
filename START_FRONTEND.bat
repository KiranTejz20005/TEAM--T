@echo off
echo ========================================
echo  FinMDA-Bot - Frontend Startup
echo ========================================
echo.

cd frontend

echo Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
if not exist node_modules (
    npm install
)

echo.
echo Starting frontend...
echo Frontend will run on: http://localhost:3000
echo.
echo Make sure backend is running on http://localhost:8000
echo.
npm start

pause



