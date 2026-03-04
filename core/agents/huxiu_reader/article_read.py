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

from core.agents.huxiu_reader.configuration import HuxiuReaderConfig
from core.agents.huxiu_reader.state import (
    HuxiuArticleInfo,
    HuxiuArticleRecommendation,
    HuxiuReaderState,
    HuxiuReadResult,
)
from core.tools.info_collect.huxiu_collect import get_huxiu_articles
from core.agents.huxiu_reader.prompts import get_system_prompt, get_article_read_prompt

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_article_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> HuxiuReadResult:
    tool_model = model.bind_tools(
        [HuxiuReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(tools=[HuxiuReadResult], first_tool_only=True)
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return a HuxiuReadResult tool call.")
    return result


def _format_recommendations(
    recommendations: list[HuxiuArticleRecommendation], found_articles: list[HuxiuArticleInfo]
) -> str:
    found_by_id = {a.id: a for a in found_articles}
    lines = ["# 虎嗅 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        article = found_by_id.get(rec.id)
        title = article.title if article else "(未匹配到文章信息)"
        link = article.link if article else ""
        lines.append(f"\n{i}. {title} (id: {rec.id})")
        if link:
            lines.append(f"- link: {link}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def article_read(
    state: HuxiuReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = HuxiuReaderConfig.from_runnable_config(config)
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

    raw_articles = get_huxiu_articles(max_count=configurable.max_read_articles)
    found_articles = [
        HuxiuArticleInfo(
            id=str(i),
            title=item["title"],
            summary=item.get("summary", ""),
            link=item["link"],
        )
        for i, item in enumerate(raw_articles, 1)
    ]

    messages = [
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=get_article_read_prompt(found_articles)),
    ]
    result = await _ainvoke_article_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_articles, found_articles)
    return Command(
        goto=END,
        update={
            "found_articles": found_articles,
            "recommended_articles": result.recommended_articles,
            "messages": [AIMessage(content=summary_text)],
        },
    )


huxiu_reader_graph = StateGraph(HuxiuReaderState)
huxiu_reader_graph.add_node("article_read", article_read)
huxiu_reader_graph.add_edge(START, "article_read")
huxiu_reader_graph.add_edge("article_read", END)

huxiu_reader_graph = huxiu_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(huxiu_reader_graph.ainvoke({}))
    print(result)
