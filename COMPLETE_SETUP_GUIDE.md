# FinMDA-Bot Complete Setup Guide

## 🚀 Prerequisites Installation

### 1. Install Node.js (Required for Frontend)
1. Go to [https://nodejs.org](https://nodejs.org)
2. Download the **LTS version** (recommended)
3. Run the installer and follow the setup wizard
4. **Important**: Check "Add to PATH" during installation
5. Restart your command prompt/PowerShell after installation

**Verify Installation:**
```cmd
node --version
npm --version
```

### 2. Install Python (Required for Backend)
1. Go to [https://python.org](https://python.org)
2. Download **Python 3.8+** (latest version recommended)
3. **Important**: Check "Add Python to PATH" during installation
4. Install pip (usually included with Python)

**Verify Installation:**
```cmd
python --version
pip --version
```

### 3. Install Git (Optional but Recommended)
1. Go to [https://git-scm.com](https://git-scm.com)
2. Download and install Git for Windows
3. Use default settings during installation

## 🛠️ Project Setup

### Step 1: Navigate to Project Directory
```cmd
cd "C:\Users\Vishnu\Downloads\Project T\TEAM--T"
```

### Step 2: Install Backend Dependencies
```cmd
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-dotenv
pip install openai langchain langchain-openai pandas numpy matplotlib plotly
pip install pymupdf openpyxl
```

### Step 3: Install Frontend Dependencies
```cmd
cd ..\frontend
npm install
```

### Step 4: Create Environment Files

**Create `backend/.env`:**
```env
DATABASE_URL=sqlite:///./finmda_bot.db
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./chromadb
REDIS_URL=redis://localhost:6379
DEBUG=true
```

**Create `frontend/.env`:**
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## 🚀 Running the Application

### Option 1: Run Both Services (Recommended)

**Terminal 1 - Backend:**
```cmd
cd "C:\Users\Vishnu\Downloads\Project T\TEAM--T\backend"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```cmd
cd "C:\Users\Vishnu\Downloads\Project T\TEAM--T\frontend"
npm start
```

### Option 2: Using Docker (Alternative)

```cmd
cd "C:\Users\Vishnu\Downloads\Project T\TEAM--T"
docker-compose up --build
```

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

## 🔧 Troubleshooting

### Common Issues:

1. **"npm is not recognized"**
   - Node.js is not installed or not in PATH
   - Solution: Reinstall Node.js with "Add to PATH" checked

2. **"python is not recognized"**
   - Python is not installed or not in PATH
   - Solution: Reinstall Python with "Add to PATH" checked

3. **Port already in use**
   - Another application is using port 3000 or 8000
   - Solution: Kill the process or change ports

4. **Module not found errors**
   - Dependencies not installed
   - Solution: Run `pip install -r requirements.txt` and `npm install`

5. **Permission denied**
   - Run PowerShell as Administrator
   - Or use `--user` flag: `pip install --user package_name`

### Windows-Specific Solutions:

1. **Enable Long Path Support:**
   ```cmd
   # Run as Administrator
   reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
   ```

2. **PowerShell Execution Policy:**
   ```cmd
   # Run as Administrator
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## 📋 Quick Commands Summary

```cmd
# 1. Install Node.js from nodejs.org
# 2. Install Python from python.org
# 3. Restart your terminal

# 4. Navigate to project
cd "C:\Users\Vishnu\Downloads\Project T\TEAM--T"

# 5. Install backend dependencies
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart python-dotenv openai langchain langchain-openai pandas numpy matplotlib plotly pymupdf openpyxl

# 6. Install frontend dependencies
cd ..\frontend
npm install

# 7. Start backend (Terminal 1)
cd ..\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 8. Start frontend (Terminal 2)
cd ..\frontend
npm start
```

## 🎯 What You'll See

1. **Backend starts**: You'll see FastAPI server running on port 8000
2. **Frontend starts**: Browser opens automatically to http://localhost:3000
3. **API Documentation**: Visit http://localhost:8000/docs for interactive API testing

## 🚨 Important Notes

- Make sure both terminals stay open while using the application
- The frontend will automatically reload when you make changes
- The backend will reload when you make changes to Python files
- If you see any errors, check the terminal output for details

## 📞 Need Help?

If you encounter any issues:
1. Check that Node.js and Python are properly installed
2. Verify you're in the correct directories
3. Make sure no other applications are using ports 3000 or 8000
4. Check the terminal output for specific error messages
