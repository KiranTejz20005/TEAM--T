# FinMDA-Bot - Complete Setup Guide

## 🚀 Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

1. **Start Backend:**
   ```
   Double-click: START_HERE.bat
   ```
   - This will install dependencies and start the backend
   - Backend runs on: http://localhost:8000

2. **Start Frontend (in new terminal):**
   ```
   Double-click: START_FRONTEND.bat
   ```
   - Frontend runs on: http://localhost:3000

3. **Get API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key
   - Edit `backend/.env` file
   - Replace `your_gemini_api_key_here` with your key

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy env.example .env
# Edit .env and add your GEMINI_API_KEY

# Initialize database
python init_db.py

# Start server
python -m app.main
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🔑 Getting Your FREE Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Paste it in `backend/.env`:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

**Note:** Gemini API is FREE with generous limits:
- 60 requests per minute
- 1 million tokens per minute
- Perfect for development and demos!

## 📝 Usage

### 1. Upload Documents

- Navigate to **Documents** page
- Click "Upload Document"
- Select PDF, Excel, or CSV file
- Wait for processing to complete

### 2. Chat with Your Data

- Go to **Chat** page
- Type questions like:
  - "What was the revenue in Q3?"
  - "Calculate the profit margin"
  - "Generate an MD&A report"
  - "Show me the year-over-year growth"

### 3. Generate MD&A Reports

```
Upload your financial statement, then ask:
"Generate a complete MD&A report for Q3 2024"
```

The system will automatically:
- Extract financial data
- Calculate KPIs and ratios
- Compute YoY/QoQ changes
- Generate sectioned narrative
- Provide citations

## 🧪 Testing the System

### Test 1: Health Check

```bash
# Visit in browser or use curl
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-..."
}
```

### Test 2: Chat API

```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is financial analysis?"}'
```

### Test 3: Document Upload

1. Go to http://localhost:3000/documents
2. Upload a sample financial PDF
3. Check that it appears in the list
4. Try asking questions about it in Chat

## 🐛 Troubleshooting

### Backend Issues

**Error: "ModuleNotFoundError"**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**Error: "API key not configured"**
```bash
# Check .env file exists and has valid key
cd backend
type .env
# Should show: GEMINI_API_KEY=your_key_here
```

**Error: "Port 8000 already in use"**
```bash
# Kill existing process or change port in main.py
# Line 88: port=8001
```

### Frontend Issues

**Error: "npm not found"**
- Install Node.js from: https://nodejs.org/

**Error: "Module not found"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error: "Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check CORS settings in backend/.env

### Common Issues

**Slow responses:**
- First request is always slower (model loading)
- Subsequent requests are faster
- Check your internet connection (API calls to Gemini)

**Empty responses:**
- Check API key is valid
- Check API quota (shouldn't hit free tier limits)
- Check backend logs in `backend/logs/`

## 📊 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎥 Recording Demo Video

### Recommended Tools
- **OBS Studio** (free): https://obsproject.com/
- **Loom** (free): https://www.loom.com/
- **Windows Game Bar**: Win + G

### Demo Script (7 minutes)

**1. Introduction (1 min)**
- Show problem statement
- Explain MD&A automation challenge

**2. Architecture (1 min)**
- Show README architecture diagram
- Explain RAG pipeline
- Mention Gemini + LangChain

**3. Live Demo (4 min)**
- Start backend and frontend
- Upload financial document
- Ask questions:
  - "What is the total revenue?"
  - "Calculate the profit margin"
  - "Generate an MD&A report"
- Show citations and sources
- Demonstrate guardrails

**4. Code Walkthrough (1 min)**
- Show agent_system.py
- Show md_a_generator.py
- Explain RAG service
- Show evaluation metrics

**5. Conclusion (30 sec)**
- Summarize features
- Mention scalability
- Future enhancements

### Recording Tips
- Use 1080p resolution
- Clear audio (use headset mic)
- Show both UI and code
- Highlight AI/ML components
- Keep it under 10 minutes

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional (defaults are fine)
DEBUG=True
MAX_FILE_SIZE_MB=50
DATABASE_URL=sqlite:///./finmda.db
```

### Customization

**Change LLM Model:**
Edit `backend/app/services/agent_system.py`:
```python
self.model = genai.GenerativeModel("gemini-1.5-pro")  # More capable
# or
self.model = genai.GenerativeModel("gemini-1.5-flash")  # Faster
```

**Adjust Prompt Templates:**
Edit `backend/app/services/agent_system.py` - `_build_prompt()` method

**Modify Guardrails:**
Edit `backend/app/services/guardrails.py`

## 📦 Deployment

### Docker (Recommended for Production)

```bash
# Build and run
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Manual Deployment

**Backend:**
```bash
# Use production WSGI server
pip install gunicorn
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

**Frontend:**
```bash
# Build for production
npm run build

# Serve with nginx or serve
npx serve -s build -p 3000
```

## 🎯 Assignment Checklist

- [x] Clear problem statement (MD&A automation)
- [x] AI/ML components (RAG, LLM, Agents, Guardrails)
- [x] LLM integration (Google Gemini)
- [x] RAG application (ChromaDB + embeddings)
- [x] Evals & Guardrails (validation, citations)
- [x] Free API (Gemini free tier)
- [x] Good UI (React + TailwindCSS)
- [x] Server-side code (FastAPI backend)
- [x] Scalability (Docker-ready, horizontal scaling)
- [x] MVP (Fully functional)
- [x] Documentation (README + API docs)
- [x] Working demo (Ready for recording)

## 📞 Support

**Check logs:**
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend console
# Open browser DevTools (F12)
```

**Common commands:**
```bash
# Restart backend
cd backend
venv\Scripts\activate
python -m app.main

# Restart frontend
cd frontend
npm start

# Run tests
cd backend
pytest tests/ -v
```

## 🎓 Learning Resources

- **Gemini API**: https://ai.google.dev/docs
- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/

---

**Good luck with your demo! 🚀**



