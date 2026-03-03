from core.agents.news_hacker_reader.state import StoryInfo


def get_system_prompt() -> str:
    return """你是 Hacker News 新闻筛选助手。

请根据用户提供的筛选规则与 Hacker News Top Stories 列表，筛选值得阅读的新闻，并严格按 schema 输出结构化结果。
""".strip()


def get_story_read_prompt(found_stories: list[StoryInfo]) -> str:
    story_blocks = []
    for story in found_stories:
        story_blocks.append(
            f"""[Story]
id: {story.id}
title: {story.title}
url: {story.url}
hn_url: {story.hn_url}
score: {story.score}
comments: {story.comments}
"""
        )

    stories_text = "\n".join(story_blocks)

    return f"""
请阅读以下 Hacker News Top Stories 列表，并从中筛选出真正值得用户阅读的新闻。

以下是待筛选列表：

{stories_text}

你的任务不是选"最火"的，而是选"最有价值且与用户目标强相关"的。

【用户筛选偏好】
用户最在意的是：
1. 是否与其技术方向和长期目标强相关；
2. 是否有真实技术深度、工程实践价值、行业洞察或产品启发；
3. 是否只是水帖、营销内容、情绪化讨论或重复话题。

【优先考虑】
- AI / LLM / Agent 相关的技术进展、工程实践、架构设计
- 系统设计、分布式系统、数据库、性能优化等深度技术文章
- 开发者工具、编程语言、编译器等基础设施相关
- 有深度的技术博客文章（而非新闻简讯）
- 开源项目发布（尤其是有实际创新的）
- 值得关注的行业趋势信号

【降低优先级或标风险】
- 纯粹的招聘帖、Show HN 但缺乏技术深度
- 政治、社会新闻等非技术内容
- 标题党、情绪化讨论
- 营销软文、产品公告但无技术细节
- 已被广泛讨论的重复话题
- 与用户目标关联较弱，即使热度高也不要勉强推荐

【推荐理由要求】
每个被推荐的新闻都必须写清楚"具体价值"，例如但不限于：
- 提供了某类技术的深入分析或最佳实践
- 介绍了值得关注的新工具/框架/库
- 包含有价值的系统设计经验或架构决策
- 揭示了某个技术方向的发展趋势
- 可以直接借鉴到日常开发工作中
另外必须简洁地概括这条新闻的核心内容。
所有专有名词不要翻译成中文。

【风险项要求】
风险项必须具体：
- 仅凭标题无法判断文章深度
- 可能是营销内容或产品推广
- 讨论较浅，缺少可操作的技术细节
- 与用户核心目标关联有限

【筛选风格】
- 宁缺毋滥
- 可以少选，但入选项必须有明确理由
- 如果某条新闻无法证明有价值，就不要因为热度而选它

【最终输出要求】
- 每个推荐项只输出：id、recommendation_reason、risk_items
- 不要在输出中重复 title、url 等基本信息
""".strip()
