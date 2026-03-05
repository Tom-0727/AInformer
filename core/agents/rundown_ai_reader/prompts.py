from core.agents.rundown_ai_reader.state import RundownItemInfo


def format_newsletter_data(found_items: list[RundownItemInfo]) -> str:
    item_blocks = []
    for item in found_items:
        content_preview = item.content[:2000] if item.content else item.summary
        item_blocks.append(
            f"""[Newsletter]
id: {item.id}
headline: {item.headline}
summary: {item.summary}
content: {content_preview}
link: {item.link}
"""
        )
    items_text = "\n".join(item_blocks)
    return f"""请阅读以下 The Rundown AI newsletter 内容：

{items_text}"""


def get_newsletter_task_instruction() -> str:
    return """你的任务不是选"最多人讨论"的，而是选"最有实质价值且与用户目标强相关"的。

【优先考虑】
- 重要 AI 模型发布或能力突破（有实质技术价值）
- Agent / workflow / 自动化方向的重要进展
- AI 行业格局变化（大厂策略、新兴公司、并购）
- 值得关注的新工具或开源项目
- 能指导用户技术选型或产品方向的洞察

【降低优先级或标风险】
- 纯市场炒作或 hype（无技术实质）
- 重复已知信息，无新增洞察
- 过度关注财务数据而缺乏技术/产品分析
- 与 AI Agent / 应用开发方向关联较弱

【推荐理由要求】
每个被推荐的内容必须写清楚"具体价值"，例如：
- 说明了哪项 AI 能力的实质进展
- 指出了某个值得跟进的技术方向
- 揭示了 AI 行业格局的重要变化信号
- 包含对用户技术选型或产品判断有帮助的信息

【风险项要求】
- 信息来源未经验证，可能存在偏差
- 内容较浅，缺乏技术细节
- 可能是厂商 PR 信息
- 与用户核心目标关联有限
""".strip()
