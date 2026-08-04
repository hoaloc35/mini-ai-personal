"""AI 383 - File Manager Tool"""
import os
from pathlib import Path
from agent import database as db
from config import UPLOAD_DIR

async def execute(params: dict) -> dict:
    action = params.get("action", "list")
    try:
        if action == "scan_dir":
            path = params.get("path", str(UPLOAD_DIR))
            return await _scan_directory(path)
        elif action == "search":
            query = params.get("query", "")
            if not query: return {"status": "error", "message": "Can tu khoa"}
            files = await db.search_files(query)
            return {"status": "success", "files": files, "count": len(files)}
        elif action == "list":
            files = await db.get_all_files(limit=params.get("limit", 50))
            return {"status": "success", "files": files, "count": len(files)}
        elif action == "index":
            filepath = params.get("path", "")
            if not filepath: return {"status": "error", "message": "Can duong dan file"}
            p = Path(filepath)
            if not p.exists(): return {"status": "error", "message": f"File khong ton tai"}
            await db.index_file(filename=p.name, filepath=str(p.absolute()), filetype=p.suffix, size=p.stat().st_size, tags=params.get("tags", []), description=params.get("description", ""))
            return {"status": "success", "message": f"Da index file: {p.name}"}
        elif action == "info":
            filepath = params.get("path", "")
            p = Path(filepath)
            if not p.exists(): return {"status": "error", "message": "File khong ton tai"}
            stat = p.stat()
            return {"status": "success", "file": {"name": p.name, "path": str(p.absolute()), "type": p.suffix, "size": stat.st_size, "size_human": _human_size(stat.st_size)}}
        else:
            return {"status": "error", "message": f"Action '{action}' khong hop le"}
    except Exception as e:
        return {"status": "error", "message": f"Loi: {str(e)}"}

async def _scan_directory(path):
    p = Path(path)
    if not p.exists(): return {"status": "error", "message": f"Thu muc khong ton tai"}
    indexed = 0; errors = 0; file_types = {}
    for item in p.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            try:
                ext = item.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                await db.index_file(filename=item.name, filepath=str(item.absolute()), filetype=ext, size=item.stat().st_size)
                indexed += 1
            except: errors += 1
    return {"status": "success", "message": f"Da scan {path}", "indexed": indexed, "errors": errors, "file_types": file_types}

def _human_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
