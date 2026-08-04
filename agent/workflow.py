"""AI 383 v4.0 - Agent Workflow Engine
Chay nhieu buoc tu dong: Research & Report, Daily Digest, Code Review."""
import json, time, asyncio
from agent import database as db

TEMPLATES = {
    "research_report": {
        "name": "Research & Report",
        "description": "Tim kiem web + tong hop kien thuc + tao bao cao",
        "steps": [
            {"type": "tool_call", "tool": "search_web", "params": {"query": "{topic}"}, "name": "Tim kiem"},
            {"type": "ai_prompt", "prompt": "Tong hop ket qua tim kiem ve {topic} thanh bao cao ngan gon", "name": "Tong hop"},
        ]
    },
    "daily_digest": {
        "name": "Daily Digest",
        "description": "Tong hop tasks + notes + tin moi hang ngay",
        "steps": [
            {"type": "tool_call", "tool": "manage_tasks", "params": {"action": "list"}, "name": "Lay tasks"},
            {"type": "tool_call", "tool": "manage_notes", "params": {"action": "list", "limit": 5}, "name": "Lay notes"},
            {"type": "ai_prompt", "prompt": "Tong hop tasks va notes thanh bao cao hang ngay", "name": "Tong hop"},
        ]
    },
    "code_review": {
        "name": "Code Review",
        "description": "Kiem tra cu phap + chay code + AI review",
        "steps": [
            {"type": "tool_call", "tool": "run_code", "params": {"code": "{code}"}, "name": "Chay code"},
            {"type": "ai_prompt", "prompt": "Review code sau va goi y cai tien:\n{code}", "name": "AI Review"},
        ]
    },
}

class WorkflowEngine:
    def __init__(self):
        self.tools = {}
        self.ai_chat = None
        self._counter = 0

    def register_tools(self, tools):
        self.tools = tools

    def set_ai_chat(self, chat_fn):
        self.ai_chat = chat_fn

    def list_templates(self):
        return {k: {"name": v["name"], "description": v["description"], "steps": len(v["steps"])} for k, v in TEMPLATES.items()}

    async def run(self, template=None, params=None, custom_steps=None, name=None, description=None):
        self._counter += 1
        wf_id = self._counter
        if template and template in TEMPLATES:
            tmpl = TEMPLATES[template]
            steps = tmpl["steps"]
            wf_name = name or tmpl["name"]
            wf_desc = description or tmpl["description"]
        elif custom_steps:
            steps = custom_steps
            wf_name = name or f"Workflow #{wf_id}"
            wf_desc = description or "Custom workflow"
        else:
            return {"status": "error", "message": "Can template hoac custom_steps"}
        params = params or {}
        await db.save_workflow(wf_id, wf_name, wf_desc, template or "custom", steps, params)
        results = []
        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i+1}")
            step_type = step.get("type", "tool_call")
            progress = (i + 1) / len(steps)
            await db.update_workflow_progress(wf_id, progress, f"Running: {step_name}")
            try:
                if step_type == "tool_call":
                    tool_name = step.get("tool", "")
                    step_params = dict(step.get("params", {}))
                    for k, v in step_params.items():
                        if isinstance(v, str):
                            for pk, pv in params.items():
                                step_params[k] = v.replace("{" + pk + "}", str(pv))
                    if tool_name in self.tools:
                        result = await self.tools[tool_name](step_params)
                        results.append({"step": step_name, "type": "tool_call", "result": result})
                    else:
                        results.append({"step": step_name, "error": f"Tool '{tool_name}' khong ton tai"})
                elif step_type == "ai_prompt":
                    prompt = step.get("prompt", "")
                    for pk, pv in params.items():
                        prompt = prompt.replace("{" + pk + "}", str(pv))
                    if self.ai_chat:
                        ai_result = await self.ai_chat(prompt)
                        results.append({"step": step_name, "type": "ai_prompt", "result": ai_result})
                    else:
                        results.append({"step": step_name, "error": "AI chat khong kha dung"})
                elif step_type == "delay":
                    await asyncio.sleep(step.get("seconds", 1))
                    results.append({"step": step_name, "type": "delay"})
            except Exception as e:
                results.append({"step": step_name, "error": str(e)})
                if not step.get("optional", False):
                    max_retries = step.get("max_retries", 0)
                    if max_retries > 0:
                        continue
        await db.update_workflow_progress(wf_id, 1.0, "Hoan thanh")
        summary = f"Workflow '{wf_name}' hoan thanh: {len(results)}/{len(steps)} buoc"
        await db.complete_workflow(wf_id, summary)
        return {"status": "success", "workflow_id": wf_id, "name": wf_name, "results": results, "summary": summary}

workflow_engine = WorkflowEngine()

async def execute(params):
    action = params.get("action", "run")
    if action == "list_templates":
        return {"status": "success", "templates": workflow_engine.list_templates()}
    elif action == "run":
        return await workflow_engine.run(template=params.get("template"), params=params.get("params", {}), custom_steps=params.get("steps"), name=params.get("name"), description=params.get("description"))
    elif action == "list":
        workflows = await db.get_workflows()
        return {"status": "success", "workflows": workflows}
    else:
        return {"status": "error", "message": f"Action '{action}' khong hop le"}
