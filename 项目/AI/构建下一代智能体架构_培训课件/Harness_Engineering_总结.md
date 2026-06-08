# Harness Engineering — 构建生产级 AI Agent 系统的工程学

> **核心认知**：如果说 SpringBoot 的 MVC 是你理解 Web 应用的骨架，那么 **Harness 五大系统 (S1-S5)** 就是理解 AI Agent 系统的骨架。MVC 管的是"请求→处理→响应"，Harness 管的是"信息→LLM→工具→安全→反馈→控制"。

---

## 一、为什么需要 Harness Engineering？

### 1.1 范式跃迁

| 阶段 | 时间 | 核心关注点 |
|------|------|-----------|
| Prompt Engineering | 2022-2023 | 单次输入质量：措辞、格式、few-shot |
| Context Engineering | 2024-2025 | 信息组装与窗口管理：放什么、放多少、放在哪 |
| **Harness Engineering** | **2025-现在** | **整个执行环境的工程化：输入→输出→约束→反馈→容错** |

Harness Engineering **包含**前两者，Context Engineering 只是它的子系统 S1。

### 1.2 概率复合效应（核心数学基础）

```
99% 的单步成功率 × 100 步 = 36.6% 的总成功率
```

Agent 是多步系统，每一步微小改进在复合效应下被巨幅放大。将单步成功率从 99% 提升到 99.9%，100 步后总成功率从 36.6% 跃升到 90.5%。**这就是 Harness Engineering 存在的根本原因。**

### 1.3 Dark Code — 传统工程方法失效

LLM 生成的行为（工具调用、代码片段、操作序列）在**运行时**才产生：
- Code Review → 无效（代码运行时才生成）
- 静态分析 → 无效（没有静态代码可分析）
- CI/CD → 无效（无法预测运行时行为）

**应对策略**：Runtime Governance — 在执行的每一步施加约束。

### 1.4 80/20 分配

| 组成部分 | 贡献比例 | 职责 |
|---------|---------|------|
| Harness（工程层） | **80-85%** | 决定可靠性——方案能不能稳定执行 |
| Model（模型） | 15-20% | 决定思维上限——能不能想出方案 |

同一模型 codex-1，仅优化工程层，SWE-bench 通过率从 45% 提升到 90%。

---

## 二、Harness 五大系统架构全景

```
┌──────────────────────────────────────────────────────────────────┐
│  S5: Entropy Management（控制平面）                                │
│  编排 + 容错 + 成本控制                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐              │
│   │   S1     │◄────►│   LLM    │◄────►│   S2     │              │
│   │ Context  │      │  推理核心 │      │  Tool    │              │
│   │ Assembly │      │          │      │ Governance│              │
│   └──────────┘      └────┬──┬──┘      └──────────┘              │
│        ▲                 │  │                                  │
│        │            ┌────┘  └────┐                              │
│        │            ▼            ▼                              │
│        │       ┌─────────┐  ┌─────────┐                         │
│        └───────│   S4    │  │   S3    │                         │
│   反馈回路      │Feedback │  │Security │                         │
│                │ & State │  │&Approval│                         │
│                └─────────┘  └─────────┘                         │
│                                                                  │
│  输入侧              运行时三件套             输出侧               │
└──────────────────────────────────────────────────────────────────┘
```

**每走一步，S1、S2、S3 各被触发一次；S4 是反馈环路；S5 在最外层管全局。**

| 系统 | 名称 | 核心问题 | 关键技术 |
|------|------|---------|---------|
| S1 | Context Assembly | 有限窗口内给 LLM 最有用的信息？ | Compaction · CLAUDE.md 层级 · 动态注入 · Prompt Caching |
| S2 | Tool Governance | 如何安全地让 LLM 操作真实世界？ | Tool schema · 参数验证 · 执行沙箱 · MCP 协议 |
| S3 | Security & Approval | 哪些操作需要人类确认？如何不过度打扰？ | Permission model · risk scoring · approval flow · 纵深防御 |
| S4 | Feedback & State | 执行结果如何反馈以改进后续决策？ | Observation · Memory · Evaluation · Drift Detection |
| S5 | Entropy Management | 如何让系统稳定、可控、经济地运行？ | Orchestration · Circuit Breaker · Cost Control · 终止条件 |

---

## 三、四大设计原则

### 原则 1：Constraint-First（约束优先）

**先定义"不能做什么"，再定义"能做什么"**

- 白名单优于黑名单（Whitelist > Blacklist）
- Default Deny > Default Allow
- 文件系统：先 sandbox，再逐步放开路径
- 网络：先全部禁止，再按需开放域名

> 反例：某 Agent 框架默认开放所有 shell 命令 → 模型 hallucinate 了 `rm -rf /home/user/data` → 用户数据被删除

### 原则 2：Verifiability（可验证性）

完整可验证性 = **Observability（看到） + Evaluation（评判） + Reproducibility（重现）**

```
行业现状：89% 有 observability，仅 52% 做 evaluation → 37% 缺口
```

### 原则 3：Progressive Trust（渐进信任）

权限是**动态的**，不是二元的（有/无）：

- 新会话：最小权限
- 连续成功：逐步放开（对数增长，越来越慢）
- 出现异常：**立即收紧**（1 次违规瞬间降级）
- 高风险操作：**永远锁定** Ask-first 或 Deny

**信任不对称**：获得信任是慢的（10+ 次安全操作），失去信任是瞬间的（1 次违规）。

### 原则 4：Design for Failure（为失败而设计）

四种失败模式 + 工程应对：

| 失败模式 | 应对机制 |
|---------|---------|
| LLM 幻觉 | Checkpoint / Rollback |
| 工具执行失败 | Circuit Breaker（熔断器） |
| 状态不一致 | Retry + Backoff |
| 无限循环 | Graceful Degradation（优雅降级） |

合理的容错设计可降低 **60-80% 成本**——无效重试和无限循环是最大的 token 浪费来源。

---

## 四、S1：Context Assembly（上下文装配系统）

**核心问题**：在有限的 context window 内，如何给 LLM 提供最大价值的信息？

### 4.1 Context 的五源模型

| # | 来源 | 稳定性 | 典型占比 | 缓存友好度 |
|---|------|--------|---------|-----------|
| 1 | System Prompt | 极稳定 | 15-25% | ★★★★★ |
| 2 | Tool Schemas | 稳定（session 内） | 5-15% | ★★★★☆ |
| 3 | Memory / RAG | 动态检索 | 10-20% | ★★☆☆☆ |
| 4 | Conversation History | 持续增长 | 30-40% | ★☆☆☆☆ |
| 5 | Current Message | 每次不同 | 5-15% | ☆☆☆☆☆ |

### 4.2 三层 Context 困境

| 困境 | 表现 | 后果 |
|------|------|------|
| **太少 (Under)** | 幻觉、编造事实、重复已完成工作 | Agent 做出错误决策 |
| **太多 (Over)** | 成本爆炸、注意力稀释 | Lost in the Middle，$5/请求 |
| **太错 (Wrong)** | 基于错误前提行动 | 不可逆的生产事故 |

### 4.3 核心排列策略

```
最优排列（自上而下）：
┌──────────────────────────────┐
│ System Prompt (Core + Rules) │ ← 最稳定，可缓存，最高权威
│ Tool Schemas                 │ ← 半稳定，可缓存
├─ ─ ─ ─ CACHE BOUNDARY ─ ─ ─ ─┤
│ Project Context (CLAUDE.md)  │ ← 半稳定，Session 级
│ Memory / RAG Results         │ ← 动态，可淘汰
│ Older Conversation History   │ ← 可压缩，优先级低
│ Recent History + Current Msg │ ← 最新，永不截断
└──────────────────────────────┘
```

**三条设计规则**：
1. **稳定内容在前** → 最大化缓存命中
2. **关键信息在首尾** → 利用 U 形注意力曲线 (Lost in the Middle)
3. **可牺牲的在中间** → 空间紧张时先淘汰

### 4.4 指令优先级（Instruction Hierarchy）

```
System Prompt  >  User Message  >  Tool Results  >  External Data
（宪法·最高权威）  （法律·可执行）   （证据·参考用）   （路人·最不可信）
```

工程含义：所有不可妥协的规则，必须在 System Prompt 中。

### 4.5 Token Budget 三级管理

| 级别 | 职责 | 示例 |
|------|------|------|
| Global Budget | 日/月 token 上限 | 日预算 10M in + 2M out ≈ $45/day |
| Task Budget | 单任务/会话上限 | 单任务 ≤ 500K in ≈ $1.50 |
| Per-Round Budget | 单次调用窗口内分配 | 200K window 各区域配额 |

### 4.6 渐进式降级（预算压力响应）

| 利用率 | 动作 |
|--------|------|
| < 80% | 正常运行 |
| 80% | 压缩旧 history（保留近 N 轮 + 摘要） |
| 90% | 触发 memory consolidation（关键信息持久化） |
| 95% | 强制压缩 + 拒绝新 tool calls |
| 99% | 硬停，输出最终摘要 |

### 4.7 Prompt Caching（最重要的成本优化）

- **底层机制**：逐字节精确前缀匹配 KV Cache
- **Anthropic**：显式标记 cache_control，写入 +25% 费用，读取 90% off
- **效果**：50K system prompt + 1000 请求/天，从 $4,545/月 → $500/月（节省 89%）
- **关键约束**：第一个不同字节之后，全部 cache miss → **稳定内容必须放最前面**
- **寿命**：5 分钟 TTL，命中续命

### 4.8 Protected Zone vs Dynamic Zone（内核空间 vs 用户空间）

| Protected Zone (~15-25%) | Dynamic Zone (~75-85%) |
|--------------------------|------------------------|
| System prompt core + Tool schemas + Critical rules | History + RAG + Tool outputs + Current |
| 永不截断 · 最前端 · 被 cache 覆盖 | 按需填充 · 优先级淘汰 · 可压缩 |
| ≈ OS kernel space | ≈ OS user space |

### 4.9 三种压缩策略

| 策略 | 原理 | 适用场景 |
|------|------|---------|
| **Summarization** | LLM 对旧 history 生成摘要替换，压缩比 5-10x | 中等长度 (10-30 轮) |
| **Selective Eviction** | 按重要性评分丢弃低分项 | 短对话 |
| **Hybrid（推荐）** | 滑动窗口 + 摘要锚点：最近 N 轮完整 + 更早压缩为摘要 | 生产环境 |

### 4.10 Context Engineering 十大原则

1. **Stability-first ordering** — 最稳定的内容放最前面
2. **U-curve awareness** — 关键信息放开头和结尾
3. **Budget discipline** — ≤80% 利用率就开始压缩
4. **Hierarchical authority** — System > User > Tool
5. **Measure everything** — Hit rate / utilization / compression loss
6. **Progressive degradation** — 渐进式压缩，不是"满了才硬停"
7. **Separation of concerns** — 稳定指令 vs 动态数据是不同管线
8. **Recency bias exploitation** — 最可操作内容放最后
9. **Format for the model** — 用结构化标记（XML）而非散文
10. **Test context, not just prompts** — A/B 测试完整 context 管线

---

## 五、S2：Tool Governance（工具治理系统）

**核心问题**：如何安全地让 LLM 操作真实世界？

### 5.1 核心范式转变

| 维度 | 传统 API 调用 | Agent 工具调用 |
|------|-------------|-------------|
| 调用目标 | 编译时确定 | 运行时由 LLM **选择** |
| 参数来源 | 开发者硬编码 | LLM 从自然语言**推理生成** |
| 调用顺序 | 代码逻辑决定 | 基于中间结果的**动态规划** |
| 可预测性 | 确定性 | 非确定性 |
| 错误来源 | Bug（可复现） | 幻觉（概率性、难复现） |
| 治理方式 | 代码审查 + 单元测试 | **运行时拦截 + 权限系统 + schema 校验** |

### 5.2 Tool 统一接口（Everything is a Tool）

```
interface Tool {
  name: string;              // 唯一标识
  description: string;       // 这就是 prompt engineering！
  inputSchema: JSONSchema;   // 参数约束
  call(input, ctx): Promise<ToolResult>;
  checkPermissions(input, ctx): PermissionResult;
}
```

类比 POSIX "everything is a file descriptor" → "everything is a Tool"。

### 5.3 四类工具 + 四种治理策略

| 类型 | 风险 | 核心威胁 | 治理重点 |
|------|------|---------|---------|
| Execution (bash) | **Critical** | 可以做任何事 | 沙箱、白名单、每次审批 |
| Network (http) | High | 数据外泄、SSRF | 域名白名单、限流、超时 |
| Agent (spawn) | Med-High | 递归失控、token 爆炸 | 深度限制、budget 继承 |
| Domain (db/file) | Medium | 不可逆副作用 | 强校验、事务回滚、路径限制 |

**关键**：治理强度应与工具能力成正比，不是"越安全越好"，而是"风险匹配"。

### 5.4 六步执行流水线（每一步失败 → 立即返回 is_error）

```
Step1 Discovery  →  Step2 Permission  →  Step3 Validation  →  
Step4 Execution  →  Step5 Result      →  Step6 Persistence
```

| 步骤 | 职责 | 防范 |
|------|------|------|
| Discovery | O(1) lookup by name，严格匹配 | 工具幻觉 |
| Permission | Free/Ask/Approve/Deny 四级 | 越权操作 |
| Validation | JSON Schema/Zod strict 校验 | 幻觉参数 |
| Execution | 超时 30s + 异常隔离 + 并发控制 | Hang/Crash |
| Result | 截断 1MB + 统一格式 | Context 溢出 |
| Persistence | Cache + History + Trace | 不可观测 |

**黄金法则**：validate BEFORE execute。

### 5.5 三大保护机制（Day 1 必须实现）

| 机制 | 默认值 | 防范 |
|------|--------|------|
| Timeout | 30s | 执行无限挂起 |
| Truncation | 1MB | 结果撑爆 context |
| Exception Isolation | always on | 工具 crash 杀死 Agent |

### 5.6 结构化输出解析（四步管线）

```
原始文本 → Candidate Extraction → Cleaning → Strict JSON Parse → Schema Validation
```

解决了 LLM 输出 JSON 的六个常见问题：markdown fences、trailing comma、unclosed（streaming）、混合文本、unicode escape、嵌套引号。

### 5.7 幻觉检测三层防御

| 层级 | 负责系统 | 检测内容 | 时机 |
|------|---------|---------|------|
| L1 结构校验 | **S2** | 工具名/参数名/类型/范围 | 执行前 |
| L2 语义校验 | S3 | 路径合法性/命令安全/权限合规 | 执行前 |
| L3 事实校验 | S4 | 文件存在/API 可达/数据过时 | 执行中/后 |

S2 的 L1 成本最低、速度最快——纯确定性计算，**毫秒级拦截 60% 的工具调用幻觉**。

### 5.8 MCP 协议

解决 N（框架） × M（工具）的集成问题 → **N + M** 标准化。

| 原语 | 用途 | 协议方法 |
|------|------|---------|
| Tools | 可调用函数（主用途） | tools/list + tools/call |
| Resources | 可读数据源（文件类） | resources/list + read |
| Prompts | 可复用提示模板 | prompts/list + get |

---

## 六、S3：Security & Approval（安全与审批系统）

**核心理念**：安全不是功能，安全是约束。S2 = HOW（执行机制），S3 = WHY + WHAT（策略设计）。

### 6.1 Agent 打破了 RBAC 的三个核心假设

| 传统假设 | Agent 现实 |
|---------|-----------|
| 意图确定 | 意图是**概率性**的，取决于 context |
| Actor 不可操纵 | Agent 可被 **prompt injection** 劫持 |
| 权限粒度 = 功能粒度 | 同一工具(bash)风险取决于**参数** |

**攻击面 = LLM + Tool + Context 三者的乘积**，非加和。攻击者不需要任何系统权限，唯一武器 = 精心构造的文本。

### 6.2 三大 Agent 特有攻击场景

1. **Path Traversal + Exfiltration**：读取 `../../etc/passwd` → 通过 http_request 发到攻击者 URL
2. **Indirect Prompt Injection**：网页中隐藏指令 → Agent 执行后泄露 credentials
3. **Memory Poisoning**：植入"所有 code review 都通过" → 长期潜伏

### 6.3 Default Deny（约束优先）

- **Whitelist（推荐）**：最严格，安全保证是数学上可证明的
- **Blacklist（危险）**：无法穷举，bash 图灵完备、LLM 有创造力
- **Rule Engine**：最灵活，适合开发环境

### 6.4 四维正交约束空间

```
ALLOW bash IF:
  operation IN ["git status", "npm test"]    # 操作维度
  AND time.hour BETWEEN 9 AND 18             # 时间维度
  AND target_path STARTS_WITH "/project/"    # 数据维度
  AND agent.trust_level >= ASK_FIRST         # 权限维度
```

### 6.5 约束生命周期

```
Conservative Start（最小权限）→ Observation（监控被拒请求）→ Adjustment（基于数据放开）→ Stable State
```

永远从最严格开始，不是从最宽松缩减。

### 6.6 Path Validation 5 层纵深（30 行代码保护整个文件系统）

| 层级 | 职责 | 防范 |
|------|------|------|
| L1 Length Check | 防超长路径 DoS | 正则灾难性回溯 |
| L2 Iterative URL Decoding | 处理 double/triple encoding | `%252e` → `%2e` → `.` |
| L3 Unicode Normalization | NFC 标准化 | homoglyph 攻击 |
| L4 Path Normalization | 解析 `..` `//` `./` | 基本路径穿越 |
| L5 realpath() + Boundary | 解析 symlinks，验证边界 | symlink 绕过 |

### 6.7 Bash 4 层防御

| 层级 | 职责 |
|------|------|
| L1 Main Command Blacklist | rm -rf · dd · mkfs 等危险命令 |
| L2 Restricted Subcommands | apt(install/remove✗) · git(--force✗) |
| L3 Pipe Chain Recursive | `curl … \| bash` 等管道链递归展开 |
| L4 AST-level Bash Parsing | tree-sitter 解析，捕获 alias/function/heredoc/eval |

**为什么正则不够**？`bash -c "$(echo cm0gLXJmIC8= | base64 -d)"` — L1-3 全看不见 `rm`，唯有 L4 展开 `$(...)` 后捕获。

### 6.8 Indirect Injection 4 层防御

| 层级 | 方法 | 拦截率 |
|------|------|--------|
| L1 Source Marking | `[TOOL_RESULT]` `[EXTERNAL_DATA]` 标记 | ~40% |
| L2 Content Filtering | regex 扫描 "ignore previous" 等模式 | ~60% |
| L3 Dual-LLM Detection | Haiku 审查是否含操纵指令 | ~85% |
| L4 Output Validation | 对比 user_intent vs agent_action | 兜底 |

假设独立，组合拦截率 ≈ **99.3%**。

### 6.9 11 类威胁模型

其中 **#9-#11 是 Agent 系统独有的威胁**，传统安全体系完全没有覆盖：
- Direct Prompt Injection、Indirect Prompt Injection
- Memory Poisoning、Inter-Agent Trust Abuse

### 6.10 Human-in-the-Loop 三种模式

| 模式 | 适用 | 关键数据 |
|------|------|---------|
| Per-operation | 高风险场景 | 频率 >15/h 时阅读率从 85% 跌到 <20% |
| **Approval Nodes（推荐）** | 大多数场景的甜点 | 控制在 5-10 次/小时 |
| Runtime Intervention | 需要灵活控制的场景 | 用户保持控制感 |

**决策矩阵**：Risk × Reversibility → 介入模式

---

## 七、S4：Feedback & State（反馈与状态系统）

**核心问题**：把 Demo 变成 Product 的关键闭环。

### 7.1 五步闭环

```
Observe → Collect → Evaluate → Remember → Inject → (回到 Observe)
```

### 7.2 三层记忆架构

| 层级 | 容量 | 生命周期 | 管理方 |
|------|------|---------|--------|
| Working Memory = Context Window | 128K-200K | 单次推理 | Model |
| Short-term Memory = Session State | JSONL append-only | 数小时-数周 | **Harness** |
| Long-term Memory = Persistent Knowledge | MEMORY.md + Embedding | 数月-数年 | **Harness** |

**关键设计哲学**：delegate to model, NOT wrap — 不要让 Harness 层做 context summarization，模型处理自己的 working memory 比任何 heuristic 都强。

### 7.3 5 种记忆类型

| 类型 | 示例 | 生命周期 | confidence |
|------|------|---------|------------|
| user | "偏好 TypeScript + Vim" | 永久 | 0.95 (用户明确) |
| project | "本项目 monorepo + pnpm" | 项目生命周期 | 0.8 (推断) |
| feedback | "不要用 semicolons" | 6 个月 | 0.95 (用户纠正) |
| reference | "内部 API v2 endpoint" | 永久 | 0.9 (用户分享) |
| episodic | "今天 debug CORS" | 30 天 | 0.7 (Agent 总结) |

### 7.4 Confidence Gating + User Control

```
< 0.5 → 阻止写入
0.5-0.7 → 标记待验证
0.7-0.9 → 正常写入
> 0.9 → 延长保留期
```

用户 5 项必备控制权：查看、审批、删除、修正、透明存储（可见文本文件，非黑箱 DB）。

### 7.5 autoDream — 周期性记忆整合

受 REM 睡眠启发，四阶段管线：

```
Orient（提取摘要）→ Gather（收集关键信息）→ Consolidate（写入+去重合并）→ Prune（过期清理）
```

触发条件：Time Gate (>24h) / Session Gate (≥5) / 手动。

**效果**：1000 条未整理 → 准确率 60%；整理后 200 条 → 准确率 90%，Token 消耗 ↓40%。

### 7.6 Hybrid Retrieval（双通道检索）

```
Keyword (BM25, <10ms) + Semantic (Embedding ANN, <50ms)
→ 加权合并 (keyword×0.4 + semantic×0.6) → 去重 + rerank → Top-N
总预算 < 100ms，用户感知不到延迟
```

### 7.7 可观测性三支柱

| 支柱 | 回答 | 工具 |
|------|------|------|
| Metrics | What（发生了什么） | 12 个核心指标、Dashboard |
| Logs | When（什么时候） | 结构化 JSON + trace_id |
| Traces | Why（为什么） | OpenTelemetry spans |

**递进关系**：Metrics 发现 → Logs 定位时间窗口 → Traces 找根因

12 个核心指标分三个维度：
- **Task**：task_success_rate / task_duration / total_tokens / cost_per_task
- **Loop**：iteration_depth / tool_call_count / tool_success_rate / tool_latency_p95
- **System**：permission_denials / llm_call_count / token_io_ratio / cache_hit_rate

### 7.8 三级评估体系

| 级别 | 问题 | 频率 | 类比 |
|------|------|------|------|
| Step-level | 选对 tool 吗？参数对吗？ | 每步 | 动作姿势 |
| Trajectory-level | 路径高效吗？走弯路了吗？ | 每 task | 战术路线 |
| Task-level | 用户目标达成了吗？ | 每 task | 比分赢了没 |

**Step 正确 ≠ Trajectory 高效 ≠ Task 成功**。

### 7.9 LLM-as-Judge 设计

关键不是"用 LLM 打分"，而是 **Rubric 设计**：
- 拆解为 4 个明确维度（Correctness / Efficiency / Safety / Communication）
- 每维度 1-5 具体定义
- 用不同模型做 judge（防自我认同偏差）
- Cohen's Kappa 校准（κ > 0.75 才可信）

### 7.10 Drift Detection（漂移检测）

最危险的不是崩溃——是**慢慢变差但没人知道**。

| 方法 | 机制 |
|------|------|
| Sliding Window | 最近 7 天 vs 前 7 天，多指标同时 ↓ > 3% → alert |
| Baseline Regression | 持续 3 天 < 95% baseline → alert |
| Distribution Shift | 工具分布/路径长度/token 消耗的 KL divergence（**先行指标**） |

---

## 八、S5：Entropy Management（熵管理系统）

**核心问题**：对抗 Agent 的热力学第二定律——没有主动管理的 Agent 必然走向漂移、耗尽、级联崩溃。

### 8.1 根本差异

| 维度 | 传统 Workflow Engine | Agent Execution |
|------|---------------------|-----------------|
| 路径 | 确定性 DAG，部署时已知 | 概率性，运行时由 LLM 决定 |
| 成本 | 可预测 | 不确定 |
| 可重现性 | Same input = Same execution | Same input → Different paths |
| 熵特性 | 低 entropy，受控 | 高 entropy，自发增长 |

**你设计 boundary，Agent 在边界内自己探索 path。**

### 8.2 Think-Act-Observe 循环

```
Think（LLM 推理，最贵） → Act（工具调用，最危险） → Observe（结果注入，最有价值）
     ↑                                                      │
     └──────────────────────────────────────────────────────┘
```

**Agent 不是 Chain（确定步数），是 Loop（步数不确定）。**

### 8.3 五大终止条件（刹车系统）

| # | 条件 | 角色 |
|---|------|------|
| 1 | Tool Calls Exhausted（Agent 决定结束） | 最自然，最不可靠 |
| 2 | Max Iterations（硬性上限，典型 25） | 防无限循环安全网 |
| 3 | Token Budget（累计 token 上限） | 防经济损失 |
| 4 | Explicit Stop（用户取消/kill/timeout） | 尊重外部中断 |
| 5 | Goal Achieved（外部验证通过） | 最可靠正面终止 |

**你需要全部五个——Defense in Depth。任何单一条件都有边缘情况。**

### 8.4 Drift 两种类型

| 类型 | 定义 | 根因 | 比喻 |
|------|------|------|------|
| **Goal Drift** | 逐渐遗忘原始目标 | Recency bias | 出门买牛奶进了书店 |
| **Scope Creep** | 自行扩大执行范围 | Helpfulness bias | 出门买牛奶把一周菜都买了 |

### 8.5 三大漂移检测机制

| 机制 | 方式 | 角色 |
|------|------|------|
| Context Similarity | 原始 task vs recent actions 的 cosine similarity | 被动监控（卫星） |
| Goal Anchoring | 每 5 轮重新注入 original task description | 主动预防（哨声） |
| Behavior Boundary | 定义 allowed tools + paths | 硬性约束（围栏） |

### 8.6 渐进式漂移恢复

```
L1: Inject Reminder (similarity < 0.7)  → 70% 修正率
L2: Context Reset (L1 后 3 轮未回归)    → 打扫房间
L3: Force Terminate (similarity < 0.4)  → 保存现场，交给人类
```

### 8.7 Agent 状态机

```
IDLE → INITIALIZING → EXECUTING ⇄ PAUSED → COMPLETED / FAILED
```

PAUSED 是关键状态——让你有机会在 Agent 执行中途介入（注入新指令），而不是只能 Kill 重来。

### 8.8 四大实时控制操作

| 操作 | 行为 |
|------|------|
| Pause | 完成当前 tool call → 进入 PAUSED，保存 checkpoint |
| Resume | 验证状态 → 重新注入 goal reminder → 从 checkpoint 继续 |
| Intervene | 运行中注入新指令（不暂停），high-priority context |
| Kill | 立即终止（不等当前 tool），state snapshot for post-mortem |

### 8.9 Token Budget 三级

| 级别 | 阈值 | 触发行为 |
|------|------|---------|
| Per-Day Global | 10M tokens/day | 全停 + alert |
| Per-Task | 500K tokens | Graceful + partial result |
| Per-Round | 继承 S1 Budget | 由 S1 管理 |

**渐进式压力响应**：80% Compress → 90% autoDream → 95% Reject New Tools → 99% Hard Stop

### 8.10 Provider Abstraction（两条路径）

| 路径 | 代表 | 优势 | 代价 |
|------|------|------|------|
| Single-Model Binding | Claude Code | 深度集成（90% cache 折扣、extended thinking） | Vendor lock-in |
| Multi-Model Routing | OpenCode | 灵活切换、故障转移 | 只能用最大公约数功能 |

**推荐混合方案**：Primary 深绑定 + Fallback-1 同 provider + Fallback-2 跨 provider。

### 8.11 Circuit Breaker（熔断器）

```
CLOSED（正常） → [5次失败/50%错误率] → OPEN（快速拒绝）
                                           ↓ 30s cooldown
                                       HALF-OPEN（探测）
                                     ↙          ↘
                               探测成功→CLOSED   探测失败→OPEN
```

每个 Provider 独立维护熔断状态，429 Rate Limiting 单独处理（用 backoff，不触发熔断）。

### 8.12 Fallback Chain

```
Primary (Sonnet 4) → Fallback-1 (Haiku 4, 同 provider 保留 cache)
→ Fallback-2 (GPT-4o-mini, 跨 provider 需格式转换)
→ Hard Fail (排队等恢复)
```

### 8.13 Bulkhead（资源隔离）

| 优先级 | 配额 | 用途 |
|--------|------|------|
| Critical | 60% | 用户实时交互 |
| Normal | 30% | 后台任务、sub-agent |
| Low | 10% | 批处理、分析、autoDream |

即使 Low 队列堆满 100 个任务，Critical 始终有 60% 容量。

### 8.14 Errors-as-Observations（自愈模式）

传统：error → exception → handler → retry or crash

Agent：error → **inject into context as observation** → LLM 分析 → 决定重试/换方案/降级

Tool 超时 → 先作为 observation 告诉 Agent（让它决策）；只有 LLM provider 级别的超时才由 S5 自动 retry。

### 8.15 六根成本杠杆（综合降低 60-80%）

| # | 杠杆 | 节省 | 难度 |
|---|------|------|------|
| 1 | Prompt Caching | 50-90% | ★☆☆ |
| 2 | Schema Caching | 10-20% | ★☆☆ |
| 3 | Smart Model Routing | 40-60% | ★★☆ |
| 4 | Result Truncation | 20-40% | ★☆☆ |
| 5 | Token Hard Limits | 防溢出 | ★☆☆ |
| 6 | History Compression | 30-50% | ★★☆ |

**实施顺序（按 ROI）**：1 → 4 → 5 → 2 → 3 → 6，零质量损失的先做。

---

## 九、生产工程

### 9.1 三层配置架构

```
L0 Hardcoded Defaults → L1 Global YAML (Git) → L2 Env Variables → L3 Runtime (API/Feature Flag)
```

合并规则：L3 > L2 > L1 > L0（类似 CSS 优先级）。黄金法则：All config in Git。

### 9.2 金丝雀发布五阶段

```
Stage 1: Internal Dogfood (3 天) → Stage 2: 1% Users (4 天)
→ Stage 3: 10% Users (3-5 天) → Stage 4: 50% Users (3-5 天)
→ Stage 5: 100% Users
```

**Agent 系统的 bug 是"删了用户代码"，不是"按钮颜色错了"——渐进发布尤其重要。**

### 9.3 性能核心目标

| 指标 | 目标 | 原因 |
|------|------|------|
| TTFT | < 1s | 超过 1s 用户感到"卡" |
| P99 Task | < 30s | 交互式任务耐心极限 |
| Streaming | 响应 > 2s 必启用 | 感知延迟降低 50%+ |

### 9.4 部署拓扑三级

| Tier | 用户规模 | 状态存储 | 适用场景 |
|------|---------|---------|---------|
| Tier 1 | < 100 | SQLite + 文件系统 | 内部工具 / MVP |
| Tier 2 | 100-10K | Redis + PostgreSQL | B2B SaaS |
| Tier 3 | 10K+ | 多区域独立集群 | 全球化产品 |

**不要过早优化——90% 的团队 Tier 1 就够了。**

### 9.5 生产就绪清单（7 大类）

| # | 维度 | 核心检查 |
|---|------|---------|
| 1 | Config | 配置版本化？能否不改代码切模型？ |
| 2 | Canary | 回滚条件预定义？自动回滚阈值已测试？ |
| 3 | Cost | 预算上限？异常可检测？ |
| 4 | Performance | TTFT < 1s？全链路 streaming？ |
| 5 | Monitoring | Dashboard + 4 级告警规则？ |
| 6 | Security | Sandbox 配置？Tool policy + audit log？ |
| 7 | Evaluation | 评估集 + 基线分数 + CI 集成？ |

---

## 十、一句话总结

如果说 SpringBoot MVC 让你记住的是 **"Controller → Service → Repository"** 三层，那么 Harness Engineering 让你记住的是 **"S1(输入) → LLM → S2(输出/工具) → S3(安全) → S4(反馈) → S5(控制)"** 五系统循环。

**模型决定 Agent "能不能想出来"，Harness 决定 "想出来之后能不能做对、做稳、做到"。**
