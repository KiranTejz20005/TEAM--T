# FinMDA-Bot - Quick Reference Guide

## 🚀 Quick Start Commands

### Start Backend
```bash
cd backend
venv\Scripts\activate
python -m app.main
```
**URL:** http://localhost:8000
**Docs:** http://localhost:8000/docs

### Start Frontend
```bash
cd frontend
npm start
```
**URL:** http://localhost:3000

### Run Tests
```bash
# API tests
python TEST_API.py

# Unit tests
cd backend
pytest tests/ -v
```

## 📝 API Endpoints

### Health & Info
```bash
GET  /api/v1/health              # Health check
GET  /                           # API info
```

### Chat
```bash
POST /api/v1/chat/query          # Send chat message
POST /api/v1/chat/sessions       # Create session
GET  /api/v1/chat/sessions/{id}  # Get session
```

### Documents
```bash
POST /api/v1/documents/upload    # Upload document
GET  /api/v1/documents/          # List documents
GET  /api/v1/documents/{id}      # Get document
DELETE /api/v1/documents/{id}    # Delete document
```

### MD&A Generation
```bash
POST /api/v1/mda/generate              # Generate full MD&A report
POST /api/v1/mda/generate-section      # Generate specific section
POST /api/v1/mda/analyze-financials    # Analyze financial data
```

### Analytics
```bash
POST /api/v1/analytics/ratios     # Calculate ratios
POST /api/v1/analytics/forecast   # Generate forecast
POST /api/v1/analytics/trends     # Analyze trends
```

## 💬 Example Queries

### Chat Examples
```
"What is financial analysis?"
"Calculate the profit margin"
"What was the revenue in Q3?"
"Generate an MD&A report"
"Explain the debt-to-equity ratio"
"Show me year-over-year growth"
```

### API Examples

**Chat Query:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROE?", "session_id": null}'
```

**Generate MD&A:**
```bash
curl -X POST "http://localhost:8000/api/v1/mda/generate?period=Q3%202024"
```

**Analyze Financials:**
```bash
curl -X POST http://localhost:8000/api/v1/mda/analyze-financials
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
GEMINI_API_KEY=your_key_here      # Required
DEBUG=True                         # Optional
DATABASE_URL=sqlite:///./finmda.db # Optional
MAX_FILE_SIZE_MB=50               # Optional
```

### Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste in `.env` file

## 📊 Project Structure

```
TEAM--T/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/     # API routes
│   │   ├── services/          # Business logic
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Unit tests
│   ├── requirements.txt       # Dependencies
│   └── .env                   # Configuration
├── frontend/
│   ├── src/
│   │   ├── pages/             # React pages
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   └── store/             # State management
│   └── package.json           # Dependencies
└── README.md                  # Documentation
```

## 🎯 Key Features

### ✅ Implemented
- Document upload (PDF, Excel, CSV)
- Financial data extraction
- KPI calculation (ratios, margins, growth)
- MD&A report generation
- RAG-based chat
- Multi-agent system
- Guardrails & validation
- Voice assistant
- Analytics dashboard

### 🔄 Demo Flow
1. **Upload** financial document
2. **Ask** questions via chat
3. **Generate** MD&A report
4. **Review** citations and sources
5. **Export** results

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Check .env file
type .env  # Should have GEMINI_API_KEY
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API errors
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check API key
# Edit .env and verify GEMINI_API_KEY is set

# Check logs
tail -f backend/logs/app.log
```

### Slow responses
- First request is always slower (model initialization)
- Check internet connection (API calls to Gemini)
- Gemini free tier: 60 requests/min

## 📚 Documentation

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Code Documentation
- `README.md` - Project overview
- `SETUP_GUIDE.md` - Detailed setup
- `API_DOCUMENTATION.md` - API reference
- `ARCHITECTURE.md` - System design

## 🎥 Demo Video Checklist

### What to Show (7 minutes)
1. **Problem** (1 min) - MD&A automation challenge
2. **Architecture** (1 min) - RAG + LLM + Agents
3. **Demo** (4 min)
   - Upload document
   - Ask questions
   - Generate MD&A
   - Show citations
4. **Code** (1 min) - Key components
5. **Wrap-up** (30s) - Impact & future

### Recording Tips
- Use OBS Studio or Loom
- 1080p resolution
- Clear audio (headset mic)
- Show both UI and code
- Keep under 10 minutes

## 🔑 Important Files

### Backend
- `app/main.py` - FastAPI application
- `app/services/agent_system.py` - AI agents
- `app/services/md_a_generator.py` - MD&A generation
- `app/services/rag_service.py` - RAG pipeline
- `app/api/endpoints/mda.py` - MD&A endpoints

### Frontend
- `src/pages/Chat.js` - Chat interface
- `src/pages/Documents.js` - Document management
- `src/services/api.js` - API client

## 💡 Tips & Tricks

### Development
```bash
# Auto-reload backend
python -m app.main  # DEBUG=True enables auto-reload

# Watch frontend
npm start  # Auto-reloads on file changes

# Format code
black backend/  # Python
npm run format  # JavaScript (if configured)
```

### Testing
```bash
# Quick API test
python TEST_API.py

# Full test suite
cd backend
pytest tests/ -v --cov

# Test specific endpoint
curl http://localhost:8000/api/v1/health
```

### Deployment
```bash
# Docker
docker-compose up -d

# Manual
# Backend: gunicorn app.main:app --workers 4
# Frontend: npm run build && serve -s build
```

## 📞 Getting Help

### Check Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend console
# Open browser DevTools (F12)
```

### Common Issues
1. **"API key not configured"** → Edit `.env` file
2. **"Port already in use"** → Kill process or change port
3. **"Module not found"** → Run `pip install -r requirements.txt`
4. **"Cannot connect"** → Check backend is running

### Resources
- **Gemini API**: https://ai.google.dev/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **LangChain**: https://python.langchain.com/

---

**Need more help?** Check `SETUP_GUIDE.md` for detailed instructions.

**Ready to demo?** Run `python TEST_API.py` to verify everything works!



