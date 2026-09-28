#!/usr/bin/env python3
"""
CLI Vector Index Builder for Brillanz Group Websites
Usage:
    python scripts/build_index.py
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.vector_store import VectorStoreManager
from app.services.chunker import ChunkerService

def main():
    print("========================================================")
    print("🧠 Brillanz Group Vector Database Index Builder (Day 3)")
    print("========================================================")
    
    start_time = time.time()
    vstore = VectorStoreManager()
    
    print("\n1. Chunking raw crawled website documents...")
    res = vstore.rebuild_index()
    
    duration = round(time.time() - start_time, 2)
    print(f"\n✅ Indexing Completed in {duration}s!")
    print(f"  • Total Vectors Indexed: {res.get('total_vectors')}")
    print(f"  • Embedding Engine Mode: {res.get('mode')}")
    
    # Test sample queries
    test_queries = [
        ("Softoo engineering services", "softoo"),
        ("YaniPro autonomous AI audit and compliance", "yanipro"),
        ("Cratus theft resistance cabinet smart city", "cratus"),
    ]
    
    print("\n🔍 Running Validation Semantic Vector Queries:")
    for query, site in test_queries:
        results = vstore.query_similar_chunks(query, website_filter=site, top_k=2)
        print(f"\nQuery: '{query}' (Filter: {site})")
        for idx, r in enumerate(results, 1):
            print(f"  [{idx}] {r['title']} ({r['relevance_score']*100:.1f}% match) -> {r['url']}")
            print(f"      Snippet: {r['snippet'][:120]}...")

if __name__ == "__main__":
    main()
