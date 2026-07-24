# 04_knowledge_governance.pdf 总结

> 文件名：`04_knowledge_governance.pdf`  
> 正文标题：Knowledge 模块(2) · 三层治理  
> 页数：14 页

## 一句话总结

这份 PDF 讲的是 AgentOS 的治理系统应该如何从经验中生长出来：不要每被 Agent 坑一次就加一条规则，而要把多次纠正背后的共同偏差蒸馏成少量 Principles，再把特定场景沉淀成可追溯、可过期的 Rules，最后只把反复违反或高风险的问题变成代码级 Gates。

## 核心问题：你纠正了 Agent 三次之后怎么办

大多数团队在使用 AI 编程工具时，会自然走向一个反模式：

- 第一次被坑：加一条 rule。
- 第二次被坑：再加一条 rule。
- 第三次被坑：继续加 rule。
- 到第五十次：规则文件臃肿到 Agent 根本不读。

这份课件指出，真正该问的问题不是“还要加什么规则”，而是：

> 这些纠正背后，是不是同一个偏差根因？

通常，几十条 correction 背后的根因并不多，可能只有 3-5 个。治理系统的任务不是把所有事故逐条写进规则，而是把重复事故压缩成更高阶的判断原则。

## 三层治理模型

课程提出的治理结构是：

```text
Principles -> Rules -> Gates
```

这三层不是三选一，而是分工不同、共同存在。

| 层级 | 定位 | 数量 | 作用 |
|---|---|---:|---|
| Principles | 方向性原则 | 3-5 条 | 覆盖一整类失败，提供优先级和判断标准 |
| Rules | 具体指导 | 不超过 10-15 条 | 处理 Principles 覆盖不到的具体场景 |
| Gates | 强制门禁 | 尽量少 | 把高风险或反复失败的问题变成代码级阻断 |

它们之间还有演化关系：

| 演化方向 | 条件 | 结果 |
|---|---|---|
| Rule -> Principle | 多条 rule 共享同一个根因 | 抽象成 Principle，减少 rule 数量 |
| Rule -> Gate | 同一条 rule 被反复违反 | 文本约束失效，变成代码级门禁 |
| Gate -> Retire / Graduate | 长期不再触发 | 说明上游治理有效，可以降级或毕业 |

这套模型的关键是：治理不是越多越好，而是要越来越短、覆盖越来越广。

## Principles：少量、抽象、可判定

Principle 是最高层的治理表达。它不是口号，而是能指导 Agent 在模糊情境中做取舍的判断标准。

坏的 Principle 通常像这样：

- 代码要干净。
- 要认真测试。
- 注意性能。
- 安全很重要。

这些话都正确，但不可判定，Agent 不知道做到什么程度才算满足。

好的 Principle 应该同时满足三个条件：

| 条件 | 含义 |
|---|---|
| 抽象到能覆盖一类问题 | 不是只处理一个 bug，而是覆盖一种失败模式 |
| 具体到能判断 | Agent 和人都能判断是否违反 |
| 自带判定标准 | 有边界、有阈值、有理由 |

课件给出的好例子包括：

| 方向 | 好的 Principle |
|---|---|
| 完成度 | 完成 = 主动尝试破坏它且失败 |
| 数据质量 | 宁可拒绝，也不放脏数据进库 |
| 用户体验 | 识别小于 5 秒、首屏小于 200ms 是红线 |
| 输入安全 | 所有外部输入必须在入口处验证，不依赖下游防御 |

这里最重要的不是某个具体阈值，而是 Principle 必须能变成实际判断。

## Principles 需要排序

Principles 之间一定会冲突。

例如：

- “数据质量是底线”可能要求更长验证时间。
- “响应小于 5 秒”要求更快返回。

这时如果没有优先级，Agent 就会随机取舍。课件强调，Principles 应该显式排序，例如：

```text
P1: 完成 = 主动破坏且失败
P2: 数据质量是底线
P3: 每个名字让陌生人秒懂
P4: 用户体验承诺
```

如果 P2 和 P4 冲突，就按 P2 优先。

这也是课程里反复出现的“品味”概念：品味不是抽象审美，而是在冲突中明确什么不可妥协。

## Rules：可追溯、可判定、可过期

Rule 是比 Principle 更具体的一层。它处理某些明确场景，但不能变成无限增长的备忘录。

一条健康的 Rule 必须有三件东西：

| 字段 | 作用 |
|---|---|
| 追溯 | 它来自哪个 Principle、哪些 corrections |
| 判定标准 | 怎么判断它是否被遵守 |
| 过期条件 | 什么时候它可以退休 |

课件示例：

```markdown
# Rule: 识别接口必须返回 confidence

## 追溯
- Principle: 数据质量是底线（P2）
- Evidence: corrections #12, #17, #23

## 判定标准
- schema 含 confidence: number
- 取值 [0,1]；不满足 -> 400 拒绝

## 过期条件
- Gate check-schema.sh 部署后退休
- 或连续 30 天无违规后重新评估
```

Rule 的反模式包括：

| 反模式 | 问题 |
|---|---|
| 没有追溯 | 孤儿 rule，不知道为什么存在 |
| 没有过期条件 | 规则只增不减，最终膨胀 |
| 没有证据 | 可能只是想象中的问题 |
| 不可判定 | Agent 读了也无法执行 |

Rule 的本质不是“写给 Agent 的提示词”，而是治理系统里有生命周期的约束单元。

## Gates：最后防线，不是第一选择

Gate 是代码级阻断。它不是“请遵守”，而是“违反就提交不了 / 合并不了 / 运行不了”。

课件示例：

```bash
# governance/gates/check-test-coverage.sh
#!/bin/bash
# Gate: 测试覆盖率必须 >= 80%
# 追溯: P1 完成=主动破坏且失败
# 证据: Rule R3 被违反 4 次
# 毕业: 连续 60 天不触发

COVERAGE=$(pytest --cov | grep TOTAL ...)
if [ "$COVERAGE" -lt 80 ]; then
  echo "GATE BLOCKED: ${COVERAGE}% < 80%"
  exit 1
fi
```

什么时候应该加 Gate？

- 同一个 Rule 被违反 3 次以上。
- 这个问题靠文本提醒已经失败。
- 风险足够高，必须物理阻断。
- 可以被脚本、测试、静态检查或 CI 明确判定。

什么时候不应该加 Gate？

- 只是风格偏好。
- 还没有证据表明 Agent 会反复犯错。
- 问题无法稳定自动判断。
- Gate 维护成本高于收益。

课件特别提醒：如果项目里到处都是 Gate，说明不是治理强，而是 Principles 太弱，或者蒸馏没有做好。

## 蒸馏：治理系统的减法机制

这份 PDF 里很重要的一点是：蒸馏不是删除，而是升级。

蒸馏前可能有很多零散规则，蒸馏后应该变成更少的规则、更好的原则和更少的硬门禁。

| 操作 | 触发条件 | 效果 |
|---|---|---|
| Rule -> Principle 吸收 | 3 条以上 rule 共享同一根因 | Principle 更精炼，Rules 减少 |
| Rule 退休 | Gate 已覆盖，或 30 天无违反 | Rules 减少 |
| Gate 毕业 | 60 天未触发 | Gates 减少 |

蒸馏的时机：

- `corrections.log` 积累到 5-10 条时。
- 每周定期一次。
- 当团队感觉 rules 太多时。

所以治理的目标不是把所有历史错误永久刻在规则里，而是定期压缩、归并、退休。

## 蒸馏示例：10 条 correction 变成 4 条治理约束

课件给了一个很清楚的例子。

原始 corrections：

```text
1. 跳过 edge case 就说 done
2. 命名 handle_stuff，不具体
3. 没跑 lint 就提交
4. 改 schema 没更新文档
5. API key 写在代码里
6. 说“应该没问题”不验证
7. 命名用缩写没人懂
8. 改 3 个文件只测 1 个
9. 新增字段没 migration
10. 完成后没自己试一遍
```

蒸馏结果：

| correction 群组 | 根因 | 治理产物 |
|---|---|---|
| #1, #6, #8, #10 | 完成度不足 | Principle：完成 = 主动破坏且失败 |
| #2, #7 | 命名不清晰 | Principle：名字让陌生人秒懂 |
| #3, #4, #9 | 遗漏配套变更 | Rule：主体变更后完成配套变更 |
| #5 | 安全风险 | Gate：pre-commit 扫描硬编码密钥 |

10 条 correction 最后不是变成 10 条 rule，而是变成：

- 2 条 Principles。
- 1 条 Rule。
- 1 个 Gate。

这就是三层治理的价值：用少量高质量约束覆盖大量错误变体。

## 推荐目录结构

课件建议的治理目录如下：

```text
governance/
├── principles.md
├── rules/
│   ├── R001-schema.md
│   ├── R002-...
│   └── _retired/
│       └── R000-no-any.md
└── gates/
    ├── check-lint.sh
    ├── check-secrets.sh
    └── _graduated/
        └── check-xxx.sh
```

设计原因：

| 路径 | 设计意图 |
|---|---|
| `principles.md` | Principles 数量少，且需要互相排序，放一个文件最清楚 |
| `rules/*.md` | 每条 Rule 有独立追溯和生命周期，适合单文件管理 |
| `rules/_retired/` | 归档退休 rule，保留演化证据 |
| `gates/*.sh` | Gate 是可执行脚本，可被 pre-commit / CI 调用 |
| `gates/_graduated/` | 归档毕业 gate，证明治理系统在变轻 |

重点是归档而不是删除。治理系统需要保留“为什么曾经存在、为什么现在退休”的证据。

## Governance 与 Knowledge 的关系

Governance 不是独立系统，而是 Knowledge 系统的产物。

完整链路是：

```text
Session 互动
  -> capture hook
  -> corrections.log
  -> 蒸馏
  -> governance/
  -> SessionStart 注入
  -> Agent 下次表现更好
  -> corrections 减少
  -> 继续蒸馏
```

也就是说：

- Knowledge 负责记录项目知道什么。
- Governance 负责表达哪些约束必须被遵守。
- Feed 捕获经验。
- Distillation 把经验压缩成治理资产。
- Retrieve 在下次 session 开始时把治理资产注入给 Agent。

这里也明确了人的角色：

| 环节 | 自动化程度 |
|---|---|
| capture | 可以自动化 |
| correction 提取 | 可以半自动 |
| distillation 草稿 | 可以由 AI 起草 |
| principle 排序 | 必须由人审批 |
| trade-off 取舍 | 必须由人负责 |

因为 Principle 的优先级本质上代表团队价值排序，这件事不能完全交给模型随机决定。

## Lab 要求

本节的实践任务包括：

1. 创建 `governance/principles.md`
   - 写 3-5 条 Principles。
   - 带优先级排序。
   - 每条都要覆盖一类问题。
   - 每条都要可判定。
   - 每条都要带判断标准。

2. 创建 `governance/rules/`
   - 写 2-3 条 Rules。
   - 每条包含追溯、判定标准、过期条件。

3. 创建 `governance/gates/`
   - 写 1 个 Gate 脚本。
   - 可以是 lint、test、secrets 等检查。

4. 可选：用 10 条模拟 corrections 做一次蒸馏练习。

Lab 的判断问题：

- 你的 P1 是什么？为什么它是最高优先级？
- 某条 Rule 追溯到哪个 Principle？
- 如果 Rule 追溯不到 Principle，是 Rule 有问题，还是缺少一条 Principle？
- 为什么某个问题需要 Gate，而不是继续用文本约束？

## 治理多样性：不同项目会长出不同 AgentOS

课件强调，同一个技术项目，不同团队可能会有不同治理哲学。

| 优先级排序 | 可能结果 | 适合场景 |
|---|---|---|
| 安全 > 质量 > 体验 > 速度 | Agent 会花更多时间做安全检查，交付更慢 | 医疗、金融、支付 |
| 体验 > 安全 > 质量 > 速度 | Agent 会优先优化 UX，但安全边界可能变松 | 早期产品探索 |
| 完成度第一 | Agent 不容易轻易交差，每次交付周期更长 | 被不完整交付反复坑过的团队 |

这些选择没有绝对对错，但后果是可预见的。

关键是不能不选。不选的话，Agent 会根据上下文、模型偏好和偶然性随机做决定。

## 健康指标

这份课件给了一组判断治理系统健康度的指标。

| 指标 | 健康状态 | 生病状态 |
|---|---|---|
| Principles 数量 | 稳定在 3-5 条 | 不断增加 |
| Rules 数量 | 稳定或减少 | 持续膨胀 |
| Gates 数量 | 最少，能毕业 | 只加不减 |
| Corrections 频率 | 递减 | 不变或上升 |
| Rule 退休率 | 有 rule 在退休 | 没有 rule 退过 |
| 新错命中率 | 新类型错误首次就被 principle 覆盖 | 每次新错都要新 rule |

其中最强信号是：

> 新类型错误第一次出现时，就能被已有 Principle 正确处理。

这说明 Principle 覆盖的是“类”，而不只是已知个体。

## 对 AgentOS 设计的启发

如果把这份课件落到我们讨论的 AgentOS 结构里，至少有几个直接启发。

### 1. 不应该让 rules 文件无限增长

AgentOS 不能只是维护一个越来越长的 `rules.md`。应该内建 rule 的生命周期字段：

- 来源 correction。
- 所属 Principle。
- 判定标准。
- 过期条件。
- 最近触发记录。
- 是否候选退休。

否则系统迟早变成“规则垃圾场”。

### 2. Governance 应该从 corrections.log 生长出来

前一份 PDF 讲 Feed，SessionEnd 把纠正、决策、发现写入 `corrections.log`。这一份说明，`corrections.log` 不是最终产物，它只是原料。

AgentOS 应该有一个明确流程：

```text
corrections.log -> distill draft -> human approve -> governance update
```

AI 可以起草蒸馏结果，但人要审批 Principle 的新增、合并、排序和 Gate 的上线。

### 3. Gate 要谨慎，但必须存在

对代码 Agent 来说，纯文本规则很容易失效。反复失效的 Rule 应该进入 Gate。

适合 Gate 化的问题包括：

- secret 泄露。
- lint/typecheck/test 不通过。
- schema/migration 不一致。
- 覆盖率或关键路径测试缺失。
- OpenAPI/DTO/数据库结构不一致。

不适合 Gate 化的问题包括：

- 抽象命名品味。
- 架构边界的轻微偏差。
- 需要人类产品判断的问题。

### 4. AgentOS 初始化时不应该一次性写太多规则

初始化时更合理的是：

- 先写 3-5 条 Principles。
- 只写少量明确 Rules。
- 只放最硬的 Gates，例如 lint/test/secrets。
- 后续根据真实 corrections 迭代。

如果一开始塞满 rules，等于假装系统已经学习过项目经验，反而会降低 Agent 对关键约束的注意力。

### 5. Review 和 Test 也应纳入治理链路

高阶模型做 code review 后产生的发现，不应该只停留在一次性 review 评论里。它们应该进入 `corrections.log` 或 `review/findings.md`，再按频率蒸馏：

- 偶发问题：记录即可。
- 重复问题：变成 Rule。
- 高风险或反复违反：变成 Gate。
- 多个具体问题共享根因：变成 Principle。

测试过程也是同理。测试失败不是只修 bug，还要反问：

- 是否缺一条 Rule？
- 是否需要一个 Gate？
- 是否暴露了 Principle 不清晰？

## 和前一份 PDF 的关系

`03_knowledge_ddd_feed.pdf` 解决的是：

> Agent 的长期知识从哪里来，怎么被捕获？

本 PDF 解决的是：

> 捕获到的 corrections 怎么变成可执行、可维护、可变短的治理系统？

两者关系如下：

| 模块 | 作用 |
|---|---|
| DDD | 稳定描述产品、技术、改进、当前项目 |
| Feed | 自动捕获 correction / decision / discovery |
| Governance | 把经验沉淀成 Principles / Rules / Gates |
| Distillation | 定期做减法，让系统变短、变强 |

所以 Knowledge 不是“文档越多越好”，而是通过 Feed 和 Governance 让 Agent 的长期记忆逐步变得更准确、更短、更有判断力。

## 最终结论

这份 PDF 的核心可以压缩成一句话：

> 成熟的 AgentOS 不是靠不断加规则，而是靠从纠正中蒸馏出少量可判定的原则，并把反复失败的地方变成可执行门禁。

对项目组来说，真正要建立的不是“规则文档”，而是一套治理生命周期：

```text
发现问题 -> 记录 correction -> 聚类根因 -> 蒸馏治理资产 -> 注入 Agent -> 观察是否减少 -> 退休或升级
```

如果没有退休机制，rules 会膨胀；如果没有 Gate，文本规则会失效；如果没有 Principle，Agent 遇到新问题只能随机判断。

因此，这一节是 AgentOS 从“知识库”走向“可进化操作系统”的关键一步。
