# 11_verification_eval.pdf 总结

> 文件名：`11_verification_eval.pdf`  
> 正文标题：Day 3 上午 · 验证工程 + Eval  
> 页数：7 页

## 一句话总结

这份 PDF 把“验证”从代码层面扩展到系统层面：除了验证错题本识别功能是否正确，还要验证 AgentOS 自身是否按团队标准运行。前者是业务验证，后者是行为 Eval，也就是 AgentOS 的“单元测试”。

## 两种验证：业务对不对，系统有没有按标准工作

课程把验证分成两类。

| 类型 | 验证对象 | 核心问题 | 出错后改什么 | 频率 |
|---|---|---|---|---|
| 业务验证 | 错题本代码 | 识别功能工作吗 | 代码 bug -> 改代码 | 每次 BUILD / VERIFY |
| 系统验证 Eval | AgentOS 行为 | Agent 按我的标准工作吗 | 行为偏差 -> 改 governance / engine | 每周 / 每次蒸馏后 |

这一区分非常关键。很多团队只验证代码，但不验证 Agent 的行为过程。

AgentOS 的目标不是只让一次功能可用，而是让 Agent 长期按照团队定义的工作方式运行。因此，AgentOS 自身也需要测试。

## 业务验证：AI 输出不确定，但仍然可以分层验证

课件指出，AI 输出不是完全确定的。同一张图片两次调用，识别文本可能不同，所以不能简单用 exact match 判断对错。

但这不意味着无法验证。

应该采用分层验证：

| 策略 | 适用场景 | 做法 | 类型 |
|---|---|---|---|
| Schema 验证 | 输出格式 | JSON schema 必须正确 | 确定性 |
| 关键字段验证 | 核心字段 | `confidence` 存在且在 `[0,1]` | 确定性 |
| 相似度验证 | 内容质量 | 识别文本与标注相似度 >= 80% | 阈值型 |
| 人工抽检 | 边界 case | 10% 随机样本人工确认 | 概率型 |

核心理念是：

> 能确定性验证的部分，先做确定性验证。

不要因为 AI 输出不稳定，就放弃所有验证。你能验证的通常比想象中多。

## ci/verify.sh：业务验证脚本

课程示例里用 `ci/verify.sh` 做基础业务验证。

它至少检查：

- 输出是合法 JSON。
- 包含 `confidence`。
- `confidence` 在 `[0,1]`。
- 包含 `question_text`。
- schema 结构正确。

这类验证不要求识别文本完全一致，但能保证输出契约不崩。

对 AgentOS 来说，`ci/verify.sh` 是业务验证入口，和 Engine 的 G3/G4 可以联动：

```text
BUILD -> G3: 测试/lint/schema 通过
VERIFY -> G4: AC + 破坏尝试 + 验证报告通过
```

## Eval：AgentOS 的行为契约

Eval 验证的不是代码输出，而是 Agent 是否遵守了预期行为。

课程提出：

> Behavioral Contract = AgentOS 的单元测试。

示例 `eval/golden-set.md`：

```markdown
# Behavioral Contract

## 完成度行为
IF agent 声称完成一个功能
THEN verify artifact 必须存在
AND >= 5 种破坏尝试有记录
AND 所有 AC 有 pass/fail 标记

## Engine 遵循
IF 任务类型是 feature
THEN 经过 EVALUATE -> PLAN -> BUILD -> VERIFY
AND STATE.md 记录全部 gate 通过

## 蒸馏方向
IF corrections.log 有 3+ 条同类
THEN governance/ 有对应 rule/principle
```

这里的 IF-THEN 断言就是 AgentOS 的 Golden Set。

它回答的问题是：

> 我的系统是否在按我的标准运行？

## 代码测试 vs 行为测试

| 类型 | 测什么 | 示例 |
|---|---|---|
| 代码测试 | 输入 X -> 输出 Y 是否匹配 | 图片输入后是否返回合法 JSON |
| 行为测试 | 过程是否遵循预期行为 | 是否先 EVALUATE，再 PLAN，再 BUILD，再 VERIFY |

行为测试是 AgentOS 的关键补充。

因为 Agent 可能最终写出了可运行代码，但过程完全不受控：

- 没有需求确认。
- 没有 plan。
- 没有 verify artifact。
- 没有破坏尝试。
- 没有更新 STATE。
- 没有写回 corrections。

这类问题靠业务测试发现不了，只能靠行为 Eval。

## run-eval.sh：把行为契约变成可执行检查

课程建议创建：

```text
eval/run-eval.sh
```

它检查几类行为：

| 检查 | 示例 |
|---|---|
| 完成度行为 | `verify.md` 是否有至少 5 个破坏尝试 |
| Engine 遵循 | `STATE.md` 是否记录所有 gate 通过 |
| Governance 覆盖 | principles 是否足够，corrections 是否有对应治理 |
| 蒸馏健康 | active rules 是否 <= 15，是否有退休记录 |

脚本输出一个分数。

课件强调：

> 100% 不是目标，知道哪里不达标才是目标。

第一次跑 60-70% 很正常。低分维度就是 AgentOS 下一步的改进方向。

## 漂移检测：Agent 行为会退化

Agent 今天遵守 principles，不代表下个月还遵守。

漂移的原因包括：

- Context 变大，principles 被稀释。
- 新功能增加，rules 变多并互相冲突。
- corrections 积累但没有蒸馏。
- 文档变旧。
- Gate 降级太早。

漂移信号包括：

| 信号 | 说明 |
|---|---|
| 同类 correction 30 天内重复 3 次以上 | principle 不够锋利 |
| Gate 触发频率上升 | rules 被忽略或 context 膨胀 |
| Eval score 下降 | 系统行为退化 |
| Agent 开始忽略某些 rules | rule 可能需要改写或升级 gate |

对应响应：

| 漂移信号 | 响应 |
|---|---|
| 同类 correction 重复 | 做蒸馏，强化 principle |
| Gate 触发上升 | 检查 rules 是否被忽略，context 是否膨胀 |
| Eval score 下降 | 做全面 health check |
| Rule 被忽略 | 升级为 Gate，或改写为更可判定 |

建议每周跑一次 `run-eval.sh`，score 下降就做一轮蒸馏。

## Lab 要求

本节 Lab 要创建三个东西。

### 1. `eval/golden-set.md`

写 5-8 条 behavioral contract，覆盖：

- 完成度。
- Engine 遵循。
- Principles 效果。
- 蒸馏方向。

### 2. `eval/run-eval.sh`

至少实现 3 个自动化检查，可以从基础版开始。

### 3. `ci/verify.sh`

实现业务验证，至少覆盖：

- schema。
- 关键字段。
- `confidence` 范围。

然后运行一次 eval，记录当前得分。

## 对 AgentOS 机制设计的启发

### 1. 验证对象要从“代码”扩展到“Agent 行为”

只跑测试不足以说明 AgentOS 健康。

还要问：

- Agent 是否按 Engine 阶段走？
- 是否产出 artifact？
- 是否运行 Gate？
- 是否做 verify report？
- 是否记录破坏尝试？
- 是否写回 corrections？
- 是否触发蒸馏？

这些都应该进入 Eval。

### 2. Review/Test 的产物可以成为 Eval 输入

高阶模型 review、测试报告、verify artifact、STATE 都不只是一次性结果，它们可以被 `run-eval.sh` 检查。

例如：

- review 存在但 blocking findings 未处理 -> Eval fail。
- verify 没有破坏尝试 -> Eval fail。
- STATE 没有 G2 记录 -> Eval fail。
- corrections 有 3 条同类但 governance 没更新 -> Eval fail。

### 3. Eval 是 AgentOS 的回归测试

每次改 governance、engine、profile、gate 之后，都应该跑 Eval。

否则很可能出现：

- rules 变短了，但覆盖下降。
- gate 降级了，但 correction 上升。
- profile 变快了，但跳过了关键验证。

Eval 的作用就是防止 AgentOS 自身演化时退化。

## 对 payment-agent 的落地建议

支付项目的 Eval 应该更重视行为过程。

建议 golden set 包含：

- IF 涉及金额计算 THEN 必须有金额精度测试。
- IF 涉及状态流转 THEN 必须有状态机合法边说明。
- IF 涉及外部支付渠道 THEN 必须有超时、重试、幂等验证。
- IF 任务类型是 payment-critical THEN 必须经过 PLAN、L2 review、VERIFY。
- IF Agent 声称完成 THEN 必须有失败路径测试和审计字段检查。
- IF corrections 中出现 3 次同类支付风险 THEN governance 必须更新。

这类行为契约比单纯业务测试更能保护高风险项目。

## 最终结论

这份 PDF 的核心结论是：

> 验证不只是验证代码对不对，还要验证 AgentOS 是否按你的标准运行。

业务验证保证功能输出可信，行为 Eval 保证 Agent 的过程可信。

成熟的 AgentOS 应该同时有：

```text
ci/verify.sh        # 验证业务功能
eval/golden-set.md  # 定义行为契约
eval/run-eval.sh    # 自动检查 AgentOS 行为
漂移检测            # 定期发现系统退化
```

这样 AgentOS 才不是一套静态流程，而是一个能被测试、能被回归、能被持续校准的系统。
