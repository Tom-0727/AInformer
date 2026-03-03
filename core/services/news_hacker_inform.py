from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.news_hacker_reader.story_read import news_hacker_reader_graph
from core.agents.news_hacker_reader.state import StoryInfo, StoryRecommendation
from core.utils.inform import inform


def _extract_found_story_map(result: dict[str, Any]) -> dict[str, StoryInfo]:
    raw = result.get("found_stories") or []
    story_map: dict[str, StoryInfo] = {}
    for item in raw:
        if isinstance(item, StoryInfo):
            story_map[item.id] = item
            continue
        if isinstance(item, dict):
            story = StoryInfo(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                url=str(item.get("url", "")),
                hn_url=str(item.get("hn_url", "")),
                score=int(item.get("score", 0)),
                comments=int(item.get("comments", 0)),
            )
            story_map[story.id] = story
    return story_map


def _extract_recommended_stories(result: dict[str, Any]) -> list[StoryRecommendation]:
    raw = result.get("recommended_stories") or []
    stories: list[StoryRecommendation] = []
    for item in raw:
        if isinstance(item, StoryRecommendation):
            stories.append(item)
            continue
        if isinstance(item, dict):
            stories.append(
                StoryRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return stories


def _build_notify_message(
    recommendations: list[StoryRecommendation], found_story_map: dict[str, StoryInfo]
) -> str:
    if not recommendations:
        return "Hacker News 今日暂无可推荐新闻。"

    lines = ["Hacker News 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        story = found_story_map.get(rec.id)
        title = story.title if story else f"(未匹配新闻，id={rec.id})"
        hn_url = story.hn_url if story else ""
        risk_text = (
            "；".join(rec.risk_items)
            if rec.risk_items
            else "未识别到明确风险点"
        )
        lines.append(f"\n{idx}. {title}")
        if hn_url:
            lines.append(f"HN讨论：{hn_url}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def news_hacker_inform() -> str:
    result = await news_hacker_reader_graph.ainvoke({})
    found_story_map = _extract_found_story_map(result)
    recommendations = _extract_recommended_stories(result)
    message = _build_notify_message(recommendations, found_story_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 Hacker News Top Stories 并发送结构化推荐到 Webhook"
    )
    args = parser.parse_args()
    asyncio.run(news_hacker_inform())


if __name__ == "__main__":
    main()
