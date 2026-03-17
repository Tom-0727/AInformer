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

from core.agents.reddit_reader.configuration import RedditReaderConfig
from core.agents.reddit_reader.state import (
    PostInfo,
    PostRecommendation,
    RedditReaderState,
    PostReadResult,
)
from core.tools.info_collect.reddit_collect import get_reddit_top_posts
from core.configs.system_prompt import SYSTEM_PROMPT
from core.agents.reddit_reader.prompts import format_post_data, get_post_task_instruction

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_post_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> PostReadResult:
    tool_model = model.bind_tools(
        [PostReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(
        tools=[PostReadResult],
        first_tool_only=True,
    )
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return a PostReadResult tool call.")
    return result


def _format_recommendations(
    recommendations: list[PostRecommendation], found_posts: list[PostInfo]
) -> str:
    found_post_by_id = {p.id: p for p in found_posts}
    lines = ["# Reddit 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        post = found_post_by_id.get(rec.id)
        title = post.title if post else "(未匹配到帖子信息)"
        subreddit = f"r/{post.subreddit}" if post else ""
        reddit_url = post.reddit_url if post else ""
        url = post.url if post else ""
        lines.append(f"\n{i}. [{subreddit}] {title} (id: {rec.id})")
        if url:
            lines.append(f"- link: {url}")
        if reddit_url:
            lines.append(f"- Reddit讨论: {reddit_url}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def post_read(
    state: RedditReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = RedditReaderConfig.from_runnable_config(config)
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

    raw_posts = get_reddit_top_posts(
        max_total=configurable.max_read_posts,
        per_sub_limit=configurable.per_sub_limit,
    )

    found_posts = [
        PostInfo(
            id=str(item.get("id", "")),
            subreddit=item["subreddit"],
            title=item["title"],
            selftext=item["selftext"],
            url=item["url"],
            reddit_url=f"https://reddit.com{item['permalink']}",
            score=item["score"],
            num_comments=item["num_comments"],
        )
        for item in raw_posts
    ]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=format_post_data(found_posts) + "\n\n" + get_post_task_instruction()),
    ]
    result = await _ainvoke_post_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_posts, found_posts)
    return Command(
        goto=END,
        update={
            "found_posts": found_posts,
            "recommended_posts": result.recommended_posts,
            "messages": [AIMessage(content=summary_text)],
        },
    )


reddit_reader_graph = StateGraph(RedditReaderState)
reddit_reader_graph.add_node("post_read", post_read)
reddit_reader_graph.add_edge(START, "post_read")
reddit_reader_graph.add_edge("post_read", END)

reddit_reader_graph = reddit_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(reddit_reader_graph.ainvoke({}))
    print(result)
