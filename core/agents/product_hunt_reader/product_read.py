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

from core.agents.product_hunt_reader.configuration import ProductHuntReaderConfig
from core.agents.product_hunt_reader.state import (
    ProductInfo,
    ProductRecommendation,
    ProductHuntReaderState,
    ProductReadResult,
)
from core.tools.info_collect.product_hunt_collect import get_product_hunt_products
from core.agents.product_hunt_reader.prompts import get_system_prompt, get_product_read_prompt

load_dotenv()

configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "temperature", "model_provider"),
)


async def _ainvoke_product_read_with_tools(
    model, messages: list[SystemMessage | HumanMessage]
) -> ProductReadResult:
    tool_model = model.bind_tools(
        [ProductReadResult],
        tool_choice="required",
        parallel_tool_calls=False,
    )
    parser = PydanticToolsParser(tools=[ProductReadResult], first_tool_only=True)
    result = await (tool_model | parser).ainvoke(messages)
    if result is None:
        raise ValueError("Model did not return a ProductReadResult tool call.")
    return result


def _format_recommendations(
    recommendations: list[ProductRecommendation], found_products: list[ProductInfo]
) -> str:
    found_by_id = {p.id: p for p in found_products}
    lines = ["# Product Hunt 推荐结果"]
    for i, rec in enumerate(recommendations, 1):
        product = found_by_id.get(rec.id)
        name = f"{product.name} — {product.tagline}" if product else "(未匹配到产品信息)"
        link = product.link if product else ""
        lines.append(f"\n{i}. {name} (id: {rec.id})")
        if link:
            lines.append(f"- link: {link}")
        lines.append(f"- 推荐理由: {rec.recommendation_reason}")
        lines.append(f"- 风险项: {'；'.join(rec.risk_items)}")
    return "\n".join(lines)


async def product_read(
    state: ProductHuntReaderState, config: RunnableConfig
) -> Command[Literal["__end__"]]:
    configurable = ProductHuntReaderConfig.from_runnable_config(config)
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

    raw_products = get_product_hunt_products(max_count=configurable.max_read_products)
    found_products = [
        ProductInfo(
            id=str(i),
            name=item["name"],
            tagline=item.get("tagline", ""),
            description=item.get("description", ""),
            link=item["link"],
        )
        for i, item in enumerate(raw_products, 1)
    ]

    messages = [
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=get_product_read_prompt(found_products)),
    ]
    result = await _ainvoke_product_read_with_tools(read_model, messages)

    summary_text = _format_recommendations(result.recommended_products, found_products)
    return Command(
        goto=END,
        update={
            "found_products": found_products,
            "recommended_products": result.recommended_products,
            "messages": [AIMessage(content=summary_text)],
        },
    )


product_hunt_reader_graph = StateGraph(ProductHuntReaderState)
product_hunt_reader_graph.add_node("product_read", product_read)
product_hunt_reader_graph.add_edge(START, "product_read")
product_hunt_reader_graph.add_edge("product_read", END)

product_hunt_reader_graph = product_hunt_reader_graph.compile()


if __name__ == "__main__":
    result = asyncio.run(product_hunt_reader_graph.ainvoke({}))
    print(result)
