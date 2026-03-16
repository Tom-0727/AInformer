import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "AInformer/1.0"})

MAX_RETRIES = 3
RETRY_DELAY = 2
ARTICLE_PREVIEW_LIMIT = 2000
DISCUSSION_PREVIEW_LIMIT = 1200
STORY_TEXT_LIMIT = 800
MAX_COMMENT_COUNT = 5
MAX_ENRICH_WORKERS = 5


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


def _normalize_text(text: str) -> str:
    return " ".join((text or "").split())


def _truncate_text(text: str, limit: int) -> str:
    normalized = _normalize_text(text)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return _normalize_text(soup.get_text(" ", strip=True))


def _fetch_article_preview(url: str) -> str:
    if not url:
        return ""
    try:
        resp = SESSION.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    content_type = resp.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    blocks: list[str] = []
    for element in soup.find_all(["p", "li"]):
        text = _normalize_text(element.get_text(" ", strip=True))
        if len(text) >= 40:
            blocks.append(text)
        if len(" ".join(blocks)) >= ARTICLE_PREVIEW_LIMIT:
            break

    if not blocks and soup.body:
        blocks.append(_normalize_text(soup.body.get_text(" ", strip=True)))

    return _truncate_text("\n".join(blocks), ARTICLE_PREVIEW_LIMIT)


def _fetch_discussion_preview(comment_ids: list[int] | None) -> str:
    if not comment_ids:
        return ""

    comments: list[str] = []
    for comment_id in comment_ids:
        item = _get_item(comment_id)
        if not item or item.get("deleted") or item.get("dead"):
            continue
        text = _html_to_text(item.get("text", ""))
        if not text:
            continue
        author = item.get("by", "unknown")
        comments.append(f"{author}: {text}")
        if len(comments) >= MAX_COMMENT_COUNT:
            break

    return _truncate_text("\n".join(comments), DISCUSSION_PREVIEW_LIMIT)


def _enrich_story(item: dict) -> dict:
    enriched = dict(item)
    enriched["story_text"] = _truncate_text(_html_to_text(item.get("text", "")), STORY_TEXT_LIMIT)
    enriched["article_preview"] = _fetch_article_preview(item.get("url", ""))
    enriched["discussion_preview"] = _fetch_discussion_preview(item.get("kids"))
    return enriched


def get_hacker_news_top_stories(max_count: int = 30) -> list[dict]:
    """Fetch top stories from Hacker News API.

    Returns list of dicts with keys: title, url, score, by, descendants, hn_url,
    story_text, article_preview, discussion_preview.
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
            "item_id": sid,
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "score": item.get("score", 0),
            "by": item.get("by", ""),
            "descendants": item.get("descendants", 0),
            "text": item.get("text", ""),
            "kids": item.get("kids", []),
            "hn_url": f"https://news.ycombinator.com/item?id={sid}",
            "story_text": "",
            "article_preview": "",
            "discussion_preview": "",
        })
        time.sleep(0.1)

    return results

def enrich_hacker_news_stories(stories: list[dict]) -> list[dict]:
    if not stories:
        return []

    enriched_results = [dict(story) for story in stories]
    with ThreadPoolExecutor(max_workers=min(MAX_ENRICH_WORKERS, len(stories))) as executor:
        future_map = {
            executor.submit(_enrich_story, enriched_results[idx]): idx
            for idx in range(len(enriched_results))
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                enriched_results[idx] = future.result()
            except Exception:
                enriched_results[idx]["story_text"] = _truncate_text(
                    _html_to_text(enriched_results[idx].get("text", "")),
                    STORY_TEXT_LIMIT,
                )

    return enriched_results


if __name__ == "__main__":
    stories = get_hacker_news_top_stories(max_count=5)
    for s in stories:
        print(f"\n{s['title']}")
        print(f"  score={s['score']}  comments={s['descendants']}")
        print(f"  {s['url']}")
        print(f"  {s['hn_url']}")
