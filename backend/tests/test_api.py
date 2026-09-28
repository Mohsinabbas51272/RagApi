import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Verifies that the /api/health endpoint returns healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data

def test_list_websites(client):
    """Verifies that all 7 Brillanz companies are registered."""
    res = client.get("/api/websites")
    assert res.status_code == 200
    data = res.json()
    websites = data.get("websites", [])
    assert len(websites) == 7
    site_ids = [w["id"] for w in websites]
    assert "softoo" in site_ids
    assert "okoinsights" in site_ids
    assert "yanipro" in site_ids
    assert "cratus" in site_ids
    assert "sctechglobal" in site_ids
    assert "thunderenergy" in site_ids
    assert "scorpbit" in site_ids

def test_get_stats(client):
    """Verifies stats endpoint returns total counts and breakdown."""
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_websites"] == 7
    assert data["total_documents"] > 0
    assert data["total_chunks"] > 0
    assert len(data["websites"]) == 7

def test_query_softoo_services(client):
    """Tests semantic query retrieval with Softoo filter."""
    res = client.post("/api/query", json={
        "question": "What custom software engineering services does Softoo offer?",
        "website_filter": "softoo",
        "top_k": 3
    })
    assert res.status_code == 200
    data = res.json()
    assert data["question"] == "What custom software engineering services does Softoo offer?"
    assert len(data["sources"]) > 0
    assert "Softoo" in data["sources"][0]["website_name"]
    assert data["grounded"] is True

def test_query_yanipro_agents(client):
    """Tests semantic query retrieval with YaniPro filter."""
    res = client.post("/api/query", json={
        "question": "How do YaniPro AI autonomous agents automate compliance?",
        "website_filter": "yanipro",
        "top_k": 3
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["sources"]) > 0
    assert data["sources"][0]["website_id"] == "yanipro"

def test_anti_hallucination_guardrail_refusal(client):
    """Tests that out-of-domain queries are rejected without fabrication."""
    res = client.post("/api/query", json={
        "question": "How much does Softoo charge for pepperoni pizza and Mars rockets?"
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["sources"]) == 0
    assert "could not find information" in data["answer"].lower()

def test_query_empty_question_validation(client):
    """Verifies that an empty question fails with 400 Bad Request."""
    res = client.post("/api/query", json={"question": "   "})
    assert res.status_code == 400

def test_inspect_chunks(client):
    """Verifies the /api/chunks inspection endpoint."""
    res = client.get("/api/chunks?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["returned_chunks"] <= 5
    assert len(data["chunks"]) > 0
    assert "chunk_id" in data["chunks"][0]
    assert "metadata" in data["chunks"][0]

def test_rebuild_index_endpoint(client):
    """Verifies the /api/rebuild-index endpoint."""
    res = client.post("/api/rebuild-index")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["total_vectors_indexed"] > 0
