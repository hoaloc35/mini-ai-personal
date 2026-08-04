"""AI 383 - Smart Notes Tool"""
import json
from agent import database as db

async def execute(params: dict) -> dict:
    action = params.get("action", "list")
    try:
        if action == "create":
            title = params.get("title", "")
            content = params.get("content", "")
            if not title: return {"status": "error", "message": "Can tieu de"}
            note_id = await db.add_note(title=title, content=content, tags=params.get("tags", []), pinned=params.get("pinned", False))
            return {"status": "success", "message": f"Da tao ghi chu #{note_id}: {title}", "note_id": note_id}
        elif action == "list":
            tag = params.get("tag")
            limit = params.get("limit", 50)
            if tag:
                notes = await db.search_notes(tag, limit)
            else:
                notes = await db.get_all_notes(limit)
            return {"status": "success", "notes": notes, "count": len(notes)}
        elif action == "get":
            note_id = params.get("note_id")
            if not note_id: return {"status": "error", "message": "Can note_id"}
            note = await db.get_note(note_id)
            if not note: return {"status": "error", "message": f"Khong tim thay ghi chu #{note_id}"}
            return {"status": "success", "note": note}
        elif action == "update":
            note_id = params.get("note_id")
            if not note_id: return {"status": "error", "message": "Can note_id"}
            updates = {}
            for key in ["title", "content", "tags", "pinned"]:
                if key in params: updates[key] = params[key]
            if not updates: return {"status": "error", "message": "Khong co gi de cap nhat"}
            await db.update_note(note_id, **updates)
            return {"status": "success", "message": f"Da cap nhat ghi chu #{note_id}"}
        elif action == "delete":
            note_id = params.get("note_id")
            if not note_id: return {"status": "error", "message": "Can note_id"}
            await db.delete_note(note_id)
            return {"status": "success", "message": f"Da xoa ghi chu #{note_id}"}
        elif action == "search":
            query = params.get("query", "")
            if not query: return {"status": "error", "message": "Can tu khoa tim kiem"}
            notes = await db.search_notes(query, params.get("limit", 20))
            return {"status": "success", "notes": notes, "count": len(notes), "query": query}
        elif action == "pin":
            note_id = params.get("note_id")
            if not note_id: return {"status": "error", "message": "Can note_id"}
            await db.update_note(note_id, pinned=True)
            return {"status": "success", "message": f"Da ghim ghi chu #{note_id}"}
        elif action == "unpin":
            note_id = params.get("note_id")
            if not note_id: return {"status": "error", "message": "Can note_id"}
            await db.update_note(note_id, pinned=False)
            return {"status": "success", "message": f"Da bo ghim ghi chu #{note_id}"}
        else:
            return {"status": "error", "message": f"Action '{action}' khong hop le"}
    except Exception as e:
        return {"status": "error", "message": f"Loi: {str(e)}"}
