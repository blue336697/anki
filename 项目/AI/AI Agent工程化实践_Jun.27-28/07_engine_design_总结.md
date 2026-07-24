# 07_engine_design.pdf 总结

> 文件名：`07_engine_design.pdf`  
> 正文标题：Day 2 · 上午第一节 · Delivery Engine 设计(1)  
> 页数：8 页

## 一句话总结

这份 PDF 开始进入 AgentOS 的 Delivery Engine 模块：Knowledge 告诉 Agent 什么是对的，但不告诉它应该按什么顺序做；Engine 的任务就是从项目的不可逆边界出发，设计一条有阶段、有产物、有检查点、不可跳步的执行轨道。

## 核心问题：Knowledge 是大脑，但大脑不能自己走路

前面几节已经搭建了 Knowledge：

- 项目知识。
- Principles。
- Rules。
- Gates。
- Capture。
- Retrieve。
- Health。

但只有 Knowledge 还不够。因为 Knowledge 解决的是：

> 什么是对的？

它没有解决：

> 先做什么，后做什么，什么时候停下来检查？

没有 Engine 时，常见情况是：

```text
你说：开发这个功能
Agent：直接开始写代码
结果：没分析需求、没设计、没 review、没测试
最后：交出一大坨方向错误的代码
```

有 Engine 后，流程变成：

```text
定义先后顺序
  -> 每步之间有检查点
  -> 阶段不可跳过
  -> 错误在源头被拦住
```

所以 Delivery Engine 的价值不是让 Agent 更会写代码，而是防止它在错误方向上高效前进。

## Engine 的设计哲学：从不可逆边界出发

课程强调，不要直接照搬别人的流程模板。

例如：

- SwarmAI 的 9 阶段。
- gstack 的 SDLC。
- 各种 best practice 流程。
- 复杂的企业研发模板。

这些都是“别人的判断”。你的 Engine 应该从你项目里的不可逆边界推导出来。

设计原则有四条。

| 原则 | 含义 |
|---|---|
| 从不可逆边界出发 | 哪些决策一旦做了很难回退，就在哪里放门 |
| 最小阶段数 | 阶段越少越好，因为每个阶段都有 gate 和注意力成本 |
| 每阶段明确产出物 | 不能只是“我思考了”，必须有可检查 artifact |
| 越早检查越便宜 | 方向性错误应该在第一步就拦住，而不是代码写完才发现 |

这和前面 Governance 的思路一致：不是约束越多越好，而是关键边界必须有约束。

## 不可逆边界是什么

课件用错题本项目举例：

| 决策 | 可逆性 | 为什么 |
|---|---|---|
| 架构选型 | 不可逆 | 例如选 DynamoDB 后，多个模块依赖它，回退成本很高 |
| 接口设计 | 半不可逆 | 发布后调用方依赖，修改需要协调 |
| 实现细节 | 可逆 | 函数内部可以重写，不影响外部契约 |

定义很直接：

> 不可逆 = 回退成本远高于前进成本。

回退成本越高的边界，越需要阶段和 Gate。

## 最小 Engine 阶段序列

课件给出一个最小阶段序列：

```text
EVALUATE -> PLAN -> BUILD -> VERIFY
```

每个阶段都有对应产出和 Gate。

| 阶段 | 目的 | 产出物 | 出口 Gate |
|---|---|---|---|
| EVALUATE | 理解与评估需求 | 需求确认 | Gate 0：需求清晰？ |
| PLAN | 设计与规划 | 技术方案 | Gate 1：方案可行？ |
| BUILD | 编码实现 | 代码 + 测试 | Gate 2：代码合格？ |
| VERIFY | 验证与交付 | 验证报告 | Gate 3：验证通过？ |

这不是唯一正确答案，而是最小可用版本。

关键是每个阶段对应一个问题：

- EVALUATE：我是不是理解对了？
- PLAN：我是不是准备以正确方式做？
- BUILD：我是不是按方案实现了？
- VERIFY：我是不是证明它真的能工作？

## 阶段的内部结构

每个 Stage 不能只是一句“做点什么”。它应该有固定结构：

```markdown
## Stage: EVALUATE

### 入口条件
- 有明确的任务描述
- Knowledge 已注入（SessionStart）

### 执行内容
1. 阅读任务 + 相关 DDD 文档
2. 澄清模糊点
3. 定义验收标准（可判定）
4. 识别不可逆决策点

### 产出物
artifacts/evaluate-{id}.md

### 出口 Gate
- 验收标准数 >= 3
- 每条验收标准必须可判定
```

也就是：

| 字段 | 作用 |
|---|---|
| 入口条件 | 什么时候可以进入这个阶段 |
| 执行内容 | 这个阶段必须做哪些动作 |
| 产出物 Artifact | Gate 检查的对象 |
| 出口 Gate | 满足什么条件才能进入下一阶段 |

其中 artifact 很重要。Gate 不能检查“Agent 有没有认真思考”，只能检查一个可见产物。

## stages.md 是 Engine 的地图

课件建议创建：

```text
engine/stages.md
```

它是 Delivery Engine 的地图，描述阶段顺序、阶段目的、产出物和 Gate 引用。

示例结构：

```markdown
# Delivery Engine — Stages

## 阶段序列
EVALUATE -> PLAN -> BUILD -> VERIFY

## Stage: EVALUATE
**目的**: 确保理解正确，在错误方向上跑之前停下来
**入口条件**: 有任务描述
**产出物**: artifacts/evaluate-{id}.md
**出口 Gate**: gates.md G1
**预估**: 5-10 min

## Stage: PLAN
**目的**: 确保方案合理，在不可逆决策之前停下来
**产出物**: artifacts/plan-{id}.md
**出口 Gate**: gates.md G2
**预估**: 10-20 min

## Stage: BUILD
**目的**: 实现方案，方向已定
**出口 Gate**: G3

## Stage: VERIFY
**目的**: 主动破坏且失败
**出口 Gate**: G4
```

这里最关键的是：Stage 文件不只是流程说明，而是 Agent 执行时要遵守的轨道定义。

## Lab：画你的 Engine

本节 Lab 要求：

1. 创建 `engine/stages.md`。
2. 设计阶段序列，至少 4 个阶段，可多可少。
3. 每个阶段写清楚：
   - 目的。
   - 入口条件。
   - 产出物。
   - 出口 Gate 引用。
4. 思考自己的阶段与示例是否一样，以及为什么。

判断提示非常实用：

| 情况 | 处理 |
|---|---|
| 找不到不可逆边界 | 合并阶段 |
| 阶段存在的理由只是“看起来完整” | 删除或合并 |
| 阶段内部还有不可逆边界 | 拆分阶段 |
| 某个阶段需要独立判断门 | 保留阶段 |

课程提醒：阶段是有成本的。

每多一个阶段，就多一次：

- 中断。
- artifact 维护。
- gate 设计。
- 人类注意力消耗。

所以 Engine 不应该为了“规范”而复杂。

## 阶段设计的多样性

课件举了三种不同设计。

### 方案 A：5 阶段，加独立 REVIEW

```text
EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY
```

理由：

> BUILD 完直接 VERIFY 太跳了，需要先让 AI 自审。

这个设计是合理的，因为 Review 确实是一个边界：发现问题后应该回到 BUILD，而不是直接进入最终验证。

### 方案 B：3 阶段，合并 EVALUATE + PLAN

```text
EVALUATE_PLAN -> BUILD -> VERIFY
```

理由：

> 错题本需求简单，理解和规划可以一起做。

课程认为这有一定风险：如果需求变复杂，理解和设计合在一起可能会漏掉问题。

但对小需求、小修复来说，这种轻流程是合理方向。

### 方案 C：6 阶段，加 DEPLOY + MONITOR

```text
EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY -> DEPLOY -> MONITOR
```

理由：

> 对有 CI/CD 的团队来说，部署也是不可逆边界。

这超出课程范围，但概念上完全合理。

这说明 Engine 是活的。今天定一版，下午跑一圈，再根据真实 friction 调整。

## 对 AgentOS 机制设计的启发

这份 PDF 对我们正在设计的 AgentOS 很关键，因为它直接回答了“什么时候要 plan，什么时候可以直接改”的问题。

### 1. 大小需求应该走不同 Engine Profile

不是所有任务都需要完整 4 阶段。

合理的 AgentOS 应该有 profile：

| Profile | 适用场景 | 阶段 |
|---|---|---|
| `tiny-fix` | 拼写、小样式、小 bug | EVALUATE + BUILD + VERIFY |
| `standard-change` | 普通功能或修复 | EVALUATE -> PLAN -> BUILD -> VERIFY |
| `reviewed-change` | 影响较大、多人协作 | EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY |
| `release-change` | 部署/发布相关 | EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY -> DEPLOY -> MONITOR |

这样就能避免“小需求力大砖飞”和“大需求必须治理”之间的冲突。

小需求可以轻，但也应该有最小验收和回写。

### 2. Plan 的存在理由是不可逆边界，不是仪式感

我们前面讨论 superpowers plan、Claude Plan 模式、Codex plan 记录时，一个核心问题是 plan 文档容易混乱。

这份课件给了判断标准：

> 如果这个任务存在不可逆或半不可逆决策，就需要 PLAN artifact；如果没有，可以走轻流程。

所以 AgentOS 可以规定：

- 有接口变化：必须 PLAN。
- 有数据库/migration：必须 PLAN。
- 有跨模块影响：必须 PLAN。
- 有外部依赖或支付链路：必须 PLAN。
- 纯内部实现、小 bug、小文案：可以轻流程。

这样 Plan 不再是“喜欢规范的人才写”，而是由不可逆边界触发。

### 3. 每个阶段必须产出可检查 artifact

Agent 不能只说：

```text
我已经分析过了。
我认为方案可行。
我已经验证了。
```

AgentOS 要求每个阶段留下 artifact，例如：

```text
agentos/artifacts/{task-id}/evaluate.md
agentos/artifacts/{task-id}/plan.md
agentos/artifacts/{task-id}/review.md
agentos/artifacts/{task-id}/verify.md
```

Gate 检查这些 artifact 是否存在、是否满足结构、是否包含可判定内容。

### 4. Engine 解决“跳步”，Knowledge 解决“判断”

两者分工要清楚：

| 模块 | 解决什么 |
|---|---|
| Knowledge | 项目是什么、什么是对、有哪些原则 |
| Governance | 哪些原则、规则、门禁必须遵守 |
| Engine | 先做什么、后做什么、什么时候不能跳 |
| Gate | 是否允许从一个阶段进入下一个阶段 |

如果只有 Knowledge，Agent 可能知道原则但仍直接写代码。

如果只有 Engine，Agent 可能按阶段走，但每步的判断标准仍然空泛。

所以 Delivery Engine 必须引用 Knowledge 和 Governance，而不是独立存在。

### 5. 对 payment-agent 的启发

如果把这个 Engine 用到 `payment-agent-ai`，阶段设计应该比错题本更谨慎，因为支付系统有更多不可逆边界。

建议的标准流程可以是：

```text
EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY
```

对于涉及发布、资金链路、幂等性、账务一致性的任务，还应扩展为：

```text
EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY -> RELEASE_CHECK
```

触发必须 PLAN 的边界包括：

- 交易状态机变化。
- 支付渠道接口变化。
- 金额计算或币种处理。
- 幂等键、重试、补偿逻辑变化。
- 数据库 schema / migration。
- 对账、清结算、退款相关逻辑。
- 风控决策或黑白名单逻辑。
- 外部 API 合约变化。

这些都不是“写完再测”能兜住的，必须在早期阶段停下来。

## 和前几份 PDF 的关系

前面的 Knowledge 模块解决了：

```text
Agent 知道什么？
Agent 应该遵守什么？
Agent 犯错后怎么记住？
```

这份开始解决：

```text
Agent 应该按什么顺序做？
哪些地方必须停下来检查？
哪些 artifact 证明阶段完成？
```

因此，它是从“Agent 有大脑”走向“Agent 有执行轨道”的第一步。

## 最终结论

这份 PDF 的核心结论是：

> Delivery Engine 不是照搬一套研发流程，而是从项目的不可逆边界中提取最小阶段序列，并要求每个阶段都有入口条件、产出物和出口 Gate。

一个好的 Engine 应该满足：

- 阶段足够少。
- 边界足够关键。
- 每步都有可检查 artifact。
- 越早发现方向错误越好。
- 小需求可以轻流程，大需求必须过边界。

如果 Knowledge 是 AgentOS 的大脑，那么 Delivery Engine 就是 AgentOS 的骨架和步态。它让 Agent 不只是“知道什么是对的”，还必须“按正确顺序做事”。
