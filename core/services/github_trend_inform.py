from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.github_trending_reader.repo_read import github_trending_reader_graph
from core.agents.github_trending_reader.state import RepoInfo
from core.utils.inform import inform


def _extract_recommended_repos(result: dict[str, Any]) -> list[RepoInfo]:
    raw_repos = result.get("recommended_repos") or []
    repos: list[RepoInfo] = []
    for item in raw_repos:
        if isinstance(item, RepoInfo):
            repos.append(item)
            continue

        if isinstance(item, dict):
            repos.append(
                RepoInfo(
                    id=str(item.get("id", "")),
                    title=str(item.get("title", "")),
                    link=str(item.get("link", "")),
                    description=str(item.get("description", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return repos


def _build_notify_message(recommended_repos: list[RepoInfo], since: str) -> str:
    if not recommended_repos:
        return f"Github Trending（{since}）暂无可推荐项目。"

    lines = [f"Github Trending（{since}）推荐："]
    for idx, repo in enumerate(recommended_repos, 1):
        risk_text = "；".join(repo.risk_items) if repo.risk_items else "未识别到明确风险点"
        lines.append(f"\n{idx}. {repo.title}")
        lines.append(f"推荐理由：{repo.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def github_trend_inform(since: str = "daily") -> str:
    result = await github_trending_reader_graph.ainvoke({"since": since})
    recommended_repos = _extract_recommended_repos(result)
    message = _build_notify_message(recommended_repos, since)
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
