# FinMDA-Bot Complete Installation Guide

## 🚀 Prerequisites

### 1. System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux Ubuntu 18.04+
- **RAM**: Minimum 8GB (16GB recommended for AI models)
- **Storage**: At least 5GB free space
- **Internet**: Required for downloading packages and AI model weights

### 2. Required Software

#### **Python 3.8+ (Required for Backend)**
- **Download**: [https://python.org](https://python.org)
- **Version**: Python 3.8 or higher (Python 3.11 recommended)
- **Important**: Check "Add Python to PATH" during installation
- **Verify**: Open command prompt and run `python --version`

#### **Node.js 16+ (Required for Frontend)**
- **Download**: [https://nodejs.org](https://nodejs.org)
- **Version**: Node.js 16 or higher (LTS version recommended)
- **Important**: npm is included with Node.js
- **Verify**: Open command prompt and run `node --version` and `npm --version`

#### **Git (Optional but Recommended)**
- **Download**: [https://git-scm.com](https://git-scm.com)
- **Purpose**: Version control and cloning repositories

## 📦 Package Installation

### **Backend Python Packages (94 packages)**

#### **Core Framework (6 packages)**
```bash
pip install fastapi==0.109.0 uvicorn==0.27.0 pydantic==2.5.3 python-multipart==0.0.6 python-dotenv==1.0.0
```

#### **Database (2 packages)**
```bash
pip install sqlalchemy==2.0.25 alembic==1.13.1
```

#### **AI/ML Libraries (7 packages)**
```bash
pip install openai==1.10.0 langchain==0.1.6 langchain-openai==0.0.5 chromadb==0.4.22 sentence-transformers==2.3.1 transformers==4.36.2 torch==2.1.2 whisper==1.1.10
```

#### **Document Processing (8 packages)**
```bash
pip install pymupdf==1.23.21 openpyxl==3.1.2 python-docx==1.1.0 camelot-py==0.11.0 tabula-py==2.8.2 pdfplumber==0.10.3 pytesseract==0.3.10 Pillow==10.1.0
```

#### **Data Processing (4 packages)**
```bash
pip install pandas==2.2.0 numpy==1.26.3 scikit-learn==1.3.2 prophet==1.1.5
```

#### **Visualization (3 packages)**
```bash
pip install plotly==5.18.0 matplotlib==3.8.2 seaborn==0.13.0
```

#### **Voice Processing (5 packages)**
```bash
pip install SpeechRecognition==3.10.0 pyttsx3==2.90 pydub==0.25.1 edge-tts==6.1.9 soundfile==0.12.1
```

#### **Web & HTTP (4 packages)**
```bash
pip install requests==2.31.0 httpx==0.26.0 beautifulsoup4==4.12.2 lxml==4.9.3
```

#### **Background Tasks (3 packages)**
```bash
pip install celery==5.3.4 redis==5.0.1 flower==2.0.1
```

#### **Storage (2 packages)**
```bash
pip install boto3==1.34.0 minio==7.2.0
```

#### **Testing (3 packages)**
```bash
pip install pytest==8.0.0 pytest-asyncio==0.23.4 pytest-cov==4.1.0
```

#### **Development Tools (3 packages)**
```bash
pip install black==23.12.1 flake8==6.1.0 mypy==1.8.0
```

#### **Security (3 packages)**
```bash
pip install cryptography==41.0.8 python-jose==3.3.0 passlib==1.7.4
```

#### **Monitoring (2 packages)**
```bash
pip install prometheus-client==0.19.0 structlog==23.2.0
```

#### **Additional Dependencies (6 packages)**
```bash
pip install python-dateutil==2.8.2 pytz==2023.3 tqdm==4.66.1 click==8.1.7 aiofiles==23.2.1
```

### **Frontend Node.js Packages (35 packages)**

#### **Core React (4 packages)**
```bash
npm install react@^18.2.0 react-dom@^18.2.0 react-scripts@5.0.1 react-router-dom@^6.8.1
```

#### **HTTP & API (1 package)**
```bash
npm install axios@^1.6.2
```

#### **File Upload (1 package)**
```bash
npm install react-dropzone@^14.2.3
```

#### **Content Display (2 packages)**
```bash
npm install react-markdown@^9.0.1 react-syntax-highlighter@^15.5.0
```

#### **Charts & Visualization (3 packages)**
```bash
npm install plotly.js@^2.27.0 react-plotly.js@^2.6.0 recharts@^2.8.0
```

#### **State Management (1 package)**
```bash
npm install zustand@^4.4.7
```

#### **Data Fetching (1 package)**
```bash
npm install react-query@^3.39.3
```

#### **UI & Notifications (2 packages)**
```bash
npm install react-hot-toast@^2.4.1 react-icons@^4.12.0
```

#### **Animations (3 packages)**
```bash
npm install framer-motion@^10.16.16 react-intersection-observer@^9.5.3 react-spring@^9.7.3
```

#### **SEO & Meta (1 package)**
```bash
npm install react-helmet-async@^1.3.0
```

#### **Utilities (4 packages)**
```bash
npm install react-use@^17.4.2 date-fns@^2.30.0 lodash@^4.17.21 classnames@^2.3.2
```

#### **Testing (3 packages)**
```bash
npm install @testing-library/jest-dom@^5.17.0 @testing-library/react@^13.4.0 @testing-library/user-event@^14.5.2
```

#### **Development Tools (11 packages)**
```bash
npm install --save-dev @types/react@^18.2.45 @types/react-dom@^18.2.18 @types/lodash@^4.14.202 @types/react-syntax-highlighter@^15.5.11 typescript@^4.9.5 tailwindcss@^3.3.6 autoprefixer@^10.4.16 postcss@^8.4.32 @tailwindcss/forms@^0.5.7 @tailwindcss/typography@^0.5.10 eslint@^8.55.0 eslint-plugin-react@^7.33.2 eslint-plugin-react-hooks@^4.6.0
```

## 🚀 Quick Installation Commands

### **Option 1: Install All Backend Packages at Once**
```bash
cd TEAM--T/backend
pip install -r requirements.txt
```

### **Option 2: Install All Frontend Packages at Once**
```bash
cd TEAM--T/frontend
npm install
```

### **Option 3: Install Everything (Both Backend & Frontend)**
```bash
# Backend
cd TEAM--T/backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## 🔧 System-Specific Installation Notes

### **Windows Users**
1. **PowerShell Execution Policy**: Run as Administrator
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Long Path Support**: Enable for deep directory structures
   ```cmd
   reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
   ```

3. **Visual C++ Redistributable**: May be required for some packages
   - Download from Microsoft website

### **macOS Users**
1. **Xcode Command Line Tools**: Required for compilation
   ```bash
   xcode-select --install
   ```

2. **Homebrew**: Recommended package manager
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

### **Linux Users**
1. **System Dependencies**: Install build tools
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3-dev python3-pip nodejs npm build-essential libpq-dev
   
   # CentOS/RHEL
   sudo yum install python3-devel python3-pip nodejs npm gcc gcc-c++ postgresql-devel
   ```

## 🐳 Docker Installation (Alternative)

If you prefer Docker:
```bash
cd TEAM--T
docker-compose up --build
```

## ✅ Verification Commands

### **Backend Verification**
```bash
cd TEAM--T/backend
python -c "import fastapi, uvicorn, openai, langchain, chromadb; print('✅ Backend packages installed successfully')"
```

### **Frontend Verification**
```bash
cd TEAM--T/frontend
npm list --depth=0
```

## 🚨 Troubleshooting

### **Common Issues & Solutions**

1. **"pip is not recognized"**
   - Solution: Reinstall Python with "Add to PATH" checked

2. **"npm is not recognized"**
   - Solution: Reinstall Node.js with "Add to PATH" checked

3. **Permission denied errors**
   - Windows: Run as Administrator
   - Linux/Mac: Use `sudo` or `--user` flag

4. **Package installation fails**
   - Update pip: `python -m pip install --upgrade pip`
   - Update npm: `npm install -g npm@latest`

5. **Memory errors during installation**
   - Install packages one by one
   - Close other applications
   - Use virtual environment

6. **Version conflicts**
   - Use virtual environment: `python -m venv venv`
   - Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)

## 📊 Package Summary

- **Backend**: 94 Python packages (~2GB)
- **Frontend**: 35 Node.js packages (~500MB)
- **Total Installation Time**: 10-30 minutes (depending on internet speed)
- **Disk Space Required**: ~3GB

## 🎯 Next Steps

After successful installation:

1. **Start Backend**: `cd TEAM--T/backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. **Start Frontend**: `cd TEAM--T/frontend && npm start`
3. **Access Application**: http://localhost:3000
4. **API Documentation**: http://localhost:8000/docs

## 📞 Support

If you encounter issues:
1. Check the error messages carefully
2. Verify Python and Node.js versions
3. Try installing packages individually
4. Use virtual environments for isolation
5. Check system requirements and available disk space
