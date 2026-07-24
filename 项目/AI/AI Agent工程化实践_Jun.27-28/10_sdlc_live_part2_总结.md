# 10_sdlc_live_part2.pdf 总结

> 文件名：`10_sdlc_live_part2.pdf`  
> 正文标题：Day 2 · 下午第二节 · SDLC 实弹(2) · 编码 -> 验证  
> 页数：8 页

## 一句话总结

这份 PDF 是 SDLC 实弹的下半场：在 G2 通过、方案已定之后，Agent 进入 BUILD 专注实现，不能偷偷改方向；随后通过 G3 自动化检查和 G4 主动破坏式验证，把“写完代码”推进到“证明它真的满足 AC、能扛住异常路径”。

## BUILD 阶段：方案已定，方向不变

BUILD 阶段的入口是：

```text
G2 通过
```

这意味着 EVALUATE 和 PLAN 已经完成：

- 需求已经理解。
- AC 已经定义。
- 技术方案已经审查。
- 不可逆决策已经记录。
- 方案已经允许进入实现。

因此 BUILD 阶段的核心原则是：

> 方案已定，方向不变，专注执行。

Agent 在 BUILD 中应该：

- 按 `plan.md` 写代码。
- 按 `plan.md` 写测试。
- 遵循 `TECH.md` 的技术约束。
- 实现所有 AC 映射。
- 如果发现方案有问题，回退 PLAN，而不是在 BUILD 中偷偷改变方向。

这点很重要。BUILD 不是重新设计阶段。

如果 Agent 在 BUILD 中说：

```text
我觉得改成异步更好。
我顺便加个缓存。
我发现接口可以换一种方式。
```

这些都属于方向性变化，应该回退 PLAN，而不是直接改。

## BUILD 阶段常见偏差

课程列出了 Agent 在 BUILD 中最容易犯的错误。

| 偏差 | 示例 | 处理 |
|---|---|---|
| 偏离方案 | “我觉得用异步更好” | 回退 PLAN |
| 过度工程 | 方案没有缓存，但 Agent 顺便加缓存 | 纠正，必要时回退 PLAN |
| 跳过测试 | “代码写完了，测试等下补” | 原地修复，违反完成度 principle |
| 忽略错误处理 | 只写 happy path，不写异常路径 | 原地修复 |
| 硬编码 | API key、超时时间写死 | Gate 阻断 |
| 不参考 DDD | 不读业务规则就开始写 | 记录 correction |

课程强调：

> 不要阻止所有偏差发生，让它发生，记录它，这是系统学习的素材。

当然，灾难性错误必须拦住，例如删库、泄露 secret、破坏生产数据。这类问题不能为了“收集 correction”而放任。

普通偏差的价值在于：

```text
纠正 -> correction
corrections 积累 -> 蒸馏原料
蒸馏 -> governance / gates 改进
```

## Gate G3：BUILD 出口检查

G3 的问题是：

> 代码是否合格，能不能进入 VERIFY？

G3 是 L1 自动化检查，适合脚本化。

判定条件包括：

- 代码文件存在。
- 测试存在且全部通过。
- lint 通过。
- 无硬编码 secrets。
- 实现覆盖 `plan.md` 中所有 AC 映射。

G3 的结果：

| 结果 | 动作 |
|---|---|
| PASS | 进入 VERIFY |
| FAIL：测试没写或没通过 | 原地修复 |
| FAIL：lint 不通过 | 原地修复 |
| FAIL：AC 覆盖不全 | 补充实现 |
| 同一问题 3 次修不好 | 回退 PLAN，方案可能有问题 |

课件指出，G3 大部分检查可以直接复用 Governance 的 gate 脚本，例如：

```text
governance/gates/check-lint.sh
governance/gates/check-secrets.sh
```

这说明 Governance Gates 和 Engine Gates 可以互相复用：

- Governance Gate 关注通用约束。
- Engine Gate 把这些约束放进阶段边界。

## VERIFY 阶段：主动破坏

VERIFY 阶段的核心原则是：

> 完成 = 我主动破坏它且失败了。

这和“检查它能跑”完全不同。

VERIFY 不是只跑 happy path，而是要尝试让系统挂掉。

示例 Verify Report：

```markdown
# Verify Report: recognize 功能

## AC 验证
- [x] AC1: 5 秒内返回 -> 通过（均 2.3s）
- [x] AC2: confidence 字段存在 -> schema 过
- [ ] AC3: 低 confidence 标记待确认 -> 未实现

## 破坏尝试
- 空图片 -> 正确返回 400
- 超大图片 -> 内存溢出，未处理
- 非图片文件 -> 正确返回 400
- Bedrock 超时 -> 无超时处理，永远挂起

## 判定
FAIL — 2 个 AC 未满足 + 2 个边界未处理
```

VERIFY 应该覆盖两类测试。

### 边界测试

- 空图片。
- 超大图片，例如 10MB+。
- 非图片文件，例如 `.txt` 改成 `.jpg`。
- 模糊图片。
- 倾斜图片。
- 手写图片。
- 同时上传多张。

### 异常路径测试

- Bedrock 超时。
- Bedrock 返回异常格式。
- 网络断开。
- 服务不可用。
- 第三方 API 限流。
- 解析失败。

这份报告就是 G4 的判定依据。

## Gate G4：VERIFY -> Done

G4 的问题是：

> 能否宣布任务完成？

G4 的判定条件：

- `verify.md` artifact 存在。
- 所有 AC 都标记 pass。
- 破坏尝试记录存在，至少 5 种。
- 没有 fail 项。

如果 G4 不通过，就回退 BUILD：

```text
BUILD -> VERIFY -> FAIL
  -> 回退 BUILD
BUILD -> VERIFY -> FAIL
  -> 回退 BUILD
BUILD -> VERIFY -> PASS
```

课程强调：

> 第一次 FAIL 不等于失败，是系统在工作。

这句话非常重要。Gate fail 不是坏事，它说明问题在交付前被发现，而不是在用户那里被发现。

通常 2-3 次循环可以通过。如果超过 3 次，问题可能在 PLAN 层面，需要回退方案，而不是继续局部修补。

完成后的 `STATE.md` 可能是：

```markdown
# STATE.md

任务: recognize 函数开发
Profile: feature
当前阶段: DONE ✅
已通过 Gates:
- G1 ✅
- G2 ✅
- G3 ✅
- G4 ✅
循环次数:
- G3: 1 次
- G4: 2 次
完成时间: 2024-01-15 16:45
```

这里记录循环次数很有价值，因为它能反映 Engine 哪个环节最容易出问题。

## Day 2 的完整产出

跑完一天后，Engine 运行会产出：

- `spec/recognize/evaluate.md`：需求确认。
- `spec/recognize/plan.md`：技术方案 + ADR。
- 代码实现。
- 测试。
- `spec/recognize/verify.md`：验证报告。

Knowledge 也会被填充：

- `TECH.md` 新增 1-2 条 ADR。
- `corrections.log` 大幅增长，可能增加 10-20 条。
- 两天积累足够做真正蒸馏。

Engine 自身也产生反馈：

| 观察 | 含义 |
|---|---|
| 哪个 Gate 最容易 fail | 那个环节 Agent 偏差最大 |
| 有没有 Gate 从不 fail | 可能不需要它，或条件太弱 |
| 循环次数多少 | 越少说明 Agent 越准 |
| 是否经常从 G3/G4 回退 PLAN | 说明方案阶段不够强 |

这说明 Engine 不只是执行流程，它本身也会被运行数据校准。

## Mini 蒸馏练习

Day 2 结束前，课程安排了 15 分钟 mini 蒸馏。

操作：

1. 打开 `corrections.log`。
2. 按类型分组。
3. 问自己：
   - Principles 覆盖了哪些 corrections？
   - 有没有新 pattern？
   - 有没有 rule 该退休？
   - 有没有 rule 应该升级为 gate？
4. 如果发现必要，就更新 Governance。

常见分组：

| 分组 | 典型条目 |
|---|---|
| 完成度类 | 跳过测试、验证太浅、说 done 太早 |
| 方案类 | 遗漏边界、不考虑异常 |
| 引用类 | 不读 DDD、不参考 plan |
| 格式类 | artifact 不完整 |

可能的蒸馏结果：

- 新增 Principle：关于“必须参考 DDD”。
- 退休 Rule：G3 lint 已机械覆盖“代码格式”类 rule。
- 精炼 Principle：让“完成度”措辞更精确。

这只是 preview，真正的蒸馏会在 Day 3 做。

## 对测试机制的启发

这份 PDF 对我们前面讨论的“测试过程怎么纳入 AgentOS”非常关键。

### 1. 测试不是 BUILD 的附属，而是 Gate 条件

测试不能是：

```text
代码写完了，有空再补。
```

在 AgentOS 里，测试是 G3 的出口条件：

```text
没有测试 / 测试不过 -> 不能进入 VERIFY
```

因此测试不是建议，而是阶段边界。

### 2. VERIFY 不是跑测试，而是主动破坏

自动化测试通过，只说明已知用例没失败。

VERIFY 要求 Agent 主动寻找失败方式：

- 边界输入。
- 异常路径。
- 第三方故障。
- 性能超时。
- 数据不一致。
- 并发场景。

所以 `verify.md` 应该不是一行“tests pass”，而是包含：

- AC 验证矩阵。
- 破坏尝试列表。
- 失败项。
- 修复循环。
- 最终结论。

### 3. 测试不足也要进入 corrections.log

如果 Agent：

- 没写测试。
- 只写 happy path。
- 没测异常。
- 没测边界。
- 测试没有断言关键业务规则。

这些都应该记录为 correction，后续可能蒸馏成：

- Principle。
- Rule。
- Gate。
- Test template。

这和美团文章强调测试的重要性非常一致：测试不是结果检查，而是 Agent 质量控制的核心机制。

## 对 AgentOS 机制设计的启发

### 1. BUILD 阶段必须禁止偷偷改方向

AgentOS 应明确规定：

```text
BUILD 中发现方案问题 -> 回退 PLAN
BUILD 中不得擅自改变架构、接口、核心策略
```

否则 PLAN 和 G2 就失去意义。

### 2. G3 要尽量脚本化

G3 是最适合自动化的 Gate，应该接入：

- 单元测试。
- lint。
- typecheck。
- secret scan。
- schema check。
- migration check。
- coverage check。

AgentOS 初始化时应该为不同语言/框架提供 G3 模板。

### 3. G4 要产出 verify artifact

`verify.md` 是“完成”的证据。

建议结构：

```markdown
# Verify Report

## AC 验证矩阵
| AC | 验证方式 | 结果 | 证据 |

## 自动化测试
| 命令 | 结果 | 备注 |

## 破坏尝试
| 场景 | 预期 | 实际 | 结果 |

## 未覆盖风险

## 最终判定
PASS / FAIL
```

没有 `verify.md`，就不能 Done。

### 4. Gate 循环次数是健康指标

AgentOS 可以记录：

- G3 fail 次数。
- G4 fail 次数。
- 是否多次回退 PLAN。
- 哪类 correction 最多。

这些指标可以反映：

- PLAN 是否太弱。
- BUILD 是否偏离方案。
- VERIFY 是否设计不足。
- Gate 是否过重或过轻。

### 5. 小需求也要有最小 VERIFY

即使是 `bugfix` 或 `hotfix` profile，也不应该完全跳过 VERIFY。

可以降低要求：

- 少量 AC。
- 最小回归测试。
- 一两个破坏尝试。
- 事后补 review。

但不能没有验证证据。

## 对 payment-agent 的落地建议

如果用于支付项目，BUILD 和 VERIFY 的要求应该更强。

### BUILD 阶段关注

- 不得擅自改变支付状态机。
- 不得绕过幂等策略。
- 不得改变金额计算方式，除非 PLAN 已明确。
- 不得硬编码渠道参数、secret、超时。
- 不得只实现 happy path。
- 必须补充失败路径测试。

### G3 自动化检查

建议包含：

- 单元测试。
- 集成测试。
- lint / typecheck。
- secret scan。
- 金额精度检查。
- migration 与实体一致性检查。
- OpenAPI / DTO schema 检查。
- 幂等相关测试。

### VERIFY 破坏尝试

支付场景的 VERIFY 应覆盖：

- 重复请求。
- 渠道超时。
- 渠道返回未知状态。
- 网络中断。
- 金额精度边界。
- 并发支付 / 重试。
- 回调乱序。
- 对账不一致。
- 退款和支付状态冲突。

如果这些场景没有验证，就不应该进入 Done。

## 和前一份 PDF 的关系

`09_sdlc_live_part1.pdf` 跑的是：

```text
EVALUATE -> PLAN
```

本 PDF 跑的是：

```text
BUILD -> VERIFY
```

合在一起，就是完整 feature 流程：

```text
EVALUATE -> PLAN -> BUILD -> VERIFY
```

前半场把方向和方案显性化，后半场把实现和验证显性化。

## 最终结论

这份 PDF 的核心结论是：

> 写完代码不是完成；通过自动化检查也不是完成；完成是所有 AC 被验证，并且主动破坏尝试失败。

BUILD 阶段让 Agent 按方案实现，G3 防止低级质量问题进入验证，VERIFY 阶段主动寻找失败路径，G4 决定是否真的 Done。

这让 AgentOS 的交付标准从“代码生成”升级为“证据驱动的完成”。
