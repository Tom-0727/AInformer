import time

import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://36kr.com",
    "Accept": "application/json",
})

MAX_RETRIES = 3
RETRY_DELAY = 2


def _get_json(url: str, params: dict | None = None) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def get_kr36_articles(max_count: int = 20) -> list[dict]:
    """Fetch latest newsflash from 36Kr API.

    Returns list of dicts with keys: id, title, description, published_at, link.
    """
    data = _get_json(
        "https://36kr.com/api/newsflash",
        params={"b_id": 0, "per_page": max_count, "is_nbhd": 0},
    )
    if not data or data.get("code") != 0:
        return []

    items = data.get("data", {}).get("items", [])
    results = []
    for item in items:
        item_id = item.get("id", "")
        title = item.get("title") or item.get("catch_title") or ""
        description = item.get("description") or ""
        published_at = item.get("published_at") or ""
        # Use original news URL if available, otherwise link to 36Kr newsflash page
        link = item.get("news_url") or f"https://36kr.com/newsflashes/{item_id}"
        if title:
            results.append({
                "id": str(item_id),
                "title": title,
                "description": description,
                "published_at": str(published_at),
                "link": link,
            })
    return results


if __name__ == "__main__":
    articles = get_kr36_articles(max_count=5)
    for a in articles:
        print(f"\n{a['title']}")
        print(f"  {a['description'][:100]}...")
        print(f"  {a['link']}")
