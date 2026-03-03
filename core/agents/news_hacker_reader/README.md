# News Hacker Reader
> 从 Hacker News Top Stories 获取新闻列表，通过 LLM 筛选出值得阅读的技术新闻并推送

## Design
> Workflow
1. 调用 `core/tools/info_collect/hacker_news_collect.py` 的 `get_hacker_news_top_stories`，通过 HN 官方 API 获取 Top Stories（默认30条），包含 title、url、score、comments、hn_url
2. 调用 LLM 结构化筛选新闻，使用 prompts 中定义的筛选偏好（AI/系统设计/开发工具/深度技术文章优先，过滤营销/水帖/非技术内容），要求按 `state.py` 定义的 schema 输出
   - 输出每条推荐：id、recommendation_reason、risk_items
3. 解析 schema，组织成结构化文本，通过 Webhook 推送通知

## 文件结构
```
core/agents/news_hacker_reader/
├── state.py           # State & Schema 定义 (StoryInfo, StoryRecommendation, StoryReadResult)
├── configuration.py   # 可配置项 (read_model, max_read_stories)
├── prompts.py         # System prompt & 筛选 prompt
├── story_read.py      # LangGraph 主流程 (StateGraph: START -> story_read -> END)
└── __init__.py

core/tools/info_collect/
└── hacker_news_collect.py   # HN API 数据采集 (带 retry)

core/services/
└── news_hacker_inform.py    # 通知服务入口 (调用 graph + webhook 推送)
```

## 运行
```bash
# 直接运行 agent
python -m core.agents.news_hacker_reader.story_read

# 通过 service 运行（含 webhook 推送）
python -m core.services.news_hacker_inform
```
