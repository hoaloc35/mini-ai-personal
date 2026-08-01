#!/usr/bin/env python3
"""
+===================================================+
|           AI 383 -- Operation OS v3.0              |
|       AI Ca Nhan Da Nang cho Android + Windows     |
|                                                    |
|  Chat thong minh (Gemini AI)                       |
|  Bach khoa toan thu + Tu hoc                       |
|  Tim kiem web                                      |
|  Quan ly task                                      |
|  Quan ly file                                      |
|  Plugin system mo rong                             |
|  AI Tools: Image / Video / Music generation        |
|  NEW v3.0: Multi-Agent SubAgent System             |
|  NEW v3.0: Translation (16+ languages)             |
|  NEW v3.0: Safe Code Runner (sandboxed)            |
|  NEW v3.0: Smart Notes (tags, search, Markdown)    |
+===================================================+

Cach chay:
    python main.py

Mo trinh duyet:
    http://localhost:8383
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from config import HOST, PORT, DB_PATH, PLUGINS_DIR, AGENT_NAME, AGENT_VERSION
from agent.database import init_db, set_db_path
from agent.plugins import load_plugins
from api.routes import router

# === App Setup ===
app = FastAPI(
    title=f"{AGENT_NAME} Operation OS",
    description="AI Ca Nhan Da Nang — v3.0 with Multi-Agent, Code Runner, Notes, Translation",
    version="3.0.0"
)

# Include API routes
app.include_router(router)

# Serve static files (UI)
UI_DIR = Path(__file__).parent / "ui"
if UI_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


@app.get("/")
async def serve_index():
    """Serve the main UI."""
    index_path = UI_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": f"{AGENT_NAME} Operation OS is running!", "api_docs": "/docs"}


@app.on_event("startup")
async def startup():
    """Initialize database and plugins on startup."""
    print(f"""
+===================================================+
|           AI 383 -- Operation OS v{AGENT_VERSION}              |
|       Smart. Creative. Multi-Agent. Unstoppable.   |
+===================================================+
|  NEW: SubAgent System (explorer/coder/planner/     |
|       researcher)                                  |
|  NEW: Translation (16+ languages)                  |
|  NEW: Safe Code Runner (sandboxed Python)          |
|  NEW: Smart Notes (tags, search, pin, Markdown)    |
+===================================================+
    """)

    # Init database
    set_db_path(DB_PATH)
    await init_db()
    print(f"  Database: {DB_PATH}")

    # Load plugins
    print(f"  Loading plugins from: {PLUGINS_DIR}")
    await load_plugins(PLUGINS_DIR)

    print(f"\n  Server: http://localhost:{PORT}")
    print(f"  API Docs: http://localhost:{PORT}/docs")
    print(f"  UI: http://localhost:{PORT}")
    print(f"\n  AI 383 v{AGENT_VERSION} is Ready!\n")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
