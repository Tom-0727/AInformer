from core.agents.reddit_reader.state import PostInfo


def format_post_data(found_posts: list[PostInfo]) -> str:
    post_blocks = []
    for post in found_posts:
        selftext_preview = post.selftext[:500] if post.selftext else "(无正文，外链帖)"
        post_blocks.append(
            f"""[Post]
id: {post.id}
subreddit: r/{post.subreddit}
title: {post.title}
score: {post.score}
comments: {post.num_comments}
url: {post.url}
reddit_url: {post.reddit_url}
selftext_preview: {selftext_preview}
"""
        )
    posts_text = "\n".join(post_blocks)
    return f"""请阅读以下 Reddit 热门帖子列表：

{posts_text}"""


def get_post_task_instruction() -> str:
    return """你的任务不是选"最火"的，而是选"最有价值且与用户目标强相关"的。

【优先考虑】
- AI / LLM / Agent 相关的技术进展、工程实践、架构设计、benchmark、模型评测
- 系统设计、分布式系统、数据库、性能优化等深度技术讨论
- 开发者工具、编程语言、编译器等基础设施相关
- 有深度的技术讨论帖（含高质量评论区讨论的帖子尤其有价值）
- 开源项目发布或重大更新（尤其是有实际创新的）
- 本地部署 LLM、模型微调、推理优化等实践经验分享
- 值得关注的行业趋势信号

【降低优先级或标风险】
- 纯 meme、段子、截图帖
- 重复的"哪个模型好"类投票帖
- 纯粹的求助帖（个人环境问题、配置问题）
- 政治、社会新闻等非技术内容
- 标题党、情绪化讨论
- 营销软文、产品公告但无技术细节
- 与用户目标关联较弱，即使热度高也不要勉强推荐

【推荐理由要求】
每个被推荐的帖子都必须写清楚"具体价值"，例如但不限于：
- 提供了某类技术的深入分析、实测数据或最佳实践
- 介绍了值得关注的新工具/框架/库/模型
- 包含有价值的系统设计经验或架构决策
- 揭示了某个技术方向的发展趋势
- 社区讨论中包含有价值的工程经验和观点碰撞
- 可以直接借鉴到日常开发工作中
另外必须简洁地概括这条帖子的核心内容。

【风险项要求】
风险项必须具体：
- 仅凭标题无法判断帖子深度
- 可能是营销内容或产品推广
- 讨论较浅，缺少可操作的技术细节
- selftext 为空，需要点击外链才能判断价值
- 与用户核心目标关联有限
""".strip()
