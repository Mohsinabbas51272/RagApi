import json
import os
import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import (
    QueryRequest, QueryResponse,
    IngestRequest, IngestResponse,
    RebuildIndexResponse, StatsResponse, WebsiteSummary,
    ChunkListResponse, ChunkItem
)
from app.services.vector_store import VectorStoreManager
from app.services.rag_engine import RAGEngine
from app.services.crawler import MultiWebsiteCrawler
from app.services.chunker import CHUNKS_PATH
from app.config import WEBSITES_INVENTORY_PATH, RAW_DOCUMENTS_PATH

router = APIRouter()

# Service singletons
vector_store = VectorStoreManager()
rag_engine = RAGEngine(vector_store=vector_store)
crawler = MultiWebsiteCrawler(max_pages_per_site=4)

@router.post("/query", response_model=QueryResponse, summary="Query Brillanz Knowledge Base")
def query_knowledge_base(payload: QueryRequest):
    """
    Answers a question grounded strictly in Brillanz Group website data.
    Returns generated response, cosine relevance scores, and direct source URL citations.
    """
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    return rag_engine.query(
        question=payload.question,
        website_filter=payload.website_filter,
        top_k=payload.top_k or 4
    )

@router.post("/ingest", response_model=IngestResponse, summary="Trigger Crawler & Auto-Index")
def trigger_ingest(payload: IngestRequest):
    """
    Crawls target websites (or all 7) and automatically re-chunks and re-indexes content.
    """
    start_time = time.time()
    crawled = crawler.crawl_all(
        target_ids=payload.target_websites,
        max_pages_per_site=payload.max_pages_per_site or 3
    )
    
    # Auto rebuild index over new crawled pages
    reindex_res = vector_store.rebuild_index()

    return IngestResponse(
        status="completed",
        total_pages_scraped=len(crawled),
        total_chunks_created=reindex_res.get("total_vectors", len(crawled) * 2),
        duration_seconds=round(time.time() - start_time, 2),
        websites_processed=list(set([c["website_id"] for c in crawled])),
        auto_reindexed=True
    )

@router.post("/rebuild-index", response_model=RebuildIndexResponse, summary="Rebuild Vector Index")
def rebuild_vector_index():
    """
    Re-chunks all crawled documents and regenerates vector embeddings in the database.
    """
    start_time = time.time()
    res = vector_store.rebuild_index()
    duration = round(time.time() - start_time, 2)
    
    return RebuildIndexResponse(
        status="success",
        collection_name="brillanz_knowledge_base",
        total_vectors_indexed=res.get("total_vectors", 0),
        embedding_mode=res.get("mode", "semantic_vector"),
        duration_seconds=duration,
        message=f"Vector database index re-indexed successfully with {res.get('total_vectors', 0)} chunks in {duration}s."
    )

@router.get("/websites", summary="List Brillanz Entities")
def list_websites():
    """Returns all 7 registered Brillanz Group companies, taglines, and target URLs."""
    if os.path.exists(WEBSITES_INVENTORY_PATH):
        with open(WEBSITES_INVENTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"websites": []}

@router.get("/chunks", response_model=ChunkListResponse, summary="Inspect Indexed Chunks")
def list_chunks(
    website_id: Optional[str] = Query(None, description="Filter chunks by website (e.g. softoo, yanipro)"),
    limit: int = Query(20, ge=1, le=100, description="Max chunks to return")
):
    """Inspects chunked text documents and metadata in the vector database."""
    chunks_data = []
    if os.path.exists(CHUNKS_PATH):
        try:
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)
                if website_id:
                    all_chunks = [c for c in all_chunks if c.get("metadata", {}).get("website_id") == website_id]
                
                total = len(all_chunks)
                for ch in all_chunks[:limit]:
                    chunks_data.append(ChunkItem(
                        chunk_id=ch.get("chunk_id", ""),
                        document_id=ch.get("document_id"),
                        text=ch.get("text", ""),
                        character_count=ch.get("character_count", len(ch.get("text", ""))),
                        metadata=ch.get("metadata", {})
                    ))
                return ChunkListResponse(
                    total_chunks=total,
                    returned_chunks=len(chunks_data),
                    website_filter=website_id,
                    chunks=chunks_data
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading chunks: {e}")
    return ChunkListResponse(total_chunks=0, returned_chunks=0, website_filter=website_id, chunks=[])

@router.get("/stats", response_model=StatsResponse, summary="System & Knowledge Analytics")
def get_system_stats():
    """Returns analytics, document counts, and chunk distributions across all 7 entities."""
    stats = vector_store.get_stats()
    websites_data = []
    
    # Count documents & chunks per website
    site_doc_counts = {}
    site_chunk_counts = {}
    
    if os.path.exists(CHUNKS_PATH):
        try:
            with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                chunks = json.load(f)
                for ch in chunks:
                    s_id = ch.get("metadata", {}).get("website_id")
                    url = ch.get("metadata", {}).get("url")
                    if s_id:
                        site_chunk_counts[s_id] = site_chunk_counts.get(s_id, 0) + 1
        except Exception:
            pass

    if os.path.exists(RAW_DOCUMENTS_PATH):
        try:
            with open(RAW_DOCUMENTS_PATH, "r", encoding="utf-8") as f:
                docs = json.load(f)
                for d in docs:
                    s_id = d.get("website_id")
                    site_doc_counts[s_id] = site_doc_counts.get(s_id, 0) + 1
        except Exception:
            pass

    if os.path.exists(WEBSITES_INVENTORY_PATH):
        with open(WEBSITES_INVENTORY_PATH, "r", encoding="utf-8") as f:
            inv = json.load(f)
            for w in inv.get("websites", []):
                s_id = w["id"]
                websites_data.append(WebsiteSummary(
                    id=s_id,
                    name=w["name"],
                    url=w["url"],
                    category=w["category"],
                    tagline=w["tagline"],
                    total_pages_indexed=site_doc_counts.get(s_id, 1),
                    total_chunks=site_chunk_counts.get(s_id, 2),
                    status="active"
                ))

    return StatsResponse(
        total_websites=len(websites_data),
        total_documents=sum(site_doc_counts.values()) or stats["total_documents"],
        total_chunks=stats["total_chunks"],
        vector_store_status=stats["vector_store_status"],
        websites=websites_data
    )
