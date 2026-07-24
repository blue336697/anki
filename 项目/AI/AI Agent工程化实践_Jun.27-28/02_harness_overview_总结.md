# 02_harness_overview.pdf 总结

> 文件名：`02_harness_overview.pdf`  
> 正文标题：Module 02 · Harness 基座速览  
> 页数：12 页

## 一句话总结

这份 PDF 讲的是 AgentOS 的底层基座：AI 引擎只是可替换的“发动机”，真正有价值的是围绕引擎建立的 Harness，也就是负责记忆、生命周期、上下文注入、流程控制、工具接入、自愈和持续进化的系统。

## 核心命题：AI 引擎是商品，Harness 才是产品

课程一开始就给出一个判断：

```text
Engine = commodity.
Harness = your IP.
```

AI 引擎可以是 Claude、Kiro、Gemini 或其他 CLI 工具。它们本质上像“无状态工人”：

- 从 stdin 读指令。
- 调模型 API 和工具。
- 从 stdout 返回结果。
- 不天然知道昨天发生了什么。
- 不天然知道项目历史。
- 不天然会自愈。

真正让 Agent 变成可持续工程系统的是 Harness：

- 管理上下文。
- 管理会话生命周期。
- 注入项目知识。
- 捕获经验。
- 维护状态。
- 触发流程。
- 阻断错误。
- 从错误中学习。

所以，模型可以换，围绕模型建立的判断系统、流程系统和记忆系统才是团队的 IP。

## 自动驾驶类比

PDF 用汽车来类比 Agent：

| 汽车组件 | Agent 组件 | 作用 |
|---|---|---|
| 发动机 | AI CLI，如 Claude、Kiro | 原始动力 |
| 传感器 | Context 文件、工具、MCP | 感知世界 |
| 控制系统 | Pipeline、路由逻辑 | 即时决策 |
| 导航系统 | 目标分解、状态管理 | 规划多步旅程 |
| 整辆车 | Agent Harness | 所有部件协同 |

这个类比的重点是：换发动机不等于换整辆车。AgentOS 可以从 Claude 换到 Gemini，但只要 Harness 接口能适配，项目知识、流程、门禁、验证和状态仍可复用。

课程也提醒：设计理念可迁移，但具体实现可能依赖 Claude Code，例如 hooks 格式、settings 结构、CLI 行为。换引擎意味着要重接 Harness 接口。

## Agent 自治五级

PDF 将 Agent 能力分为 L1 到 L5：

| 级别 | 名称 | Agent 做什么 | 人做什么 | 代表产品 |
|---|---|---|---|---|
| L1 | 辅助 | 单次调用，展示结果 | 决定问什么、何时问 | ChatGPT 网页版 |
| L2 | 副驾驶 | 观察 + 建议补全 | 接受或拒绝 | Copilot、Cursor Tab |
| L3 | 智能体 | 多步推理 + 工具 + 检查点 | 设目标、审查、批准 | Claude Code、Kiro |
| L4 | 自主 | 无人值守 + 记忆 + 自愈 + 并发 | 设意图、偶尔检查 | SwarmAI、Devin |
| L5 | 自进化 | 跨天规划 + 从错误学习 + 扩展自身 | 设方向 | 2026 年无完整 L5 |

课程认为，大多数团队现在处于 L3。课程目标不是一天做到真正 L4，而是搭出 L4 的骨架和进化路径。

## L3 到 L4 的跃迁

L4 不是凭空多出来的能力，而是在 L1-L3 之上继续叠加：

- 跨 session 记忆。
- 无人值守运行。
- 崩溃后自动恢复。
- 同时处理多任务。
- 随时间改进自身行为。

PDF 将 L3 → L4 的关键总结为三件事：

```text
记忆 + 无人值守 + 自愈
```

对应课程后续模块：

| 能力 | 课程模块 |
|---|---|
| 记忆 | Knowledge |
| 无人值守流程 | Delivery Engine |
| 自愈 | Loop Engineering |

这也是 AgentOS 的主线：先让 Agent 记得住，再让它按流程跑，最后让它在验证和熔断保护下自动修复。

## Harness 的六大能力

PDF 给出 Harness 的六种基座能力：

| 能力 | 做什么 | 被谁使用 |
|---|---|---|
| Rules | 文本约束，从 prose 到可判定 spec | Knowledge → Governance |
| Hooks | 事件触发的自动执行 | Knowledge capture、Engine gate |
| Skills | 按需加载的工作流包 | Engine stage、Knowledge distill |
| MCP | 外部系统能力接入 | 领域工具、DB、CI、Cloud |
| Context | 上下文组装与预算管理 | SessionStart 注入 |
| Sessions | 会话生命周期管理 | State 持久化、中断恢复 |

这六种能力本身是通用零件，关键不在于“会不会写 hook”，而在于知道：

- 哪个模块为什么需要它。
- 应该放在哪里。
- 什么事件触发。
- 触发后产生什么状态变化。

## Rules：从自然语言建议到可判定约束

Rules 被描述为一个硬度递增的光谱：

| 层级 | 形态 | 示例 | 特点 |
|---|---|---|---|
| L1 prose | 自然语言建议 | 代码要清晰 | 容易被忽略 |
| L2 spec | 可判定规格 | 圈复杂度 ≤ 10 | 能自查 |
| L3 gate | 结构化阻断 | 反复违反后变成代码门禁 | 可追溯、可退休 |

课程特别强调：Rules 不是一开始就靠人拍脑袋写出来的一堆条款，而是 Knowledge / Governance 的产物。

正确链路是：

```text
Agent 犯错
  -> 人纠正
  -> corrections 积累
  -> 发现 pattern
  -> 蒸馏成 rule
  -> 反复违反则升级为 gate
```

每条 rule 都应该：

- link 到 principle。
- 有 evidence。
- 有过期条件。
- 被 gate 覆盖后可以退休。

这里的心智转变是：

```text
从“我来写规则管 Agent”
变成“系统从经验中蒸馏规则，我来审批”
```

## Hooks：让系统自动做事

Hooks 被称为 Agent 的“神经反射”。

典型触发点包括：

- `SessionStart`
- `PreToolUse`
- `PostToolUse`
- `PreCommit`
- `SessionEnd`

Knowledge 用 hooks：

| Hook | 作用 |
|---|---|
| SessionStart | Retrieve，注入 DDD + principles |
| SessionEnd | Capture，自动捕获 corrections |

Engine 用 hooks：

| Hook | 作用 |
|---|---|
| PreCommit | Gate，阻断不合格产出 |
| PostToolUse | Stage 触发，推进阶段判定 |

Hook 的价值是把“我记得要做”变成“系统自动做”。这是从人记得（L1）到系统执行（L3）的关键通道。

## Skills：按需加载的工作流包

Skill 是 Agent 的专业技能包，典型结构：

```text
my-skill/
├── SKILL.md      # 触发条件 + 执行流程 + 产出规范
├── scripts/      # 可选脚本
└── templates/    # 可选模板
```

Skills 的核心是 lazy load：

- 触发时才加载。
- 用完释放。
- 不常驻上下文。
- 避免把所有规则塞进有限 context。

在 AgentOS 中：

| 场景 | Skill 用法 |
|---|---|
| Engine | 每个 stage 可以是一个 skill |
| Knowledge | distill / evolve 可以是 skill |
| 第三方能力 | gstack `/review`、`/ship` 可以装进 Engine |

课程给出一个重要定位：第三方 skill 像 App Store 里的 app，应该被装进你的 Engine 轨道里运行。如果第三方 skill 的标准和你项目的 Gate 冲突，应该由你的 Gate 拦住。

## MCP：外部能力接入

MCP 是 Agent 的工具箱扩展，可以接入：

- DB
- CI
- Cloud
- API
- 领域工具

但课程提出一个务实原则：

```text
能用 CLI 解决的不用 MCP。
```

原因是 Claude Code 自带 bash 和文件操作，大部分事情用 CLI 已经足够。MCP 应该用于 CLI 做不到的领域逻辑，而不是为了接工具而接工具。

首要安全机制是：

```text
给工具 = 给权限
permissions.deny 是第一道防线
```

所以 MCP 不是越多越好，而是要围绕具体 Engine 阶段和领域工具需求谨慎接入。

## Context：上下文工程

Context 是 Agent 的工作记忆。PDF 提醒 context window 虽然有 100K-200K token，但注意力不是均匀的。

推荐注入顺序：

```text
Principles（最高 attention）
DDD 摘要
Rules（按需 / lazy load）
Engine State
```

Context Engineering 三原则：

1. 最重要的放最前，对抗 attention decay。
2. 不需要的不加载，使用渐进式 / lazy load。
3. 定期清理过期内容，避免 stale context。

这也是课程反复强调“不要把 CLAUDE.md 塞成垃圾场”的原因。塞太多不仅浪费 token，还会让关键约束被稀释。

## Sessions：会话生命周期

Session 是 Agent 的作息规律：

```text
Session Start -> inject
Work -> 执行任务
Session End -> capture
```

跨 session 持久化的内容包括：

- DDD 文档。
- Memory。
- `STATE.md`。

课程强调：

```text
每次新 session，Agent 都是白纸。
SessionStart 的注入质量 = 这个 session 的智力上限。
```

Session 能力支撑两件事：

| 场景 | 作用 |
|---|---|
| Engine / State 持久化 | 跑到 BUILD 下班，明天新 session 续跑 |
| Knowledge / Memory 积累 | 经验跨 session 沉淀，越用越懂项目 |

跨 session 记忆不是模型自带的，而是 Harness 提供的。

## 六大能力如何组合成两个模块

PDF 最后一页给了 Knowledge 和 Engine 对 Harness 能力的使用对照：

| Harness 能力 | Knowledge 怎么用 | Engine 怎么用 |
|---|---|---|
| Rules | Governance 产出 principles / rules | 不直接使用 |
| Hooks | Capture + Retrieve | Gate + Stage 触发 |
| Skills | distill / evolve | Stage 执行逻辑 |
| MCP | 未来可接向量库 | 领域工具接入 |
| Context | 注入策略，什么放前、什么 lazy load | State 占位管理 |
| Sessions | 跨 session 记忆积累 | 跨 session 状态恢复 |

这张表的价值在于说明：Knowledge 和 Engine 不是凭空出现的两个文件夹，而是用同一组 Harness 原语组合出来的两个系统模块。

## 对 AgentOS 初始化的启发

如果把这份 PDF 落实到 AgentOS 初始化脚本中，至少应该有这些设计：

### 1. 引擎适配层

因为 AI 引擎可替换，所以不要把项目事实写死在 Claude Code 专属配置里。

推荐结构：

```text
agentos/adapters/
├── claude-code.md
├── codex.md
└── superpowers.md
```

`CLAUDE.md` 和 `AGENTS.md` 只是入口，真正的项目协议放在 `agentos/`。

### 2. Knowledge / Engine 分层

推荐结构：

```text
agentos/
├── knowledge/
├── governance/
├── engine/
├── eval/
├── test/
├── review/
└── adapters/
```

Knowledge 负责“知道什么、记住什么、约束什么”。Engine 负责“按什么流程做、在哪检查、什么时候停”。

### 3. Context 注入顺序

AgentOS 的入口文件应明确要求先读：

1. `agentos/governance/principles.md`
2. `agentos/knowledge/PRODUCT.md`
3. `agentos/knowledge/TECH.md`
4. `agentos/engine/STATE.md`
5. 当前任务相关 plan / artifact

不要让长文档和历史材料淹没 principles。

### 4. Hooks 可选但协议必须稳定

不同 agent 对 hooks 支持不同：

- Claude Code 可能有 session hooks。
- Codex 可能需要手工或脚本读取 session JSONL。
- 其他 agent 可能没有 hook。

所以 AgentOS 应该定义：

```text
如果有 hook，就自动 capture/retrieve。
如果没有 hook，就通过 runbook 要求人手动补 artifacts/corrections。
```

不能让 AgentOS 的正确性依赖某一个工具的 hook 能力。

### 5. Rules 必须可蒸馏、可退休

初始化时不要塞几十条 rules。只放少量原则，并为 rules 保留：

- 追溯。
- 证据。
- 过期条件。
- 退休目录。

推荐结构：

```text
agentos/governance/
├── principles.md
├── rules/
│   └── _retired/
└── gates/
    └── _graduated/
```

## 可直接复用的落地清单

### 初始化 Harness 时

- [ ] 明确 AI 引擎只是 adapter，不是项目事实源。
- [ ] 建立 `agentos/adapters/`。
- [ ] 建立 `knowledge/` 和 `engine/` 两个主模块。
- [ ] 不把所有规则塞进 `CLAUDE.md`。
- [ ] 明确 context 注入顺序。
- [ ] 明确 session start/end 的 capture/retrieve 策略。

### 写 Rules 时

- [ ] rule 能追溯到 principle。
- [ ] rule 有 corrections 或事故证据。
- [ ] rule 有判定标准。
- [ ] rule 有过期条件。
- [ ] 被 gate 覆盖后可退休。

### 设计 Hooks 时

- [ ] SessionStart 注入 DDD + principles + state。
- [ ] SessionEnd 捕获 corrections / decisions / discoveries。
- [ ] PreCommit 或 Pre-PR 触发 gate。
- [ ] PostToolUse 可触发 stage 推进。
- [ ] 没有 hook 的 agent 有手动替代路径。

### 使用 Skills 时

- [ ] skill 只在需要时加载。
- [ ] stage skill 有明确产出物。
- [ ] 第三方 skill 受本项目 gate 约束。
- [ ] skill 的输出要回写到 AgentOS artifact。

### 接 MCP 时

- [ ] CLI 能解决的不要接 MCP。
- [ ] MCP 权限最小化。
- [ ] permissions.deny 优先配置。
- [ ] MCP 只服务具体领域工具需求。

## 我的理解

这份 PDF 的价值在于帮我们把“Agent”拆成了两个层面：一个是可替换的 AI 引擎，另一个是不可轻易替代的 Harness。

很多团队会把注意力放在“哪个模型更强”“哪个工具更会写代码”，但课程提醒我们：真正决定系统上限的是你有没有自己的记忆、流程、门禁、上下文策略和状态管理。

因此，一个好的 AgentOS 不应该只是 Claude Code 配置，也不应该只是 Codex 指令。它应该是一套稳定的项目协议，让不同引擎都能接入，让项目判断沉淀下来，让系统从错误中进化。
