# 13_capstone_roadmap.pdf 总结

> 文件名：`13_capstone_roadmap.pdf`  
> 正文标题：Capstone + Roadmap · Day 3 下午  
> 页数：8 页

## 一句话总结

这份 PDF 是三天课程的最终整合：把 Knowledge、Governance、Engine、Eval、Loop、Hooks、Skills、Corrections 和 CI 组装成一个可运行的 `my-agentos/`，并用互评和 30/60/90 行动计划，把课堂成果变成真实项目里的持续实践。

## 三天你到底造出了什么

课程回顾三天路径：

| 日期 | 内容 | Agent 获得什么 |
|---|---|---|
| Day 1 | AgentOS 全景 + Knowledge 模块 | 记忆 |
| Day 2 | Delivery Engine + SDLC 实弹 | 纪律 |
| Day 3 | 验证 + Loop Engineering | 自我检测与自动驾驶 |

三件事合起来，才是一个可运转的 AgentOS。

核心成果是：

> 你的判断被编译成了系统。

这句话是整门课的收束。课程不是教你做一个错题本，也不是教你配一个 Claude Code 工具箱，而是教你把人的判断、品味和约束变成 Agent 绕不过去的运行机制。

## 最终 repo 结构

最终 `my-agentos/` 应该长这样：

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
│   │   ├── R001-*.md
│   │   └── _retired/
│   └── gates/
│       ├── check-*.sh
│       └── _graduated/
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
│   ├── on-session-start.sh
│   └── on-session-end.sh
├── skills/
│   ├── distill/
│   └── gate-review/
├── spec/
│   └── recognize/
├── corrections.log
├── ci/
│   └── verify.sh
└── docs/
    └── 30-60-90-action-plan.md
```

各部分职责：

| 路径 | 作用 |
|---|---|
| `README.md` | 使用说明，Capstone 产出 |
| `knowledge/` | DDD、项目事实、技术决策、健康检查 |
| `governance/` | Principles、Rules、Gates、退休记录 |
| `engine/` | 阶段、门禁、profile、状态、loop 配置 |
| `eval/` | 行为契约和 AgentOS 自测 |
| `hooks/` | SessionStart / SessionEnd |
| `skills/` | 蒸馏、gate review 等可复用能力 |
| `spec/` | Engine 运行产生的 artifacts |
| `corrections.log` | 蒸馏原料 |
| `ci/verify.sh` | 业务验证 |
| `docs/30-60-90-action-plan.md` | 后续路线图 |

## Capstone 任务

最终整合任务包括四件事：

1. 补缺失部分
   - 对照最终目录结构检查文件。
   - 补齐 hooks、eval、engine、governance 等。

2. 写 `README.md`
   - 说明 AgentOS 是什么。
   - 列出核心 principles。
   - 写使用方式。
   - 写健康检查和行为验证命令。

3. 跑一次 Eval
   - 执行 `eval/run-eval.sh`。
   - 记录当前得分。
   - 找最低分维度。

4. 写 30/60/90 action plan
   - 说明接下来三个月怎么落地到真实项目。

## README.md 应该写什么

课件给了 README 的最小结构：

```markdown
# My AgentOS

## 是什么
[一句话：AgentOS 核心理念]

## 核心 Principles
[列出你的 3-5 条原则]

## 使用方式
1. 克隆 repo 到项目根目录
2. 配置 hooks（settings.json）
3. 启动 session — Knowledge 注入
4. 下发任务 — Engine 驱动

## 健康检查 / 行为验证
bash knowledge/health.sh
bash eval/run-eval.sh
```

README 的目标不是长，而是让团队成员知道：

- 这套东西是什么。
- 怎么启动。
- 怎么检查健康。
- 怎么验证行为。
- 遇到任务时怎么走 Engine。

## 整合 Lab：45 分钟

课件把最终整合拆成 4 段：

| 时间 | 任务 |
|---:|---|
| 15 min | 结构补全 |
| 15 min | 写 README.md |
| 10 min | 跑 Eval |
| 5 min | Git commit |

结构补全要检查：

- 缺失文件。
- hooks 是否注册到 settings。
- `eval/run-eval.sh` 是否可执行。
- `knowledge/health.sh` 是否能跑。
- `engine/STATE.md` 是否存在。
- `loop-config.md` 是否补齐。

最后 Git commit 的意义是：

> 你的 AgentOS v1.0 诞生了。

## 互评：跨视角审查

Capstone 不是只自己看，还要互评。

方式：

- 2-3 人一组。
- 交换 repo 或屏幕分享。
- 15 分钟审查。
- 5 分钟反馈。

互评不是评对错，而是讨论：

> 为什么你和我不一样？

审查维度：

| 维度 | 怎么看 | 信号 |
|---|---|---|
| Principles 可判定性 | 对每条做反例测试 | 能想到模糊场景 = 不够可判定 |
| Gates 合理性 | gate 级别是否太重/太轻 | 全 L3 没收益，全 L1 形同虚设 |
| 覆盖度 | 随机抽 3 条 correction，看能追溯到哪里 | 追溯不到 = 覆盖缺口 |
| 蒸馏度 | rules 数量、退休记录、governance/corrections 比例 | 只增不减 = 没蒸馏 |
| 差异点 | 最大差异是什么，为什么不同 | 差异 = 品味的多样性 |

## 互评的价值

课程强调，同一个错题本，会长出 N 种 AgentOS。

预期差异包括：

- Principles 优先级不同。
- Gates 级别不同。
- 有的人全 L1，比较激进。
- 有的人全 L3，比较保守。
- corrections 数量不同。
- corrections 质量不同。
- 蒸馏程度不同。

关键不是统一答案，而是：

> 每个判断都应该有理由。

说不出为什么选，就不是“选了”，而是“没选”。

互评最大的价值是拓展判断维度。有理由的差异是品味，没理由的是随意。

## 30/60/90 行动计划

课程强调，三天只是开始，真正价值来自回到真实项目后持续运行。

## 30 天：运行 + 积累

目标：

- 挂到真实项目。
- 跑 2-3 个 feature。
- 积累 50+ corrections。
- 每周一次 eval。
- 做 2 次蒸馏。

成功指标：

- Principles <= 5 条。
- Rules 有退休记录。

## 60 天：渐进 + Loop

目标：

- Gates 从 L3 -> L2 -> L1 渐进降级。
- 第一次 loop 实验，建议从 bugfix 开始。
- Knowledge 维护自动化。
- Eval score 呈上升趋势。

成功指标：

- 至少 1 类任务可以 loop 运行。

## 90 天：进化 + 迁移

目标：

- 应用到第二个项目。
- Principles 跨项目复用。
- Rules 项目特定重写。
- 蒸馏到核心，文件变短。

成功指标：

- 新项目接入小于 1 天。

## 行动计划模板

课件建议创建：

```text
docs/30-60-90-action-plan.md
```

模板：

```markdown
# 30/60/90 Action Plan

## 30 Days: 运行 + 积累
- [ ] 将 AgentOS 接入项目 [名]
- [ ] 跑 3 个 feature 通过 Engine
- [ ] 积累 50+ corrections
- [ ] 做 2 次蒸馏（第 15、30 天）
成功指标: principles <= 5, rules 有退休

## 60 Days: 渐进 + Loop
- [ ] G1/G3 降为 L1
- [ ] 第一次 bugfix loop 实验
- [ ] PROJECT.md 自动更新
成功指标: 至少 1 类任务可 loop

## 90 Days: 进化 + 迁移
- [ ] 接入第二个项目
- [ ] Principles 跨项目复用
- [ ] Governance 总量 < Day30 的 70%
成功指标: 新项目接入 < 1 天
```

课件问了一个最重要的问题：

> 明天回到办公室，你第一件做的事情是什么？

“配 hooks”是具体行动；“继续学习”不够具体。课程认为你已经够了，接下来要的是做。

## 对 AgentOS 机制设计的启发

### 1. AgentOS v1 必须能被使用，而不是只被阅读

最终 repo 里必须有启动路径：

- README 告诉人怎么用。
- hooks 能注入。
- Engine 能触发。
- Eval 能跑。
- Health 能检查。
- Action plan 能推进。

这套系统如果没有 README 和命令入口，就很容易变成文档集合。

### 2. 互评应该成为团队机制

团队内可以定期互评 AgentOS：

- 每两周审一次 principles。
- 随机抽 corrections 追溯治理覆盖。
- 检查 rules 是否有退休。
- 检查 gates 是否过重或过轻。
- 检查 eval score 是否下降。

这比单人维护更稳，因为很多“品味”只有在对比中才会显性化。

### 3. 30/60/90 是落地节奏，不是愿景文档

行动计划必须写具体动作和成功指标。

例如：

- 接入哪个项目。
- 跑几个 feature。
- 积累多少 corrections。
- 什么时候蒸馏。
- 哪些 gate 降级。
- 哪类任务进入 loop。

否则 AgentOS 会停留在课程产物，而不是成为团队运行系统。

## 对 payment-agent 的落地建议

如果要把这套结构初始化到 `payment-agent-ai`，最终目录可以映射为：

```text
payment-agent-ai/
├── agentos/
│   ├── README.md
│   ├── knowledge/
│   ├── governance/
│   ├── engine/
│   ├── eval/
│   ├── hooks/
│   ├── skills/
│   ├── spec/
│   ├── corrections.log
│   ├── ci/
│   └── docs/30-60-90-action-plan.md
├── AGENTS.md
├── .claude/
└── .codex/
```

`AGENTS.md` / Claude / Codex 只作为适配入口，事实源放在 `agentos/`。

支付项目的 30 天行动可以是：

- 接入 AgentOS 到一个低风险服务。
- 跑 2 个非资金核心 feature。
- 跑 1 个 bugfix。
- 建立支付关键 principles。
- 为金额、幂等、secret、状态机建立 G3/G4 gate。
- 每周跑 eval。

60 天再做：

- 小 bugfix loop。
- G1/G3 自动化。
- 高阶模型 L2 review。
- payment-critical profile。

90 天再迁移：

- 接入第二个支付子系统。
- 抽取跨项目 principles。
- 项目特定 rules 重写。
- governance 总量下降。

## 课程终章的核心思想

课件最后总结了四个能力：

| 能力 | 含义 |
|---|---|
| 判断编译 | 把品味变成 Agent 跑不掉的约束 |
| 蒸馏思维 | 做减法大于做加法 |
| 三件套模子 | 人站哪 -> 品味是什么 -> 编译成什么 |
| 系统思维 | 不是配 rules，而是建会进化的系统 |

它还强调：

> 工具会变，模型会换。你的判断只会越来越锋利。

这也是整套课程对项目组最重要的启发：不要把核心能力绑定到某个模型、某个 IDE、某个 CLI，而要把团队判断沉淀成可迁移、可演化的系统。

## 最终结论

这份 PDF 的核心结论是：

> AgentOS 的最终交付不是一堆规则文件，而是一个可运行、可验证、可互评、可迁移、可持续变短的系统。

Capstone 的标准不是“目录齐全”，而是：

- README 能指导使用。
- Eval 能跑出分数。
- Health 能发现问题。
- Engine 能跑真实任务。
- corrections 能持续进入蒸馏。
- governance 有退休和毕业。
- 30/60/90 有具体行动。

三天课程结束时，真正带走的不是错题本，而是一套把团队判断编译进 AI Agent 工作流的能力。
