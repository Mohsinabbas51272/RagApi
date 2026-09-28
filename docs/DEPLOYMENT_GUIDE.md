# Brillanz Group Multi-Website RAG Platform - Deployment Guide

## 1. Quick Local Deployment (Docker Compose)

The fastest and most reliable way to run the full stack (Frontend + Backend + Persistent Vector Storage) in production mode:

```bash
# 1. Clone or navigate to the repository
cd "/Users/mohsinabbas/Brillanz group webistes development"

# 2. Configure environment (Optional: add your Gemini API Key)
cp backend/.env.example backend/.env

# 3. Start all services via Docker Compose
docker-compose up --build -d

# 4. View logs
docker-compose logs -f
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 2. Standalone Development Run (Without Docker)

### Step 1: Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 3. Running Automated Tests & Verification

```bash
# Pytest full backend test suite
cd backend
venv/bin/pytest tests/test_api.py -v

# RAG Grounding & Anti-Hallucination verification
backend/venv/bin/python scripts/test_rag_grounding.py

# Rebuild Vector Index
backend/venv/bin/python scripts/build_index.py

# Run Live Web Crawler
backend/venv/bin/python scripts/crawl_all.py --limit 3
```
