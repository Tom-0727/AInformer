from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.taaft_reader.tool_read import taaft_reader_graph
from core.agents.taaft_reader.state import AiToolInfo, AiToolRecommendation
from core.utils.inform import inform


def _extract_found_tool_map(result: dict[str, Any]) -> dict[str, AiToolInfo]:
    raw = result.get("found_tools") or []
    tool_map: dict[str, AiToolInfo] = {}
    for item in raw:
        if isinstance(item, AiToolInfo):
            tool_map[item.id] = item
            continue
        if isinstance(item, dict):
            tool = AiToolInfo(
                id=str(item.get("id", "")),
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                use_case=str(item.get("use_case", "")),
                link=str(item.get("link", "")),
            )
            tool_map[tool.id] = tool
    return tool_map


def _extract_recommended_tools(result: dict[str, Any]) -> list[AiToolRecommendation]:
    raw = result.get("recommended_tools") or []
    tools: list[AiToolRecommendation] = []
    for item in raw:
        if isinstance(item, AiToolRecommendation):
            tools.append(item)
            continue
        if isinstance(item, dict):
            tools.append(
                AiToolRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return tools


def _build_notify_message(
    recommendations: list[AiToolRecommendation],
    found_tool_map: dict[str, AiToolInfo],
) -> str:
    if not recommendations:
        return "There's An AI for That 今日暂无可推荐工具。"

    lines = ["There's An AI for That 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        tool = found_tool_map.get(rec.id)
        name = tool.name if tool else f"(未匹配工具，id={rec.id})"
        link = tool.link if tool else ""
        risk_text = "；".join(rec.risk_items) if rec.risk_items else "未识别到明确风险点"
        lines.append(f"\n{idx}. {name}")
        if link:
            lines.append(f"链接：{link}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def taaft_inform() -> str:
    result = await taaft_reader_graph.ainvoke({})
    found_tool_map = _extract_found_tool_map(result)
    recommendations = _extract_recommended_tools(result)
    message = _build_notify_message(recommendations, found_tool_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 There's An AI for That 工具列表并发送结构化推荐到 Webhook"
    )
    parser.parse_args()
    asyncio.run(taaft_inform())


if __name__ == "__main__":
    main()
