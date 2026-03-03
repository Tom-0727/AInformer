import time

import requests

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AInformer/1.0"})

MAX_RETRIES = 3
RETRY_DELAY = 2


def _get_json(url: str) -> dict | list | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def _get_item(item_id: int) -> dict | None:
    return _get_json(f"{HN_API_BASE}/item/{item_id}.json")


def get_hacker_news_top_stories(max_count: int = 30) -> list[dict]:
    """Fetch top stories from Hacker News API.

    Returns list of dicts with keys: title, url, score, by, descendants, hn_url.
    """
    story_ids = _get_json(f"{HN_API_BASE}/topstories.json")
    if not story_ids:
        return []

    results = []
    for sid in story_ids[:max_count]:
        item = _get_item(sid)
        if not item or item.get("type") != "story":
            continue
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "score": item.get("score", 0),
            "by": item.get("by", ""),
            "descendants": item.get("descendants", 0),
            "hn_url": f"https://news.ycombinator.com/item?id={sid}",
        })
        time.sleep(0.1)

    return results


if __name__ == "__main__":
    stories = get_hacker_news_top_stories(max_count=5)
    for s in stories:
        print(f"\n{s['title']}")
        print(f"  score={s['score']}  comments={s['descendants']}")
        print(f"  {s['url']}")
        print(f"  {s['hn_url']}")
