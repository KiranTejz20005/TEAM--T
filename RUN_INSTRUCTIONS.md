# FinMDA-Bot Setup and Run Instructions

## Prerequisites

Before running FinMDA-Bot, ensure you have the following installed:

- **Python 3.8+** (recommended: Python 3.9)
- **Node.js 16+** (for frontend development)
- **Git** (for version control)
- **Docker** (optional, for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/finmda-bot.git
cd finmda-bot
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp env.example .env
```

Edit the `.env` file with your configuration:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./finmda.db

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=FinMDA-Bot
APP_VERSION=1.0.0
DEBUG=True

# File Upload Settings
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,xlsx,xls,csv

# ChromaDB Settings
CHROMA_PERSIST_DIRECTORY=./chromadb
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

#### Initialize Database

```bash
python -c "from app.database import create_tables; create_tables()"
```

#### Run the Backend

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Frontend Setup (Optional)

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Environment Configuration

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

#### Run the Frontend

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Docker Deployment

### 1. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### 2. Individual Service Deployment

#### Backend Only

```bash
cd backend
docker build -t finmda-backend .
docker run -p 8000:8000 --env-file .env finmda-backend
```

#### Frontend Only

```bash
cd frontend
docker build -t finmda-frontend .
docker run -p 3000:3000 finmda-frontend
```

## Production Deployment

### 1. Render Deployment

#### Backend Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9
4. Add environment variables in Render dashboard
5. Deploy

#### Frontend Deployment

1. Create a new Static Site
2. Configure:
   - **Build Command**: `npm run build`
   - **Publish Directory**: `build`
3. Add environment variables
4. Deploy

### 2. Railway Deployment

#### Backend

1. Connect GitHub repository
2. Add `railway.json` configuration:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health"
  }
}
```

3. Set environment variables
4. Deploy

### 3. AWS Deployment

#### Using AWS App Runner

1. Create a new App Runner service
2. Configure source:
   - **Repository**: Your GitHub repository
   - **Branch**: main
3. Configure build:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Set environment variables
5. Deploy

## Testing

### 1. Run Unit Tests

```bash
cd backend
pytest tests/ -v
```

### 2. Run Integration Tests

```bash
pytest tests/ -v --integration
```

### 3. Run All Tests with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@sample_document.pdf"
```

## Development

### 1. Code Formatting

```bash
# Format Python code
black app/
isort app/

# Format JavaScript code
cd frontend
npm run format
```

### 2. Linting

```bash
# Python linting
flake8 app/
pylint app/

# JavaScript linting
cd frontend
npm run lint
```

### 3. Type Checking

```bash
# Python type checking
mypy app/

# TypeScript type checking
cd frontend
npm run type-check
```

## Monitoring and Logging

### 1. Health Monitoring

The API provides health check endpoints:

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status

### 2. Logging Configuration

Logs are configured in `app/config.py`:

```python
LOGGING_LEVEL = "INFO"
LOG_FILE = "logs/finmda-bot.log"
```

### 3. Metrics Collection

The system collects the following metrics:

- Request/response times
- Error rates
- Document processing times
- AI model usage
- Database query performance

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Error**: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file`

**Solution**:
```bash
# Create database directory
mkdir -p data
# Set proper permissions
chmod 755 data
```

#### 2. OpenAI API Issues

**Error**: `openai.error.AuthenticationError: Invalid API key`

**Solution**:
1. Check your OpenAI API key in `.env`
2. Ensure you have sufficient credits
3. Verify API key permissions

#### 3. ChromaDB Issues

**Error**: `chromadb.errors.InvalidDimensionException`

**Solution**:
```bash
# Clear ChromaDB data
rm -rf chromadb/
# Restart the application
```

#### 4. Memory Issues

**Error**: `MemoryError` or `OutOfMemoryError`

**Solution**:
1. Reduce batch sizes in processing
2. Increase system memory
3. Use smaller embedding models

### Performance Optimization

#### 1. Database Optimization

```python
# Enable connection pooling
DATABASE_URL = "postgresql://user:pass@host:port/db?pool_size=20&max_overflow=30"
```

#### 2. Caching Configuration

```python
# Redis caching
REDIS_URL = "redis://localhost:6379"
CACHE_TTL = 3600  # 1 hour
```

#### 3. Async Processing

```python
# Enable background tasks
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
```

## Security Considerations

### 1. API Security

- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Use JWT tokens for authentication

### 2. Data Security

- Encrypt sensitive data
- Use secure file storage
- Implement access controls
- Regular security audits

### 3. Environment Security

- Never commit `.env` files
- Use environment-specific configurations
- Rotate API keys regularly
- Monitor access logs

## Scaling

### 1. Horizontal Scaling

- Use load balancers
- Implement database sharding
- Use distributed caching
- Deploy multiple instances

### 2. Vertical Scaling

- Increase server resources
- Optimize database queries
- Use faster storage (SSD)
- Implement connection pooling

### 3. Microservices Architecture

- Split into smaller services
- Use message queues
- Implement service discovery
- Use container orchestration

## Backup and Recovery

### 1. Database Backup

```bash
# SQLite backup
cp finmda.db finmda_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump finmda > finmda_backup_$(date +%Y%m%d).sql
```

### 2. File Storage Backup

```bash
# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Backup ChromaDB
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz chromadb/
```

### 3. Configuration Backup

```bash
# Backup configuration
cp .env .env_backup_$(date +%Y%m%d)
```

## Support

For additional support:

- **Documentation**: [Architecture Guide](ARCHITECTURE.md)
- **API Reference**: [API Documentation](API_DOCUMENTATION.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@finmda-bot.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
