import time
import xml.etree.ElementTree as ET

import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "AInformer/1.0",
    "Accept": "application/atom+xml,application/xml,text/xml",
})

MAX_RETRIES = 3
RETRY_DELAY = 2

ATOM_NS = "http://www.w3.org/2005/Atom"


def _strip_html(html: str) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Remove all <a> tags (links like Discussion, Link, etc.)
    for a in soup.find_all("a"):
        a.decompose()
    # Extract paragraph text only
    parts = []
    for p in soup.find_all("p"):
        text = " ".join(p.get_text(separator=" ", strip=True).split())
        # Filter out pipe-only or very short fragments
        cleaned = text.strip(" |").strip()
        if cleaned and len(cleaned) > 5:
            parts.append(cleaned)
    return " ".join(parts) if parts else " ".join(soup.get_text(separator=" ", strip=True).split())


def _fetch_xml(url: str) -> str | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def get_product_hunt_products(max_count: int = 20) -> list[dict]:
    """Fetch latest products from Product Hunt Atom feed.

    Returns list of dicts with keys: id, name, tagline, description, link.
    """
    xml_text = _fetch_xml("https://www.producthunt.com/feed")
    if not xml_text:
        return []

    root = ET.fromstring(xml_text)
    results = []

    for i, entry in enumerate(root.findall(f"{{{ATOM_NS}}}entry"), 1):
        title_el = entry.find(f"{{{ATOM_NS}}}title")
        link_el = entry.find(f"{{{ATOM_NS}}}link")
        content_el = entry.find(f"{{{ATOM_NS}}}content")
        id_el = entry.find(f"{{{ATOM_NS}}}id")

        title_text = title_el.text.strip() if title_el is not None and title_el.text else ""
        link_href = link_el.get("href", "") if link_el is not None else ""
        content_html = content_el.text or "" if content_el is not None else ""
        entry_id = id_el.text.strip() if id_el is not None and id_el.text else str(i)

        name = title_text
        description = _strip_html(content_html)[:500]

        if name:
            results.append({
                "id": str(i),
                "name": name,
                "tagline": "",
                "description": description,
                "link": link_href,
            })
        if len(results) >= max_count:
            break

    return results


if __name__ == "__main__":
    products = get_product_hunt_products(max_count=5)
    for p in products:
        print(f"\n{p['name']} — {p['tagline']}")
        print(f"  {p['description'][:100]}...")
        print(f"  {p['link']}")
