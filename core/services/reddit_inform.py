from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.reddit_reader.post_read import reddit_reader_graph
from core.agents.reddit_reader.state import PostInfo, PostRecommendation
from core.utils.inform import inform


def _extract_found_post_map(result: dict[str, Any]) -> dict[str, PostInfo]:
    raw = result.get("found_posts") or []
    post_map: dict[str, PostInfo] = {}
    for item in raw:
        if isinstance(item, PostInfo):
            post_map[item.id] = item
            continue
        if isinstance(item, dict):
            post = PostInfo(
                id=str(item.get("id", "")),
                subreddit=str(item.get("subreddit", "")),
                title=str(item.get("title", "")),
                selftext=str(item.get("selftext", "")),
                url=str(item.get("url", "")),
                reddit_url=str(item.get("reddit_url", "")),
                score=int(item.get("score", 0)),
                num_comments=int(item.get("num_comments", 0)),
            )
            post_map[post.id] = post
    return post_map


def _extract_recommended_posts(result: dict[str, Any]) -> list[PostRecommendation]:
    raw = result.get("recommended_posts") or []
    posts: list[PostRecommendation] = []
    for item in raw:
        if isinstance(item, PostRecommendation):
            posts.append(item)
            continue
        if isinstance(item, dict):
            posts.append(
                PostRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return posts


def _build_notify_message(
    recommendations: list[PostRecommendation], found_post_map: dict[str, PostInfo]
) -> str:
    if not recommendations:
        return "Reddit 今日暂无可推荐帖子。"

    lines = ["Reddit 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        post = found_post_map.get(rec.id)
        title = post.title if post else f"(未匹配帖子，id={rec.id})"
        subreddit = f"r/{post.subreddit}" if post else ""
        reddit_url = post.reddit_url if post else ""
        risk_text = (
            "；".join(rec.risk_items)
            if rec.risk_items
            else "未识别到明确风险点"
        )
        lines.append(f"\n{idx}. [{subreddit}] {title}")
        if reddit_url:
            lines.append(f"Reddit讨论：{reddit_url}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def reddit_inform() -> str:
    result = await reddit_reader_graph.ainvoke({})
    found_post_map = _extract_found_post_map(result)
    recommendations = _extract_recommended_posts(result)
    message = _build_notify_message(recommendations, found_post_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 Reddit 热门帖子并发送结构化推荐到 Webhook"
    )
    args = parser.parse_args()
    asyncio.run(reddit_inform())


if __name__ == "__main__":
    main()
