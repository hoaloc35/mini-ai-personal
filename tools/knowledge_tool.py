"""AI 383 - Knowledge Tool: Bach khoa toan thu + Tu hoc"""
import httpx
from bs4 import BeautifulSoup
from agent import database as db

async def learn(params: dict) -> dict:
    action = params.get("action", "from_text")
    try:
        if action == "from_text":
            title = params.get("title", "Untitled")
            content = params.get("content", "")
            if not content: return {"status": "error", "message": "Can noi dung de hoc"}
            kid = await db.add_knowledge(title=title, content=content, source="user", category=params.get("category", "general"), tags=params.get("tags", []))
            return {"status": "success", "message": f"Da hoc: '{title}' (ID: {kid})", "knowledge_id": kid}
        elif action == "from_url":
            url = params.get("url", "")
            if not url: return {"status": "error", "message": "Can URL"}
            page_data = await _fetch_and_extract(url)
            if page_data["status"] == "error": return page_data
            title = params.get("title", page_data.get("title", "Web content"))
            content = page_data["content"]
            kid = await db.add_knowledge(title=title, content=content, source=url, category=params.get("category", "web"), tags=params.get("tags", []))
            await db.save_learning_source(url=url, content_type="webpage", summary=content[:500], raw_content=content)
            return {"status": "success", "message": f"Da hoc tu web: '{title}'", "knowledge_id": kid, "chars_learned": len(content)}
        elif action == "from_file":
            filepath = params.get("filepath", "")
            if not filepath: return {"status": "error", "message": "Can duong dan file"}
            try:
                with open(filepath, "r", encoding="utf-8") as f: content = f.read()
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as f: content = f.read()
            title = params.get("title", filepath.split("/")[-1])
            kid = await db.add_knowledge(title=title, content=content[:50000], source=f"file:{filepath}", category=params.get("category", "file"), tags=params.get("tags", []))
            return {"status": "success", "message": f"Da hoc tu file: '{title}'", "knowledge_id": kid}
        else:
            return {"status": "error", "message": f"Action '{action}' khong hop le"}
    except Exception as e:
        return {"status": "error", "message": f"Loi: {str(e)}"}

async def query(params: dict) -> dict:
    search_query = params.get("query", "")
    limit = params.get("limit", 5)
    try:
        results = await db.search_knowledge(search_query, limit) if search_query else await db.get_all_knowledge(limit)
        if not results:
            return {"status": "success", "message": "Chua co kien thuc nao.", "results": []}
        return {"status": "success", "query": search_query, "results": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "message": f"Loi: {str(e)}"}

async def _fetch_and_extract(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]): tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.find("body") or soup
        text = main.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        clean_text = "\n".join(lines)
        title = soup.title.string if soup.title else url
        return {"status": "success", "title": title, "content": clean_text[:30000], "url": url}
    except Exception as e:
        return {"status": "error", "message": f"Khong the doc URL: {str(e)}"}
