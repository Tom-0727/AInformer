from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.huxiu_reader.article_read import huxiu_reader_graph
from core.agents.huxiu_reader.state import HuxiuArticleInfo, HuxiuArticleRecommendation
from core.utils.inform import inform


def _extract_found_article_map(result: dict[str, Any]) -> dict[str, HuxiuArticleInfo]:
    raw = result.get("found_articles") or []
    article_map: dict[str, HuxiuArticleInfo] = {}
    for item in raw:
        if isinstance(item, HuxiuArticleInfo):
            article_map[item.id] = item
            continue
        if isinstance(item, dict):
            article = HuxiuArticleInfo(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                summary=str(item.get("summary", "")),
                link=str(item.get("link", "")),
            )
            article_map[article.id] = article
    return article_map


def _extract_recommended_articles(result: dict[str, Any]) -> list[HuxiuArticleRecommendation]:
    raw = result.get("recommended_articles") or []
    articles: list[HuxiuArticleRecommendation] = []
    for item in raw:
        if isinstance(item, HuxiuArticleRecommendation):
            articles.append(item)
            continue
        if isinstance(item, dict):
            articles.append(
                HuxiuArticleRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return articles


def _build_notify_message(
    recommendations: list[HuxiuArticleRecommendation],
    found_article_map: dict[str, HuxiuArticleInfo],
) -> str:
    if not recommendations:
        return "虎嗅今日暂无可推荐文章。"

    lines = ["虎嗅推荐："]
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


async def huxiu_inform() -> str:
    result = await huxiu_reader_graph.ainvoke({})
    found_article_map = _extract_found_article_map(result)
    recommendations = _extract_recommended_articles(result)
    message = _build_notify_message(recommendations, found_article_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="读取虎嗅文章并发送结构化推荐到 Webhook")
    parser.parse_args()
    asyncio.run(huxiu_inform())


if __name__ == "__main__":
    main()
