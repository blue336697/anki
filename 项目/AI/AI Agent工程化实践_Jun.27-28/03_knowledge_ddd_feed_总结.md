# 03_knowledge_ddd_feed.pdf 总结

> 文件名：`03_knowledge_ddd_feed.pdf`  
> 正文标题：Module 03 · Knowledge (1) · DDD + Feed  
> 页数：14 页

## 一句话总结

这份 PDF 讲的是 AgentOS 的 Knowledge 模块如何起步：不要把所有信息塞进一个臃肿的 `CLAUDE.md`，而是用 DDD 四文档组织长期知识，再用 Feed / Capture Hook 把 session 中的纠正、决策和发现自动流入 `corrections.log`，为后续 Governance 和 Distillation 提供原料。

## 核心命题：Knowledge 是 Agent 的长期记忆系统

课程指出，Agent 每次启动时本质上都是“白纸”：

- 不知道项目做什么。
- 不知道上次做到哪。
- 不知道踩过什么坑。
- 不知道团队底线是什么。
- 不知道哪些架构决策不能轻易推翻。

Knowledge 模块要解决的就是这个问题。它不是单个文档，而是一个长期记忆系统，包含：

| 部分 | 作用 |
|---|---|
| DDD | 结构化领域知识 |
| Feed | 经验流入入口 |
| Governance | 三层治理，后续模块展开 |
| Distillation | 蒸馏进化，后续模块展开 |

本 PDF 聚焦前两块：DDD + Feed。

## 为什么不能继续堆 CLAUDE.md

很多项目会把所有内容都塞进一个 `CLAUDE.md`：

- 项目描述。
- 代码规范。
- API 配置。
- 一堆 rules。
- 很多 IMPORTANT。
- 越来越多的补丁式提醒。

问题是：

```text
什么都有 = 什么都不突出
```

Context Window 虽然很大，但注意力不是均匀分布的：

- 前段 attention 最强。
- 中段变弱。
- 尾段可能被忽略。

所以，如果把所有规则、背景、状态、历史决策都塞在一起，Agent 不一定能在当下任务中读到真正重要的部分。

课程建议把 `CLAUDE.md` 从“垃圾场”变成“图书馆”：信息分门别类，按需注入。

## DDD 四文档

课程定义了四份 Knowledge 文档：

| 文档 | 存什么 | 什么时候注入 | 类比 |
|---|---|---|---|
| `PRODUCT.md` | 业务领域：用户是谁、解决什么问题、核心概念、业务规则 | 每次 SessionStart | 新员工入职手册 |
| `TECH.md` | 技术架构：技术栈、架构决策、不可逆约束、接口契约 | 每次 SessionStart | 架构设计文档 |
| `IMPROVEMENT.md` | 改进方向：已知技术债、优先级、禁止事项 | 涉及重构时 | 团队 retro 产出 |
| `PROJECT.md` | 项目状态：当前 sprint、进行中任务、阻塞项 | 每次 SessionStart | 站会白板 |

四份文档的关键是单一职责：

- `PRODUCT.md` 不写技术细节。
- `TECH.md` 不写业务逻辑。
- `IMPROVEMENT.md` 不写正在做的事。
- `PROJECT.md` 不写历史决策。

这样 Agent 才能在不同场景下按需获取正确知识。

## PRODUCT.md：记录业务判断，不只是事实

错题本示例：

```md
# 错题本 — 产品知识

## 用户
K12 学生家长（代孩子管理错题）

## 核心概念
- 错题
- 识别
- 知识点
- 复习计划

## 业务规则
- 一道错题必须关联至少一个知识点
- 识别 confidence < 0.7 必须标记“待确认”
- 同一知识点连续 3 次正确 -> “已掌握”
```

这里真正有价值的不是“错题本有错题、知识点、复习计划”这种 AI 很容易编出来的事实，而是团队做出的判断：

- 为什么 confidence 阈值是 `0.7`，不是 `0.8` 或 `0.5`？
- 为什么连续 `3` 次正确算掌握，不是 `5` 次？
- 这个阈值背后愿意承担什么代价？

课程给出一个重要定义：

```text
品味 = 选择 + 理由 + 判定标准
```

DDD 不是事实罗列，而是判断记录。

## TECH.md：记录不可逆决策

`TECH.md` 的核心是 ADR，尤其是不可逆决策。

错题本示例：

```md
# 错题本 — 技术知识

## 技术栈
React19 · FastAPI · DynamoDB · Bedrock · Lambda

## 不可逆决策（ADR）

[ADR-001] DynamoDB 而非 RDS
理由：单表设计适合读多写少
代价：复杂查询能力受限
不可逆：数据模型不同，迁移 = 重写

[ADR-002] Bedrock 而非自建模型
不可逆：prompt 与后处理和 Claude 耦合
```

ADR 的价值是防止 Agent “优化”掉团队已经做出的架构决策。

例如 Agent 可能建议：

```text
建议迁移到 PostgreSQL 简化查询
```

如果它不知道 DynamoDB 是一个高回退成本决策，就会很自然地提出这种破坏性建议。

课程建议：`TECH.md` 不必记录所有技术细节，只记录“一改就是重写”的重要决策，帮助 Knowledge 做减法。

## IMPROVEMENT.md 与 PROJECT.md

这两份文档寿命更短，变化更快。

### IMPROVEMENT.md

记录：

- 改进优先级。
- 已知技术债。
- 禁止事项。
- 重构方向。

示例：

```md
# 错题本 — 改进方向

## 优先级
1. 识别准确率（baseline 未建立）
2. 首次体验（拍照 -> 识别 < 5s）

## 已知 Tech Debt
- 错误处理不统一

## 禁止事项
- 不要动 auth 模块（重构中）
- 不要添加 ORM（与单表冲突）
```

### PROJECT.md

记录当前状态：

```md
# 错题本 — 项目状态

## 当前 Sprint
Sprint 3: 核心识别功能

## 进行中
- [ ] 拍照上传 API
- [ ] Bedrock 识别调用
- [x] DynamoDB schema 设计

## 阻塞
- Bedrock 配额申请中（周三到）
```

课程给出维护频率：

| 文档 | 稳定性 | 维护方式 |
|---|---|---|
| PRODUCT.md | 稳定，低频变化 | 手动 |
| TECH.md | 稳定，低频变化 | 手动 |
| IMPROVEMENT.md | 中频变化 | 人 + 自动 |
| PROJECT.md | 高频变化 | 主要自动 |

## Feed：Knowledge 不是手填表格

课程强调：

```text
Knowledge 不是手动填的表格，它需要自动化输入源。
```

Feed 来源包括：

| Feed 来源 | 信号 | 流入哪里 |
|---|---|---|
| Session 结束 | corrections、decisions、discoveries | `corrections.log`，待蒸馏 |
| 代码变更 | commit diff、PR 描述 | `PROJECT.md`，更新状态 |
| 外部系统 | CI 结果、deploy 状态、告警 | `PROJECT.md` / `IMPROVEMENT.md` |

本 PDF 聚焦最核心的 feed：

```text
SessionEnd capture
```

也就是在每次会话结束时，把这次 session 里产生的经验捕获下来。

## Capture Hook：SessionEnd 是 Knowledge 的耳朵

PDF 给出一个 `on-session-end.sh` 示例：

```bash
#!/bin/bash

claude --print "Review this session transcript.
Extract:
1. corrections (CORRECTION: ...)
2. decisions w/ rationale (DECISION: ...)
3. new facts (DISCOVERY: ...)
Output ONLY items, one per line.
If none found, output NONE." \
>> knowledge/corrections.log
```

要提取三类东西：

| 类型 | 含义 |
|---|---|
| `CORRECTION` | 你纠正 Agent 的每一处 |
| `DECISION` | 重要设计 / 架构决策及理由 |
| `DISCOVERY` | 新发现的事实，如 rate limit |

Capture Hook 有三个关键约束：

1. 只提取，不判断。
2. 追加模式，不覆盖已有 log。
3. 格式统一，便于后续蒸馏脚本解析。

这里“只提取，不判断”非常重要。因为蒸馏是后续动作，不能在捕获阶段就急着把每条 correction 变成 rule。

## corrections.log 的价值

课程反复强调：

```text
corrections.log = 蒸馏的原料库
```

它不是 rules，不应该直接被 Agent 读取。

原因：

- 一次 correction 可能是偶然。
- 三次同方向才可能说明存在 pattern。
- 五次以上、形式各异但同源，才可能值得升级为 principle。
- 过早把 correction 变成 rule，会过拟合单次事件。

`corrections.log` 生命周期：

```text
capture hook 追加
  -> 积累到阈值（5-10 条）
  -> 蒸馏，识别 pattern
  -> 升级为 rule / 发现 principle / 更新 IMPROVEMENT
  -> 已处理内容归档
```

课程的比喻是：

```text
corrections.log 是原油，蒸馏是炼油过程。
不要把原油直接灌进发动机。
```

## Feed 完整流程

Knowledge 的信号流是：

```text
Session
  -> Capture Hook
  -> corrections.log
  -> 达到阈值
  -> Distill
  -> principles / rules / IMPROVEMENT.md
```

前半段是“吸入经验，确保不丢失”。  
后半段是“处理经验，更新知识”。

课程把它称为：

```text
Knowledge 的一次呼吸
```

## Lab：初始化 Knowledge 骨架

实验要搭出：

```text
my-agentos/
├── knowledge/
│   ├── PRODUCT.md
│   ├── TECH.md
│   ├── IMPROVEMENT.md
│   └── PROJECT.md
├── hooks/
│   └── on-session-end.sh
└── corrections.log
```

必做项：

- 写 `PRODUCT.md` 骨架。
- 写 `TECH.md` 骨架。
- `TECH.md` 至少写 2 条 ADR。
- `IMPROVEMENT.md` 和 `PROJECT.md` 先留骨架。
- 配置 capture hook。
- 今天不追求完美，后面跑 Engine 时自然填充。

判断点：

- `PRODUCT.md` 的 confidence 阈值选多少？为什么？
- `TECH.md` 哪条 ADR 标为不可逆？标准是什么？

课程强调没有标准答案。你的选择和理由就是你的品味。

## 判断的多样性

同一个错题本，不同人可能对识别 confidence 阈值做不同选择：

| 选择 | 理由 | 后果 |
|---|---|---|
| 0.6 | 用户可以自己修正，宁可多识别 | 需要 gate 覆盖错误识别导致的数据污染 |
| 0.8 | 错误识别体验太差，宁可少识别 | 需要处理大量待确认堆积的 UX 问题 |
| 0.7 分级 | 0.5-0.7 标黄，<0.5 不展示 | 实现复杂度上升，需要额外 UI 状态 |

课程的结论：

```text
没有谁对谁错，但每个选择都有后果。
```

品味不是“我喜欢”，而是：

```text
选择 + 理由 + 对后果的预判 + 愿意承担代价
```

这些判断就是 principles / rules 的来源。

## DDD 的维护策略

课程提醒：

```text
文档不更新 = 有毒文档
```

维护策略：

| 文档 | 更新频率 | 谁负责 | 过期风险 |
|---|---|---|---|
| PRODUCT.md | 低，需求变更时 | 人 | 低 |
| TECH.md | 低，架构决策时 | 人 | 低 |
| IMPROVEMENT.md | 中，每 sprint | 人 + 自动 | 中 |
| PROJECT.md | 高，每天 / 每 session | 主要自动 | 高 |

具体建议：

- `PRODUCT.md` + `TECH.md`：手动维护，纳入架构决策 checklist。
- `IMPROVEMENT.md`：sprint 时人工更新优先级，hook 自动追加 debt。
- `PROJECT.md`：session 开始时从 git / task 系统自动同步。

后续 Health 模块会做新鲜度检查，例如：

```text
PROJECT.md 超过 3 天未更新 = 健康警报
```

## 对 AgentOS 的启发

### 1. Knowledge 目录必须拆分职责

推荐：

```text
agentos/knowledge/
├── PRODUCT.md
├── TECH.md
├── IMPROVEMENT.md
└── PROJECT.md
```

不要把这些混进一个大文件。

### 2. AgentOS 初始化时不能编造项目事实

初始化脚本应从已有文件读取：

- README
- AGENTS / CLAUDE
- 架构文档
- package / pom / requirements
- docs / specs

不确定就写 `TBD`，不要让 AI 编一个看似合理的项目知识库。

### 3. corrections.log 不是 rules

推荐：

```text
agentos/corrections.log
agentos/corrections/archive/
```

格式：

```text
CORRECTION: ...
DECISION: ...
DISCOVERY: ...
TEST_DEBT: ...
```

只捕获，不立即治理。

### 4. Hook 要兼容不同 Agent

Claude Code 可能有 SessionEnd hook。Codex 可以通过读取：

```text
%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl
```

提取 `response_item/message`。其他 Agent 可能没有 hook，则需要手动补：

```text
agentos/corrections.log
agentos/artifacts/<task-id>/
```

所以 AgentOS 应定义 capture 协议，而不是只绑定 Claude Code hook。

### 5. 文档新鲜度要成为 Health 检查

至少检查：

- `PROJECT.md` 是否超过 3 天未更新。
- `IMPROVEMENT.md` 是否超过一个 sprint 未更新。
- `TECH.md` 是否有新 ADR 未记录。
- `PRODUCT.md` 是否和当前需求冲突。

## 可直接复用的检查清单

### 初始化 Knowledge

- [ ] 创建 `PRODUCT.md`。
- [ ] 创建 `TECH.md`。
- [ ] 创建 `IMPROVEMENT.md`。
- [ ] 创建 `PROJECT.md`。
- [ ] `TECH.md` 至少有 2 条 ADR。
- [ ] `corrections.log` 存在。
- [ ] Capture Hook 或手动 capture 机制存在。
- [ ] 不确定信息标记为 `TBD`。

### 写 PRODUCT.md

- [ ] 用户是谁。
- [ ] 解决什么问题。
- [ ] 核心概念是什么。
- [ ] 业务规则有哪些。
- [ ] 关键阈值的选择和理由是什么。
- [ ] 这些选择的代价是什么。

### 写 TECH.md

- [ ] 技术栈。
- [ ] 架构决策。
- [ ] 不可逆约束。
- [ ] 接口契约。
- [ ] ADR 包含理由、代价、不可逆性。

### 写 IMPROVEMENT.md

- [ ] 当前技术债。
- [ ] 改进优先级。
- [ ] 禁止事项。
- [ ] 哪些模块不该动。
- [ ] 哪些风险要在 plan 阶段考虑。

### 写 PROJECT.md

- [ ] 当前 sprint。
- [ ] 正在做什么。
- [ ] 已完成什么。
- [ ] 阻塞项。
- [ ] 最近更新时间。

### Capture Hook

- [ ] 提取 `CORRECTION`。
- [ ] 提取 `DECISION`。
- [ ] 提取 `DISCOVERY`。
- [ ] 只追加，不覆盖。
- [ ] 不在 capture 阶段直接生成 rule。
- [ ] 输出格式统一。

## 我的理解

这份 PDF 最重要的地方，是把 Knowledge 从“写一堆规则给 Agent 看”升级成“可维护的长期记忆系统”。

它提醒我们：项目知识不是越多越好，关键是职责清晰、按需注入、持续更新、能够从经验中进化。`PRODUCT.md` 和 `TECH.md` 记录稳定判断，`IMPROVEMENT.md` 和 `PROJECT.md` 记录动态状态，`corrections.log` 记录原始经验，蒸馏机制再把经验变成治理。

真正的 Knowledge 不是静态文档，而是有输入、有处理、有过期检测、有生命周期的系统。
