from core.agents.taaft_reader.state import AiToolInfo


def format_tool_data(found_tools: list[AiToolInfo]) -> str:
    tool_blocks = []
    for tool in found_tools:
        tool_blocks.append(
            f"""[Tool]
id: {tool.id}
name: {tool.name}
use_case: {tool.use_case}
description: {tool.description}
link: {tool.link}
"""
        )
    tools_text = "\n".join(tool_blocks)
    return f"""请阅读以下 AI 工具列表：

{tools_text}"""


def get_tool_task_instruction() -> str:
    return """你的任务不是选"最新"的，而是选"最有价值且与用户目标强相关"的。

【优先考虑】
- 能直接提升 AI Agent 开发或调试效率的工具
- Workflow 自动化、数据处理、信息提取相关工具
- 有独特技术能力的 AI 研究或分析工具
- 开发者友好的 API / SDK / 集成工具
- 能填补现有工具链空白的新兴工具

【降低优先级或标风险】
- 功能单薄的 ChatGPT wrapper 或套壳产品
- 描述模糊，无法判断核心差异化能力
- 消费级产品（无明显开发者/工程师价值）
- 已有大量功能相似的成熟替代品
- 仅有演示，无实际可用产品

【推荐理由要求】
每个被推荐的工具必须写清楚"具体价值"，例如：
- 解决了某类 AI 开发流程中的具体痛点
- 提供了其他工具不具备的独特能力
- 可以直接集成到用户的 Agent 开发工作流中
- 代表了某个新兴 AI 工具方向的典型产品

【风险项要求】
- 功能描述过于模糊
- 疑似套壳或简单封装
- 产品早期，可用性未经验证
- 与用户核心目标关联有限
""".strip()
