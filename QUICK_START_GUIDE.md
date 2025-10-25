# FinMDA-Bot Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd TEAM--T

# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

### 2. Environment Configuration
```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit environment variables
nano backend/.env
```

**Required Environment Variables:**
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://finmda_user:finmda_password@postgres:5432/finmda_bot
REDIS_URL=redis://redis:6379
```

### 3. Start All Services
```bash
# Start with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

## 🎯 Quick Demo

### 1. Upload a Document
1. Go to http://localhost:3000
2. Navigate to "Documents" page
3. Upload a PDF financial statement
4. Wait for processing to complete

### 2. Ask Questions
1. Go to "Chat" page
2. Ask: "What is the revenue trend?"
3. Get AI-powered insights from your document

### 3. Use Voice Assistant
1. Go to "Voice Assistant" page
2. Click "Start Recording"
3. Speak: "Calculate the profit margin"
4. Get voice response with analysis

### 4. View Analytics
1. Go to "Analytics" page
2. See financial ratios and trends
3. Download reports

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Setup
```bash
# Run migrations
cd backend
alembic upgrade head

# Create sample data
python scripts/create_sample_data.py
```

## 📊 Testing

### Run Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# Full test suite
python test_runner.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_financial_statement.pdf"

# Chat with AI
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the revenue trend?"}'
```

## 🐛 Troubleshooting

### Common Issues

**1. Docker containers not starting**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

**2. Database connection issues**
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U finmda_user -d finmda_bot

# Reset database
docker-compose down -v
docker-compose up -d
```

**3. Frontend build issues**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**4. Voice assistant not working**
- Ensure microphone permissions are granted
- Check browser compatibility
- Try different browsers (Chrome recommended)

### Performance Optimization

**1. Increase Docker resources**
- Allocate more RAM (8GB+ recommended)
- Increase CPU cores (4+ recommended)

**2. Database optimization**
```bash
# Check database performance
docker-compose exec postgres psql -U finmda_user -d finmda_bot -c "SELECT * FROM pg_stat_activity;"
```

**3. Redis optimization**
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory
```

## 📚 Next Steps

### 1. Explore Features
- **Dashboard**: Overview of your financial data
- **Documents**: Upload and manage financial documents
- **Chat**: Ask questions about your data
- **Analytics**: View financial insights and trends
- **Voice Assistant**: Use voice commands
- **FAQ**: Get help and support

### 2. Customize Settings
- Go to "Settings" page
- Configure voice settings
- Adjust notification preferences
- Set up data retention policies

### 3. Advanced Usage
- **API Integration**: Use the REST API for custom applications
- **Webhook Setup**: Configure real-time notifications
- **Custom Models**: Train domain-specific models
- **Enterprise Features**: Set up multi-tenant deployment

## 🆘 Support

### Documentation
- **API Documentation**: http://localhost:8000/docs
- **Architecture Guide**: ARCHITECTURE.md
- **Run Instructions**: RUN_INSTRUCTIONS.md
- **Project Summary**: PROJECT_COMPLETION_SUMMARY.md

### Getting Help
1. Check the FAQ page in the application
2. Review the troubleshooting section above
3. Check Docker logs for errors
4. Verify environment variables are set correctly

### Sample Data
- Upload sample financial statements for testing
- Use the provided demo notebooks
- Try the example API calls in the documentation

---

**Ready to explore FinMDA-Bot! 🎉**

For detailed setup instructions, see `RUN_INSTRUCTIONS.md`  
For architecture details, see `ARCHITECTURE.md`  
For API reference, see `API_DOCUMENTATION.md`
