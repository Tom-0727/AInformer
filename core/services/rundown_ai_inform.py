from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.rundown_ai_reader.newsletter_read import rundown_ai_reader_graph
from core.agents.rundown_ai_reader.state import RundownItemInfo, RundownItemRecommendation
from core.utils.inform import inform


def _extract_found_item_map(result: dict[str, Any]) -> dict[str, RundownItemInfo]:
    raw = result.get("found_items") or []
    item_map: dict[str, RundownItemInfo] = {}
    for item in raw:
        if isinstance(item, RundownItemInfo):
            item_map[item.id] = item
            continue
        if isinstance(item, dict):
            info = RundownItemInfo(
                id=str(item.get("id", "")),
                headline=str(item.get("headline", "")),
                summary=str(item.get("summary", "")),
                content=str(item.get("content", "")),
                link=str(item.get("link", "")),
            )
            item_map[info.id] = info
    return item_map


def _extract_recommended_items(result: dict[str, Any]) -> list[RundownItemRecommendation]:
    raw = result.get("recommended_items") or []
    items: list[RundownItemRecommendation] = []
    for item in raw:
        if isinstance(item, RundownItemRecommendation):
            items.append(item)
            continue
        if isinstance(item, dict):
            items.append(
                RundownItemRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return items


def _build_notify_message(
    recommendations: list[RundownItemRecommendation],
    found_item_map: dict[str, RundownItemInfo],
) -> str:
    if not recommendations:
        return "The Rundown AI 今日暂无可推荐内容。"

    lines = ["The Rundown AI 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        item = found_item_map.get(rec.id)
        headline = item.headline if item else f"(未匹配内容，id={rec.id})"
        link = item.link if item else ""
        risk_text = "；".join(rec.risk_items) if rec.risk_items else "未识别到明确风险点"
        lines.append(f"\n{idx}. {headline}")
        if link:
            lines.append(f"链接：{link}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def rundown_ai_inform() -> str:
    result = await rundown_ai_reader_graph.ainvoke({})
    found_item_map = _extract_found_item_map(result)
    recommendations = _extract_recommended_items(result)
    message = _build_notify_message(recommendations, found_item_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="读取 The Rundown AI newsletter 并发送结构化推荐到 Webhook")
    parser.parse_args()
    asyncio.run(rundown_ai_inform())


if __name__ == "__main__":
    main()
