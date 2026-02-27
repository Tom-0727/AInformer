import asyncio
import sys
from pathlib import Path
from typing import Literal

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph, START
from langgraph.types import Command

from core.agents.github_trending_reader.configuration import GithubTrendingReaderConfig
from core.agents.github_trending_reader.state import (
    RepoInfo,
    RepoRecommendation,
    GithubTrendingReaderState,
    RepoReadResult,
)
from core.tools.info_collect.github_trending_collect import get_github_trending
from core.agents.github_trending_reader.prompts import get_system_prompt, get_repo_read_prompt

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_repo_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> RepoReadResult:
    tool_model = model.bind_tools(
        [RepoReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(
        tools=[RepoReadResult],
        first_tool_only=True,
    )
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return a RepoReadResult tool call.")
    return result



def _format_recommendations(
    recommendations: list[RepoRecommendation], found_repos: list[RepoInfo]
) -> str:
    found_repo_by_id = {repo.id: repo for repo in found_repos}
    lines = ["# Github Trending 推荐结果"]
    for i, recommendation in enumerate(recommendations, 1):
        repo = found_repo_by_id.get(recommendation.id)
        title = repo.title if repo else "(未匹配到仓库信息)"
        link = repo.link if repo else ""
        lines.append(f"\n{i}. {title} (id: {recommendation.id})")
        if link:
            lines.append(f"- link: {link}")
        lines.append(f"- 推荐理由: {recommendation.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(recommendation.risk_items)}")
    return "\n".join(lines)


async def repo_read(
    state: GithubTrendingReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = GithubTrendingReaderConfig.from_runnable_config(config)
    read_model = configurable_model.with_config(
        {
            "configurable": {
                "model": configurable.read_model,
                "model_provider": "openai",
                "max_tokens": 4000,
                "temperature": 0.1,
            }
        }
    )

    trending_items = get_github_trending(
        since=state.get('since', 'daily'),
        max_count=configurable.max_read_repos,
        max_length=configurable.max_repo_read_size,
    )

    found_repos = [
        RepoInfo(
            id=str(i),
            title=item["name"],
            link=f"https://github.com/{item['name']}",
            description=item["readme_summary"],
        )
        for i, item in enumerate(trending_items, 1)
    ]

    messages = [
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=get_repo_read_prompt(state.get('since', 'daily'), found_repos)),
    ]
    result = await _ainvoke_repo_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_repos, found_repos)
    return Command(
        goto=END,
        update={
            "found_repos": found_repos,
            "recommended_repos": result.recommended_repos,
            "messages": [AIMessage(content=summary_text)],
        },
    )


github_trending_reader_graph = StateGraph(GithubTrendingReaderState)
github_trending_reader_graph.add_node("repo_read", repo_read)
github_trending_reader_graph.add_edge(START, "repo_read")
github_trending_reader_graph.add_edge("repo_read", END)

github_trending_reader_graph = github_trending_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(github_trending_reader_graph.ainvoke({}))
    print(result)
