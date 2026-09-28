# Brillanz Group Multi-Website RAG Platform 🌐🤖

An enterprise Retrieval-Augmented Generation (RAG) platform that indexes, retrieves, and answers questions with verified grounded citations across all 7 companies of the **Brillanz Group**:

1. **Softoo** (`https://softoo.co/`) — Custom Software Development & Agile Engineering Teams
2. **OKO Insights** (`https://okoinsights.ai/`) — AI Vision Analytics & Real-Time Crowd Intelligence
3. **YaniPro** (`https://yanipro.ai/`) — Autonomous AI Agents & Customer Interaction Workflows
4. **Cratus UK** (`https://cratus.uk/`) — Smart City IoT Telemetry & Utility Grid Control
5. **SC Tech Global** (`https://www.sctechglobal.com/`) — Enterprise Supply Chain Cloud Solutions
6. **Thunder Energy AI** (`https://www.thunderenergy.ai/`) — Renewable Clean Energy & Battery Storage (BESS)
7. **Scorpbit** (`https://scorpbit.com/`) — Cybersecurity & Offensive Threat Intelligence

---

## 🏛️ System Architecture

```text
  [ 7 Brillanz Websites ]
             │
             ▼
  [ Multi-Website Web Crawler (crawler.py) ] ──► [ data/raw_documents.json ]
             │
             ▼
  [ Recursive Semantic Chunker (chunker.py) ] ──► [ data/chunks.json (50 Chunks) ]
             │
             ▼
  [ Gemini text-embedding-004 Vector Store ] ──► [ data/vector_index.json ]
             │
   User Question (React Chat UI) ──► [ FastAPI Backend ]
                                              │
                                              ▼
                               [ Cosine Similarity Retrieval ]
                                              │
                                              ▼
                               [ Anti-Hallucination Guardrail ]
                                              │
                                              ▼
                               [ Gemini Grounded Synthesis ]
                                              │
                                              ▼
                               [ Answer + Inline Citations + URLs ]
```

---

## 📅 Complete 7-Day Deliverables Matrix

| Day | Milestone | Key Features Completed |
| :--- | :--- | :--- |
| **Day 1** | **Architecture & Foundation** | 7-company discovery catalog, project workspace, React + Tailwind base, FastAPI base. |
| **Day 2** | **Multi-Website Crawler** | Noise-stripping scraper, structured extraction, JSON persistence, CLI crawling script. |
| **Day 3** | **Chunking & Vector Database** | 600-char semantic chunking, Gemini embeddings, cosine distance index, index builder CLI. |
| **Day 4** | **FastAPI Full Services** | `POST /query`, `POST /ingest`, `POST /rebuild-index`, `GET /stats`, `GET /chunks`, automated tests. |
| **Day 5** | **Grounded RAG & Guardrails** | Anti-hallucination system prompt, confidence thresholding, out-of-domain refusal evaluator. |
| **Day 6** | **Frontend UI & Chunk Explorer** | Interactive Chunk Explorer tab, citation highlighting, dialogue export/clear, analytics dashboard. |
| **Day 7** | **Docker & Production Package** | `Dockerfile` (frontend + backend), `docker-compose.yml`, Nginx config, technical documentation. |

---

## 🚀 Quick Start Instructions

### Option A: Run with Docker Compose (Production Mode)
```bash
docker-compose up --build -d
```
- **Web App**: `http://localhost:3000`
- **FastAPI OpenAPI Swagger**: `http://localhost:8000/docs`

### Option B: Run Locally (Development Mode)

**1. Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Start Frontend:**
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🧪 Testing & Verification Commands

```bash
# 1. Run full backend pytest suite (9 tests, 100% pass)
backend/venv/bin/pytest backend/tests/test_api.py -v

# 2. Run Grounding & Anti-Hallucination Evaluator
backend/venv/bin/python scripts/test_rag_grounding.py

# 3. Build/Rebuild Vector Index CLI
backend/venv/bin/python scripts/build_index.py

# 4. Run Live Crawler CLI
backend/venv/bin/python scripts/crawl_all.py --limit 3
```

---

## 📚 Technical Documentation

- 📘 [Complete Architecture & Mathematical Specification](file:///Users/mohsinabbas/Brillanz%20group%20webistes%20development/docs/ARCHITECTURE.md)
- 📗 [REST API Reference Guide](file:///Users/mohsinabbas/Brillanz%20group%20webistes%20development/docs/API_REFERENCE.md)
- 📙 [Production Deployment Guide](file:///Users/mohsinabbas/Brillanz%20group%20webistes%20development/docs/DEPLOYMENT_GUIDE.md)
