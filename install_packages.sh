#!/bin/bash

echo "🚀 FinMDA-Bot Package Installation Script"
echo "=========================================="

echo ""
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
else
    echo "✅ Python 3 is installed"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
else
    echo "✅ Node.js is installed"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed or not in PATH"
    echo "Please install npm (comes with Node.js)"
    exit 1
else
    echo "✅ npm is installed"
fi

echo ""
echo "📦 Installing Backend Dependencies..."
echo "====================================="

cd backend
echo "Installing Python packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    echo "Try running: pip3 install --upgrade pip"
    exit 1
else
    echo "✅ Backend dependencies installed successfully"
fi

echo ""
echo "📦 Installing Frontend Dependencies..."
echo "======================================"

cd ../frontend
echo "Installing Node.js packages..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    echo "Try running: npm install -g npm@latest"
    exit 1
else
    echo "✅ Frontend dependencies installed successfully"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "🚀 To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd TEAM--T/backend"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd TEAM--T/frontend"
echo "  npm start"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
