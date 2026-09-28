import os
import re
from pathlib import Path
from dotenv import load_dotenv

# Base directory paths - dynamically resolved
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Check potential locations for .env
env_files = [
    BASE_DIR / ".env",
    BASE_DIR / "backend" / ".env",
    Path.cwd() / ".env",
    Path.cwd() / "backend" / ".env"
]

gemini_key_from_file = ""
for env_path in env_files:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                        val = line.split("=", 1)[1].strip().strip("\"'").strip()
                        if val and val != "your_gemini_api_key_here":
                            gemini_key_from_file = val
        except Exception:
            pass

# App settings - prioritize environment variables (e.g. Vercel dashboard)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or gemini_key_from_file or ""
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Database & Storage paths
DATA_DIR = BASE_DIR / "data"
if not DATA_DIR.exists():
    DATA_DIR = Path.cwd() / "data"

CHROMA_PERSIST_DIRECTORY = str(DATA_DIR / "chroma_db")
CHROMA_COLLECTION_NAME = "brillanz_knowledge_base"
WEBSITES_INVENTORY_PATH = str(DATA_DIR / "websites_inventory.json")
RAW_DOCUMENTS_PATH = str(DATA_DIR / "raw_documents.json")
