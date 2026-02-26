# Github Trending Reader
> 从 github trending 网页爬取到的 repos 有很多，对这些 repos 阅读，并筛选我需要看的推送到群里

## Design
> Workflow
输入：时间类别['daily', 'weekly', 'monthly']
1. 调用 core/tools/info_collect/github_trending_collect.py 的 get_github_trending 并输入对应时间类别，根据环境配置输入 max_count 和 max_length 然后得到repo信息列表
2. 调用 LLM 结构化构造 repo 信息，以及prompt的repo感兴趣的与筛选逻辑，要求按 state.py 定义的schema输出
    2.1. 输出符合要求的repo，包含 推荐理由（根据用户的兴趣和筛选逻辑，为什么推荐阅读这个repo，必须说明“具体价值”），风险项（判断是否是过度营销，套壳等），以及 repo title，repo link，repo description（这后面三个可以靠后续逻辑，比如仅输入某个标识如id，然后hardcode索引回这些基本信息）
3. 解析 schema，组织成结构化文本
输出：结构化文本