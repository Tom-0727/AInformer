from core.agents.taaft_reader.state import AiToolInfo


def get_system_prompt() -> str:
    return """你是 There's An AI for That 工具筛选助手。

请根据用户提供的筛选规则与 AI 工具列表，筛选值得关注的工具，并严格按 schema 输出结构化结果。
""".strip()


def get_tool_read_prompt(found_tools: list[AiToolInfo]) -> str:
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

    return f"""
请阅读以下 AI 工具列表，并从中筛选出真正值得用户关注的工具。

以下是待筛选工具列表：

{tools_text}

你的任务不是选"最新"的，而是选"最有价值且与用户目标强相关"的。

【用户背景】
用户是 AI Agent Engineer + 创业者：
- 技术方向：AI Agent、workflow 自动化、LLM 应用开发、效率工具
- 需要发现能提升研究效率、开发效率或自动化能力的工具
- 对套壳产品无兴趣，关注有真实技术深度或独特用例的工具

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
所有专有名词不要翻译成中文（如 Agent、workflow、LLM 等）。

【风险项要求】
- 功能描述过于模糊
- 疑似套壳或简单封装
- 产品早期，可用性未经验证
- 与用户核心目标关联有限

【筛选风格】
- 宁缺毋滥，少选但必须有理由
- 关注工具的实际能力，而非营销文案

【最终输出要求】
- 每个推荐项只输出：id、recommendation_reason、risk_items
- 不要在输出中重复 name、description 等基本信息
""".strip()
