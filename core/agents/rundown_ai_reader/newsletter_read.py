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

from core.agents.rundown_ai_reader.configuration import RundownAiReaderConfig
from core.agents.rundown_ai_reader.state import (
    RundownItemInfo,
    RundownItemRecommendation,
    RundownAiReaderState,
    RundownReadResult,
)
from core.tools.info_collect.rundown_ai_collect import get_rundown_ai_newsletters
from core.configs.system_prompt import SYSTEM_PROMPT
from core.agents.rundown_ai_reader.prompts import format_newsletter_data, get_newsletter_task_instruction

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_newsletter_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> RundownReadResult:
    tool_model = model.bind_tools(
        [RundownReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(tools=[RundownReadResult], first_tool_only=True)
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return a RundownReadResult tool call.")
    return result


def _format_recommendations(
    recommendations: list[RundownItemRecommendation], found_items: list[RundownItemInfo]
) -> str:
    found_by_id = {item.id: item for item in found_items}
    lines = ["# The Rundown AI 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        item = found_by_id.get(rec.id)
        headline = item.headline if item else "(未匹配到内容)"
        link = item.link if item else ""
        lines.append(f"\n{i}. {headline} (id: {rec.id})")
        if link:
            lines.append(f"- link: {link}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def newsletter_read(
    state: RundownAiReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = RundownAiReaderConfig.from_runnable_config(config)
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

    raw_items = get_rundown_ai_newsletters(
        max_count=configurable.max_read_items,
        fetch_content=True,
    )
    found_items = [
        RundownItemInfo(
            id=str(i),
            headline=item["headline"],
            summary=item.get("summary", ""),
            content=item.get("content", ""),
            link=item["link"],
        )
        for i, item in enumerate(raw_items, 1)
    ]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=format_newsletter_data(found_items) + "\n\n" + get_newsletter_task_instruction()),
    ]
    result = await _ainvoke_newsletter_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_items, found_items)
    return Command(
        goto=END,
        update={
            "found_items": found_items,
            "recommended_items": result.recommended_items,
            "messages": [AIMessage(content=summary_text)],
        },
    )


rundown_ai_reader_graph = StateGraph(RundownAiReaderState)
rundown_ai_reader_graph.add_node("newsletter_read", newsletter_read)
rundown_ai_reader_graph.add_edge(START, "newsletter_read")
rundown_ai_reader_graph.add_edge("newsletter_read", END)

rundown_ai_reader_graph = rundown_ai_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(rundown_ai_reader_graph.ainvoke({}))
    print(result)
