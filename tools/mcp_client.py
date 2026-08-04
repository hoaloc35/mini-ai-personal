"""AI 383 v4.0 - MCP Protocol Client (GitHub/Notion/Slack)"""
import httpx
from config import MCP_SERVERS

BUILTIN_SERVERS = {
    "github": {"description": "GitHub: repos, issues, PRs", "tools": ["search_repos", "get_repo", "list_issues", "create_issue"]},
    "notion": {"description": "Notion: pages, databases", "tools": ["search", "get_page", "create_page"]},
    "slack": {"description": "Slack: messages, channels", "tools": ["send_message", "list_channels", "get_messages"]},
}

class MCPClient:
    def __init__(self):
        self.servers = dict(BUILTIN_SERVERS)
        for name, cfg in MCP_SERVERS.items():
            self.servers[name] = {"description": cfg.get("description", name), "url": cfg.get("url", ""), "api_key": cfg.get("api_key", ""), "tools": []}

    def list_servers(self):
        return [{"name": k, "description": v.get("description", ""), "tools": v.get("tools", []), "connected": bool(v.get("url", ""))} for k, v in self.servers.items()]

    def list_tools(self, server_name):
        server = self.servers.get(server_name)
        if not server: return {"status": "error", "message": f"Server '{server_name}' khong ton tai"}
        return {"status": "success", "server": server_name, "tools": server.get("tools", [])}

    async def call_tool(self, server_name, tool_name, arguments=None):
        server = self.servers.get(server_name)
        if not server: return {"status": "error", "message": f"Server '{server_name}' khong ton tai"}
        url = server.get("url", "")
        if url:
            try:
                headers = {"Content-Type": "application/json"}
                if server.get("api_key"): headers["Authorization"] = f"Bearer {server['api_key']}"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(f"{url}/tools/{tool_name}", json=arguments or {}, headers=headers)
                    return {"status": "success", "result": resp.json()}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        # Simulated response for builtin servers
        return {"status": "success", "server": server_name, "tool": tool_name, "result": f"[Simulated] {server_name}.{tool_name}({arguments})", "note": "Them url + api_key vao MCP_SERVERS de ket noi that"}

    def add_server(self, name, url, description="", api_key=""):
        self.servers[name] = {"description": description or name, "url": url, "api_key": api_key, "tools": []}
        return {"status": "success", "message": f"Da them MCP server: {name}"}

mcp_client = MCPClient()

async def execute(params: dict) -> dict:
    action = params.get("action", "list_servers")
    if action == "list_servers":
        return {"status": "success", "servers": mcp_client.list_servers()}
    elif action == "list_tools":
        server_name = params.get("server_name", "")
        return mcp_client.list_tools(server_name)
    elif action == "call_tool":
        server_name = params.get("server_name", "")
        tool_name = params.get("tool_name", "")
        arguments = params.get("arguments", {})
        return await mcp_client.call_tool(server_name, tool_name, arguments)
    elif action == "add_server":
        return mcp_client.add_server(params.get("name", ""), params.get("url", ""), params.get("description", ""), params.get("api_key", ""))
    else:
        return {"status": "error", "message": f"Action '{action}' khong hop le"}
