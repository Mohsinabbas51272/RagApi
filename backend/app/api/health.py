from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Brillanz RAG Platform API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "day": "Day 1 Architecture Foundation"
    }
