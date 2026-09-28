import os
import json
import logging
import re
from typing import List, Dict, Any, Optional
from app.config import DATA_DIR, RAW_DOCUMENTS_PATH

logger = logging.getLogger(__name__)

CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.json")

class ChunkerService:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120):
        """
        Recursive semantic text chunker.
        :param chunk_size: Target characters per chunk
        :param chunk_overlap: Overlapping characters between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks_file = CHUNKS_PATH

    def split_text_into_chunks(self, text: str) -> List[str]:
        """Splits text intelligently using sentence and paragraph boundaries."""
        if not text or not text.strip():
            return []

        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text]

        # Break text into paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If paragraph itself is larger than chunk_size, split by sentences
            if len(para) > self.chunk_size:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 1 <= self.chunk_size:
                        current_chunk = f"{current_chunk} {sent}".strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            # Overlap by taking the tail of the current chunk
                            overlap_text = current_chunk[-self.chunk_overlap:]
                            current_chunk = f"{overlap_text} {sent}".strip()
                        else:
                            # Sentence itself is huge, hard slice
                            chunks.append(sent[:self.chunk_size])
                            current_chunk = sent[self.chunk_size - self.chunk_overlap:]
            else:
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip() if current_chunk else para
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                        overlap_text = current_chunk[-self.chunk_overlap:]
                        current_chunk = f"{overlap_text}\n\n{para}".strip()
                    else:
                        current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def process_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits a single document into enriched chunks with metadata."""
        content = doc.get("content", "")
        text_chunks = self.split_text_into_chunks(content)
        total_chunks = len(text_chunks)
        
        doc_chunks = []
        for idx, text in enumerate(text_chunks):
            chunk_id = f"{doc.get('id', 'doc')}-c{idx+1:02d}"
            doc_chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc.get("id"),
                "text": text,
                "character_count": len(text),
                "metadata": {
                    "website_id": doc.get("website_id", ""),
                    "website_name": doc.get("website_name", ""),
                    "url": doc.get("url", ""),
                    "title": doc.get("title", ""),
                    "category": doc.get("category", "General"),
                    "headings": doc.get("headings", []),
                    "chunk_index": idx + 1,
                    "total_chunks": total_chunks,
                    "last_crawled": doc.get("last_crawled", "")
                }
            })
        return doc_chunks

    def chunk_all_documents(self, documents: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Processes all raw documents into chunks and writes to data/chunks.json."""
        if documents is None:
            if os.path.exists(RAW_DOCUMENTS_PATH):
                try:
                    with open(RAW_DOCUMENTS_PATH, "r", encoding="utf-8") as f:
                        documents = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading raw documents: {e}")
                    documents = []
            else:
                documents = []

        all_chunks = []
        for doc in documents:
            chunks = self.process_document(doc)
            all_chunks.extend(chunks)

        # Persist chunks
        try:
            with open(self.chunks_file, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, indent=2)
            logger.info(f"Generated and saved {len(all_chunks)} chunks to {self.chunks_file}")
        except Exception as e:
            logger.error(f"Failed to write chunks file: {e}")

        return all_chunks
