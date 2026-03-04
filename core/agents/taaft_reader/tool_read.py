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

from core.agents.taaft_reader.configuration import TaaftReaderConfig
from core.agents.taaft_reader.state import (
    AiToolInfo,
    AiToolRecommendation,
    TaaftReaderState,
    AiToolReadResult,
)
from core.tools.info_collect.taaft_collect import get_taaft_tools
from core.agents.taaft_reader.prompts import get_system_prompt, get_tool_read_prompt

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_tool_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> AiToolReadResult:
    tool_model = model.bind_tools(
        [AiToolReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(tools=[AiToolReadResult], first_tool_only=True)
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return an AiToolReadResult tool call.")
    return result


def _format_recommendations(
    recommendations: list[AiToolRecommendation], found_tools: list[AiToolInfo]
) -> str:
    found_by_id = {t.id: t for t in found_tools}
    lines = ["# There's An AI for That 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        tool = found_by_id.get(rec.id)
        name = tool.name if tool else "(未匹配到工具信息)"
        link = tool.link if tool else ""
        lines.append(f"\n{i}. {name} (id: {rec.id})")
        if link:
            lines.append(f"- link: {link}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def tool_read(
    state: TaaftReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = TaaftReaderConfig.from_runnable_config(config)
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

    raw_tools = get_taaft_tools(max_count=configurable.max_read_tools)
    if not raw_tools:
        return Command(
            goto=END,
            update={
                "found_tools": [],
                "recommended_tools": [],
                "messages": [AIMessage(content="# There's An AI for That\n暂无数据（页面可能为纯 JS 渲染）")],
            },
        )

    found_tools = [
        AiToolInfo(
            id=str(i),
            name=item["name"],
            description=item.get("description", ""),
            use_case=item.get("use_case", ""),
            link=item["link"],
        )
        for i, item in enumerate(raw_tools, 1)
    ]

    messages = [
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=get_tool_read_prompt(found_tools)),
    ]
    result = await _ainvoke_tool_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_tools, found_tools)
    return Command(
        goto=END,
        update={
            "found_tools": found_tools,
            "recommended_tools": result.recommended_tools,
            "messages": [AIMessage(content=summary_text)],
        },
    )


taaft_reader_graph = StateGraph(TaaftReaderState)
taaft_reader_graph.add_node("tool_read", tool_read)
taaft_reader_graph.add_edge(START, "tool_read")
taaft_reader_graph.add_edge("tool_read", END)

taaft_reader_graph = taaft_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(taaft_reader_graph.ainvoke({}))
    print(result)
