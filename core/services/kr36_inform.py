from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.kr36_reader.article_read import kr36_reader_graph
from core.agents.kr36_reader.state import Kr36ArticleInfo, Kr36ArticleRecommendation
from core.utils.inform import inform


def _extract_found_article_map(result: dict[str, Any]) -> dict[str, Kr36ArticleInfo]:
    raw = result.get("found_articles") or []
    article_map: dict[str, Kr36ArticleInfo] = {}
    for item in raw:
        if isinstance(item, Kr36ArticleInfo):
            article_map[item.id] = item
            continue
        if isinstance(item, dict):
            article = Kr36ArticleInfo(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                description=str(item.get("description", "")),
                published_at=str(item.get("published_at", "")),
                link=str(item.get("link", "")),
            )
            article_map[article.id] = article
    return article_map


def _extract_recommended_articles(result: dict[str, Any]) -> list[Kr36ArticleRecommendation]:
    raw = result.get("recommended_articles") or []
    articles: list[Kr36ArticleRecommendation] = []
    for item in raw:
        if isinstance(item, Kr36ArticleRecommendation):
            articles.append(item)
            continue
        if isinstance(item, dict):
            articles.append(
                Kr36ArticleRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return articles


def _build_notify_message(
    recommendations: list[Kr36ArticleRecommendation],
    found_article_map: dict[str, Kr36ArticleInfo],
) -> str:
    if not recommendations:
        return "36Kr 今日暂无可推荐文章。"

    lines = ["36Kr 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        article = found_article_map.get(rec.id)
        title = article.title if article else f"(未匹配文章，id={rec.id})"
        link = article.link if article else ""
        risk_text = "；".join(rec.risk_items) if rec.risk_items else "未识别到明确风险点"
        lines.append(f"\n{idx}. {title}")
        if link:
            lines.append(f"链接：{link}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def kr36_inform() -> str:
    result = await kr36_reader_graph.ainvoke({})
    found_article_map = _extract_found_article_map(result)
    recommendations = _extract_recommended_articles(result)
    message = _build_notify_message(recommendations, found_article_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="读取 36Kr 文章并发送结构化推荐到 Webhook")
    parser.parse_args()
    asyncio.run(kr36_inform())


if __name__ == "__main__":
    main()
