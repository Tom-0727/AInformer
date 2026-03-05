from core.agents.github_trending_reader.state import RepoInfo


def format_repo_data(since: str, found_repos: list[RepoInfo]) -> str:
    repo_blocks = []
    for repo in found_repos:
        repo_blocks.append(
            f"""[Repo]
id: {repo.id}
title: {repo.title}
link: {repo.link}
description: {repo.description}
"""
        )
    repos_text = "\n".join(repo_blocks)
    return f"""请阅读以下 GitHub Trending ({since}) 仓库列表：

{repos_text}"""


def get_repo_task_instruction() -> str:
    return """你的任务不是选"最火"的，而是选"最有价值且与用户目标强相关"的。

【优先考虑】
- AI Agent / Agent memory / 长期状态管理 / 持续学习 / 工作流系统
- 能帮助构建长期可积累、可复利的智能体系统
- 有明确工程实现、架构启发、研究价值、效率价值的项目
- 能直接提升用户在研究、分析、自动化、知识管理上的能力

【降低优先级或标风险】
- 仅概念上蹭热点
- README 风格过度营销
- 套壳、换皮、简单封装但缺乏独立价值
- 描述太短，无法判断核心能力
- 和用户目标关联较弱，即使热度高也不要勉强推荐

【推荐理由要求】
每个被推荐项目都必须写清楚"具体价值"，例如但不限于：
- 可作为某类 Agent 架构参考
- 可借鉴其 memory / workflow / context 管理设计
- 可用于提升研究效率、信息处理效率或自动化能力
- 可作为趋势信号，帮助判断某个方向是否值得继续跟进
- 可迁移其工程实现思路到用户自己的系统中
另外必须简洁地说明这个repo的核心用途是什么，怎么使用的（不用到具体启动脚本之类的，只是说大概用法）。

【风险项要求】
风险项必须具体，不要写空话。若信息不足，也请明确写出：
- 信息不足，暂无法判断真实技术深度
- 描述更像营销话术，缺少可验证细节
- 疑似已有能力的重新包装
- 与用户核心目标关联有限

【筛选原则】
- 你必须仅基于输入的仓库信息进行判断，不得编造输入中不存在的事实
- 如果信息不足，可以保守处理，并在风险项中明确指出"不足以判断"
""".strip()
