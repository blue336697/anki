# 11b_distillation_workshop.pdf 总结

> 文件名：`11b_distillation_workshop.pdf`  
> 正文标题：Day 3 上午 · 蒸馏工坊  
> 页数：6 页

## 一句话总结

这份 PDF 是蒸馏实操课：当 `corrections.log` 已经积累 20+ 条后，不应该继续加规则，而要通过“上提、下沉、毕业”三招，把零散 corrections 压缩成更少、更强、更可执行的 governance。

## 核心问题：corrections.log 有很多条之后怎么办

两天实战后，`corrections.log` 里可能已经有很多内容：

- 没加 `confidence` 字段。
- 不处理图片太大。
- 跳过 EVALUATE。
- AC 写成“体验好”。
- 没参考 `TECH.md`。
- 只测 happy path。

这些都是原料，不是最终产物。

蒸馏的目标是：

```text
corrections 很多条
  -> 找 pattern
  -> 压缩成少量 principles / rules / gates
  -> governance 行数变少
  -> 覆盖范围变广
```

课程强调：

> 行数变少，覆盖变广。

这才是蒸馏成功的标志。

## 蒸馏三招

课程把蒸馏压缩成三个动作：

```text
上提 -> 下沉 -> 毕业
```

没有第四招。

## 第一招：上提，Rules -> Principle

触发信号：

> 3 条以上 rules 或 corrections 追溯到同一个根因。

动作：

- 写一条覆盖整类问题的 principle。
- 把被吸收的 rules 退休到 `_retired/`。
- 保留证据，不直接删除。

验证：

- 新 principle 能不能覆盖未来同类问题？
- rules 数量是否减少？
- eval coverage 是否不下降？

例子：

```text
没写测试
只测 happy path
说 done 太早
验证太浅
```

这些可以上提为：

```text
完成 = 主动尝试破坏且失败。
```

## 第二招：下沉，Rule -> Gate 后退休

触发信号：

> 某条 rule 被违反 3 次以上，而且每次形式相同。

动作：

- 把 prose rule 做成代码级 gate。
- Gate 上线后，退休原来的文本 rule。

验证：

- Gate 存在后，这条 rule 是否还需要保留？
- 这个问题是否能被机械阻断？

例子：

```text
Rule: 不允许硬编码 secret
```

如果反复违反，就应该下沉为：

```text
governance/gates/check-secrets.sh
```

下沉不是“多加一个 gate 再保留 rule”，而是用 gate 替代文本 rule。

## 第三招：毕业，Gate 不再触发 -> 移除

触发信号：

> Gate 连续 30 天或 10 次运行未触发。

动作：

- 移入 `_graduated/`。
- 保留证据，不直接删除。

验证：

- 上游 principles / rules 是否已经足够强？
- 移除 gate 后 eval coverage 是否不下降？
- correction 是否没有反弹？

Gate 毕业说明系统变轻了。它不是风险，而是治理成熟的结果。

## 蒸馏第一步：找 pattern

课件强调，蒸馏第一步不是写 principle，而是看 corrections、打标签、找 cluster。

示例：

| correction | 标签 |
|---|---|
| 没加 confidence 字段 | 格式遗漏 |
| 不处理图片太大 | 深度不足 |
| 跳过 EVALUATE 写代码 | 流程跳步 |
| AC 写成“体验好” | 深度不足 |
| 没参考 TECH.md 的 ADR | 引用缺失 |
| 错误响应没 error_code | 格式遗漏 |
| 没考虑 Bedrock 限流 | 深度不足 |
| 测试只测 happy path | 深度不足 |

分组结果：

```text
格式遗漏: 2
流程跳步: 1
引用缺失: 1
深度不足: 4
```

`深度不足` 达到 3 条以上，就是蒸馏候选。

## 找 pattern 的方法

步骤：

1. 给每条 correction 打标签。
2. 按标签分组。
3. 粗粒度数数。
4. 找 >= 3 条的 cluster。
5. 写一句话根因。

这里不需要模型抢着做判断，因为核心问题是：

> 表面不同的 correction 背后，是不是同一个根因？

这是人的判断位置。

AI 可以辅助整理，但根因归类和是否合并需要人审批。

## Lab：25 分钟让 governance 变短

Lab 分三步。

### Step 1：Pattern 识别，8 分钟

- 打开 `corrections.log`。
- 打标签分组。
- 找 >= 3 条 cluster。
- 写一句话根因。

### Step 2：执行蒸馏，12 分钟

- cluster + rules 存在 -> 上提。
- rule 反复违反 -> 下沉为 gate。
- gate 从未触发 -> 标记毕业。

### Step 3：验证，5 分钟

检查：

- 行数是否减少。
- eval coverage 是否不下降。
- 退休是否有 `_retired/` 记录。

课件建议比较蒸馏前后行数：

```bash
wc -l governance/principles.md governance/rules/*.md | tail -1
```

蒸馏后应该更短。

## 判断辅助

课程给了几个很实用的判断。

| 情况 | 建议 |
|---|---|
| 找不到 cluster | corrections 还不够，继续积累 |
| principle 已存在仍违反 | 改措辞更锋利，不急着加 rule |
| 不确定能否合并 | 保守处理，先不合并 |
| corrections 少于 5 条 | 用参考 corrections 集练习动作 |
| 蒸馏后 eval score 降了 | 过度合并，回退 |

这说明蒸馏不是越激进越好。目标是变短，但不能牺牲覆盖。

## 首次蒸馏的典型结果

课件给出的首次蒸馏预期：

| 指标 | 典型结果 |
|---|---|
| governance 总行数 | 减少 10-30% |
| 退休 rules | 2-4 条进入 `_retired/` |
| principles | 5 条变 4 条，或 3 条更强，或不变但措辞更精准 |
| eval coverage score | 不下降 |

如果有人觉得“每条 correction 都不一样，合并不了”，通常是标签粒度太细。

如果 principle 已经覆盖但 Agent 还犯，可能是：

- Principle 措辞不可判定，需要改硬。
- 这个问题需要 gate 兜底。

如果蒸馏后 eval score 降了，说明合并过度，需要回退。

## 蒸馏不是加规则

课件里最重要的一句话是：

> 加了 principle 但旧 rules 还在 = 积累，不是蒸馏。

真正蒸馏应该是：

```text
加一条更强的上层表达
  -> 退休多条下层规则
  -> coverage 不下降
```

如果只是不断加，系统会越来越长，Agent 会越来越不读。

## 节奏建议

课后建议节奏：

```text
每 10-15 条新 corrections 做一次蒸馏
大约两周一次
```

太频繁会样本不足，容易过拟合偶发问题。

太久不做会导致 rules 膨胀、context 稀释、Agent 行为漂移。

## 对 AgentOS 机制设计的启发

### 1. AgentOS 必须内建蒸馏入口

不能只提供 `corrections.log`，还要提供：

- `skills/distill/` 或 `scripts/distill`。
- correction 标签模板。
- cluster 统计。
- governance 行数对比。
- eval 前后对比。
- `_retired/` 和 `_graduated/` 归档机制。

否则 corrections 只会积累，不会进化。

### 2. 蒸馏结果必须通过 Eval 回归

做减法有风险，因此每次蒸馏后都应该跑：

```bash
bash eval/run-eval.sh
```

如果 coverage 降了，说明删错了或合并过度。

### 3. 退休是治理健康的核心指标

一个健康 AgentOS 不仅有新增，还要有退休。

可以统计：

- active rules 数量。
- retired rules 数量。
- graduated gates 数量。
- 每次蒸馏前后行数。
- corrections 重复率。

如果从来没有退休，说明团队在积累，不是在蒸馏。

## 对 payment-agent 的落地建议

支付项目里，蒸馏应该更保守，但更必要。

常见 cluster 可能包括：

| Cluster | 可能治理产物 |
|---|---|
| 幂等遗漏 | Principle：所有外部副作用必须可幂等 |
| 金额精度问题 | Gate：禁止浮点金额计算 |
| 状态机遗漏 | Rule：状态变更必须更新状态图和测试 |
| 异常路径不足 | Principle：完成必须覆盖未知/超时/重复回调 |
| 审计字段遗漏 | Gate：资金链路写入必须包含 trace/audit 字段 |

蒸馏时尤其要避免把支付高风险 rule 过早退休。退休前必须有 Eval 和真实运行数据支撑。

## 最终结论

这份 PDF 的核心结论是：

> 蒸馏不是整理文档，而是让 governance 变短、覆盖变广、行为不退化。

三招足够：

```text
上提：3+ 同类 correction -> Principle
下沉：3+ 次违反 rule -> Gate
毕业：长期未触发 gate -> _graduated/
```

验证标准也很清楚：

```text
行数减少 + coverage 不降 + 退休有记录
```

做减法是反直觉的，所以它必须被设计成一个固定动作，而不是依赖团队“想起来再整理”。
