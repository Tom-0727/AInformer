import time

import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AInformer/1.0"})

MAX_RETRIES = 3
RETRY_DELAY = 2

DEFAULT_SUBREDDITS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
    "programming",
    "ExperiencedDevs",
    "systemdesign",
    "devops",
    "golang",
    "rust",
    "opensource",
]


def _get_json(url: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = SESSION.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError):
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def _fetch_subreddit_top(subreddit: str, limit: int = 10, time_filter: str = "day") -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time_filter}&limit={limit}"
    data = _get_json(url)
    if not data:
        return []

    posts = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("stickied"):
            continue
        posts.append({
            "subreddit": subreddit,
            "title": d.get("title", ""),
            "selftext": (d.get("selftext") or "")[:2000],
            "url": d.get("url", ""),
            "permalink": d.get("permalink", ""),
            "score": d.get("score", 0),
            "num_comments": d.get("num_comments", 0),
            "author": d.get("author", ""),
            "is_self": d.get("is_self", False),
        })
    return posts


def get_reddit_top_posts(
    subreddits: list[str] | None = None,
    per_sub_limit: int = 5,
    time_filter: str = "day",
    max_total: int = 30,
) -> list[dict]:
    """Fetch top posts from multiple subreddits.

    Returns list of dicts with keys: subreddit, title, selftext, url, permalink, score, num_comments, author, is_self.
    """
    subs = subreddits or DEFAULT_SUBREDDITS
    results = []
    for sub in subs:
        posts = _fetch_subreddit_top(sub, limit=per_sub_limit, time_filter=time_filter)
        results.extend(posts)
        time.sleep(1)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_total]


if __name__ == "__main__":
    posts = get_reddit_top_posts(max_total=10)
    for p in posts:
        print(f"\nr/{p['subreddit']} | score={p['score']} | comments={p['num_comments']}")
        print(f"  {p['title']}")
        print(f"  https://reddit.com{p['permalink']}")
