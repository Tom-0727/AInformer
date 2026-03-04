from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from core.agents.product_hunt_reader.product_read import product_hunt_reader_graph
from core.agents.product_hunt_reader.state import ProductInfo, ProductRecommendation
from core.utils.inform import inform


def _extract_found_product_map(result: dict[str, Any]) -> dict[str, ProductInfo]:
    raw = result.get("found_products") or []
    product_map: dict[str, ProductInfo] = {}
    for item in raw:
        if isinstance(item, ProductInfo):
            product_map[item.id] = item
            continue
        if isinstance(item, dict):
            product = ProductInfo(
                id=str(item.get("id", "")),
                name=str(item.get("name", "")),
                tagline=str(item.get("tagline", "")),
                description=str(item.get("description", "")),
                link=str(item.get("link", "")),
            )
            product_map[product.id] = product
    return product_map


def _extract_recommended_products(result: dict[str, Any]) -> list[ProductRecommendation]:
    raw = result.get("recommended_products") or []
    products: list[ProductRecommendation] = []
    for item in raw:
        if isinstance(item, ProductRecommendation):
            products.append(item)
            continue
        if isinstance(item, dict):
            products.append(
                ProductRecommendation(
                    id=str(item.get("id", "")),
                    recommendation_reason=str(item.get("recommendation_reason", "")),
                    risk_items=[str(x) for x in item.get("risk_items", [])],
                )
            )
    return products


def _build_notify_message(
    recommendations: list[ProductRecommendation],
    found_product_map: dict[str, ProductInfo],
) -> str:
    if not recommendations:
        return "Product Hunt 今日暂无可推荐产品。"

    lines = ["Product Hunt 推荐："]
    for idx, rec in enumerate(recommendations, 1):
        product = found_product_map.get(rec.id)
        name = f"{product.name} — {product.tagline}" if product else f"(未匹配产品，id={rec.id})"
        link = product.link if product else ""
        risk_text = "；".join(rec.risk_items) if rec.risk_items else "未识别到明确风险点"
        lines.append(f"\n{idx}. {name}")
        if link:
            lines.append(f"链接：{link}")
        lines.append(f"推荐理由：{rec.recommendation_reason}")
        lines.append(f"风险点：{risk_text}")
    return "\n".join(lines)


async def product_hunt_inform() -> str:
    result = await product_hunt_reader_graph.ainvoke({})
    found_product_map = _extract_found_product_map(result)
    recommendations = _extract_recommended_products(result)
    message = _build_notify_message(recommendations, found_product_map)
    print(message)
    inform(message)
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="读取 Product Hunt 产品并发送结构化推荐到 Webhook")
    parser.parse_args()
    asyncio.run(product_hunt_inform())


if __name__ == "__main__":
    main()
