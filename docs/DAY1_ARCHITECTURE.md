# Brillanz Group Multi-Website RAG Platform - Day 1 Architecture & Specifications

## 1. Project Goal
Develop an enterprise-grade Retrieval-Augmented Generation (RAG) system answering questions accurately and with grounded citations across all 7 companies of the **Brillanz Group**:
1. **Softoo** (`https://softoo.co/`)
2. **OKO Insights** (`https://okoinsights.ai/`)
3. **YaniPro** (`https://yanipro.ai/`)
4. **Cratus UK** (`https://cratus.uk/`)
5. **SC Tech Global** (`https://www.sctechglobal.com/`)
6. **Thunder Energy AI** (`https://www.thunderenergy.ai/`)
7. **Scorpbit** (`https://scorpbit.com/`)

---

## 2. Day 1 Completed Foundations

### A. Discovery Matrix & Inventory
- `data/websites_inventory.json`: Registered all 7 entities, root URLs, categories, and targeted crawl paths.
- `data/raw_documents.json`: Seeded initial verified ground-truth data.

### B. Backend Services (FastAPI + ChromaDB + Gemini)
- `backend/app/main.py`: CORS-enabled application serving API endpoints.
- `backend/app/models/schemas.py`: Defined `QueryRequest`, `QueryResponse`, `IngestRequest`, `RebuildIndexResponse`, `StatsResponse`.
- `backend/app/api/routes.py`:
  - `POST /api/query`: Semantic retrieval with grounded prompt synthesis and source attribution.
  - `POST /api/ingest`: Crawler ingestion trigger.
  - `POST /api/rebuild-index`: Vector index refresh.
  - `GET /api/stats`: Knowledge graph statistics.
  - `GET /api/websites`: Website discovery catalog.
  - `GET /api/health`: Health monitoring.

### C. Frontend Architecture (React + Tailwind CSS)
- **Glassmorphism Design System**: Modern dark UI with radiant gradients, custom scrollbars, and micro-animations.
- **Navbar**: Entity filter bar for 1-click filtering by specific Brillanz company.
- **Chat Interface**: Grounded message cards with exact source URLs, similarity confidence, snippet previews, and copy utilities.
- **Stats Dashboard**: Entity grid, document counts, and system status indicators.
- **Admin Modal**: Triggering ingestion and rebuilding index with real-time feedback.

---

## 3. Next Steps (Day 2 - Day 7)
- **Day 2**: Deep crawler using BeautifulSoup & Playwright with sitemap auto-discovery and rate-limiting.
- **Day 3**: Gemini Embeddings (`text-embedding-004`) + ChromaDB persistent vector storage.
- **Day 4**: Complete integration of FastAPI endpoints with live vector collection.
- **Day 5**: Strict anti-hallucination prompt guardrails & confidence thresholding.
- **Day 6**: Interactive UI enhancements with streaming chat responses.
- **Day 7**: Docker Compose (`frontend` + `backend` + `chroma`), unit tests, and final presentation README.
