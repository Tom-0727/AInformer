from core.agents.product_hunt_reader.state import ProductInfo


def get_system_prompt() -> str:
    return """你是 Product Hunt 产品筛选助手。

请根据用户提供的筛选规则与 Product Hunt 产品列表，筛选值得关注的产品，并严格按 schema 输出结构化结果。
""".strip()


def get_product_read_prompt(found_products: list[ProductInfo]) -> str:
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

    return f"""
请阅读以下 Product Hunt 产品列表，并从中筛选出真正值得用户关注的产品。

以下是待筛选产品列表：

{products_text}

你的任务不是选"票数最高"的，而是选"最有价值且与用户目标强相关"的。

【用户背景】
用户是 AI Agent Engineer + 创业者：
- 技术方向：AI Agent、workflow 自动化、LLM 应用、开发者工具
- 产品感知：关注能提升研发效率、信息处理、自动化能力的工具
- 创业视角：关注商业模式创新、新兴产品方向、潜在竞品或合作对象

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
所有专有名词不要翻译成中文（如 Agent、workflow、LLM 等）。

【风险项要求】
- 功能描述模糊，核心能力不明
- 疑似套壳或简单封装
- 与用户目标关联有限
- 产品早期，稳定性和可用性未知

【筛选风格】
- 宁缺毋滥，少选但必须有理由
- 关注产品的实际功能价值，而非营销包装

【最终输出要求】
- 每个推荐项只输出：id、recommendation_reason、risk_items
- 不要在输出中重复 name、tagline、link 等基本信息
""".strip()
