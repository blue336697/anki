# 06_knowledge_lab_integration.pdf 总结

> 文件名：`06_knowledge_lab_integration.pdf`  
> 正文标题：Day 1 · 下午 · Knowledge Lab 整合  
> 页数：8 页

## 一句话总结

这份 PDF 是 Day 1 Knowledge 模块的端到端验收实验：前面已经分别搭好了 DDD、Governance、Capture、Retrieve 和 Health，现在要用一次真实 session 验证这些零件是否能连成闭环，让 Agent 在启动时读到知识、工作时受到原则影响、结束时把纠正写回 `corrections.log`。

## 核心问题：文件建好了，系统真的在工作吗

前面几节已经创建了一堆 AgentOS 组件：

- DDD 文档。
- Governance 三层治理。
- Capture Hook。
- Retrieve 注入机制。
- Health Check。
- `corrections.log`。

但课程强调，文件存在不等于系统可用。

这份 Lab 要验证的是：

> Knowledge 模块是否真的能从 SessionStart 到 SessionEnd 跑完一圈？

完整闭环是：

```text
启动 session
  -> 验证注入成功
  -> 下发任务
  -> 观察 principles 是否影响 Agent
  -> Agent 犯错
  -> 人类纠正
  -> 结束 session
  -> Capture 提取 correction / decision / discovery
  -> 检查 corrections.log
```

如果这 5 个关键点都通过，说明 Knowledge 模块已经在工作。

需要注意的是：此时还没有 Delivery Engine。也就是说，Agent 仍然可能直接写代码、跳流程，这在 Day 1 是预期行为。Day 2 才会用 Engine 解决不可跳步的问题。

## 实验任务：实现 recognize 函数

课程设计了一个统一实验任务：

> 为错题本写一个 `recognize` 函数：接收一张图片，调用 Bedrock Claude 识别题目内容，返回结构化 JSON。

这个任务被选中，是因为它很适合触发 Knowledge 模块的多个部分。

| 设计原因 | 说明 |
|---|---|
| 足够复杂 | Agent 会做出设计决策，而不是只改一行 |
| 关联 principles | 数据质量、完成度都会被触发 |
| 容易出错 | 很可能漏掉 confidence、异常处理、schema 校验、测试 |
| 适合产生 correction | 人类能自然纠正 Agent 的错误 |
| 可用于后续蒸馏 | 错误类型会形成 pattern |

这个任务不是为了完美实现识别功能，而是为了制造一次可观测的 Knowledge 循环。

## 实验流程

完整流程是：

| 步骤 | 操作 | 验证什么 |
|---:|---|---|
| 1 | 开新 session | SessionStart 是否执行 |
| 2 | 先问 Agent 知道哪些 principles | Retrieve 注入是否成功 |
| 3 | 下发 recognize 函数任务 | Agent 是否拿到项目上下文 |
| 4 | 观察 Agent 行为 | Principles 是否影响设计和实现 |
| 5 | 等待 Agent 犯错并纠正 | 是否能产生 corrections |
| 6 | 结束 session | SessionEnd hook 是否触发 |
| 7 | 检查 `corrections.log` | Capture 是否落盘 |

这是一条非常清晰的端到端测试链路。它验证的不是代码功能，而是 AgentOS 的 Knowledge 子系统能不能转起来。

## Step 1：验证 SessionStart 注入

实验开始后，先不要直接派任务，而是问 Agent：

```text
在开始工作之前，请告诉我你知道的关于这个项目的 principles 是什么？
```

预期结果：

- Agent 能复述 3-5 条 principles。
- 措辞可以不同，但核心必须正确。
- Agent 知道项目基本信息，例如错题本、Bedrock、DynamoDB。
- Health status 没有红色警报。

例如 Agent 应该能说出：

- 完成 = 主动破坏且失败，而不是“没发现问题”。
- 数据质量是底线，`confidence` 必填。
- 项目是错题本，涉及 Bedrock 和 DynamoDB。

如果失败，可以按症状排查：

| 症状 | 排查方向 |
|---|---|
| Agent 完全不知道 principles | 检查 `on-session-start.sh` 是否有执行权限 |
| 知道部分但不完整 | 检查注入顺序，可能后面的内容被截断 |
| Health 报红 | 检查 Knowledge / Governance 文件是否齐全 |

这个步骤的意义是：不要等 Agent 写完代码才发现上下文根本没有注入。

## Step 2-3：下发任务、观察行为、纠正错误

下发 recognize 函数任务后，要观察 Agent 是否受 principles 影响。

好的信号包括：

- Agent 在设计阶段主动提到 principles。
- Agent 主动添加 `confidence` 字段。
- Agent 主动考虑数据质量。
- Agent 完成后主动做验证。
- Agent 主动写测试或说明测试策略。

课程也提醒，不要过早干预。这个实验需要让错误自然发生，因为 correction 本身就是 Knowledge 的原料。

常见错误包括：

| 错误类型 | 示例 |
|---|---|
| 异常处理不足 | 不处理 Bedrock API 异常 |
| 数据质量不足 | 不验证返回 JSON schema |
| 测试不足 | 不写测试，或只跑 happy path |
| 配置不清晰 | 用 magic number 而不是配置 |
| 并发错误 | 错误处理异步/并发识别 |

人类在这里的工作不是替 Agent 写代码，而是：

1. 观察 Agent 的实际行为。
2. 记录它犯了什么错。
3. 用自然语言纠正。
4. 让这些纠正成为后续 `corrections.log` 的来源。

这也是课程前面讲的“人站在哪”：在 Day 1 的 Knowledge Lab 中，人站在观察和纠正的位置。

## Step 4-5：结束 Session，验证 Capture

任务完成后，操作流程是：

1. 告诉 Agent：“任务完成，结束 session”。
2. 退出 Claude Code session。
3. 等待 SessionEnd hook 执行。
4. 检查 `corrections.log`。

预期 `corrections.log` 至少有几条结构化内容，例如：

```text
CORRECTION: 没有处理 Bedrock API 异常
CORRECTION: 返回 JSON 没有验证 schema 完整性
DECISION: try-except 包裹整个识别流程，异常时返回标准错误
DISCOVERY: Bedrock Claude 对数学公式识别率低于文字
```

成功标志是：

> `corrections.log` 有至少 2 条提取结果。

如果 log 为空，排查方向包括：

| 问题 | 排查方向 |
|---|---|
| SessionEnd 没触发 | 检查 hook 是否注册 |
| 脚本没执行 | 检查执行权限 |
| 提取失败 | 检查 Claude CLI 是否可用 |
| 输出为空 | 检查对话里是否真的有 correction / decision / discovery |

这一步验证的是 Knowledge 闭环的最后一环：经验是否能从 session 回流到长期记忆。

## Principles 的效果如何判断

课程没有把 Principles 神化。它明确说：

> Principles 提供方向，不提供保证。

因此，观察结果要分层理解。

| 观察 | 含义 |
|---|---|
| Agent 主动提到 principles | 好信号，说明 principle 被读到并影响推理 |
| 有 principles 仍犯相关错误 | 正常，原则不是硬约束 |
| Agent 行为明显受到约束 | 很好，说明 principle 可操作化成功 |
| Principles 100% 失效 | 说明写得不够可判定，需要重写 |

课程还建议做一个对比实验：

```text
不注入 principles，再跑同样任务
```

通常会看到：

- 有 principles 时，Agent 更容易主动考虑边界。
- 有 principles 时，Agent 更可能写测试。
- 有 principles 时，Agent 更可能主动提到数据质量。
- 但仍不可能 100% 正确。

所以三层治理的作用是组合覆盖：

| 层级 | 作用 |
|---|---|
| Principles | 约 80% 情况下提供方向 |
| Rules | 约 15% 情况下做具体提醒 |
| Gates | 最后 5% 用门禁强制阻断 |

这也解释了为什么只有 Principles 不够，只有 Gates 也不对。好的 AgentOS 需要三层共同工作。

## 常见 Corrections 的初步模式

课件提到，收集全班 corrections 后，通常会自然分组。

常见类别包括：

| 类别 | correction 示例 |
|---|---|
| 完成度类 | 没写测试、测试不充分、太早说完成、没有自验证 |
| 防御性编程类 | 缺少错误处理、缺少输入验证 |
| 可读性类 | 命名不清晰、magic number |

然后要反问：

- 我的 principles 覆盖了哪些 corrections？
- 有没有完全没被覆盖的新类型？
- 是需要新 principle，还是要调整现有 principle？
- 是否只是 rule 层面的具体问题？
- 是否有问题严重到需要 gate？

但课程也提醒：Day 1 不急着立刻蒸馏。因为此时样本还少。

更合理的做法是：

```text
Day 1 产生真实 corrections
Day 2 跑 SDLC 继续积累
Day 3 再做真正蒸馏
```

这能避免把一次偶发错误过早固化成永久规则。

## Day 1 完成标准

这份 PDF 最后给出 Day 1 的成果盘点：

- 理解 AgentOS 全景。
- 理解两个模块加 Harness 基座。
- 理解 Harness 六大能力。
- 建好 Knowledge 骨架。
- 建好 DDD 四文档。
- 建好 Governance 三层治理。
- 建好 Capture。
- 建好 Retrieve。
- 建好 Health Check。
- 完成 Knowledge 端到端验证。
- `corrections.log` 有真实内容。

也就是说，Day 1 的目标不是“让 Agent 完美开发”，而是：

> 让 AgentOS 的大脑能够启动、注入、观察、记忆。

Delivery Engine 是 Day 2 的任务。

## 对 AgentOS 初始化机制的启发

这份 Lab 对我们设计项目组 AgentOS 初始化流程很有价值，因为它强调了“初始化后必须能自验”。

### 1. 初始化脚本不能只创建目录

如果初始化完只是生成：

- `knowledge/`
- `governance/`
- `hooks/`
- `corrections.log`

但没有验证 session 是否真的读到了这些内容，那只是文件脚手架，不是工作系统。

初始化完成后应该提供一个 smoke test：

```text
1. 开一个新 Agent session
2. 问它知道哪些 principles
3. 检查它是否能复述项目、技术栈、治理原则
4. 下发一个小任务
5. 人为纠正一次
6. 结束 session
7. 检查 corrections.log 是否有内容
```

这就是 Knowledge 模块的验收标准。

### 2. Retrieve / Inject 必须有可观测输出

AgentOS 不能只是默默注入上下文。它应该让用户能验证：

- 本次注入了哪些文件。
- 注入顺序是什么。
- 哪些文件因为过长被截断。
- Health 是否通过。
- Agent 是否能复述核心 principles。

否则用户不知道 Agent 是没读、读少了、还是读了但没执行。

### 3. corrections.log 是真实进化的起点

一套 AgentOS 是否开始运转，不看 rules 写得多漂亮，而看是否有真实 corrections 回流。

初始化后的第一圈至少要产生：

- 1-2 条 correction。
- 1 条 decision。
- 可能还有 1 条 discovery。

这些内容后续会进入 Governance 和 Distillation。

### 4. 小需求可以轻流程，但不能没有回写

Day 1 还没有 Engine，Agent 会直接写代码，这是预期。但即使没有完整流程，也应该保留：

- SessionStart 注入。
- 人类纠正。
- SessionEnd capture。
- `corrections.log` 回写。

这对我们前面讨论的小需求很重要：小需求可以不走 superpowers 大 plan，但不能完全没有记忆和记录。

### 5. Principles 失败不一定说明系统失败

如果 Agent 注入了 Principles 但仍犯错，这不代表 AgentOS 没用。

要看：

- 是否比未注入时更好。
- 是否有部分行为受到影响。
- 错误是否能被 capture。
- 后续是否能蒸馏成 rule 或 gate。

AgentOS 的目标不是一次性防住所有错误，而是让错误能被记录、聚类、压缩、治理。

## 对 payment-agent 这类真实项目的落地映射

如果把这份 Lab 套到真实项目，例如 `payment-agent-ai`，可以把实验任务换成一个项目内真实但可控的小功能。

例如：

```text
为某个支付场景实现一个风险校验函数：
输入支付请求，输出结构化风险结果，包括 decision、reason、confidence、traceId。
```

然后观察：

- Agent 是否知道支付项目的 Principles。
- Agent 是否主动考虑金额精度、幂等性、审计、错误码。
- Agent 是否处理外部 API 异常。
- Agent 是否写测试。
- Agent 是否遗漏日志 / trace / metrics。
- 人类纠正是否进入 `corrections.log`。

对于支付类项目，常见 Principles 可能包括：

- 金额与状态一致性优先于交付速度。
- 所有外部副作用必须可追踪、可幂等。
- 不确定时拒绝，不默认放行。
- 完成等于通过失败路径验证，而不是 happy path 成功。

Lab 的关键不是任务本身，而是验证 Agent 是否真的被这些原则影响。

## 和前几份 PDF 的关系

这份 PDF 是前面 Knowledge 内容的整合验收。

| PDF | 主题 | 本 PDF 如何使用它 |
|---|---|---|
| `03_knowledge_ddd_feed.pdf` | DDD + Feed | 使用项目知识和 capture 回写 |
| `04_knowledge_governance.pdf` | Principles / Rules / Gates | 验证 principles 是否影响 Agent |
| `05_knowledge_retrieve_health.pdf` | 实际是 Opening 全景 | 落实 AgentOS 第一阶段的闭环 |
| `06_knowledge_lab_integration.pdf` | Knowledge Lab 整合 | 端到端证明 Knowledge 模块可运行 |

如果说前几份是“造零件”，这份就是“第一次通电”。

## 最终结论

这份 PDF 的核心结论是：

> Knowledge 模块是否成功，不看目录是否齐全，而看一次真实 session 是否能完成“注入 -> 影响行为 -> 产生纠正 -> 捕获回写”的闭环。

对 AgentOS 初始化来说，这意味着脚本最后必须给出一个可执行的验收实验，而不只是生成文件。

成熟的初始化流程应该至少回答：

- Agent 启动时是否读到了 Principles？
- Agent 是否知道项目基本事实？
- Health 是否正常？
- 工作中是否能看到 Principles 的影响？
- 人类纠正是否被提取？
- `corrections.log` 是否有真实内容？

只有这些都成立，Knowledge 才不是静态文档，而是真正开始成为 AgentOS 的大脑。
