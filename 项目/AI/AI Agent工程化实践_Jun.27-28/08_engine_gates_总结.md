# 08_engine_gates.pdf 总结

> 文件名：`08_engine_gates.pdf`  
> 正文标题：Delivery Engine 设计(2) · Gates 门禁设计  
> 页数：8 页

## 一句话总结

这份 PDF 讲的是 Delivery Engine 的门禁设计：阶段之间不能只是画线，还要放可判定、可回退、可升级/降级的 Gate；并且不是所有 Gate 都一样重，应该用 L1 AI 自查、L2 AI 互查、L3 人工审批三层门禁控制成本和风险。

## 核心命题：不是所有门都一样重

上一份 PDF 解决了阶段设计：

```text
EVALUATE -> PLAN -> BUILD -> VERIFY
```

但只有阶段还不够。Agent 仍然可能从 EVALUATE 直接跳到 BUILD，或者在 Gate 失败后不知道该怎么办。

本节解决的问题是：

> 阶段之间的门禁怎么设计，才能既不阻塞，又能拦住关键错误？

课程提出三级门禁体系：

| 级别 | 名称 | 执行者 | 成本 | 适用场景 |
|---|---|---|---|---|
| L1 | AI 自查 | 当前 Agent 自查 artifact | 低 | 格式完整性、条件数量、自动化检查 |
| L2 | AI 互查 | 另一个 Agent / 另一个 prompt 审查 | 中 | 方案合理性、代码质量、主观判断 |
| L3 | 人工审批 | 人看一眼确认 | 高 | 不可逆决策、架构选型、重大风险 |

设计原则是：

- 大部分 Gate 应该是 L1，快速自检，不阻塞。
- 少数关键 Gate 是 L2，引入独立视角。
- 极少数 Gate 是 L3，只放在不可逆决策处。

随着系统变成熟，门禁还可以演进：

```text
corrections 减少 -> L3 降 L2 -> L2 降 L1
```

这和前面 Governance 的思想一致：系统越用越轻，而不是越来越重。

## Gate 的核心是判定条件

Gate 不是一句“检查一下”，而是一组可判定条件。

好的判定条件应该满足：

- 可判定。
- 尽量可自动化。
- 对通过/失败没有歧义。
- 不要求人读大量内容才能判断。

示例：

```markdown
## Gate G1: EVALUATE -> PLAN

### 级别
L1（AI 自查）

### 判定条件
- [ ] artifact `evaluate-{id}.md` 存在
- [ ] 包含 "Acceptance Criteria" 段落
- [ ] AC 数量 >= 3
- [ ] 每条 AC 可判定（boolean，非模糊）
- [ ] 包含 "Irreversible Decisions" 段落

### 失败动作
回退 EVALUATE + 提示缺项

### 降级 / 升级路径
当前 L1 -> 连续 3 次失败 -> 升 L2
L2 连续 5 次通过 -> 降回 L1
```

课程把判定条件分为三类：

| 类型 | 示例 | 适合级别 |
|---|---|---|
| 形式检查 | 文件存在、格式正确、段落齐全 | L1 / 脚本 |
| 内容检查 | AC 是否可判定、风险是否列出 | L1 / L2 |
| 质量检查 | 方案是否合理、架构是否有坑 | L2 / L3 |

越靠近质量判断，越需要独立视角或人工审批。

## 错题本 Engine 的四道 Gate

课程为最小 Engine 设计了 4 道 Gate：

| Gate | 边界 | 级别 | 核心判定 |
|---|---|---|---|
| G1 | EVALUATE -> PLAN | L1 | AC 存在且可判定 |
| G2 | PLAN -> BUILD | L2 | 方案合理、风险可控 |
| G3 | BUILD -> VERIFY | L1 | 代码存在、测试通过、lint 通过 |
| G4 | VERIFY -> Done | L1 | 验证报告存在，所有 AC 标记通过 |

### G2 为什么是 L2

PLAN -> BUILD 是非常关键的边界，因为一旦进入 BUILD，Agent 会开始实现方案。

G2 需要 L2 的原因：

- 方案合理性判断有主观性。
- 自己设计的方案自己审，容易自我确认偏差。
- 独立 prompt 可以用 `devil's advocate` 角色找问题。
- 如果方案本身错了，后面写再多代码也是错的。

所以 G2 是典型的“值得花中等成本”的 Gate。

### G3 为什么通常是 L1

BUILD -> VERIFY 的很多检查可以自动化：

- 测试是否通过。
- lint 是否通过。
- typecheck 是否通过。
- 是否存在硬编码 secret。
- 代码文件是否存在。

这些不需要人类判断，也不需要另一个模型优先介入。

但如果代码质量反复出问题，G3 可以升级为 L2，让另一个 Agent 做 review。

## Gate 失败后的回退设计

Gate 不通过时，必须知道回退到哪里。

课程给出三种处理方式：

| 处理方式 | 适用场景 | 成本 |
|---|---|---|
| 原地修复 | 小问题，例如格式缺失、少写一段 | 低 |
| 回退上一步 | 根本性问题，例如方案不合理 | 中 |
| 回退到起点 | 方向性错误，例如需求理解错 | 高 |

具体到四道 Gate：

| Gate 失败 | 回退策略 |
|---|---|
| G1 失败 | 原地修复，补充 evaluate artifact |
| G2 失败 | 回退 PLAN，重新设计方案 |
| G3 失败 | 原地修复 bug、补测试 |
| G3 同一问题 3 次修不好 | 回退 PLAN，说明方案可能有问题 |
| G4 失败 | 回退 BUILD，修复验证发现的问题 |

这里最重要的是“连续失败升级”：

> 同一 Gate 连续 3 次不通过，要升级处理。

原因是：如果一个问题在当前阶段反复修不好，问题很可能出在更上游。

没有回退路径的 Engine 会导致 Agent 陷入无限循环：

```text
修复 -> Gate 失败 -> 再修复 -> Gate 再失败 -> 继续猜
```

有回退路径后，Agent 才知道什么时候停止局部修补，回到上游重新判断。

## gates.md 文件格式

课件建议把门禁设计固化到：

```text
engine/gates.md
```

示例结构：

```markdown
# Delivery Engine — Gates

## G1: EVALUATE -> PLAN
**级别**: L1（AI 自查）
**判定条件**:
- artifact 存在
- AC >= 3 且可判定
- 不可逆决策已声明
**失败处理**: 原地修复
**降级路径**: 3 次失败 -> L2

## G2: PLAN -> BUILD
**级别**: L2（AI 互查 — devil's advocate）
**判定条件**:
- 方案覆盖所有 AC
- 风险已识别并有缓解
- 不可逆决策有 ADR
- devil's advocate 无法找到致命缺陷
**失败处理**: 回退 PLAN
**Prompt**: skills/gate-review/
**降级路径**: 连续 5 次通过 -> L1

## G3: BUILD -> VERIFY
**级别**: L1（自动化检查）
**判定条件**:
- 代码存在
- 测试全通过
- lint 通过
- 无硬编码 secrets
**失败处理**: 原地修复；3 次同问题 -> 回退 PLAN

## G4: VERIFY -> Done
**级别**: L1（AI 自查）
**判定条件**:
- verify artifact 存在
- 所有 AC 有 pass/fail
- 无 fail 项
- 有主动破坏尝试记录
**失败处理**: 回退 BUILD
```

这个格式比单纯写“要检查测试”强很多，因为它明确了：

- 级别。
- 判定条件。
- 失败处理。
- 使用的 prompt / skill。
- 升级或降级路径。

## Profiles：不同任务走不同路径

课程明确回答了一个实际问题：

> bugfix 需要完整 EVALUATE -> PLAN -> BUILD -> VERIFY 吗？一行 typo 修复也需要 PLAN 吗？

答案是：不需要所有任务走同一条路径。

因此 Engine 需要 `profiles.md`。

示例：

| Profile | 路径 | 适用场景 / Gate 调整 |
|---|---|---|
| `feature` | EVALUATE -> PLAN -> BUILD -> VERIFY | 新功能、重大变更，默认路径 |
| `bugfix` | EVALUATE -> BUILD -> VERIFY | 已知 bug；G1 AC 要求降低到 >= 1 |
| `hotfix` | BUILD -> VERIFY | 紧急修复；G3 不要求覆盖率 |
| `refactor` | PLAN -> BUILD -> VERIFY | 重构；G4 要求回归测试 |

课程特别强调：

> 这不是跳过 Gate，而是为不同路径设计适合的 Gate 级别。

也就是说，轻流程不是无流程。小需求可以省略某些阶段，但仍然应该有最小验证和状态记录。

## STATE.md：运行时状态

Engine 还需要记录当前任务走到哪一步。

课件建议创建：

```text
engine/STATE.md
```

示例：

```markdown
# Engine State

任务: recognize 函数开发
Profile: feature
当前阶段: BUILD
已通过 Gates: G1 ✅, G2 ✅
开始时间: 2024-01-15 14:30
```

`STATE.md` 的作用是：

- 记录当前 profile。
- 记录当前阶段。
- 记录已经通过的 Gates。
- 支持下次 session 启动时续上。
- 防止 Agent 忘记自己执行到哪里。

这和 Knowledge 的长期记忆不同，`STATE.md` 更像当前任务的运行时状态。

## Lab 要求

本节 Lab 要完成三个文件：

```text
engine/
├── gates.md
├── profiles.md
└── STATE.md
```

具体任务：

1. 创建 `engine/gates.md`
   - 为每个阶段间写 Gate。
   - 包含级别、判定条件、失败处理。

2. 创建 `engine/profiles.md`
   - 至少写 2 个 profile。
   - 必须包含 `feature`。
   - 再加一个轻量级 profile，例如 `bugfix` 或 `hotfix`。

3. 创建 `engine/STATE.md`
   - 先写空模板。
   - 下午跑 Engine 时再填充真实状态。

Lab 里的关键思考题：

- G2 你选 L1 还是 L2？
- 你有多信任 Agent 的方案设计能力？
- 你是否被“方案看着合理其实有坑”坑过？
- hotfix profile 省略了哪些 Gate？
- 为什么这些 Gate 可以省？

这些问题本质上仍然是“选择 + 后果 = 品味”。

## Day 2 上午产出

到本节结束，Delivery Engine 的设计文件应该包括：

```text
engine/
├── stages.md      # 阶段序列 + 每阶段结构
├── gates.md       # 门禁级别 + 判定 + 回退
├── profiles.md    # 任务类型 -> 路径映射
└── STATE.md       # 运行时状态模板
```

上午完成的是设计，下午会跑一个完整 feature：

```text
EVALUATE -> PLAN -> BUILD -> VERIFY
```

每一步都要有真实 artifact、触发 Gate，并产生 corrections。

这时 Knowledge 和 Engine 开始联动：

- Knowledge 提供上下文和原则。
- Engine 控制执行轨道。
- Gate 决定是否允许前进。
- Session 结束后 corrections 写回 Knowledge。

## 对 AgentOS 机制设计的启发

这份 PDF 对我们讨论的项目组 AgentOS 很关键，尤其是如何平衡“规范”和“效率”。

### 1. Gate 必须分级，否则流程会过重

如果所有 Gate 都要求人审，AgentOS 很快会变成负担。

更合理的是：

- L1 用脚本和当前 Agent 自查覆盖高频低风险问题。
- L2 用高阶模型或独立 prompt 审查方案和代码质量。
- L3 只用于不可逆、高风险、需要业务/架构判断的位置。

例如在支付项目中：

| 场景 | Gate 级别 |
|---|---|
| lint / typecheck / unit test | L1 |
| 普通方案 review | L2 |
| 金额状态机、清结算、幂等策略变更 | L3 |
| hotfix 中的最小验证 | L1 |
| 高风险发布前复核 | L3 |

### 2. Code Review 可以作为 L2 Gate

前面用户问过“如何用更高阶模型做 code review”。这份 PDF 给了位置：

> 高阶模型 review 应该作为 L2 Gate，通常放在 PLAN -> BUILD 或 BUILD -> VERIFY 之间。

也就是说，review 不是游离流程，而是 Engine 的一类 Gate。

它需要输入：

- task 背景。
- evaluate artifact。
- plan artifact。
- diff。
- relevant Knowledge。
- principles / rules。
- tests run。
- known risks。

输出则是：

- pass / fail。
- blocking findings。
- non-blocking suggestions。
- 是否回退 PLAN 或 BUILD。

### 3. 测试也可以作为 L1 / L2 Gate

测试不是最后随手跑一下，而是 G3 和 G4 的关键内容：

- G3：代码进入 VERIFY 前，测试、lint、typecheck 必须过。
- G4：最终完成前，所有 AC 必须有 pass/fail 记录，并且有主动破坏尝试。

如果测试反复漏掉边界，就可以升级：

- 从普通 L1 测试 Gate。
- 升级为 L2 测试计划审查。
- 对关键路径再加入 L3 人工验收。

这和美团文章强调测试重要性是一致的：测试不是可选项，而是阶段边界。

### 4. 小需求可以轻，但要有 Profile 约束

这份 PDF 正好回答了“小需求是不是力大砖飞直接改”的问题。

可以快，但要明确它走的是 `bugfix` / `hotfix` profile，而不是没有流程。

例如：

```text
hotfix: BUILD -> VERIFY
```

它可以省略 PLAN，但必须说明：

- 为什么是 hotfix。
- 省略了哪些 Gate。
- 最小验证是什么。
- 是否需要事后补充 review / correction。

这样团队不会因为小需求太多而把 AgentOS 绕开。

### 5. STATE.md 是跨 Claude Code / Codex 的共同锚点

Claude Code 有自己的 session，Codex 有自己的 thread 和 JSONL 记录，但 Engine 状态不应该只存在于工具内部。

`engine/STATE.md` 可以作为共同锚点：

- Claude Code 启动时读取它。
- Codex 启动时读取它。
- 任意 Agent 都能知道当前任务在哪一阶段。
- 不依赖某个工具自己的 plan 模式或 session 文件。

这能减少 Claude Code plan、Codex plan、superpowers plan 之间的冲突。

## 对 payment-agent 的落地建议

如果把这套 Gate 机制用于 `payment-agent-ai`，建议默认采用更保守的分级。

### 推荐 Profiles

```text
feature:
  EVALUATE -> PLAN -> BUILD -> REVIEW -> VERIFY

bugfix:
  EVALUATE -> BUILD -> VERIFY

hotfix:
  BUILD -> VERIFY -> POST_REVIEW

payment-critical:
  EVALUATE -> PLAN -> ARCH_REVIEW -> BUILD -> CODE_REVIEW -> VERIFY -> RELEASE_CHECK
```

### 推荐 Gate 分级

| Gate | 边界 | 级别 | 原因 |
|---|---|---|---|
| G1 | EVALUATE -> PLAN | L1/L2 | 普通任务 L1，高风险任务 L2 |
| G2 | PLAN -> BUILD | L2 | 方案合理性需要独立视角 |
| G2.5 | PLAN -> BUILD | L3 | 涉及资金、状态机、幂等、外部合约时人审 |
| G3 | BUILD -> REVIEW | L1 | 测试、lint、typecheck、secret scan |
| G4 | REVIEW -> VERIFY | L2 | 高阶模型 code review |
| G5 | VERIFY -> Done | L1/L3 | 普通任务 L1，支付关键路径 L3 |

### 支付项目必须关注的 Gate 条件

- 金额精度不能用浮点。
- 状态流转必须有明确合法边。
- 外部调用必须有幂等键。
- 重试必须有上限和退避。
- 失败必须可追踪。
- 数据写入必须有审计字段。
- 资金相关变更必须有回归测试。
- schema / migration / API 文档必须同步。
- 不确定结果不能默认成功。

这些条件可以分别落到 L1 脚本、L2 review prompt 和 L3 人审清单里。

## 和前一份 PDF 的关系

`07_engine_design.pdf` 解决的是：

> 阶段怎么画？

本 PDF 解决的是：

> 阶段之间怎么放门？门失败了怎么回退？不同任务是否能走不同路径？

二者合在一起，Delivery Engine 才完整：

```text
stages.md   定义轨道
gates.md    定义边界
profiles.md 定义不同任务路径
STATE.md    记录当前运行位置
```

## 最终结论

这份 PDF 的核心结论是：

> 一个可用的 Delivery Engine，不只是有阶段，还必须有分级 Gate、可判定条件、失败回退、profile 路径和运行时状态。

好的 Gate 机制应该做到：

- 低风险问题 L1 自动过。
- 中风险问题 L2 独立审。
- 高风险不可逆问题 L3 人审。
- Gate 失败知道回退到哪里。
- 连续失败能升级处理。
- 小需求有轻流程，但不失控。
- 状态能跨 session 恢复。

如果说 `stages.md` 是 Engine 的地图，那么 `gates.md`、`profiles.md` 和 `STATE.md` 就是红绿灯、导航路线和当前位置。没有它们，Agent 仍然会在流程里迷路；有了它们，AgentOS 才开始真正“受控运行”。
