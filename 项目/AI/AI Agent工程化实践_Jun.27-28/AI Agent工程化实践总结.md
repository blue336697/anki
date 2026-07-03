# AI Agent 工程化实践课程总结

> 来源：同目录下 14 份 PDF 课件。本文按课件内容脉络整理，而不是严格按文件名排序；其中 `01_opening_agentos.pdf` 正文是 Day 3 的 Loop Engineering，`05_knowledge_retrieve_health.pdf` 正文是 Opening/AgentOS 全景。

## 一句话总览

这套课程的核心不是“怎么把提示词写得更好”，而是把人的工程判断、项目品味、流程纪律和验证标准编译成 Agent 物理上绕不过去的系统。最终产物是一个能在项目中受控运行、持续进化的 `AgentOS`：它有长期记忆，有治理规则，有不可跳步的交付流程，有自我验证，也有无人值守时的停止条件、熔断和成本控制。

课程反复强调一个模子：

1. 人应该站在哪个判断点？
2. 你的品味是什么，也就是可判定的选择、理由和标准？
3. 如何把品味编译成 Agent 跑不掉的约束？

## 核心观点

- AI 引擎是商品，Harness 才是产品。模型、CLI、工具会变化，但围绕它们建立的记忆、流程、门禁、验证和进化机制，才是团队或个人的真实 IP。
- AgentOS 的目标不是让 Agent “自由发挥”，而是让它在你的边界内自主运行。
- 好的系统应该越用越短，而不是越用越臃肿。不断添加规则会稀释注意力；真正的进化来自蒸馏：把重复纠正上提为原则，把反复违反下沉为门禁，把长期无用的规则和门禁退休。
- Agent 的 L3 到 L4 跃迁，关键不是更强的模型，而是三件事：跨 session 记忆、无人值守流程、自愈循环。
- 没有验证的 Loop 是全自动错误放大器。人一旦离开循环，验证体系就成了唯一裁判。

## AgentOS 架构

AgentOS 由两个核心模块和一组 Harness 原语组成：

| 部分 | 作用 | 解决的问题 |
|---|---|---|
| Knowledge | Agent 的“大脑”，保存领域知识、经验、治理约束和进化结果 | Agent 每次启动都是白纸 |
| Delivery Engine | Agent 的“手脚”，定义阶段、门禁、任务路径和状态 | Agent 会跳步、乱序、提前写代码 |
| Eval | AgentOS 的自我检测 | 不只验证代码，也验证 Agent 是否按标准工作 |
| Harness | Rules、Hooks、Skills、MCP、Context、Session 等运行基座 | 提供自动注入、事件触发、工具接入、状态管理 |

一个最终的 `my-agentos/` 结构大致如下：

```text
my-agentos/
├── README.md
├── knowledge/
│   ├── PRODUCT.md
│   ├── TECH.md
│   ├── IMPROVEMENT.md
│   ├── PROJECT.md
│   └── health.sh
├── governance/
│   ├── principles.md
│   ├── rules/
│   └── gates/
├── engine/
│   ├── SKILL.md
│   ├── stages.md
│   ├── gates.md
│   ├── profiles.md
│   ├── STATE.md
│   └── loop-config.md
├── eval/
│   ├── golden-set.md
│   └── run-eval.sh
├── hooks/
├── skills/
├── spec/
├── corrections.log
└── ci/verify.sh
```

## Day 1：Knowledge 模块

### 1. DDD 四文档

课程把 `CLAUDE.md` 这种“大杂烩上下文”拆成四份职责清晰的文档，目的是对抗上下文膨胀和注意力衰减。

| 文档 | 存什么 | 更新频率 | 注入时机 |
|---|---|---|---|
| `PRODUCT.md` | 用户、业务概念、业务规则、产品判断 | 低 | 每次 SessionStart |
| `TECH.md` | 技术栈、架构决策、不可逆约束、接口契约 | 低 | 每次 SessionStart |
| `IMPROVEMENT.md` | 技术债、改进优先级、禁止事项 | 中 | 涉及重构或改进时 |
| `PROJECT.md` | 当前 sprint、进行中任务、阻塞项 | 高 | 每次 SessionStart |

重点不是罗列事实，而是记录“判断”：例如识别置信度为什么是 `0.7`，为什么选择 DynamoDB 而不是 RDS，为什么 Bedrock 是不可逆耦合。这些选择、理由和后果才是 Agent 需要继承的项目品味。

### 2. Feed：经验流入 Knowledge

Knowledge 不能只靠手动维护，它需要 Feed。最核心的 Feed 是 `SessionEnd` capture hook：在每次会话结束时提取三类信息，追加到 `corrections.log`：

- `CORRECTION`：你纠正 Agent 的地方。
- `DECISION`：重要设计决策和理由。
- `DISCOVERY`：新发现的事实，如 API 限制、识别质量问题。

`corrections.log` 不是规则文件，不能直接塞给 Agent。它是原料库，后续要经过蒸馏，识别重复偏差，再升级成 principle、rule 或 gate。

### 3. 三层治理：Principles → Rules → Gates

治理不是无限加 rules，而是三层共存、逐层兜底。

| 层级 | 数量 | 作用 | 示例 |
|---|---:|---|---|
| Principles | 3-5 条 | 覆盖一整类失败，提供方向和优先级 | 完成 = 主动破坏且失败 |
| Rules | 10-15 条以内 | 具体指导，可追溯、可过期 | 识别接口必须返回 confidence |
| Gates | 尽量少 | 代码级强制阻断 | pre-commit 扫描 secrets、测试覆盖率门禁 |

好的 Principle 必须同时满足三点：

- 抽象到能覆盖一类问题。
- 具体到可以判断是否遵守。
- 自带判定标准。

Rules 要有“出生证明”和“死亡条件”：追溯到哪个 principle、由哪些 corrections 催生、什么条件下退休。Gates 是最后防线，只在文本约束反复失败，或安全类问题必须硬阻断时使用。

### 4. 蒸馏方向

蒸馏的目标是让系统变短、覆盖变广。

- 上提：多条 rules 或 corrections 共享同一根因，上提为一条 principle。
- 下沉：某条 rule 被同样形式违反 3 次以上，下沉为可执行 gate。
- 毕业：gate 长期不触发，说明上游约束已经有效，可以降级或归档。

健康信号是：principles 稳定在 3-5 条，rules 稳定或减少，gates 最少且能毕业，corrections 频率下降，新类型错误首次就能被原则覆盖。

## Day 2：Delivery Engine

### 1. Engine 的设计哲学

Knowledge 告诉 Agent 什么是对的，但不告诉它先做什么后做什么。Delivery Engine 的任务是建立不可跳步的执行轨道。

设计 Engine 不应照搬模板，而应从“不可逆边界”出发：

- 哪些决策一旦做错，回退成本极高？
- 哪些阶段必须产生可检查 artifact？
- 哪些地方越早检查越便宜？
- 阶段是否太多，导致 gate 和人工关注成本过高？

课程中的最小阶段序列是：

```text
EVALUATE → PLAN → BUILD → VERIFY
```

| 阶段 | 目的 | 产出物 | 典型问题 |
|---|---|---|---|
| EVALUATE | 确认需求和验收标准 | `evaluate.md` | AC 模糊、没识别不可逆决策 |
| PLAN | 设计技术方案 | `plan.md` | 方案遗漏、ADR 不完整、风险低估 |
| BUILD | 按方案编码和测试 | 代码 + 测试 | 偏离方案、过度工程、跳过测试 |
| VERIFY | 主动破坏式验证 | `verify.md` | 只测 happy path、边界条件没覆盖 |

每个阶段都要有入口条件、执行内容、产出 artifact 和出口 gate。没有 artifact，gate 就没有检查对象。

### 2. Gates：阶段之间的硬隔离

课程将 gate 分为三级：

| 级别 | 含义 | 适用场景 |
|---|---|---|
| L1 | Agent 自查或脚本检查 | 格式完整性、测试、lint、文件存在 |
| L2 | AI 互查 | 方案合理性、代码质量、主观性较强的检查 |
| L3 | 人工审批 | 架构选型、不可逆决策、数据迁移 |

错题本示例中的四道门：

| Gate | 边界 | 级别 | 核心判定 |
|---|---|---|---|
| G1 | EVALUATE → PLAN | L1 | AC 存在且可判定，不可逆决策已声明 |
| G2 | PLAN → BUILD | L2 | 方案覆盖 AC，风险可控，ADR 完整，devil's advocate 找不到致命缺陷 |
| G3 | BUILD → VERIFY | L1 | 代码存在，测试和 lint 通过，无硬编码 secrets，覆盖 plan 中 AC |
| G4 | VERIFY → Done | L1 | 验证报告存在，所有 AC pass，有主动破坏尝试，无 fail 项 |

Gate 失败后必须定义回退路径：

- 小问题原地修复。
- 方案级问题回退 PLAN。
- 需求理解错误回退 EVALUATE。
- 同一问题连续 3 次修不好，说明当前阶段可能不是问题根源，要升级或回退上游。

### 3. Profiles 与 State

不是所有任务都走完整流程。Profiles 用于定义不同任务的路径：

| Profile | 路径 | 适用场景 |
|---|---|---|
| feature | EVALUATE → PLAN → BUILD → VERIFY | 新功能、重大变更 |
| bugfix | EVALUATE → BUILD → VERIFY | 已知 bug，方向较明确 |
| hotfix | BUILD → VERIFY | 紧急修复，降低部分 gate 要求 |
| refactor | PLAN → BUILD → VERIFY | 重构，需要回归验证 |

`STATE.md` 记录当前任务、profile、当前阶段、已通过 gates、开始时间、循环次数。它解决跨 session 的断点续做问题。

### 4. SDLC 实弹

课程用“错题本拍照识别”作为统一任务，完整跑一遍 Engine：

1. EVALUATE：读 `PRODUCT.md`，明确需求、AC、风险和不可逆决策点。
2. G1：检查 AC 是否可判定。
3. PLAN：读 `TECH.md`，设计 API schema、Bedrock 调用、错误处理、confidence 逻辑和 ADR。
4. G2：用 devil's advocate 审查方案。
5. BUILD：按 `plan.md` 编码并写测试，不允许在 BUILD 里偷偷改方向。
6. G3：跑测试、lint、secrets 检查、AC 覆盖检查。
7. VERIFY：主动破坏，测空图片、超大图片、非图片、模糊图、Bedrock 超时、异常格式等。
8. G4：验证报告全部 pass 才 Done。

重要心智是：第一次 VERIFY fail 不是失败，而是系统在工作。它把问题留在开发阶段，而不是放到用户现场。

## Day 3：验证、蒸馏与 Loop

### 1. Verification 与 Eval

课程区分两种验证：

| 类型 | 验证对象 | 问题 | 失败后改谁 |
|---|---|---|---|
| 业务验证 | 代码功能 | 识别功能工作吗？ | 改代码 |
| 系统验证 Eval | AgentOS 行为 | Agent 按我的标准工作吗？ | 改 governance / engine |

对于 AI 识别这类非确定输出，不能只做 exact match，而要分层验证：

- Schema 验证：JSON 格式和必填字段正确。
- 关键字段验证：如 `confidence` 存在且在 `[0,1]`。
- 相似度验证：识别文本与标注达到阈值。
- 人工抽检：覆盖边界样本。

系统验证则使用 Behavioral Contract 和 Golden Set。例如：

- IF 任务是新 feature，THEN Agent 必须先进入 EVALUATE，不得直接写代码。
- IF PLAN 产生 ADR，THEN 必须写入 `TECH.md`。
- IF G4 验证报告有 fail，THEN 不得标记 Done。

每周跑一次 `eval/run-eval.sh`，如果分数下降，说明 governance、context 或 engine 出现漂移。

### 2. 蒸馏工坊

蒸馏不是继续加规则，而是把 `corrections.log` 里的原始经验变成更短、更强的治理结构。

流程：

1. 给每条 correction 打标签，例如格式遗漏、深度不足、流程跳步、引用缺失。
2. 分组统计，找出 3 条以上的 cluster。
3. 判断根因：这些表面问题是否属于同一类偏差？
4. 执行上提、下沉或毕业。
5. 验证：总行数减少，eval coverage 不下降，退休记录保留。

典型结果是 governance 总行数减少 10%-30%，rules 退休 2-4 条，principles 变少或措辞更精确。

### 3. Loop Engineering

Loop Engineering 的核心是：不再直接 prompt Agent，而是写一个控制程序，让它调用 Agent、运行验证、回灌失败信息，并在满足条件时停止或熔断。

一个最小 loop 的本质是：

```text
while not stopped:
    call_agent(context)
    run_verification()
    if success:
        create_pr()
        stop
    else:
        feed_error_back_as_context()
    if breaker_triggered:
        save_state()
        call_human()
        stop
```

Loop 的三件灵魂工程判断：

| 要素 | 问题 | 示例 |
|---|---|---|
| 停止条件 | 什么算真的完成？ | G4 通过、所有 AC pass、eval score 达标 |
| 熔断机制 | 什么情况必须紧急停？ | 最大轮数、时间上限、token 预算、破坏性操作、API 连续失败 |
| 外部状态 | 如何避免每轮失忆？ | `STATE.md` 记录试过什么、为何失败、下一轮别重复 |

课程特别强调：停止条件必须外部可验证，不能让 Agent 自己说“差不多了”。熔断也不是可选项，否则一个写错停止条件的 loop 可以持续烧 token 和 API 费用。

Loop 的成熟度分三层：

| 级别 | 形态 | 适合场景 |
|---|---|---|
| L1 本地 loop | 本机跑，验证失败则让 Agent 修到绿 | 训练 TDD + loop 习惯 |
| L2 CI loop | 草稿 PR 触发，CI 中自动修复 | 外包琐碎 bug 修复 |
| L3 生产自愈 loop | 线上报错后自动定位、修复、提 PR | 需要监控、沙箱、可观测和 webhook |

务实建议是先从 L1 bugfix loop 开始，不要一上来追求生产自愈。

## 成本治理

无人值守运行必须显式治理成本。Loop 的成本来自两边：

- Agent 修改代码消耗模型 token。
- 验证如果调用 Bedrock 等外部服务，也会继续烧钱。

关键策略：

- 每轮优先跑确定性、低成本、mock 化的结构和契约验证。
- 不要每轮都调用真实 Bedrock。
- 控制 `max_iterations`、时间上限、token 或金额预算。
- 记录 tokens/AC，识别无效循环。
- 同一 gate 连续失败多次就停，不继续沉没成本。

`engine/loop-config.md` 应至少包含：

- 停止条件：目标达成、timeout、cost cap、最大 gate retry、eval 阈值。
- 熔断条件：无限循环、成本 spike、破坏性操作、API 连续异常。
- 成本治理：单任务预算、单 session 预算、效率告警。
- 升级策略：何时通知人、何时要求 L3 审批。

## 30 / 60 / 90 天路线图

### 30 天：运行 + 积累

- 接入真实项目。
- 用 Engine 跑 2-3 个 feature。
- 积累 50+ corrections。
- 每周一次 eval。
- 做 2 次蒸馏。

成功指标：principles 不超过 5 条，rules 开始有退休。

### 60 天：渐进 + Loop

- 将部分 gates 从 L3 降到 L2，再降到 L1。
- 跑第一次 bugfix loop。
- 自动化维护 `PROJECT.md` 或部分 Knowledge feed。
- 观察 eval score 是否上升。

成功指标：至少一类任务可以 loop 运行。

### 90 天：进化 + 迁移

- 接入第二个项目。
- 抽取跨项目可复用 principles。
- 重写项目特定 rules。
- 继续蒸馏，让文件更短。

成功指标：新项目接入时间小于 1 天。

## 最值得带走的实践清单

1. 不要把所有内容塞进一个 `CLAUDE.md`，拆成 DDD 四文档并按需注入。
2. 每次纠正 Agent 都进入 `corrections.log`，但不要直接变成 rule。
3. Principles 保持 3-5 条，必须可判定，并显式排序。
4. Rule 必须可追溯、有证据、有过期条件。
5. Gate 是最后防线，应该少且可毕业。
6. Engine 阶段从不可逆边界推导，不从模板照抄。
7. 每个阶段必须有 artifact，否则 gate 无法检查。
8. PLAN 阶段的 G2 适合用独立视角审查，避免自我确认偏差。
9. VERIFY 要主动破坏，而不是只确认 happy path 能跑。
10. Eval 验证的是 AgentOS 行为，不只是业务代码。
11. Loop 上线前先问：验证体系敢不敢当唯一裁判？
12. Loop 必须有停止条件、熔断、状态记忆和成本预算。
13. 信任是赢得的：corrections 下降才逐步降低 gate 级别。
14. 系统健康的方向是更短、更准、更可解释，而不是规则越来越多。

## 个人理解

这套课真正要训练的不是某个工具的配置能力，而是一种工程化的控制感：你不再把 Agent 当成“聪明的外包”，而是把它放进一个能记忆、能检查、能回退、能反思、能停止的系统里。人的价值也没有消失，而是从“盯着每一行代码”上移到更高价值的位置：定义边界、排序原则、审批不可逆决策、判断哪些经验值得蒸馏。

最终目标不是得到一个完美 Agent，而是得到一个会变好的系统。它每跑一次任务，都能留下经验；每做一次蒸馏，都能变短一点；每一次 gate 失败，都能告诉你偏差发生在哪个阶段。工具会换，模型会换，但这套判断被编译进系统以后，会继续复利。
