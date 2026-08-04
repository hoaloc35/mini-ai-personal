"""AI 383 - Web Search Tool (DuckDuckGo)"""
import httpx
from bs4 import BeautifulSoup

async def execute(params: dict) -> dict:
    query = params.get("query", "")
    num_results = params.get("num_results", 5)
    if not query:
        return {"status": "error", "message": "Can tu khoa tim kiem"}
    try:
        results = await _duckduckgo_search(query, num_results)
        return {"status": "success", "query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"status": "error", "message": f"Loi tim kiem: {str(e)}"}

async def _duckduckgo_search(query, num_results=5):
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, data={"q": query}, headers=headers)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for result in soup.select(".result"):
        title_el = result.select_one(".result__title a")
        snippet_el = result.select_one(".result__snippet")
        if title_el:
            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            if "uddg=" in link:
                from urllib.parse import unquote, parse_qs, urlparse
                parsed = urlparse(link)
                qs = parse_qs(parsed.query)
                if "uddg" in qs:
                    link = unquote(qs["uddg"][0])
            results.append({"title": title, "url": link, "snippet": snippet})
            if len(results) >= num_results:
                break
    return results

async def fetch_page(url, max_chars=5000):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        clean_text = "\n".join(lines)[:max_chars]
        return {"status": "success", "url": url, "title": soup.title.string if soup.title else "", "content": clean_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
