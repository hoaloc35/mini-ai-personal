"""AI 383 v4.0 - Database Manager (SQLite)
Tables: conversations, tasks, knowledge, files, plugins, notes, document_chunks, workflows"""
import aiosqlite, json
from datetime import datetime
from pathlib import Path

DB_PATH = None

def set_db_path(path):
    global DB_PATH
    DB_PATH = str(path)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT DEFAULT '', status TEXT DEFAULT 'pending', priority TEXT DEFAULT 'normal', due_date TEXT, tags TEXT DEFAULT '[]', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, source TEXT DEFAULT 'user', category TEXT DEFAULT 'general', tags TEXT DEFAULT '[]', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, filepath TEXT, filetype TEXT DEFAULT '', size INTEGER DEFAULT 0, tags TEXT DEFAULT '[]', description TEXT DEFAULT '', indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS plugins (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, description TEXT DEFAULT '', filepath TEXT, enabled INTEGER DEFAULT 1, config TEXT DEFAULT '{}', installed_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS learning_sources (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, content_type TEXT DEFAULT 'text', summary TEXT DEFAULT '', raw_content TEXT DEFAULT '', learned_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, tags TEXT DEFAULT '[]', pinned INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS document_chunks (id INTEGER PRIMARY KEY AUTOINCREMENT, document_name TEXT, chunk_index INTEGER DEFAULT 0, chunk_text TEXT, file_path TEXT DEFAULT '', file_type TEXT DEFAULT '', doc_hash TEXT DEFAULT '', total_chunks INTEGER DEFAULT 0, is_metadata INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS workflows (id INTEGER PRIMARY KEY AUTOINCREMENT, workflow_id INTEGER UNIQUE, name TEXT, description TEXT DEFAULT '', template TEXT DEFAULT '', status TEXT DEFAULT 'created', steps_json TEXT DEFAULT '[]', context_json TEXT DEFAULT '{}', progress REAL DEFAULT 0.0, result_summary TEXT DEFAULT '', error TEXT DEFAULT '', created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        await db.commit()

# === Conversations ===
async def save_message(session_id, role, content):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
        await db.commit()

async def get_history(session_id, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT role, content FROM conversations WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id, limit))
        rows = await cursor.fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

# === Tasks ===
async def add_task(title, description="", priority="normal", due_date=None, tags=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO tasks (title, description, priority, due_date, tags) VALUES (?, ?, ?, ?, ?)", (title, description, priority, due_date, json.dumps(tags or [])))
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        return (await cursor.fetchone())[0]

async def get_tasks(status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            cursor = await db.execute("SELECT * FROM tasks WHERE status=? ORDER BY created_at DESC", (status,))
        else:
            cursor = await db.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        return [dict(r) for r in await cursor.fetchall()]

async def update_task(task_id, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in ("title", "description", "status", "priority", "due_date", "tags"):
                sets.append(f"{k}=?"); vals.append(json.dumps(v) if k == "tags" else v)
        if sets:
            sets.append("updated_at=?"); vals.append(datetime.now().isoformat()); vals.append(task_id)
            await db.execute(f"UPDATE tasks SET {','.join(sets)} WHERE id=?", vals)
            await db.commit()

async def delete_task(task_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM tasks WHERE id=?", (task_id,)); await db.commit()

# === Knowledge ===
async def add_knowledge(title, content, source="user", category="general", tags=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO knowledge (title, content, source, category, tags) VALUES (?, ?, ?, ?, ?)", (title, content, source, category, json.dumps(tags or [])))
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        return (await cursor.fetchone())[0]

async def search_knowledge(query, limit=5):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM knowledge WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in await cursor.fetchall()]

async def get_all_knowledge(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM knowledge ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in await cursor.fetchall()]

async def delete_knowledge(kid):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM knowledge WHERE id=?", (kid,)); await db.commit()

# === Files ===
async def index_file(filename, filepath, filetype="", size=0, tags=None, description=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO files (filename, filepath, filetype, size, tags, description) VALUES (?, ?, ?, ?, ?, ?)", (filename, filepath, filetype, size, json.dumps(tags or []), description))
        await db.commit()

async def search_files(query, limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM files WHERE filename LIKE ? OR description LIKE ? ORDER BY indexed_at DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in await cursor.fetchall()]

async def get_all_files(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM files ORDER BY indexed_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in await cursor.fetchall()]

# === Plugins ===
async def register_plugin(name, description, filepath, config=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO plugins (name, description, filepath, config) VALUES (?, ?, ?, ?)", (name, description, filepath, json.dumps(config or {})))
        await db.commit()

async def get_plugins(enabled_only=True):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM plugins WHERE enabled=1" if enabled_only else "SELECT * FROM plugins")
        return [dict(r) for r in await cursor.fetchall()]

# === Learning Sources ===
async def save_learning_source(url=None, content_type="text", summary="", raw_content=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO learning_sources (url, content_type, summary, raw_content) VALUES (?, ?, ?, ?)", (url, content_type, summary, raw_content[:50000]))
        await db.commit()

# === Notes ===
async def add_note(title, content, tags=None, pinned=False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO notes (title, content, tags, pinned) VALUES (?, ?, ?, ?)", (title, content, json.dumps(tags or []), 1 if pinned else 0))
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        return (await cursor.fetchone())[0]

async def get_note(note_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM notes WHERE id=?", (note_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

async def get_all_notes(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM notes ORDER BY pinned DESC, updated_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in await cursor.fetchall()]

async def search_notes(query, limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY pinned DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in await cursor.fetchall()]

async def update_note(note_id, **kwargs):
    async with aiosqlite.connect(DB_PATH) as db:
        sets, vals = [], []
        for k, v in kwargs.items():
            if k in ("title", "content", "tags", "pinned"):
                sets.append(f"{k}=?")
                vals.append(json.dumps(v) if k == "tags" and isinstance(v, list) else (1 if v else 0) if k == "pinned" else v)
        if sets:
            sets.append("updated_at=?"); vals.append(datetime.now().isoformat()); vals.append(note_id)
            await db.execute(f"UPDATE notes SET {','.join(sets)} WHERE id=?", vals)
            await db.commit()

async def delete_note(note_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM notes WHERE id=?", (note_id,)); await db.commit()

# === Document Chunks (RAG v4.0) ===
async def add_document_chunk(document_name, chunk_index, chunk_text, file_path="", file_type="", doc_hash="", total_chunks=0, is_metadata=False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO document_chunks (document_name, chunk_index, chunk_text, file_path, file_type, doc_hash, total_chunks, is_metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (document_name, chunk_index, chunk_text, file_path, file_type, doc_hash, total_chunks, 1 if is_metadata else 0))
        await db.commit()
        cursor = await db.execute("SELECT last_insert_rowid()")
        return (await cursor.fetchone())[0]

async def get_document_chunks(document_id=None, doc_hash=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if doc_hash:
            cursor = await db.execute("SELECT * FROM document_chunks WHERE doc_hash=? AND is_metadata=0 ORDER BY chunk_index", (doc_hash,))
        else:
            cursor = await db.execute("SELECT * FROM document_chunks WHERE is_metadata=0 ORDER BY chunk_index")
        return [dict(r) for r in await cursor.fetchall()]

async def get_documents():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM document_chunks WHERE is_metadata=1 ORDER BY created_at DESC")
        return [dict(r) for r in await cursor.fetchall()]

# === Workflows (v4.0) ===
async def save_workflow(wf_id, name, description, template, steps, context):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO workflows (workflow_id, name, description, template, steps_json, context_json, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (wf_id, name, description, template, json.dumps(steps), json.dumps(context), "running"))
        await db.commit()

async def update_workflow_progress(wf_id, progress, status_msg=""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE workflows SET progress=?, status=?, updated_at=? WHERE workflow_id=?", (progress, status_msg, datetime.now().isoformat(), wf_id))
        await db.commit()

async def complete_workflow(wf_id, summary):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE workflows SET status='completed', result_summary=?, progress=1.0, updated_at=? WHERE workflow_id=?", (summary, datetime.now().isoformat(), wf_id))
        await db.commit()

async def get_workflows(limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM workflows ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in await cursor.fetchall()]

# === Stats ===
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        for table in ["tasks", "knowledge", "files", "plugins", "learning_sources", "notes", "document_chunks", "workflows"]:
            cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM tasks WHERE status='pending'")
        stats["pending_tasks"] = (await cursor.fetchone())[0]
        return stats
