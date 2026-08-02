"""
AI 383 Operation OS v4.0 - Configuration
Cau hinh he thong AI ca nhan - RAG, MCP, Workflows, Native Tool-Calling
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Paths ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PLUGINS_DIR = BASE_DIR / "plugins"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
UPLOAD_DIR = BASE_DIR / "uploads"

for d in [DATA_DIR, PLUGINS_DIR, KNOWLEDGE_DIR, UPLOAD_DIR]:
    d.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "ai383.db"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8383"))
AGENT_NAME = "AI 383"
AGENT_VERSION = "4.0"
AGENT_LANGUAGE = "vi"
MAX_HISTORY = 50
MAX_SEARCH_RESULTS = 5
SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "30"))
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))

MCP_SERVERS = {}
_mcp_json = os.getenv("MCP_SERVERS", "")
if _mcp_json:
    try:
        import json
        MCP_SERVERS = json.loads(_mcp_json)
    except: pass

IMAGE_GEN_API_KEY = os.getenv("IMAGE_GEN_API_KEY", "")
IMAGE_GEN_PROVIDER = os.getenv("IMAGE_GEN_PROVIDER", "gemini")
VIDEO_GEN_API_KEY = os.getenv("VIDEO_GEN_API_KEY", "")
MUSIC_GEN_API_KEY = os.getenv("MUSIC_GEN_API_KEY", "")

SYSTEM_PROMPT = """Ban la AI 383 v4.0 - tro ly AI ca nhan da nang.
Chat thong minh, tu hoc, tim kiem web, quan ly task/file/notes.
RAG doc tai lieu, MCP ket noi GitHub/Notion/Slack, Workflow tu dong.
Tra loi tieng Viet tu nhien, vui ve, than thien.
Khi can dung tool, tra ve JSON: {"tool": "ten_tool", "params": {...}}
"""
