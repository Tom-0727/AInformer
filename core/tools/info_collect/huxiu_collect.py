import re
import time

import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

MAX_RETRIES = 3
RETRY_DELAY = 2


def _fetch_html(url: str) -> str | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def get_huxiu_articles(max_count: int = 20) -> list[dict]:
    """Fetch latest articles from 虎嗅.

    Returns list of dicts with keys: id, title, summary, link.
    """
    html = _fetch_html("https://www.huxiu.com")
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen_ids: set[str] = set()

    # Find article cards via .article-title class (SSR-rendered by Nuxt)
    title_els = soup.find_all(class_="article-title")
    for title_el in title_els:
        link_tag = title_el.find("a") or (title_el if title_el.name == "a" else None)
        if not link_tag:
            continue
        href = link_tag.get("href", "")
        m = re.search(r"/article/(\d+)", href)
        if not m:
            continue
        article_id = m.group(1)
        if article_id in seen_ids:
            continue
        seen_ids.add(article_id)

        title = title_el.get_text(strip=True)
        if not title or len(title) < 3:
            continue

        full_link = f"https://www.huxiu.com/article/{article_id}.html"
        results.append({
            "id": article_id,
            "title": title,
            "summary": "",
            "link": full_link,
        })
        if len(results) >= max_count:
            break

    return results


if __name__ == "__main__":
    articles = get_huxiu_articles(max_count=5)
    for a in articles:
        print(f"\n{a['title']}")
        print(f"  {a['summary'][:100]}...")
        print(f"  {a['link']}")
