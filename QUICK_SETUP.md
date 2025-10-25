# FinMDA-Bot Quick Setup Guide

## Prerequisites

### For Windows:
1. **Python 3.8+**: Download from [python.org](https://python.org)
2. **Node.js 16+**: Download from [nodejs.org](https://nodejs.org)
3. **Git**: Download from [git-scm.com](https://git-scm.com)

### For Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm git

# macOS (with Homebrew)
brew install python node git
```

## Quick Start (Windows)

### 1. Install Backend Dependencies
```cmd
cd TEAM--T\backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-dotenv
pip install openai langchain langchain-openai
pip install pandas numpy matplotlib plotly
pip install pymupdf openpyxl
```

### 2. Install Frontend Dependencies
```cmd
cd TEAM--T\frontend
npm install
```

### 3. Run the Application
```cmd
# Option 1: Run both services
run_all.bat

# Option 2: Run separately
# Terminal 1 (Backend)
run_backend.bat

# Terminal 2 (Frontend) 
run_frontend.bat
```

## Quick Start (Linux/Mac)

### 1. Install Dependencies
```bash
# Backend
cd TEAM--T/backend
pip3 install -r requirements.txt

# Frontend
cd TEAM--T/frontend
npm install
```

### 2. Run the Application
```bash
# Option 1: Run both services
./run_all.sh

# Option 2: Run separately
# Terminal 1 (Backend)
./run_backend.sh

# Terminal 2 (Frontend)
./run_frontend.sh
```

## Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Troubleshooting

### Common Issues:

1. **Python not found**: Make sure Python is installed and added to PATH
2. **npm not found**: Make sure Node.js is installed
3. **Port already in use**: Change ports in the run scripts
4. **Permission denied**: Run as administrator (Windows) or use sudo (Linux/Mac)

### Manual Installation:

If automated scripts fail, install dependencies manually:

```bash
# Backend (Python)
pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-dotenv openai langchain langchain-openai pandas numpy matplotlib plotly pymupdf openpyxl

# Frontend (Node.js)
npm install react react-dom react-router-dom react-query react-hot-toast react-helmet-async zustand axios recharts react-syntax-highlighter react-dropzone
```

## Environment Setup

Create `.env` files:

**backend/.env**:
```
DATABASE_URL=sqlite:///./finmda_bot.db
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=true
```

**frontend/.env**:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Features Available

✅ **Document Processing**: Upload PDF, Excel, CSV files
✅ **Chat Interface**: Natural language queries
✅ **Financial Analytics**: Ratios, trends, forecasting
✅ **Voice Assistant**: Speech-to-text and text-to-speech
✅ **FAQ System**: Common questions and answers
✅ **Multi-Agent System**: Intelligent document analysis
✅ **RAG System**: Retrieval-augmented generation

## Support

If you encounter issues:
1. Check the console output for error messages
2. Ensure all prerequisites are installed
3. Try running services individually
4. Check firewall/antivirus settings
