from core.agents.product_hunt_reader.state import ProductInfo


def format_product_data(found_products: list[ProductInfo]) -> str:
    product_blocks = []
    for product in found_products:
        product_blocks.append(
            f"""[Product]
id: {product.id}
name: {product.name}
tagline: {product.tagline}
description: {product.description}
link: {product.link}
"""
        )
    products_text = "\n".join(product_blocks)
    return f"""请阅读以下 Product Hunt 产品列表：

{products_text}"""


def get_product_task_instruction() -> str:
    return """你的任务不是选"票数最高"的，而是选"最有价值且与用户目标强相关"的。

【优先考虑】
- AI Agent / workflow 自动化工具
- 开发者工具（代码、调试、部署、监控）
- 效率工具（信息处理、知识管理、自动化）
- 有真实功能、清晰用例的 AI 应用
- 可能成为趋势方向的早期产品

【降低优先级或标风险】
- 功能单薄的套壳产品（仅是 ChatGPT wrapper）
- 描述过度营销，缺乏具体功能说明
- 与用户目标关联弱（纯娱乐、消费品、非技术类）
- Tagline 过于模糊，无法判断核心价值
- 已有大量同类竞品，无明显差异化

【推荐理由要求】
每个被推荐的产品必须写清楚"具体价值"，例如：
- 解决了某类 AI 开发或自动化的具体痛点
- 提供了新颖的 Agent 或 workflow 设计思路
- 可作为某类工具的替代或补充
- 代表了某个产品方向的趋势信号

【风险项要求】
- 功能描述模糊，核心能力不明
- 疑似套壳或简单封装
- 与用户目标关联有限
- 产品早期，稳定性和可用性未知
""".strip()
