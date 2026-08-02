"""AI 383 - Task Manager Tool"""
from agent import database as db

async def execute(params: dict) -> dict:
    action = params.get("action", "list")
    try:
        if action == "add":
            task_id = await db.add_task(
                title=params.get("title", "Untitled"),
                description=params.get("description", ""),
                priority=params.get("priority", "normal"),
                due_date=params.get("due_date"),
                tags=params.get("tags", [])
            )
            return {"status": "success", "message": f"Da them task #{task_id}", "task_id": task_id}
        elif action == "list":
            tasks = await db.get_tasks(status=params.get("status"))
            return {"status": "success", "tasks": tasks, "count": len(tasks)}
        elif action == "update":
            task_id = params.get("task_id")
            if not task_id: return {"status": "error", "message": "Can task_id"}
            updates = {k: params[k] for k in ["title","description","status","priority","due_date","tags"] if k in params}
            await db.update_task(task_id, **updates)
            return {"status": "success", "message": f"Da cap nhat task #{task_id}"}
        elif action == "complete":
            task_id = params.get("task_id")
            if not task_id: return {"status": "error", "message": "Can task_id"}
            await db.update_task(task_id, status="done")
            return {"status": "success", "message": f"Hoan thanh task #{task_id}!"}
        elif action == "delete":
            task_id = params.get("task_id")
            if not task_id: return {"status": "error", "message": "Can task_id"}
            await db.delete_task(task_id)
            return {"status": "success", "message": f"Da xoa task #{task_id}"}
        else:
            return {"status": "error", "message": f"Action '{action}' khong hop le"}
    except Exception as e:
        return {"status": "error", "message": f"Loi: {str(e)}"}
