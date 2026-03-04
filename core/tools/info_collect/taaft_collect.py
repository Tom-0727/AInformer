import time

import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
})

MAX_RETRIES = 3
RETRY_DELAY = 2


def _fetch_html(url: str) -> str | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def get_taaft_tools(max_count: int = 20) -> list[dict]:
    """Fetch latest AI tools from There's An AI for That.

    Note: The site is a JS-rendered SPA. This scraper works if
    server-side rendering provides initial HTML content.
    Returns list of dicts with keys: id, name, description, use_case, link.
    """
    html = _fetch_html("https://theresanaiforthat.com/")
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Try to find tool cards via known CSS selectors
    tool_links = soup.find_all("a", class_=lambda c: c and "ai_link" in c)
    if not tool_links:
        # Fallback: look for any link with /ai/ in href pattern
        tool_links = soup.find_all("a", href=lambda h: h and "/ai/" in h)

    for link_tag in tool_links[:max_count]:
        href = link_tag.get("href", "")
        name = link_tag.get_text(strip=True)
        if not name:
            continue

        full_link = f"https://theresanaiforthat.com{href}" if href.startswith("/") else href

        # Look for description and use_case in nearby elements
        parent = link_tag.parent
        description = ""
        use_case = ""
        for _ in range(3):
            if parent is None:
                break
            desc_el = parent.find(class_=lambda c: c and "short_desc" in c)
            if desc_el:
                description = desc_el.get_text(strip=True)
            task_el = parent.find(class_=lambda c: c and "task_label" in c)
            if task_el:
                use_case = task_el.get_text(strip=True)
            if description or use_case:
                break
            parent = parent.parent

        results.append({
            "id": str(len(results) + 1),
            "name": name,
            "description": description,
            "use_case": use_case,
            "link": full_link,
        })

    if not results:
        print("[taaft_collect] 警告: 未能获取工具列表（页面可能为纯 JS 渲染，需要 Playwright）")

    return results


if __name__ == "__main__":
    tools = get_taaft_tools(max_count=5)
    if tools:
        for t in tools:
            print(f"\n{t['name']} ({t['use_case']})")
            print(f"  {t['description'][:100]}...")
            print(f"  {t['link']}")
    else:
        print("未获取到工具，页面可能需要 Playwright 渲染")
