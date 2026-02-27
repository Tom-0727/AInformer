from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.github_trending_reader.repo_read import github_trending_reader_graph
from core.agents.github_trending_reader.state import RepoInfo, RepoRecommendation
from core.utils.inform import inform


def _extract_found_repo_map(result: dict[str, Any]) -> dict[str, RepoInfo]:
    raw_found_repos = result.get("found_repos") or []
    found_repo_map: dict[str, RepoInfo] = {}
    for item in raw_found_repos:
        if isinstance(item, RepoInfo):
            found_repo_map[item.id] = item
            continue

        if isinstance(item, dict):
            repo = RepoInfo(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                link=str(item.get("link", "")),
                description=str(item.get("description", "")),
            )
            found_repo_map[repo.id] = repo
    return found_repo_map


def _extract_recommended_repos(result: dict[str, Any]) -> list[RepoRecommendation]:
    raw_repos = result.get("recommended_repos") or []
    repos: list[RepoRecommendation] = []
    for item in raw_repos:
        if isinstance(item, RepoRecommendation):
            repos.append(item)
            continue
        if isinstance(item, dict):
            repos.append(
                RepoRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return repos


def _build_notify_message(
    recommendations: list[RepoRecommendation], found_repo_map: dict[str, RepoInfo], since: str
) -> str:
    if not recommendations:
        return f"Github Trending（{since}）暂无可推荐项目。"

    lines = [f"Github Trending（{since}）推荐："]
    for idx, recommendation in enumerate(recommendations, 1):
        found_repo = found_repo_map.get(recommendation.id)
        title = found_repo.title if found_repo else f"(未匹配仓库，id={recommendation.id})"
        risk_text = (
            "；".join(recommendation.risk_items)
            if recommendation.risk_items
            else "未识别到明确风险点"
        )
        lines.append(f"\n{idx}. {title}")
        lines.append(f"推荐理由：{recommendation.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def github_trend_inform(since: str = "daily") -> str:
    result = await github_trending_reader_graph.ainvoke({"since": since})
    found_repo_map = _extract_found_repo_map(result)
    recommendations = _extract_recommended_repos(result)
    message = _build_notify_message(recommendations, found_repo_map, since)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(
        description="读取 Github Trending 并发送结构化推荐到 Webhook"
    )
    parser.add_argument(
        "--since",
        choices=["daily", "weekly", "monthly"],
        default="daily",
        help="Trending 时间范围",
    )
    args = parser.parse_args()
    asyncio.run(github_trend_inform(args.since))


if __name__ == "__main__":
    main()
