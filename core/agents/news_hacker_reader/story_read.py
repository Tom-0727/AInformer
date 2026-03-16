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

from core.agents.news_hacker_reader.configuration import NewsHackerReaderConfig
from core.agents.news_hacker_reader.state import (
    StoryInfo,
    StoryShortlistResult,
    StoryRecommendation,
    NewsHackerReaderState,
    StoryReadResult,
)
from core.tools.info_collect.hacker_news_collect import (
    enrich_hacker_news_stories,
    get_hacker_news_top_stories,
)
from core.configs.system_prompt import SYSTEM_PROMPT
from core.agents.news_hacker_reader.prompts import (
    format_story_deep_data,
    format_story_title_data,
    get_story_shortlist_instruction,
    get_story_task_instruction,
)

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_with_tool(
    model,
    messages: list[SystemMessage | HumanMessage],
    tool_cls,
):
    tool_model = model.bind_tools(
        [tool_cls],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(
        tools=[tool_cls],
        first_tool_only=True,
    )
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError(f"Model did not return a {tool_cls.__name__} tool call.")
    return result


def _format_recommendations(
    recommendations: list[StoryRecommendation], found_stories: list[StoryInfo]
) -> str:
    found_story_by_id = {s.id: s for s in found_stories}
    lines = ["# Hacker News 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        story = found_story_by_id.get(rec.id)
        title = story.title if story else "(未匹配到新闻信息)"
        hn_url = story.hn_url if story else ""
        url = story.url if story else ""
        lines.append(f"\n{i}. {title} (id: {rec.id})")
        if url:
            lines.append(f"- link: {url}")
        if hn_url:
            lines.append(f"- HN讨论: {hn_url}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def story_read(
    state: NewsHackerReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = NewsHackerReaderConfig.from_runnable_config(config)
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

    raw_stories = get_hacker_news_top_stories(max_count=configurable.max_read_stories)

    found_stories = [
        StoryInfo(
            id=str(i),
            title=item["title"],
            url=item.get("url", ""),
            hn_url=item["hn_url"],
            score=item["score"],
            comments=item["descendants"],
            story_text=item.get("story_text", ""),
            article_preview=item.get("article_preview", ""),
            discussion_preview=item.get("discussion_preview", ""),
        )
        for i, item in enumerate(raw_stories, 1)
    ]

    shortlist_messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=format_story_title_data(found_stories)
            + "\n\n"
            + get_story_shortlist_instruction(configurable.max_shortlist_stories)
        ),
    ]
    shortlist_result: StoryShortlistResult = await _ainvoke_with_tool(
        read_model,
        shortlist_messages,
        StoryShortlistResult,
    )

    shortlist_ids = {
        story_id for story_id in shortlist_result.shortlisted_ids if story_id
    }
    shortlisted_pairs = [
        (str(idx), item) for idx, item in enumerate(raw_stories, 1) if str(idx) in shortlist_ids
    ]

    if not shortlisted_pairs:
        shortlisted_pairs = [
            (str(idx), item)
            for idx, item in enumerate(raw_stories[: configurable.max_shortlist_stories], 1)
        ]

    enriched_raw_stories = enrich_hacker_news_stories([item for _, item in shortlisted_pairs])
    enriched_found_stories = [
        StoryInfo(
            id=story_id,
            title=item["title"],
            url=item.get("url", ""),
            hn_url=item["hn_url"],
            score=item["score"],
            comments=item["descendants"],
            story_text=item.get("story_text", ""),
            article_preview=item.get("article_preview", ""),
            discussion_preview=item.get("discussion_preview", ""),
        )
        for (story_id, _), item in zip(shortlisted_pairs, enriched_raw_stories, strict=False)
    ]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=format_story_deep_data(enriched_found_stories) + "\n\n" + get_story_task_instruction()),
    ]
    result: StoryReadResult = await _ainvoke_with_tool(read_model, messages, StoryReadResult)

    summary_text = _format_recommendations(result.recommended_stories, enriched_found_stories)
    return Command(
        goto=END,
        update={
            "found_stories": enriched_found_stories,
            "recommended_stories": result.recommended_stories,
            "messages": [AIMessage(content=summary_text)],
        },
    )


news_hacker_reader_graph = StateGraph(NewsHackerReaderState)
news_hacker_reader_graph.add_node("story_read", story_read)
news_hacker_reader_graph.add_edge(START, "story_read")
news_hacker_reader_graph.add_edge("story_read", END)

news_hacker_reader_graph = news_hacker_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(news_hacker_reader_graph.ainvoke({}))
    print(result)
