const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    console.error('API health check error:', err);
    return { status: 'offline' };
  }
}

export async function fetchWebsites() {
  try {
    const res = await fetch(`${API_BASE_URL}/websites`);
    if (!res.ok) throw new Error('Failed to fetch websites');
    return await res.json();
  } catch (err) {
    console.error('API fetch websites error:', err);
    return { websites: [] };
  }
}

export async function fetchStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return await res.json();
  } catch (err) {
    console.error('API fetch stats error:', err);
    return null;
  }
}

export async function fetchChunks(websiteId = null, limit = 50) {
  try {
    const url = new URL(`${API_BASE_URL}/chunks`);
    if (websiteId) url.searchParams.append('website_id', websiteId);
    url.searchParams.append('limit', limit);
    
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch chunks');
    return await res.json();
  } catch (err) {
    console.error('API fetch chunks error:', err);
    return { chunks: [], total_chunks: 0 };
  }
}

export async function queryRAG(question, websiteFilter = null) {
  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        website_filter: websiteFilter || null,
        top_k: 4
      })
    });
    if (!res.ok) throw new Error('Query request failed');
    return await res.json();
  } catch (err) {
    console.error('Query RAG error:', err);
    throw err;
  }
}

export async function triggerRebuildIndex() {
  try {
    const res = await fetch(`${API_BASE_URL}/rebuild-index`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Rebuild index failed');
    return await res.json();
  } catch (err) {
    console.error('Rebuild index error:', err);
    throw err;
  }
}

export async function triggerIngest(targetWebsites = null) {
  try {
    const res = await fetch(`${API_BASE_URL}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_websites: targetWebsites })
    });
    if (!res.ok) throw new Error('Ingest trigger failed');
    return await res.json();
  } catch (err) {
    console.error('Ingest trigger error:', err);
    throw err;
  }
}
