# Redis 深度版重写报告

## 结果

- 版本基线：Redis 7.4 OSS，官方源码 commit `93a16ee`
- 独立主题：50
- 卡片：250
- 每主题：固定 5 张连续追问卡
- APKG：`D:\claudeProjects\anki\牌组\八股文\Redis\Redis八股文.apkg`
- 唯一知识源与构建入口：`knowledge/`
- 旧版提纲：归档在 `knowledge_legacy/`，不再参与构建
- Python 职责：只解析、校验和打包 Markdown，不保存知识正文

## 相比上一版的实质变化

上一版 20 个主题、124 张卡，主要覆盖“是什么、为什么、怎么用”。本版把宽主题拆到真实实现单元，例如：

- 原“SDS、字典、跳表与对象编码”拆成 redisObject、SDS 布局、SDS 扩容、dict、rehash/SCAN、跳表、ZSet 双索引等主题。
- 原“事件驱动与单线程”拆成 aeEventLoop、一次事件循环、请求解析/命令检查/传播/回包、I/O threads/BIO/fork。
- 原“RDB 与 AOF”拆成 RDB 文件格式、BGSAVE/fork/COW、AOF 三层缓冲与 fsync、Redis 7 多部件 AOF、加载与损坏恢复。
- 原“主从复制”拆成 replid/replid2/offset、共享 replBufBlock backlog、PSYNC 全量/部分同步、WAIT/min-replicas 的保证边界。
- 原“Sentinel/Cluster”补齐 SDOWN/ODOWN、epoch 投票、failover 状态机、clusterState/clusterNode、bus gossip、PFAIL/FAIL、MOVED/ASK 和迁槽状态。
- 原“事务与锁”补齐 multiState/multiCmd、WATCH 双向索引、DIRTY_CAS/DIRTY_EXEC、Lua 运行错误无回滚、Redisson Hash 重入计数、watchdog 与 fencing。

## 自动质量检查

- Markdown 文件：50
- 二级卡片分区：250
- 每文件分区数：全部为 5
- 唯一问题数：250，无重复问题
- 答案长度：最短超过 120 个字符，中位数约 213 个字符
- 代码围栏：全部闭合
- APKG notes/cards：250/250
- 重复 GUID：0
- Redis/追问链标签缺失：0

## 同步策略

- 已先写入并验证 250 张带 `源码机制级`、`Redis-7.4` 标签的新卡，再删除精确匹配的 124 张上一版 `Redis + 追问链` 笔记。
- 删除预演结果为 124 notes / 124 cards；正式删除后未找到项为 0。
- 最终本地 Anki：深度版 250，上一版 0，`八股文::Redis` 树下总计 250。
- MCP 同步时将 250 张卡放在 `八股文::Redis` 根牌组，通过模块/主题标签区分；APKG 仍保留完整的 50 个叶子牌组层级。
- 旧版 Markdown 仍归档在 `knowledge_legacy/`，需要时可以人工查阅；当前 APKG 只由 `knowledge/` 的深度版 Markdown 构建。
- 本次没有触碰其他技术栈或不带 `追问链` 标签的用户笔记；旧卡的复习进度没有迁移到结构完全不同的新卡。

## 单一事实源

- 内容维护：直接编辑 `knowledge/<模块>/<主题>/*.md`。
- APKG 构建：`build_redis_all.py` 读取 Markdown 后打包。
- Anki 同步：`export_redis_notes_json.py` 读取同一批 Markdown 后输出 JSON。
- 仓库不再保留用 Python 常量生成这些 Markdown 的脚本，避免知识正文出现双份来源。
