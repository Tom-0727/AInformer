# Reddit Reader
> 从 Reddit 多个技术 subreddit 获取热门帖子，通过 LLM 筛选出值得阅读的技术帖子并推送

## Design
> Workflow
1. 调用 `core/tools/info_collect/reddit_collect.py` 的 `get_reddit_top_posts`，通过 Reddit 公开 JSON API 获取多个 subreddit 的 Top Posts（默认30条），包含 subreddit、title、selftext、url、permalink、score、num_comments
2. 调用 LLM 结构化筛选帖子，使用 prompts 中定义的筛选偏好（AI/LLM/Agent/系统设计/开发工具优先，过滤 meme/水帖/非技术内容），要求按 `state.py` 定义的 schema 输出
   - 输出每条推荐：id、recommendation_reason、risk_items
3. 解析 schema，组织成结构化文本，通过 Webhook 推送通知

## 默认 Subreddit 列表
MachineLearning, LocalLLaMA, artificial, programming, ExperiencedDevs, systemdesign, devops, golang, rust, opensource

## 文件结构
```
core/agents/reddit_reader/
├── state.py           # State & Schema 定义 (PostInfo, PostRecommendation, PostReadResult)
├── configuration.py   # 可配置项 (read_model, max_read_posts, per_sub_limit)
├── prompts.py         # System prompt & 筛选 prompt
├── post_read.py       # LangGraph 主流程 (StateGraph: START -> post_read -> END)
└── __init__.py

core/tools/info_collect/
└── reddit_collect.py  # Reddit JSON API 数据采集 (带 retry)

core/services/
└── reddit_inform.py   # 通知服务入口 (调用 graph + webhook 推送)
```

## 运行
```bash
# 直接运行 agent
python -m core.agents.reddit_reader.post_read

# 通过 service 运行（含 webhook 推送）
python -m core.services.reddit_inform
```
