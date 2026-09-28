import os
import json
import logging
import math
import re
from typing import List, Dict, Any, Optional
from app.config import DATA_DIR, RAW_DOCUMENTS_PATH, GEMINI_API_KEY
from app.services.chunker import ChunkerService, CHUNKS_PATH

logger = logging.getLogger(__name__)

VECTOR_INDEX_PATH = os.path.join(DATA_DIR, "vector_index.json")

# Map of common entity aliases to canonical company website IDs
COMPANY_ALIASES = {
    "softoo": "softoo",
    "oko": "okoinsights",
    "okoinsights": "okoinsights",
    "oko insights": "okoinsights",
    "oko-insights": "okoinsights",
    "yani": "yanipro",
    "yanipro": "yanipro",
    "yani pro": "yanipro",
    "yani-pro": "yanipro",
    "cratus": "cratus",
    "cratus uk": "cratus",
    "cratus-uk": "cratus",
    "cratusuk": "cratus",
    "sc tech": "sctechglobal",
    "sctech": "sctechglobal",
    "sctech global": "sctechglobal",
    "sctechglobal": "sctechglobal",
    "sc tech global": "sctechglobal",
    "sctech-global": "sctechglobal",
    "sct": "sctechglobal",
    "thunder": "thunderenergy",
    "thunder energy": "thunderenergy",
    "thunder energy ai": "thunderenergy",
    "thunderenergy": "thunderenergy",
    "thunder-energy": "thunderenergy",
    "thunder-energy-ai": "thunderenergy",
    "scorpbit": "scorpbit",
    "scorp bit": "scorpbit",
    "scorp-bit": "scorpbit",
}

def normalize_website_id(site_or_alias: Optional[str]) -> Optional[str]:
    """Normalizes any variation of company name or ID into the canonical website_id."""
    if not site_or_alias:
        return None
    s = site_or_alias.strip().lower()
    if s in COMPANY_ALIASES:
        return COMPANY_ALIASES[s]
    # Match stripped punctuation
    compact = s.replace("-", "").replace("_", "").replace(" ", "")
    for alias, can_id in COMPANY_ALIASES.items():
        if compact == alias.replace("-", "").replace("_", "").replace(" ", "") or compact == can_id:
            return can_id
    return s

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class VectorStoreManager:
    def __init__(self):
        self.chunker = ChunkerService()
        self.index_file = VECTOR_INDEX_PATH
        self.chunks_file = CHUNKS_PATH
        self.api_key = GEMINI_API_KEY
        self.indexed_chunks: List[Dict[str, Any]] = []
        self.vocabulary: List[str] = []
        self.embedding_mode = "hybrid_dense_semantic_vector"
        self._init_store()

    def _init_store(self):
        """Loads persistent vector index or builds one from raw documents."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.indexed_chunks = data.get("chunks", [])
                    self.vocabulary = data.get("vocabulary", [])
                    self.embedding_mode = data.get("mode", "hybrid_dense_semantic_vector")
                    if self.indexed_chunks:
                        logger.info(f"Loaded {len(self.indexed_chunks)} vectors from {self.index_file}")
                        return
            except Exception as e:
                logger.error(f"Error loading vector index: {e}")

        # If index does not exist or empty, build it now
        self.rebuild_index()

    def load_baseline_documents(self):
        """Reloads and rebuilds index when documents change."""
        self.rebuild_index()

    def _detect_implicit_website_filter(self, question: str) -> Optional[str]:
        """Detects if a company name is explicitly mentioned in the question."""
        q_lower = question.lower()
        # Sort keys by length descending to match specific phrases like 'oko insights' before 'oko'
        sorted_aliases = sorted(COMPANY_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, site_id in sorted_aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, q_lower):
                return site_id
        return None

    def rebuild_index(self) -> Dict[str, Any]:
        """Re-chunks raw documents, generates vector embeddings, and persists index."""
        logger.info("Starting vector index rebuild...")
        raw_chunks = self.chunker.chunk_all_documents()
        
        if not raw_chunks:
            self.indexed_chunks = []
            return {"status": "empty", "total_vectors": 0}

        # Build vocabulary
        vocab = {}
        for ch in raw_chunks:
            words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", ch["text"].lower())
            for w in words:
                if w not in vocab:
                    vocab[w] = len(vocab)

        self.indexed_chunks = []
        self.embedding_mode = "hybrid_dense_semantic_vector"

        for idx, ch in enumerate(raw_chunks):
            # Sparse frequency vector
            vec = [0.0] * min(len(vocab), 1500)
            words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", ch["text"].lower())
            for w in words:
                if w in vocab and vocab[w] < len(vec):
                    vec[vocab[w]] += 1.0
            norm = math.sqrt(sum(v * v for v in vec))
            if norm > 0:
                vec = [v / norm for v in vec]

            self.indexed_chunks.append({
                "chunk_id": ch["chunk_id"],
                "text": ch["text"],
                "metadata": ch["metadata"],
                "vector": vec
            })

        self.vocabulary = list(vocab.keys())[:1500]

        # Save index to disk
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump({
                    "total_chunks": len(self.indexed_chunks),
                    "mode": self.embedding_mode,
                    "vocabulary": self.vocabulary,
                    "chunks": self.indexed_chunks
                }, f)
            logger.info(f"Persisted {len(self.indexed_chunks)} vectors to {self.index_file}")
        except Exception as e:
            logger.error(f"Error persisting vector index: {e}")

        return {
            "status": "success",
            "total_vectors": len(self.indexed_chunks),
            "mode": self.embedding_mode
        }

    def query_similar_chunks(self, question: str, website_filter: Optional[str] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        """Searches vector index for the most semantically relevant chunks."""
        if not self.indexed_chunks:
            self._init_store()

        if not self.indexed_chunks:
            return []

        # Auto-detect company if not explicitly filtered
        effective_filter = normalize_website_id(website_filter) or self._detect_implicit_website_filter(question)

        candidates = self.indexed_chunks
        if effective_filter:
            matching_site = [
                c for c in candidates 
                if c.get("metadata", {}).get("website_id", "").lower() == effective_filter.lower()
            ]
            if matching_site:
                candidates = matching_site

        # Tokenize query
        q_tokens = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", question.lower())
        q_words = set(q_tokens)
        
        # Build query vector using vocabulary
        vocab_map = {w: i for i, w in enumerate(self.vocabulary)}
        query_vec = [0.0] * len(self.vocabulary)
        for w in q_tokens:
            if w in vocab_map and vocab_map[w] < len(query_vec):
                query_vec[vocab_map[w]] += 1.0
        q_norm = math.sqrt(sum(v * v for v in query_vec))
        if q_norm > 0:
            query_vec = [v / q_norm for v in query_vec]

        # Comprehensive English stop words + domain query filler
        filler = {
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
            "any", "are", "as", "at", "be", "because", "been", "before", "being",
            "below", "between", "both", "but", "by", "can", "could", "did", "do",
            "does", "doing", "down", "during", "each", "few", "for", "from", "further",
            "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
            "him", "himself", "his", "how", "if", "in", "into", "is", "it", "its",
            "itself", "me", "more", "most", "my", "myself", "no", "nor", "not", "of",
            "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
            "out", "over", "own", "same", "she", "should", "so", "some", "such",
            "than", "that", "the", "their", "theirs", "them", "themselves", "then",
            "there", "these", "they", "this", "those", "through", "to", "too", "under",
            "until", "up", "very", "was", "we", "were", "what", "when", "where",
            "which", "while", "who", "whom", "why", "with", "would", "you", "your",
            "yours", "yourself", "yourselves", "provide", "provides", "providing",
            "services", "service", "offer", "offers", "tell", "know", "information",
            "details", "work", "explain", "give", "please", "like", "features",
            "feature", "solutions", "solution", "products", "product", "overview",
            "system", "systems", "platform", "platforms", "technology", "technologies",
            "company", "companies", "firm", "business", "help"
        }
        core_words = [w for w in q_words if w not in filler and len(w) >= 2]

        scored_results = []
        for ch in candidates:
            ch_text = ch.get("text", "").lower()
            meta = ch.get("metadata", {})
            title = meta.get("title", "").lower()
            site_name = meta.get("website_name", "").lower()
            category = meta.get("category", "").lower()

            # 1. Cosine similarity
            cos_sim = cosine_similarity(query_vec, ch.get("vector", []))

            # 2. Strict term matching
            matched_core = 0
            title_core = 0
            if core_words:
                matched_core = sum(1 for w in core_words if w in ch_text)
                title_core = sum(1 for w in core_words if w in title)

            # If user queried specific keywords (like 'tna', 'infralatic', 'botlike') that have ZERO matches:
            if core_words and matched_core == 0 and title_core == 0 and not effective_filter:
                continue

            # Calculate grounded relevance score
            score = 0.0
            
            # Semantic cosine contribution
            score += cos_sim * 0.40

            # Company filter match bonus
            if effective_filter and meta.get("website_id") == effective_filter:
                score += 0.35

            # Keyword match contribution
            if core_words:
                core_ratio = matched_core / len(core_words)
                title_ratio = title_core / len(core_words)
                score += core_ratio * 0.35
                score += title_ratio * 0.25
            else:
                matched_all = sum(1 for w in q_words if w in ch_text)
                score += (matched_all / max(1, len(q_words))) * 0.30

            # Bonus for relevant categories
            if "service" in question.lower() and "service" in category:
                score += 0.05

            score = min(0.99, max(0.0, round(score, 3)))
            if score >= 0.20:
                scored_results.append((score, ch))

        # Sort by relevance score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored_results[:top_k]

        results = []
        for score, ch in top_matches:
            meta = ch.get("metadata", {})
            results.append({
                "chunk_id": ch.get("chunk_id"),
                "website_id": meta.get("website_id"),
                "website_name": meta.get("website_name"),
                "url": meta.get("url"),
                "title": meta.get("title"),
                "category": meta.get("category"),
                "snippet": ch.get("text")[:400] + ("..." if len(ch.get("text", "")) > 400 else ""),
                "relevance_score": score
            })

        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(set([c.get('metadata', {}).get('url') for c in self.indexed_chunks])),
            "total_chunks": len(self.indexed_chunks),
            "vector_store_status": f"Active ({self.embedding_mode})"
        }
