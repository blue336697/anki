# 05_knowledge_retrieve_health.pdf 总结

> 文件名：`05_knowledge_retrieve_health.pdf`  
> 正文标题：AgentOS 工程实践（进阶）· 01 · Opening · AgentOS 全景  
> 页数：15 页  
> 备注：该 PDF 的文件名与正文内容不一致。正文并不是 Retrieve + Health，而是课程 Opening / AgentOS 全景。

## 一句话总结

这份 PDF 是整套 AgentOS 课程的总开场：它提出 AgentOS 的核心命题不是“配置一套 AI 编程工具”，而是把人的判断、品味和约束编译成一套能让 AI Agent 受控运行、持续进化的项目操作系统。

## 开场问题：AI 代码越来越多，但掌控感没有同步增长

课程从一个非常现实的问题切入：

- 很多人已经在用 AI 写大量代码。
- 很多人用过 gstack、superpowers、Cursor Rules、Claude Code 等工具。
- 也有很多人被 AI 写出的代码坑过。

工具越来越多，模型越来越强，代码生成速度越来越快，但团队的掌控感并没有对应提升。

这说明问题已经不只是“怎么让 AI 写代码”，而是：

> 当 AI 能快速执行时，人如何保持判断权、约束权和演化权？

这也是 AgentOS 要解决的问题。

## 执行已经商品化

课件指出，现在让 AI 生成一套 Harness 清单已经非常容易。

例如，AI 可以在几十秒内给出：

- `CLAUDE.md` 项目约定。
- 分类 rules。
- hooks。
- skills。
- MCP server 接入清单。
- 子代理与并行编排建议。
- 以及为什么这么配置的解释。

这些东西已经变得便宜、通用、人人可得。

所以课程强调：

> 你的 IP 不在工具配置本身，而在你如何判断、如何取舍、如何把这些判断变成 Agent 绕不过去的约束。

换句话说，`rules/`、`hooks/`、`skills/`、`MCP` 是执行材料，不是核心壁垒。真正有差异的是团队自己的架构红线、验证标准、成本底线、质量品味和治理方式。

## 中心命题：三件套模子

课程提出一个贯穿三天的核心框架：

```text
人站在哪 -> 品味是什么 -> 编译成什么
```

这套框架会被反复用于架构、设计、编码、验证、运维等研发阶段。

### 1. 人站在哪

要先识别这个阶段中：

- 判断密度最高的位置在哪里。
- 一旦判断错，Agent 会高效放大错误的位置在哪里。
- 哪些选择不能完全交给模型自动决定。

例如：

- 架构阶段，人应该站在边界、不可逆决策和复杂度预算处。
- 编码阶段，人应该站在约束、验证和阶段切换处。
- 测试阶段，人应该站在风险覆盖和验收标准处。

### 2. 品味是什么

“品味”不是一句模糊口号，而是：

```text
可判定的选择 + 理由 + 判定标准
```

例如：

| 模糊表达 | 可判定表达 |
|---|---|
| 代码要清晰 | 单函数圈复杂度不超过 10，超过必须解释原因 |
| 要认真测试 | 完成 = 主动尝试破坏它且失败 |
| 性能要好 | 首屏渲染小于 200ms，否则视为 P1 bug |

课程在这里把“品味”工程化了：只有能被判定、能被执行、能被复盘的品味，才有可能进入 AgentOS。

### 3. 编译成什么

最后一步是把人的判断编译成 Agent 绕不过去的机制。

这不是写文档提醒 Agent，而是把判断变成：

- Knowledge。
- Principles。
- Rules。
- Gates。
- Hooks。
- Engine stage。
- Eval。
- CI / pre-commit。
- SessionStart 注入。
- SessionEnd 捕获。

核心是让 Agent 物理上不能跳过关键判断点。

## AgentOS 的定义

课件给出的定义是：

> AgentOS = 让 AI Agent 在你的项目中受控运行、持续进化的操作系统。

它有两个关键词。

### 受控运行

Agent 必须按你定义的流程走：

- 该停的地方停。
- 该检查的地方检查。
- 该升级判断的地方升级判断。
- 不能自己觉得“差不多了”就跳步。

### 持续进化

系统应该越用越精，不是越用越臃肿：

- 文件越来越短。
- 原则覆盖越来越广。
- 重复错误越来越少。
- Gate 触发越来越少。
- 新类型错误也能首次处理对。

这和普通项目文档最大的区别是：AgentOS 不是一次性配置，而是通过 corrections、distillation、governance 不断进化。

## 三天后要带走的 deliverable

课件里给出的 AgentOS 交付物大致是：

```text
my-agentos/
├── knowledge/
│   └── 领域知识 + 经验
├── governance/
│   └── 三层治理：原则 / 规则 / 门禁
├── engine/
│   └── Delivery Engine
├── eval/
│   └── 行为契约自测
├── hooks/
├── skills/
└── corrections.log
```

这说明 AgentOS 不是一个单文件 prompt，而是一套项目级运行结构。

其中：

- `knowledge/` 是 Agent 的大脑。
- `governance/` 是行为约束。
- `engine/` 是不可跳步的执行轨道。
- `eval/` 是自我校验。
- `hooks/` 和 `skills/` 是运行原语。
- `corrections.log` 是进化证据。

## AgentOS 架构：两个模块 + 一层原语

课件把 AgentOS 分成两个核心模块和一层 Harness 基座。

```text
AgentOS
├── Module: Knowledge
│   ├── DDD
│   ├── Memory
│   ├── Governance
│   └── Distillation
├── Module: Delivery Engine
│   ├── Stages
│   ├── Gates
│   ├── Profiles
│   └── State
├── Eval
└── Harness
    ├── Rules
    ├── Hooks
    ├── Skills
    ├── MCP
    ├── Context
    └── Session
```

### Knowledge = 大脑

Knowledge 负责：

- 知道项目是什么。
- 记住跨 session 经验。
- 约束 Agent 行为。
- 通过蒸馏持续进化。

它包含：

| 组件 | 作用 | 类比 |
|---|---|---|
| DDD | 项目的结构化领域知识 | Agent 可读的团队 wiki |
| Memory | 跨 session 经验积累 | 人的长期记忆 |
| Governance | 三层行为治理 | 道德 / 法律 / 执法 |
| Distillation | 做减法的进化机制 | 免疫系统 |

### Delivery Engine = 手脚

Delivery Engine 负责：

- Agent 按什么流程做。
- 哪些阶段不能跳。
- 哪些任务走轻流程。
- 中断后怎么恢复状态。

它包含：

| 组件 | 一句话 | 解决的问题 |
|---|---|---|
| Stages | 有序执行阶段 | Agent 会乱序做事 |
| Gates | 阶段间硬隔离 | Agent 会跳步 |
| Profiles | 任务类型到路径 | 小 bug 不需要完整重流程 |
| State | 执行位置记录 | 中断后 Agent 不知道自己在哪 |

典型阶段是：

```text
EVALUATE -> THINK -> PLAN -> BUILD -> REVIEW -> VERIFY
```

其中 Gate 负责阶段边界，防止 Agent 直接从“想到方案”跳到“我已经完成了”。

### Eval = 自我意识

课件把 Eval 描述为“我还在正轨吗”的自测能力。

它不只是测试代码功能，而是检查 Agent 行为是否符合系统契约，例如：

- 是否按阶段执行。
- 是否跑了必要验证。
- 是否产出必要上下文。
- 是否遵守治理约束。
- 是否把经验写回 Knowledge。

这部分在后续验证阶段展开。

### Harness = 基座

Harness 是 Agent 运行时基础设施，包括：

- Rules。
- Hooks。
- Skills。
- MCP。
- Context。
- Session。

AgentOS 不是替代 Harness，而是组合和编排这些 Harness 原语。

## AgentOS 与 gstack / superpowers 的关系

课件特别强调，AgentOS 不替代 gstack 或 superpowers，而是编排它们。

| 对比维度 | gstack / superpowers 等工具 | 你的 AgentOS |
|---|---|---|
| 编码的是什么 | 别人的最佳实践 | 你的判断 |
| 知道什么 | 通用经验 | 你的架构红线、验证标准、成本底线 |
| 如何进化 | 作者更新时进化 | 你每次纠正时进化 |
| 是否能替代 | 不能替代 AgentOS | 可以编排它们 |

课件用一个类比说明：

> gstack 是 App Store 里的 app，AgentOS 是操作系统。

你可以安装和使用 gstack 的 `/review`、`/ship`，也可以引入 superpowers 的 plan 机制，但这些工具应该运行在你的 Engine 中，受你的 Gates 约束，产出也要写回你的 Knowledge。

换句话说：

- 工具可以是外部的。
- 判断必须是你的。
- 产物要回到你的系统。
- 最终谁说了算，是 AgentOS。

这也直接对应我们前面讨论过的问题：superpowers 可以作为高质量技能进入 AgentOS，但不应该反过来决定 AgentOS 的目录、治理和归档机制。

## 飞轮：Knowledge 与 Engine 相互增强

课件提出 AgentOS 的复合飞轮：

```text
Knowledge 提供上下文
  -> Engine 产出更精准
  -> REFLECT 写回经验
  -> Knowledge 更丰富
  -> Engine 下次更好
  -> Corrections 减少
  -> Governance 蒸馏
  -> Principles 更锋利
  -> 回到顶部
```

这个飞轮的目标不是“零错误”，而是：

> 新类型错误也能首次处理对。

这句话非常关键。它说明系统的成熟度不看有没有历史错误，而看 Principle 是否能覆盖新变体。

如果同一个偏差换个皮又出现，说明治理还停留在枚举症状；如果新错能被已有 Principle 正确约束，说明系统开始有“类”的判断能力。

## 进化方向：蒸馏大于积累

课程反复强调一个反直觉判断：

> 好的 AgentOS 越用越短，不是越用越长。

它给出的依据包括：

- 臃肿的 `CLAUDE.md` 会让模型忽略指令。
- 反思条目过多会降低质量。
- 实战里，很多 correction 其实是同一偏差重复出现。

所以正确方向不是持续堆 rules，而是蒸馏：

| 原始状态 | 蒸馏动作 |
|---|---|
| 多条 rules 同源 | 吸收为一条 Principle |
| Gate 已机械覆盖 | 对应 Rule 退休 |
| Gate 长期不触发 | 考虑毕业 |
| 同类错误反复出现 | 找根因，而不是加枚举 |

健康的 AgentOS 应该表现为：

- 文件变短但质量提升。
- Gate 触发趋近于零。
- 新错首次处理对。
- 同一偏差不再换皮重复。

生病的 AgentOS 则表现为：

- 文件持续膨胀。
- 每个新错都需要新 gate。
- 同一偏差反复出现。
- rules 成为症状枚举清单。

## 三层治理模型预告

这份 Opening 也预告了后续的三层治理：

```text
Principles -> Rules -> Gates
```

覆盖关系大致是：

| 层级 | 定位 | 覆盖 |
|---|---|---|
| Principles | 方向性原则 | 约 70-80% |
| Rules | 具体指导 | 约 85-90% |
| Gates | 强制检查 | 接近 99% |

这里的重点不是精确百分比，而是分层思路：

- Principles 数量少，每条覆盖一类失败。
- Rules 有限、可追溯、可过期。
- Gates 最少化、机械化，只在文本约束失效后加入。

进化方向应该是向上：

- 高层原则越来越强。
- 低层门禁越来越少触发。
- 规则和门禁都可以退休。

## 三天课程路线图

课件把三天安排拆成三步：

| 日期 | 内容 | 产出 |
|---|---|---|
| Day 1 | AgentOS 全景 + Knowledge 模块 | `knowledge/`、`governance/`、`hooks/` |
| Day 2 | Delivery Engine + SDLC 实弹 | `engine/`、Knowledge 丰富化 |
| Day 3 | 蒸馏 + 验证 + Capstone | governance 精炼、`eval/`、完整 repo |

一句话：

```text
Day 1 造壳 -> Day 2 填肉 -> Day 3 精炼
```

从工程落地角度看，这个顺序很合理：

1. 先有 Knowledge 和 Governance，让 Agent 知道上下文和约束。
2. 再有 Engine，让 Agent 在不可跳步的流程中执行。
3. 最后做 Distillation 和 Eval，让系统能变短、能自测、能复盘。

## 项目载体：错题本

课程使用“错题本”作为统一项目载体：

- 拍照上传。
- AI 识别。
- 数字化管理。
- 复习推荐。

选择统一载体的好处是：

- 代码基础一致。
- 需求一致。
- 技术栈一致。
- 架构场景一致。
- 产出可比。
- 环境稳定。
- 方便互评。

但个人差异会体现在：

- Principles 怎么选。
- Rules 怎么写。
- Gate 放在哪里。
- 验证标准是什么。
- 蒸馏时保留什么、退休什么。

这说明 AgentOS 的差异不在项目题材，而在人的判断系统。

同一个错题本，不同团队最终会长出不同 AgentOS。

## 环境准备

课程环境包括：

- AWS Workshop。
- 每人独立环境。
- VSCode Server。
- Claude Code CLI。
- Amazon Bedrock 访问能力。
- 通过 `claude --version` 确认 CLI 可运行。

课件也提到后续 loop 实验会消耗 token，Day 3 会讲成本治理。

这和后续 Loop Engineering 的内容能对应起来：当 Agent 开始循环执行时，必须有验证、停止条件、成本控制和状态管理，否则会变成不可控消耗。

## 对我们 AgentOS 方案的启发

这份 Opening 对我们前面讨论的项目组 AgentOS 方案，有几个直接启发。

### 1. AgentOS 不是 Claude Code 配置，也不是 Codex 配置

课程把 AgentOS 放在工具之上。

所以我们的设计应该保持：

- 可以支持 Claude Code。
- 可以支持 Codex。
- 可以支持 superpowers。
- 可以支持 gstack。
- 但核心目录、治理规则、执行状态、测试契约、review packet 都归 AgentOS 管。

也就是说，Claude Code 的 `.claude/`、Codex 的用户目录、superpowers 的默认 plan 目录，都可以作为适配层存在，但不能成为唯一事实源。

### 2. 初始化不应该只生成工具配置

一个有效的初始化流程不应该只创建：

- `CLAUDE.md`
- `.codex/`
- `.claude/`
- hooks
- skills

还必须创建：

- `knowledge/`
- `governance/`
- `engine/`
- `eval/`
- `corrections.log`
- `STATE.md`
- review/test 的输入输出约定

否则只是 Harness 配置，不是 AgentOS。

### 3. 人的判断点要显式进入结构

AgentOS 初始化时应该要求团队至少回答：

- 项目不可妥协的 P1 是什么？
- 哪些架构决策不可逆？
- 哪些质量标准必须验证？
- 小需求可以快改到什么程度？
- 大需求什么时候必须进入 plan / spec / review / test 流程？
- 哪些问题需要 gate，而不是提醒？

这正是“人站在哪”的落地。

### 4. superpowers 可以被编排，不应该直接接管

我们之前讨论过 superpowers 的 plan 机制比现有 plan 规范更成熟，但它的问题是：

- 默认目录和我们的 AgentOS 目录不一致。
- 团队里有人不用它，会导致归档不完整。
- 小需求不一定需要完整 superpowers 流程。

这份课件给出的答案是：AgentOS 编排工具。

也就是说：

- 大需求可以调用 superpowers 风格 plan。
- 小需求可以走轻量 profile。
- 所有 plan 产物最终登记到 AgentOS 的 registry。
- 所有 correction / decision / discovery 最终写回 Knowledge。
- 外部工具是 app，AgentOS 是 OS。

### 5. 健康指标比文件数量更重要

初始化一套目录不难，难的是保证它不会变成文档坟场。

从这份课件看，AgentOS 应该内建健康检查：

- `CLAUDE.md` / `AGENTS.md` 是否膨胀。
- Principles 是否超过 5 条。
- Rules 是否持续增加。
- Gates 是否只加不退。
- Corrections 是否递减。
- 最近 session 是否有回写。
- PROJECT 是否过期。
- plan registry 是否混乱。

这些健康指标比“目录是否存在”更重要。

## 和前几份 PDF 的关系

这份 PDF 虽然文件名排在 `05`，但内容实际上是课程总览，它和前面几份关系如下：

| 已总结 PDF | 实际主题 | 在 AgentOS 中的位置 |
|---|---|---|
| `01_opening_agentos.pdf` | 实际是 Loop Engineering | Day 3：控制程序、验证、停止条件 |
| `02_harness_overview.pdf` | Harness 基座 | Rules / Hooks / Skills / MCP / Context / Session |
| `03_knowledge_ddd_feed.pdf` | Knowledge：DDD + Feed | 长期知识和经验流入 |
| `04_knowledge_governance.pdf` | Knowledge：三层治理 | Principles / Rules / Gates |
| `05_knowledge_retrieve_health.pdf` | 实际是 Opening：AgentOS 全景 | 整套课程总框架 |

因此，这份 PDF 可以当作整套总结的“总纲”来读，而不是 Retrieve + Health 的细节课。

## 最终结论

这份 PDF 的核心观点可以压缩为：

> AI 执行已经商品化，真正稀缺的是人如何把判断、品味和约束编译成 Agent 不能绕过的项目操作系统。

AgentOS 的价值不在于生成更多工具配置，而在于形成一个会进化的闭环：

```text
Knowledge 给上下文
  -> Engine 控制执行
  -> Gates 阻断跳步
  -> Eval 自测行为
  -> Corrections 记录经验
  -> Governance 蒸馏约束
  -> 下一次 Agent 做得更好
```

如果说 Harness 是工具箱，那么 AgentOS 是团队自己的运行制度。

这也解释了为什么课程反复强调“越用越短”：真正成熟的系统，不是记录了更多事故细节，而是能用更少、更高质量的原则覆盖更多未知情境。
