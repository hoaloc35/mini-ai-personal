"""AI 383 v4.0 - Gemini Native Tool-Calling
AI tu dong chon tool phu hop qua function-calling."""
import json, re
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME, SYSTEM_PROMPT

def _build_function_declarations(tools_dict):
    declarations = []
    tool_schemas = {
        "search_web": {"description": "Tim kiem tren internet", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Tu khoa tim kiem"}, "num_results": {"type": "integer", "description": "So ket qua"}}, "required": ["query"]}},
        "manage_tasks": {"description": "Quan ly todo/nhac nho", "parameters": {"type": "object", "properties": {"action": {"type": "string"}, "title": {"type": "string"}, "task_id": {"type": "integer"}}, "required": ["action"]}},
        "manage_files": {"description": "Quan ly file", "parameters": {"type": "object", "properties": {"action": {"type": "string"}, "query": {"type": "string"}, "path": {"type": "string"}}, "required": ["action"]}},
        "learn_knowledge": {"description": "Hoc kien thuc moi", "parameters": {"type": "object", "properties": {"action": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}}, "required": ["action"]}},
        "query_knowledge": {"description": "Tra cuu kien thuc", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        "translate": {"description": "Dich van ban", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "target_lang": {"type": "string"}}, "required": ["text"]}},
        "run_code": {"description": "Chay code Python", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}},
        "manage_notes": {"description": "Ghi chu thong minh", "parameters": {"type": "object", "properties": {"action": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "string"}}, "required": ["action"]}},
        "spawn_subagent": {"description": "Tao SubAgent", "parameters": {"type": "object", "properties": {"agent_type": {"type": "string"}, "task": {"type": "string"}}, "required": ["agent_type", "task"]}},
        "rag_query": {"description": "Hoi dap tren tai lieu", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "top_k": {"type": "integer"}}, "required": ["query"]}},
        "mcp_call": {"description": "Goi MCP tool", "parameters": {"type": "object", "properties": {"action": {"type": "string"}, "server_name": {"type": "string"}, "tool_name": {"type": "string"}}, "required": ["action"]}},
    }
    for tool_name in tools_dict:
        if tool_name in tool_schemas:
            schema = tool_schemas[tool_name]
            declarations.append(genai.protos.FunctionDeclaration(name=tool_name, description=schema["description"], parameters=schema["parameters"]))
    return declarations

def create_tool_enabled_model(tools_dict, system_prompt=None):
    if not GEMINI_API_KEY: return None, False
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        declarations = _build_function_declarations(tools_dict)
        if declarations:
            tools_config = genai.protos.Tool(function_declarations=declarations)
            model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=system_prompt or SYSTEM_PROMPT, tools=[tools_config])
            return model, True
    except Exception:
        pass
    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=system_prompt or SYSTEM_PROMPT)
    return model, False

async def handle_native_tool_call(response, tools_dict):
    results = []
    for part in response.parts:
        if hasattr(part, "function_call") and part.function_call:
            fn = part.function_call
            tool_name = fn.name
            args = dict(fn.args) if fn.args else {}
            if tool_name in tools_dict:
                try:
                    result = await tools_dict[tool_name](args)
                    results.append({"tool": tool_name, "result": result})
                except Exception as e:
                    results.append({"tool": tool_name, "error": str(e)})
            else:
                results.append({"tool": tool_name, "error": f"Tool '{tool_name}' khong ton tai"})
    return results

def extract_tool_call_from_text(text):
    patterns = [
        r'\{"tool"\s*:\s*"(\w+)"\s*,\s*"params"\s*:\s*(\{[^}]*\})\}',
        r'```json\s*(\{.*?\})\s*```',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                if len(match.groups()) == 2:
                    return match.group(1), json.loads(match.group(2))
                else:
                    data = json.loads(match.group(1))
                    if "tool" in data:
                        return data["tool"], data.get("params", {})
            except (json.JSONDecodeError, KeyError):
                continue
    try:
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("{") and '"tool"' in line:
                data = json.loads(line)
                if "tool" in data:
                    return data["tool"], data.get("params", {})
    except: pass
    return None, None
