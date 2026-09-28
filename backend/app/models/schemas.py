from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceAttribution(BaseModel):
    chunk_id: Optional[str] = None
    website_id: str
    website_name: str
    url: str
    title: str
    category: Optional[str] = "General"
    snippet: str
    relevance_score: float = Field(0.95, description="Cosine relevance similarity score (0.0 - 1.0)")

class QueryRequest(BaseModel):
    question: str = Field(..., description="User query about Brillanz Group companies")
    website_filter: Optional[str] = Field(None, description="Optional website filter (e.g. 'softoo', 'okoinsights', 'yanipro')")
    top_k: Optional[int] = Field(4, description="Number of context chunks to retrieve (1-10)", ge=1, le=10)

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceAttribution]
    website_filter: Optional[str] = None
    processing_time_ms: float
    grounded: bool = True
    embedding_mode: Optional[str] = "semantic_vector"

class IngestRequest(BaseModel):
    target_websites: Optional[List[str]] = Field(None, description="List of website IDs to crawl/ingest or null for all 7")
    max_pages_per_site: Optional[int] = Field(3, description="Max pages to crawl per site (1-10)", ge=1, le=10)
    force_refresh: bool = False

class IngestResponse(BaseModel):
    status: str
    total_pages_scraped: int
    total_chunks_created: int
    duration_seconds: float
    websites_processed: List[str]
    auto_reindexed: bool = True

class RebuildIndexResponse(BaseModel):
    status: str
    collection_name: str
    total_vectors_indexed: int
    embedding_mode: str
    duration_seconds: float
    message: str

class WebsiteSummary(BaseModel):
    id: str
    name: str
    url: str
    category: str
    tagline: str
    total_pages_indexed: int = 0
    total_chunks: int = 0
    status: str = "active"

class StatsResponse(BaseModel):
    total_websites: int
    total_documents: int
    total_chunks: int
    vector_store_status: str
    websites: List[WebsiteSummary]

class ChunkItem(BaseModel):
    chunk_id: str
    document_id: Optional[str]
    text: str
    character_count: int
    metadata: Dict[str, Any]

class ChunkListResponse(BaseModel):
    total_chunks: int
    returned_chunks: int
    website_filter: Optional[str] = None
    chunks: List[ChunkItem]
