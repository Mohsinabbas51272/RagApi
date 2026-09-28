# Brillanz Group Multi-Website RAG Platform - REST API Reference

Base URL: `http://localhost:8000/api`

---

## 1. Grounded Query Endpoint

### `POST /api/query`
Executes semantic vector similarity search and returns a grounded response with source citations.

#### Request Body:
```json
{
  "question": "What custom software engineering services does Softoo offer?",
  "website_filter": "softoo",
  "top_k": 4
}
```

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How does YaniPro automate AI audit workflows?", "website_filter": "yanipro"}'
```

#### Response:
```json
{
  "question": "How does YaniPro automate AI audit workflows?",
  "answer": "Based on verified knowledge from YaniPro [1] (https://yanipro.ai/features)...",
  "sources": [
    {
      "chunk_id": "doc-yanipro-01-c01",
      "website_id": "yanipro",
      "website_name": "Yani Pro",
      "url": "https://yanipro.ai/features",
      "title": "YaniPro - Next-Generation AI Autonomous Agents",
      "category": "AI Platform",
      "snippet": "YaniPro is an autonomous AI agent platform designed for customer interaction...",
      "relevance_score": 0.89
    }
  ],
  "website_filter": "yanipro",
  "processing_time_ms": 1.45,
  "grounded": true,
  "embedding_mode": "gemini_text_embedding_004"
}
```

---

## 2. Ingestion & Crawler Endpoint

### `POST /api/ingest`
Triggers the multi-website scraper and automatically re-indexes the vector database.

#### Request Body:
```json
{
  "target_websites": ["softoo", "thunderenergy"],
  "max_pages_per_site": 3
}
```

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{"max_pages_per_site": 3}'
```

---

## 3. Rebuild Vector Index Endpoint

### `POST /api/rebuild-index`
Re-chunks all raw documents and regenerates vector embeddings.

#### Example cURL:
```bash
curl -X POST "http://localhost:8000/api/rebuild-index"
```

---

## 4. Chunk Inspector Endpoint

### `GET /api/chunks`
Inspects chunked text documents in the vector database.

#### Query Parameters:
- `website_id` (optional string): e.g. `softoo`
- `limit` (optional integer): default 20, max 100

#### Example cURL:
```bash
curl "http://localhost:8000/api/chunks?website_id=cratus&limit=5"
```

---

## 5. Analytics & Statistics Endpoint

### `GET /api/stats`
Returns counts of documents, active vector chunks, and entity distribution.

#### Example cURL:
```bash
curl "http://localhost:8000/api/stats"
```

---

## 6. Website Discovery & Health Endpoints

- `GET /api/websites` — Catalog of all 7 registered Brillanz companies.
- `GET /api/health` — Service uptime and status.
