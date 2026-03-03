# AInformer

AI 驱动的信息聚合与推送工具。自动抓取 GitHub Trending、Hacker News、Reddit 等平台的热门内容，通过 LLM 按用户偏好筛选过滤，将有价值的信息推送到飞书 / 钉钉机器人。

## 功能

- **GitHub Trending** — 筛选与 AI Agent、工程架构等方向相关的优质仓库
- **Hacker News** — 抓取热门故事并提炼要点
- **Reddit** — 订阅感兴趣的 subreddit，过滤低价值内容

## 技术栈

- Python 3.13+，[LangGraph](https://github.com/langchain-ai/langgraph) 构建 Agent 工作流
- LLM 调用：LangChain + OpenAI
- 通知推送：飞书 / 钉钉 Webhook

## 快速开始

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 填写 OPENAI_API_KEY 和 NOTIFY_WEBHOOK_URLS（逗号分隔多个 Webhook）
```

运行示例：

```bash
# GitHub Trending 每日推荐
uv run python -m core.services.github_trend_inform --since daily

# Hacker News
uv run python -m core.services.news_hacker_inform

# Reddit
uv run python -m core.services.reddit_inform
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API Key |
| `OPENAI_API_BASE` | OpenAI Base URL |
| `NOTIFY_WEBHOOK_URLS` | Webhook 地址，多个用逗号分隔（支持飞书、钉钉） |

