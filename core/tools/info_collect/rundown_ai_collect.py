import time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "AInformer/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

MAX_RETRIES = 3
RETRY_DELAY = 2

RSS_URL = "https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml"


def _fetch(url: str, accept: str = "text/html") -> str | None:
    headers = {**SESSION.headers, "Accept": accept}
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def _extract_article_text(html: str, max_length: int = 3000) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove nav, footer, script, style, ads
    for tag in soup(["script", "style", "nav", "footer", "header", "button", "form"]):
        tag.decompose()
    # Try to find the main article body
    article = soup.find("article") or soup.find("main") or soup.find("div", class_=lambda c: c and "content" in c.lower())
    if article:
        text = article.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)
    # Collapse whitespace and filter out template artifacts
    lines = [line.strip() for line in text.splitlines() if line.strip() and len(line.strip()) > 3]
    # Remove Beehiiv header boilerplate (Read Online, Sign Up, Advertise lines)
    skip_prefixes = ("Read Online", "Sign Up", "Advertise", "Good morning", "View in browser")
    filtered = []
    for line in lines:
        if any(line.startswith(p) for p in skip_prefixes):
            continue
        filtered.append(line)
    return "\n".join(filtered)[:max_length]


def get_rundown_ai_newsletters(max_count: int = 5, fetch_content: bool = True) -> list[dict]:
    """Fetch latest newsletters from The Rundown AI RSS feed.

    Returns list of dicts with keys: id, headline, summary, content, link.
    If fetch_content=True, fetches the first article's full content.
    """
    xml_text = _fetch(RSS_URL, accept="application/rss+xml,application/xml")
    if not xml_text:
        return []

    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    items = channel.findall("item")
    results = []

    for i, item in enumerate(items[:max_count], 1):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")

        headline = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        summary_html = desc_el.text or "" if desc_el is not None else ""

        # Strip HTML from summary
        soup = BeautifulSoup(summary_html, "html.parser")
        summary = soup.get_text(separator=" ", strip=True)[:500]

        content = ""
        if fetch_content and link and i == 1:
            article_html = _fetch(link)
            if article_html:
                content = _extract_article_text(article_html)

        if headline:
            results.append({
                "id": str(i),
                "headline": headline,
                "summary": summary,
                "content": content,
                "link": link,
            })

    return results


if __name__ == "__main__":
    newsletters = get_rundown_ai_newsletters(max_count=3)
    for n in newsletters:
        print(f"\n{n['headline']}")
        print(f"  summary: {n['summary'][:100]}...")
        if n["content"]:
            print(f"  content: {n['content'][:200]}...")
        print(f"  {n['link']}")
