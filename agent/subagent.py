"""AI 383 - Multi-Agent SubAgent System
4 loai agent: Explorer, Coder, Planner, Researcher"""
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME

AGENT_TYPES = {
    "explorer": {"description": "Chi doc — tim kiem, duyet file", "tools": ["search_web", "manage_files", "query_knowledge"], "prompt": "Ban la explorer agent. Tim kiem va phan tich, KHONG sua doi file. Tra ve ket qua ngan gon."},
    "coder": {"description": "Day du — doc, viet, chay code", "tools": "*", "prompt": "Ban la coder agent. Viet code hieu qua. Tra ve ket qua."},
    "planner": {"description": "Chi doc — phan tich, lap ke hoach", "tools": ["search_web", "query_knowledge"], "prompt": "Ban la planner agent. Phan tich va lap ke hoach. KHONG thay doi gi."},
    "researcher": {"description": "Web search + knowledge", "tools": ["search_web", "query_knowledge", "learn_knowledge"], "prompt": "Ban la researcher agent. Nghien cuu sau ve chu de duoc giao."},
}

class SubAgent:
    def __init__(self, agent_type, tools=None):
        self.agent_type = agent_type
        self.config = AGENT_TYPES.get(agent_type, AGENT_TYPES["explorer"])
        self.tools = tools or {}
        self.history = []

    async def run(self, task, max_turns=5):
        if not GEMINI_API_KEY: return {"status": "error", "message": "Can GEMINI_API_KEY"}
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=self.config["prompt"])
        chat = model.start_chat(history=[])
        prompt = f"Nhiem vu: {task}\n\nHoan thanh va tra ve ket qua ngan gon."
        try:
            response = chat.send_message(prompt)
            return {"status": "success", "agent_type": self.agent_type, "task": task, "result": response.text, "turns": 1}
        except Exception as e:
            return {"status": "error", "message": str(e)}

class SubAgentManager:
    def __init__(self):
        self.tools = {}

    def register_tools(self, tools):
        self.tools = tools

    async def spawn(self, agent_type="explorer", task="", max_turns=5):
        if agent_type not in AGENT_TYPES:
            return {"status": "error", "message": f"Loai agent '{agent_type}' khong hop le. Chon: {list(AGENT_TYPES.keys())}"}
        if not task: return {"status": "error", "message": "Can mo ta nhiem vu"}
        agent = SubAgent(agent_type, self.tools)
        return await agent.run(task, max_turns)

    def list_types(self):
        return {k: v["description"] for k, v in AGENT_TYPES.items()}

subagent_manager = SubAgentManager()
