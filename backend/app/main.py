import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.health import router as health_router
from app.config import DEBUG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Brillanz Group Multi-Website RAG Platform API",
    description="Intelligent RAG system for Softoo, OKO Insights, YaniPro, Cratus, SC Tech Global, Thunder Energy AI, and Scorpbit.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(api_router, prefix="/api", tags=["RAG Services"])

@app.get("/")
def root():
    return {
        "message": "Brillanz Group Multi-Website RAG API is live",
        "documentation": "/docs",
        "health_check": "/api/health",
        "stats": "/api/stats"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=DEBUG)
