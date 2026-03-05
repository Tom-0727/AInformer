from core.agents.kr36_reader.state import Kr36ArticleInfo


def format_article_data(found_articles: list[Kr36ArticleInfo]) -> str:
    article_blocks = []
    for article in found_articles:
        article_blocks.append(
            f"""[Article]
id: {article.id}
title: {article.title}
description: {article.description}
published_at: {article.published_at}
link: {article.link}
"""
        )
    articles_text = "\n".join(article_blocks)
    return f"""请阅读以下 36Kr 文章列表：

{articles_text}"""


def get_article_task_instruction() -> str:
    return """你的任务不是选"最热"的，而是选"最有价值且与用户目标强相关"的。

【优先考虑】
- AI 创业项目的产品动态、融资事件、商业模式分析
- AI 应用落地的真实案例与深度分析
- 行业趋势信号（有实质内容，非蹭热点）
- 值得关注的技术方向或产品策略分析
- 大厂 AI 战略与竞争格局分析

【降低优先级或标风险】
- 标题党、情绪化内容、焦虑贩卖
- 低质量快讯（信息密度极低）
- 重复话题或已有广泛报道
- 纯营销软文，无实质分析
- 与 AI/创业方向关联较弱

【推荐理由要求】
每个被推荐的文章必须写清楚"具体价值"，例如：
- 提供了某个 AI 应用方向的落地案例
- 揭示了值得关注的商业模式或竞争动态
- 包含可借鉴的产品策略或增长逻辑
- 是某个趋势方向的早期信号

【风险项要求】
- 仅凭标题和摘要，内容深度无法保证
- 可能是营销内容或公关稿
- 信息过于宏观，缺乏可操作的洞察
- 与用户核心目标关联有限
""".strip()
