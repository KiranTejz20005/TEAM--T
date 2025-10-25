# FinMDA-Bot — Quick, complete run instructions

This file gives copy-paste PowerShell commands to run the project locally (backend + frontend) or bring up the full stack with Docker Compose.

## Goal / contract
- Inputs: your local machine (Windows) with optional Docker installed and environment variables (OpenAI key, optional AWS creds).
- Outputs: running backend API (http://localhost:8000) and frontend (http://localhost:3000) or a full Docker-based stack.

---

## Prerequisites (Windows)
- Python 3.8+ (recommended 3.10/3.11) added to PATH
- Node.js 16+ and npm
- Git
- (Optional, recommended) Docker Desktop for Windows if you want containers

If you need installs:
1. Python: https://python.org
2. Node.js: https://nodejs.org
3. Git: https://git-scm.com
4. Docker Desktop: https://www.docker.com/products/docker-desktop

---

## Recommended approach
1. For fastest, isolated full-stack: use Docker Compose (requires Docker Desktop).
2. For local development of frontend/backend: run backend in a Python venv and frontend with npm.

Below are PowerShell commands ready to copy/paste. Open a PowerShell terminal at the repository root (the folder that contains `backend`, `frontend`, and `docker-compose.yml`).

### 1) Check environment (optional quick checks)
```powershell
# Check python and node
python --version
node --version
npm --version

# Check Docker (if you plan to use docker-compose)
docker --version
docker compose version
```

### 2) Run full stack with Docker Compose (recommended to 'do everything')
Use this to start Postgres, Redis, backend, frontend, celery workers, flower, and nginx exactly as configured in `docker-compose.yml`.

Note: make sure you set required secrets in your environment (OpenAI / AWS) before running. On Windows, set them in the PowerShell session or in an `.env` file referenced by Docker.

Set required env vars (example):
```powershell
# replace values with your real keys
$env:OPENAI_API_KEY = 'sk-...'
$env:AWS_ACCESS_KEY_ID = 'AKIA...'
$env:AWS_SECRET_ACCESS_KEY = '...'
$env:AWS_REGION = 'us-east-1'
$env:S3_BUCKET_NAME = 'my-bucket'
```

Then build & run (from repo root):
```powershell
# Use docker compose v2 syntax
docker compose up --build -d

# Watch logs (example: backend)
docker compose logs -f backend

# When done, stop and remove
docker compose down
```

If Docker Desktop is not installed or you prefer local dev, follow the local steps next.

---

### 3) Run backend locally (PowerShell)
This boots the FastAPI app using uvicorn on port 8000. Note: the repository's `requirements.txt` includes heavy ML packages (torch, whisper, etc.) that may be slow to install. If you hit issues, see the note below.

```powershell
# 1. Create and activate a venv (from repository root)
python -m venv .venv

# allow activation for this session if execution policy blocks it
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

.\.venv\Scripts\Activate.ps1

# 2. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r .\backend\requirements.txt

# 3. Copy env.example to .env in backend and edit it (or set env vars in PowerShell)
Copy-Item .\backend\env.example .\backend\.env -ErrorAction SilentlyContinue
# Edit .\backend\.env to add your OPENAI_API_KEY and any AWS creds if needed

# 4. Run the backend (reload on file changes if DEBUG enabled)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Health check: http://localhost:8000/api/v1/health
```

Quick alternative: run the module directly (uses uvicorn in main):
```powershell
python .\backend\app\main.py
```

Notes about heavy dependencies:
- If `torch` or `whisper` fail to install, consider either using Docker (it encapsulates dependencies) or creating a trimmed `requirements-dev.txt` that excludes heavy packages for quick API development. Tell me if you want that file and I will create it.

---

### 4) Run frontend locally (PowerShell)
```powershell
cd .\frontend
npm install
npm start

# Frontend will be at http://localhost:3000 and proxies API calls to http://localhost:8000
```

Open a separate terminal for the frontend so both run concurrently.

---

### 5) Run tests
- Backend (pytest):
```powershell
# from repository root
.\.venv\Scripts\Activate.ps1
cd .\backend
pytest -q
```

- Frontend:
```powershell
cd .\frontend
npm test
```

---

### 6) Troubleshooting / tips
- If venv activation errors occur: run PowerShell as your user and run the Set-ExecutionPolicy line above.
- If some Python packages fail building on Windows, try Docker Compose or use WSL2 (Windows Subsystem for Linux) which often has better compatibility for ML packages.
- If ports 8000 or 3000 are occupied, stop the process using them or change ports in `backend/app/main.py` or `frontend` start script.

---

### 7) Next steps I can do for you
1. Run `docker compose up --build -d` in your terminal now and stream logs here. (I can run it for you if you want.)
2. Create a `requirements-dev.txt` without heavy ML libs for fast local backend dev.
3. Add simple PowerShell run scripts (`run_backend.ps1`, `run_frontend.ps1`, `run_all.ps1`) into the repo.

Reply with which of the three (1/2/3) you'd like me to execute now. If you want me to run Docker Compose here, tell me and I will attempt to run it and report back the output.

---

Access URLs (local)
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

Support: If you get errors while running any command, copy the terminal output here and I'll triage.

