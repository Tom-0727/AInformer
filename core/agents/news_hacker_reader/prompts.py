from core.agents.news_hacker_reader.state import StoryInfo


def format_story_title_data(found_stories: list[StoryInfo]) -> str:
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
    return f"""请先阅读以下 Hacker News Top Stories 列表，只基于标题和基础元数据做第一轮粗筛：

{stories_text}"""


def get_story_shortlist_instruction(max_shortlist_stories: int) -> str:
    return f"""你的任务是先做“标题粗筛”，从全部 Hacker News 帖子中挑出最多 {max_shortlist_stories} 条最值得进一步深挖的候选。

这一轮不要假装自己已经读过正文。你只能依据 title、url、score、comments 判断“是否值得继续读”。

【粗筛目标】
- 优先保留看起来可能和 AI / LLM / Agent、系统设计、数据库、性能优化、开发工具、编程语言、基础设施相关的帖子
- 优先保留标题显示可能有深度技术内容、工程复盘、架构分析、基准测试、开源发布的帖子
- 即使热度不最高，只要标题明显更贴近用户目标，也应该入围

【降低优先级】
- 招聘、纯社会新闻、政治争议、泛商业新闻
- 明显缺乏技术深度的 Show HN、营销标题、情绪化标题
- 与开发者价值弱相关的话题

只返回最值得做第二轮深挖的 shortlisted_ids。""".strip()


def format_story_deep_data(found_stories: list[StoryInfo]) -> str:
    story_blocks = []
    for story in found_stories:
        story_text = story.story_text[:500] if story.story_text else "(无 HN 正文)"
        article_preview = story.article_preview[:1200] if story.article_preview else "(未抓取到外链正文预览)"
        discussion_preview = story.discussion_preview[:800] if story.discussion_preview else "(未抓取到有效评论预览)"
        story_blocks.append(
            f"""[Story]
id: {story.id}
title: {story.title}
url: {story.url}
hn_url: {story.hn_url}
score: {story.score}
comments: {story.comments}
story_text: {story_text}
article_preview: {article_preview}
discussion_preview: {discussion_preview}
"""
        )
    stories_text = "\n".join(story_blocks)
    return f"""请阅读以下已经通过第一轮粗筛、并补充了正文与讨论上下文的 Hacker News 候选列表：

{stories_text}"""


def get_story_task_instruction() -> str:
    return """你的任务不是选"最火"的，而是选"最有价值且与用户目标强相关"的。

判断时请优先依据 story_text、article_preview、discussion_preview，而不是只看标题。
如果正文预览缺失，要在推荐理由或风险项里明确说明判断依据不足。

【优先考虑】
- AI / LLM / Agent 相关的技术进展、工程实践、架构设计
- 系统设计、分布式系统、数据库、性能优化等深度技术文章
- 开发者工具、编程语言、编译器等基础设施相关
- 有深度的技术博客文章（而非新闻简讯）
- HN 评论区里出现高质量工程讨论、补充案例、反驳或实践经验的帖子
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
- 评论区补充了重要背景、工程争议点或实际落地经验
- 可以直接借鉴到日常开发工作中
另外必须简洁地概括这条新闻的核心内容。

【风险项要求】
风险项必须具体：
- 仅凭标题无法判断文章深度
- 可能是营销内容或产品推广
- 讨论较浅，缺少可操作的技术细节
- 与用户核心目标关联有限
""".strip()
