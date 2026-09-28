#!/usr/bin/env python3
"""
Automated RAG Grounding & Anti-Hallucination Evaluator
Usage:
    python scripts/test_rag_grounding.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.vector_store import VectorStoreManager
from app.services.rag_engine import RAGEngine

def main():
    print("================================================================")
    print("🛡️  Brillanz Group RAG Grounding & Anti-Hallucination Evaluator")
    print("================================================================")

    vstore = VectorStoreManager()
    rag = RAGEngine(vector_store=vstore)

    in_domain_tests = [
        ("What custom software engineering services does Softoo offer?", "softoo"),
        ("How does YaniPro automate AI audit and compliance workflows?", "yanipro"),
        ("What smart city and theft resistance solutions does Cratus UK provide?", "cratus"),
        ("What telecom and supply chain infrastructure does SC Tech Global enable?", "sctechglobal"),
        ("How does Thunder Energy AI optimize battery storage systems?", "thunderenergy"),
        ("What offensive cybersecurity services does Scorpbit provide?", "scorpbit"),
        ("How does OKO Insights use AI computer vision for crowd analytics?", "okoinsights")
    ]

    out_of_domain_tests = [
        "Does Softoo sell pepperoni pizza?",
        "How much does Cratus charge for Mars rocket fuel?",
        "Can I play casino roulette with Thunder Energy AI?",
        "What is the weather in Tokyo today?"
    ]

    print("\n--- Phase 1: In-Domain Verified Retrieval Evaluation ---")
    in_domain_success = 0
    for q, expected_site in in_domain_tests:
        res = rag.query(q, website_filter=expected_site)
        print(f"\nQ: '{q}'")
        print(f"Filter: {expected_site} | Time: {res.processing_time_ms}ms")
        print(f"Sources Count: {len(res.sources)}")
        if res.sources:
            print(f"Top Source: {res.sources[0].title} ({res.sources[0].url}) - Match: {res.sources[0].relevance_score*100:.1f}%")
            print(f"Answer Preview: {res.answer[:120]}...")
            in_domain_success += 1
        else:
            print("❌ FAILED: No sources returned for in-domain query")

    print(f"\nIn-Domain Success Rate: {in_domain_success}/{len(in_domain_tests)} ({in_domain_success/len(in_domain_tests)*100:.1f}%)")

    print("\n--- Phase 2: Anti-Hallucination & Out-of-Domain Refusal Evaluation ---")
    refusal_success = 0
    for q in out_of_domain_tests:
        res = rag.query(q)
        print(f"\nTrick Q: '{q}'")
        print(f"Sources: {len(res.sources)} | Grounded: {res.grounded}")
        print(f"Response: {res.answer}")
        if "could not find information" in res.answer.lower() and len(res.sources) == 0:
            print("✅ PASSED: Refusal triggered without hallucination.")
            refusal_success += 1
        else:
            print("❌ FAILED: Hallucination detected or failed refusal.")

    print(f"\nAnti-Hallucination Guardrail Success Rate: {refusal_success}/{len(out_of_domain_tests)} ({refusal_success/len(out_of_domain_tests)*100:.1f}%)")

    print("\n================================================================")
    if in_domain_success == len(in_domain_tests) and refusal_success == len(out_of_domain_tests):
        print("🎉 ALL RAG GROUNDING & ANTI-HALLUCINATION TESTS PASSED (100%)!")
    else:
        print("⚠️ Some tests did not pass.")

if __name__ == "__main__":
    main()
