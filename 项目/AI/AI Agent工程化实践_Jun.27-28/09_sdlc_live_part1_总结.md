# 09_sdlc_live_part1.pdf 总结

> 文件名：`09_sdlc_live_part1.pdf`  
> 正文标题：Day 2 · 下午第一节 · SDLC 实弹(1) · EVALUATE -> PLAN  
> 页数：8 页

## 一句话总结

这份 PDF 是 Delivery Engine 的第一次实战运行：用“拍照识别”功能作为统一任务，启动 Engine，跑完 `EVALUATE -> PLAN` 两个阶段，并通过 G1、G2 Gate 验证需求理解和技术方案，让 Engine 产出的 artifact 自然反哺 Knowledge。

## 核心目标：让 Engine 跑起来

前面两份 PDF 已经完成了 Engine 设计：

- `stages.md` 定义阶段。
- `gates.md` 定义门禁。
- `profiles.md` 定义任务路径。
- `STATE.md` 记录运行位置。

本节开始进入实弹：

```text
EVALUATE -> PLAN -> BUILD -> VERIFY
```

上半场只跑前两步：

```text
EVALUATE -> PLAN
```

实验任务是：

> 为错题本开发“拍照识别”功能：用户拍照，上传图片，调用 Bedrock 识别，返回结构化 JSON。

任务覆盖：

- API 设计。
- 识别逻辑。
- 错误处理。
- 置信度判定。
- 结构化输出。

这个任务足够复杂，能触发需求理解、技术方案、不可逆决策和风险识别。

## Engine 需要显式触发

课件强调一个重要事实：

> Engine 文件存在磁盘上，Agent 不会自动读。

这和 Knowledge 一样。仅仅创建 `engine/stages.md`、`engine/gates.md` 不够，还需要一个明确触发入口。

推荐方式是创建：

```text
engine/SKILL.md
```

触发方式可以是：

```text
开始任务
run engine
任务下发时
```

`engine/SKILL.md` 的执行流程大致是：

```text
1. 读取 engine/STATE.md，确定当前位置
2. 如果是新任务：
   - 确定 profile
   - 初始化 STATE.md
   - 进入第一阶段
3. 如果是续做：
   - 读取 STATE.md
   - 继续当前阶段
4. 每个阶段结束：
   - 产出 artifact
   - 读取 gates.md
   - 跑出口 gate
   - 通过则更新 STATE，进入下一阶段
   - 失败则原地修复或回退
```

课程提到两种注入方式：

| 方式 | 作用 | 评价 |
|---|---|---|
| SessionStart hook | 注入 `STATE.md` 和当前阶段指引 | 可用 |
| Engine `SKILL.md` | 作为明确触发入口 | 推荐 |

为什么要有触发入口？

因为 Agent 即使看到了文件，也可能觉得“我知道该怎么做”，然后跳过流程。Engine 必须被显式启动。

## EVALUATE 阶段：在跑错方向前停下来

EVALUATE 的目标是：

> 确保 Agent 真的理解需求，而不是凭感觉直接设计和编码。

操作步骤：

1. 开新 session，验证 Knowledge 已注入。
2. 告诉 Agent：用 `feature` profile 跑 Engine。
3. 下发任务：为错题本开发拍照识别功能。
4. 观察 Agent 是否进入 EVALUATE。

课件设计了一个很好的教学动作：

> 在 Agent 输出 AC 之前，人先用 30 秒写 3 条 AC。

然后对比：

- 你写的和 Agent 写的有什么不同？
- 谁的 AC 更可判定？
- 差异说明了什么判断偏差？

这一步的价值是让“人类判断”和“Agent 判断”显性化。

## EVALUATE 阶段 Agent 应该做什么

Agent 在 EVALUATE 阶段应该：

- 阅读 `PRODUCT.md` 理解业务。
- 澄清模糊点。
- 输出 `evaluate.md` artifact。
- 写清楚 What / Why / Acceptance Criteria / Risks / Irreversible Decisions。

观察点包括：

| 观察点 | 判断意义 |
|---|---|
| 是否真的读了 DDD | 防止凭空编需求 |
| AC 是否可判定 | “体验好”不算可判定 |
| 是否识别不可逆决策 | 为后续 PLAN 和 ADR 做准备 |
| 是否跳过 EVALUATE 直接写代码 | 说明 Engine 触发不够强 |

如果 Agent 直接写代码，需要提醒：

```text
请按 Engine 流程走，先完成 EVALUATE。
```

这不是失败，而是正好暴露 Engine 要解决的问题。

## Gate G1：EVALUATE -> PLAN

G1 检查 EVALUATE 的产出物是否合格。

检查清单：

- artifact 文件存在。
- AC 数量不少于 3。
- 每条 AC 可判定。
- 不可逆决策已声明。

G1 可能通过，也可能失败。

常见失败原因：

- AC 太模糊。
- AC 数量不足。
- artifact 段落缺失。
- 没有声明不可逆决策。

失败处理：

```text
纠正 -> 原地修复 -> 再检查
```

G1 的价值是：

| 没有 G1 | 有 G1 |
|---|---|
| Agent 模糊地说“理解了需求”就开始设计 | 必须输出可检查 artifact |
| 需求理解留在模型上下文里 | 需求理解被显性化 |
| 人很晚才发现方向偏差 | 早期就能纠正 |

如果全班都一次通过，说明前面的 Principles 生效了；如果有人不通过，也很好，因为 correction 正是系统进化的原料。

## PLAN 阶段：在不可逆决策前停下来

PLAN 的目标是：

> 在真正编码前，把技术方案、接口、风险和不可逆决策想清楚。

Agent 在 PLAN 阶段应该：

- 阅读 `TECH.md` 了解技术约束。
- 为每个 AC 设计实现方案。
- 做不可逆决策，并记录 ADR。
- 设计 API schema。
- 识别风险和缓解方案。

关键观察点：

| 观察点 | 判断意义 |
|---|---|
| 是否参考 `TECH.md` 中的 ADR | 防止推翻已有架构决策 |
| 不可逆决策是否完整 | 要有理由、代价、回退 |
| 每个 AC 是否映射到实现 | 防止方案漏覆盖需求 |
| 风险是否有缓解方案 | 防止只列风险不处理 |

示例 Plan 内容：

```markdown
# Plan: 拍照识别功能

## 技术方案
- API: POST /api/recognize
- 输入: multipart/form-data (image)
- 输出: JSON { question_text, confidence, knowledge_points[] }

## 不可逆决策（ADR）
- [ADR-003] 同步调用 Bedrock
  - 理由: MVP 简单优先，<5s 满足 AC
  - 代价: 并发高时可能超时
  - 回退: P99 > 5s -> 重构为异步

## 风险
- Bedrock 冷启动首调超时
- 图片模糊 / 倾斜导致识别失败

## 每个 AC 的实现映射
- AC1 5s 内返回 -> 同步 + 超时配置
- AC3 低 confidence 标待确认 -> 后处理
```

这一步开始把 Engine 和 Knowledge 连接起来：PLAN 中的新 ADR 应该回写到 `TECH.md`。

## Gate G2：PLAN -> BUILD

G2 是 L2 Gate，用来审查方案是否可以进入 BUILD。

它需要独立视角，原因是：

- 方案合理性不能由产出者自己说了算。
- 自己审自己的方案容易有确认偏差。
- 方案错了，后面 BUILD 和 VERIFY 都会浪费。

G2 的审查角色是 `devil's advocate`。

审查目标：

```text
1. 找出致命缺陷：无法交付或需要重写
2. 找出重大遗漏：AC 没有被覆盖
3. 找出风险低估：没有可行缓解方案
```

判定方式：

| 结果 | 动作 |
|---|---|
| PASS | 进入 BUILD |
| FAIL | 回退 PLAN，修正方案 |

G2 可以用两种方式执行：

| 方式 | 说明 |
|---|---|
| session 内调用 | 用一段 prompt 让 Agent 切换为 `devil's advocate` 审查 |
| 人工审查 | 人自己花 2 分钟看遗漏、AC 覆盖、风险是否可控 |

如果 G2 抓住了遗漏，修正后继续。这说明 G2 有价值。

如果 G2 没抓住，问题拖到 BUILD 或 VERIFY 才暴露，说明 G2 太弱，下次要加强。

这类数据本身也应该记录，因为它是 Engine 进化的依据。

## 前半段产出物

跑完 EVALUATE 和 PLAN 后，目录大致会变成：

```text
my-agentos/
├── engine/
│   └── STATE.md
│       当前: BUILD, G1 ✅, G2 ✅
├── spec/
│   └── recognize/
│       ├── evaluate.md
│       └── plan.md
├── knowledge/
│   └── TECH.md
└── corrections.log
```

关键变化：

- `evaluate.md` 是 EVALUATE 产出物。
- `plan.md` 是 PLAN 产出物，可能包含新 ADR。
- `TECH.md` 可能被更新。
- `corrections.log` 新增若干 correction。
- `STATE.md` 更新为当前阶段 BUILD。

这就是课程说的飞轮：

```text
Engine 运行 -> 产出 artifact -> 更新 Knowledge -> 产生 corrections -> 后续蒸馏
```

Knowledge 不是靠人手动维护，而是 Engine 跑起来后自然生成副产品。

## 快速复盘：不同阶段产生不同 correction

本节最后要求快速复盘：

> 你纠正了什么？

典型 corrections 包括：

| 类型 | 示例 |
|---|---|
| 方案遗漏类 | 没考虑某个边界情况 |
| 格式类 | artifact 不完整 |
| 引用类 | 没参考 DDD 文档 |
| 深度类 | AC 写得太模糊 |

课件强调一个重要观察：

```text
Day 1 代码层面 correction 较多
Day 2 设计层面 correction 开始出现
```

这说明 Engine 的阶段划分是有意义的。

不同阶段会暴露不同类型的问题：

- EVALUATE 暴露需求理解问题。
- PLAN 暴露方案设计问题。
- BUILD 暴露实现问题。
- VERIFY 暴露验证不足问题。

如果没有阶段，这些问题会混在最后一大坨代码里，很难定位根因。

## 对 AgentOS 机制设计的启发

### 1. Engine 必须有触发入口，不能只靠文档存在

我们的 AgentOS 初始化脚本不能只创建 `engine/`，还要提供明确入口：

- `engine/SKILL.md`
- Claude Code command。
- Codex 指令片段。
- SessionStart 注入当前 state。
- 任务启动模板。

否则 Agent 很可能看不到或绕过 Engine。

### 2. Artifact 是阶段完成的唯一证据

Agent 说“我理解了”“方案没问题”都不算。

必须有：

```text
spec/{task-id}/evaluate.md
spec/{task-id}/plan.md
```

并且 Gate 检查这些文件。

这对团队协作尤其重要：另一个模型、另一个人、下一次 session 都可以接着 artifact 继续，而不是依赖上一轮对话记忆。

### 3. G2 是高阶模型 review 的天然位置

如果要用更高阶模型做 review，不一定只放在代码写完后。

更高价值的位置之一是：

```text
PLAN -> BUILD
```

因为方案问题越早发现越便宜。

高阶模型可以审：

- AC 是否完整覆盖。
- 风险是否低估。
- 不可逆决策是否合理。
- 是否违背 `TECH.md` / ADR。
- 是否遗漏安全、性能、成本、兼容性。

### 4. Knowledge 更新应该是 Engine 的副产品

当 PLAN 产生新的 ADR，不应该只留在 `plan.md`。

应该有规则：

```text
如果 PLAN 中产生新 ADR -> 更新 knowledge/TECH.md
如果人纠正了方案遗漏 -> 写入 corrections.log
如果发现新业务事实 -> 更新 PRODUCT.md 或 PROJECT.md
```

这样 Knowledge 才会随 Engine 运行自然增长。

### 5. Corrections 应带阶段标签

这份 PDF 暗示了一个很好的增强点：

> 不同阶段产生不同 correction。

因此 `corrections.log` 最好记录 stage，例如：

```text
CORRECTION [PLAN]: 方案未覆盖低 confidence 待确认流程
CORRECTION [EVALUATE]: AC 写成“体验好”，不可判定
```

这样 Day 3 蒸馏时可以按阶段聚类：

- EVALUATE 类错误：需求理解和 AC。
- PLAN 类错误：方案遗漏和风险。
- BUILD 类错误：实现质量。
- VERIFY 类错误：测试与验收。

## 对 payment-agent 的落地建议

如果在 `payment-agent-ai` 中跑类似流程，建议选择一个真实但受控的任务，例如：

```text
为支付请求增加风险识别结果字段：
返回 decision、reason、confidence、traceId，并保证低 confidence 不默认放行。
```

EVALUATE 阶段重点检查：

- AC 是否包含金额精度、幂等、错误处理、审计字段。
- 是否识别外部接口、数据库、状态机的不可逆边界。
- 是否明确“不确定不放行”的验收标准。

PLAN 阶段重点检查：

- 是否参考已有支付状态机 ADR。
- 是否说明接口 schema。
- 是否有数据库 / DTO / OpenAPI 同步策略。
- 是否覆盖重试、幂等、超时、降级。
- 是否说明风险和回退。

G2 应该至少是 L2；涉及资金状态变化时应该升级 L3。

## 和前几份 PDF 的关系

| PDF | 主题 | 本 PDF 的作用 |
|---|---|---|
| `07_engine_design.pdf` | 阶段设计 | 定义 EVALUATE / PLAN / BUILD / VERIFY |
| `08_engine_gates.pdf` | Gate 设计 | 定义 G1 / G2 等阶段边界 |
| `09_sdlc_live_part1.pdf` | SDLC 实弹上半场 | 实际跑 EVALUATE -> PLAN，并产出 artifact |

这份 PDF 是从“设计 Engine”走向“运行 Engine”的关键一步。

## 最终结论

这份 PDF 的核心结论是：

> Engine 只有在真实任务中被显式触发、产出 artifact、通过 Gate、更新 STATE、反哺 Knowledge，才算真正跑起来。

`EVALUATE -> PLAN` 的价值在于把最容易被 Agent 跳过的两个前置判断显性化：

- 需求是否真的理解。
- 方案是否真的合理。

如果这两步做扎实，后面的 BUILD 和 VERIFY 成本会显著下降；如果这两步跳过，Agent 只会更快地把错误方向写成代码。
