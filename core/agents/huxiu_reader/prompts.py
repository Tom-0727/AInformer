from core.agents.huxiu_reader.state import HuxiuArticleInfo


def format_article_data(found_articles: list[HuxiuArticleInfo]) -> str:
    article_blocks = []
    for article in found_articles:
        article_blocks.append(
            f"""[Article]
id: {article.id}
title: {article.title}
summary: {article.summary}
link: {article.link}
"""
        )
    articles_text = "\n".join(article_blocks)
    return f"""请阅读以下虎嗅文章列表：

{articles_text}"""


def get_article_task_instruction() -> str:
    return """你的任务不是选"最火"的，而是选"最有价值且与用户目标强相关"的。尤其要过滤制造焦虑、标题党内容。

【优先考虑】
- AI 应用落地的深度分析与真实案例
- 商业模式创新与行业格局变化
- 值得关注的创业方向或产品策略
- 中国科技行业的趋势信号（AI、SaaS、出海等）
- 有具体数据支撑的行业分析文章

【降低优先级或标风险】
- 焦虑制造类文章（贩卖危机感、恐惧）
- 蹭热点但无实质内容
- 情绪化标题党
- 纯粹的品牌软文或公关稿
- 与 AI/创业方向无关的社会娱乐内容

【推荐理由要求】
每个被推荐的文章必须写清楚"具体价值"，例如：
- 提供了某个行业的深度洞察
- 揭示了 AI 应用落地的真实挑战或机会
- 包含可借鉴的商业逻辑或竞争策略
- 是某个方向的早期趋势信号

【风险项要求】
- 仅凭标题，内容深度无法判断
- 可能是情绪化内容或焦虑贩卖
- 信息密度低，以观点代替事实
- 与用户核心目标关联有限
""".strip()
