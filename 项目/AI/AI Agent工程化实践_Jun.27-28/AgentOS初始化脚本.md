# 初始化项目级 AgentOS

> 本文档是给 AI Coding Agent 执行的初始化脚本。适用于已有项目，不要求项目只使用某一个 agent。目标是让 Claude Code、Codex、superpowers、手工开发都能在同一个项目治理协议下协作。

## 目标

请在当前仓库初始化一套项目级 `agentos/` 机制，用于统一管理：

- 项目长期知识
- AI Coding 治理原则
- Delivery Engine 执行流程
- 多来源计划索引
- 技术债雷达
- 主 R 打样 SOP
- 测试契约与测试门禁
- 高阶模型 Review Packet / Judge Review
- Pre-PR 审查
- 多 Agent / 多工具适配

本任务面向已有项目，不允许粗暴覆盖现有协作文件。尤其需要兼容：

- `AGENTS.md`
- `CLAUDE.md`
- `backend/AGENTS.md`
- `frontend/AGENTS.md`
- `backend/CLAUDE.md`
- `frontend/CLAUDE.md`
- `docs/plans/`
- Claude Code 自带 Plan Mode
- superpowers 默认计划结构
- Codex / Claude Code 两类 Code Agent
- 已有 `.claude/skills`、`.claude/rules`、项目自定义 skills

## 核心原则

1. 不覆盖现有 `AGENTS.md` / `CLAUDE.md`，只追加 AgentOS 入口说明。
2. `agentos/` 是项目级治理中枢，不替代已有 `docs/plans/`、`.claude/skills` 或 superpowers。
3. superpowers 生成的计划不搬家、不复制、不重排，只登记到 `agentos/plans/registry.md`。
4. Claude Code Plan Mode 生成的 `.claude` 或用户目录私有计划只视为草稿，确认后 promote 成 repo 内 snapshot。
5. 小需求允许快速开发，但必须留下轻量记录；大需求必须有正式 Plan ID。
6. 统一的是索引、最低信息要求、测试证据和审查流程，不强制统一所有工具的物理目录结构。
7. Review 不能只看 diff，必须先生成 Review Packet，把需求背景、计划、验收标准、项目红线、技术上下文和测试证据交给高阶模型。
8. 测试是一等公民。M/L 任务必须先有 Test Contract，再进入 BUILD。

## 第一步：读取项目现状

先读取并总结以下文件，不要直接修改：

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `backend/AGENTS.md`，如果存在
- `frontend/AGENTS.md`，如果存在
- `backend/CLAUDE.md`，如果存在
- `frontend/CLAUDE.md`，如果存在
- `frontend/package.json`，如果存在
- 后端依赖和测试说明文件，例如 `backend/requirements.txt`、`pyproject.toml`、`pom.xml`、`go.mod`
- 已有 `docs/plans/` 和 `docs/templates/`
- 已有 `.claude/skills/`、`.claude/rules/`、`.claude/settings.json`
- 已有测试、评测、构建脚本，例如 `scripts/`、`app/evals/`、`tests/`

根据这些文件抽取：

- 项目产品定位
- 技术架构
- 前后端边界
- 启动命令
- 测试/构建/评测命令
- 配置和密钥规则
- LLM/Agent 使用边界
- 现有计划归档规范
- 已有 Claude Code / Codex / superpowers / skill 生态

如果信息不确定，标记为 `TBD`，不要编造。

## 第二步：创建目录结构

如果不存在，请创建：

```text
agentos/
├── README.md
├── corrections.log
├── knowledge/
│   ├── PRODUCT.md
│   ├── TECH.md
│   ├── PROJECT.md
│   └── IMPROVEMENT.md
├── governance/
│   ├── principles.md
│   ├── rules/
│   │   ├── R001-protocol-sync.md
│   │   ├── R002-config-approval.md
│   │   ├── R003-eval-required.md
│   │   ├── R004-llm-boundary.md
│   │   ├── R005-test-contract-required.md
│   │   └── _retired/
│   └── gates/
│       ├── check-backend.ps1
│       ├── check-frontend.ps1
│       ├── check-eval.ps1
│       ├── check-secrets.ps1
│       ├── check-tests.ps1
│       └── _graduated/
├── engine/
│   ├── intake.md
│   ├── runbook.md
│   ├── stages.md
│   ├── gates.md
│   ├── profiles.md
│   ├── STATE.md
│   └── loop-config.md
├── plans/
│   ├── README.md
│   ├── levels.md
│   ├── registry.md
│   └── snapshots/
├── artifacts/
│   ├── README.md
│   └── quick-changes/
├── test/
│   ├── README.md
│   ├── strategy.md
│   ├── test-contract-template.md
│   ├── test-plan-template.md
│   ├── coverage-policy.md
│   ├── mutation-policy.md
│   ├── regression-policy.md
│   ├── flaky-tests.md
│   ├── run-tests.ps1
│   └── reports/
├── eval/
│   ├── behavioral-contract.md
│   ├── golden-set.md
│   └── run-eval.ps1
├── debt/
│   ├── radar.md
│   ├── links.md
│   └── scans/
├── sops/
│   ├── README.md
│   ├── protocol-change-sop.md
│   ├── backend-tool-sop.md
│   ├── config-change-sop.md
│   ├── agent-loop-change-sop.md
│   ├── frontend-result-card-sop.md
│   └── eval-case-sop.md
├── review/
│   ├── pre-pr-checklist.md
│   ├── pr-template.md
│   ├── review-packet-template.md
│   ├── packets/
│   ├── reports/
│   └── judge-prompts/
│       ├── architecture-judge.md
│       ├── backend-judge.md
│       ├── frontend-judge.md
│       ├── protocol-judge.md
│       └── test-judge.md
├── skills/
│   ├── judge-review/
│   │   └── SKILL.md
│   └── test-contract/
│       └── SKILL.md
├── adapters/
│   ├── claude-code.md
│   ├── codex.md
│   └── superpowers.md
└── hooks/
    ├── on-session-start.md
    └── on-session-end.md
```

如果某些文件已存在，不要覆盖，先读取并增量补齐缺失内容。

## 第三步：写入核心文件

### `agentos/README.md`

写入：

```md
# AgentOS

本目录是项目级 AI Coding 治理中枢。

它不替代 Claude Code、Codex、superpowers、既有 `.claude/skills` 或 `docs/plans`，而是统一管理：

- 项目长期知识
- AI Coding 治理原则
- Delivery Engine 执行流程
- 多来源计划索引
- 测试契约与测试证据
- 技术债雷达
- 主 R 打样 SOP
- Review Packet 与高阶模型 Judge Review
- Pre-PR 审查
- 多 Agent 适配

## 工作流

1. 任务进入时先做 intake 分级。
2. XS/S 任务可快速开发，但要留下 quick-change 记录。
3. M/L 任务必须有 Plan ID。
4. 计划可以来自 superpowers、Claude Code Plan Mode、manual docs/plans 或 Codex artifact。
5. 正式计划必须登记到 `agentos/plans/registry.md`。
6. M/L 任务进入 BUILD 前必须有 Test Contract。
7. 实现必须遵守 `agentos/engine/runbook.md`。
8. 提交前必须生成 Review Packet，并完成 `agentos/review/pre-pr-checklist.md`。
```

### `agentos/plans/levels.md`

写入：

```md
# Task Levels

## XS: Direct Change

适用：
- typo
- 注释调整
- 文案微调
- 无行为变化的小改动

要求：
- 不需要正式 plan
- PR/提交说明写清楚即可

## S: Quick Change

适用：
- 小 bug
- 小 UI 调整
- 局部兼容修复
- 低风险测试补充

要求：
- 不需要 `docs/plans`
- 需要记录到 `agentos/artifacts/quick-changes/YYYY-MM.md`

## M: Standard Plan

适用：
- 后端逻辑变化
- 前端行为变化
- API/SSE 协议变化
- 配置变化
- eval/test 行为变化

要求：
- 必须有 Plan ID
- 必须有 Test Contract
- 可使用 superpowers、manual docs/plans、Claude promoted snapshot 或 Codex artifact

## L: Full Plan

适用：
- 架构调整
- AgentLoop / RAG / OCR / 解析核心改动
- 数据库或配置转正链路
- 跨模块重构
- 高风险业务链路

要求：
- 优先使用 superpowers 或 Claude Code Plan Mode
- 必须登记到 registry
- 必须有 Test Contract、风险、回滚、验证和 Pre-PR 审查
- 建议使用高阶模型 Judge Review
```

### `agentos/plans/registry.md`

写入：

```md
# Plan Registry

只有登记到本文件的 M/L 计划才是项目正式计划。

| ID | Level | Source | Path / Snapshot | Scope | Status | Owner | Updated |
|---|---|---|---|---|---|---|---|
| 示例 | L | superpowers | .superpowers/... | backend/app/... | active | TBD | YYYY-MM-DD |

## Source 类型

- `superpowers`
- `claude-plan-mode`
- `codex`
- `manual`
- `retro-plan`

## 规则

1. superpowers 计划不搬家，只登记真实路径。
2. Claude Code Plan Mode 的计划必须 promote 成 `agentos/plans/snapshots/P-*.md`。
3. manual 计划可以放在 `docs/plans/`。
4. Codex 计划可以放在 `agentos/plans/snapshots/`。
5. PR 中必须引用 Plan ID，或说明为什么不需要 Plan。
```

### `agentos/engine/intake.md`

写入：

```md
# Intake

每个任务开始前先完成分级。

## Task

- Name:
- Request:
- Owner:
- Date:

## Level

- [ ] XS
- [ ] S
- [ ] M
- [ ] L

## 判断依据

- 是否涉及后端逻辑:
- 是否涉及前端行为:
- 是否涉及协议/API/SSE:
- 是否涉及配置/密钥/数据库:
- 是否涉及 LLM/AgentLoop/RAG/OCR/解析核心:
- 是否影响 eval/test baseline:
- 是否需要人工审批:
- 是否需要高阶模型 Judge Review:

## Plan

- [ ] No plan needed
- [ ] Quick-change note
- [ ] superpowers plan
- [ ] Claude Plan Mode promoted snapshot
- [ ] manual docs/plans
- [ ] codex snapshot
- [ ] retro-plan

Plan ID:

## Test

- [ ] No explicit test contract needed
- [ ] Test Contract required

Test Contract Path:
```

### `agentos/engine/runbook.md`

写入：

```md
# Delivery Engine Runbook

非 XS/S 的任务必须按本流程执行。

## 0. Intake

读取：

- `agentos/plans/levels.md`
- `agentos/engine/intake.md`
- `agentos/governance/principles.md`
- `agentos/knowledge/PRODUCT.md`
- `agentos/knowledge/TECH.md`

完成任务分级。

## 1. EVALUATE

目标：先确认需求，不直接写代码。

产出：
- Scope
- Acceptance Criteria
- 风险
- 是否需要 plan
- 是否涉及不可逆决策
- 是否能顺带消化技术债
- 是否需要高阶模型 Judge Review

## 2. PLAN

目标：写清实现方案和验证方案。

M/L 任务必须有 Plan ID。

计划来源可以是：
- superpowers
- Claude Code Plan Mode promoted snapshot
- docs/plans manual plan
- Codex artifact

必须同时生成或引用 Test Contract：
- `agentos/test/test-contract-template.md`
- 或计划中等价的测试契约章节

## 3. BUILD

目标：严格按 plan 实现。

要求：
- 不在 BUILD 阶段偷偷改变方向
- 发现方案问题时回退 PLAN
- 后端工作继续读取 `backend/AGENTS.md`
- 前端工作继续读取 `frontend/AGENTS.md`

## 4. TEST

目标：用测试证明实现正确。

要求：
- AC 到测试方式有映射
- 阻塞测试必须通过
- 未运行测试必须写明原因和风险
- eval delta 必须记录
- flaky test 必须登记

## 5. VERIFY

目标：主动破坏式验证。

要求：
- 正常路径
- 边界输入
- 异常路径
- 降级路径
- 协议同步
- eval/test/build/lint 记录

## 6. REVIEW

目标：在人工 PR 前生成机器可读审查上下文。

要求：
- 生成 `agentos/review/packets/P-*-review-packet.md`
- 需要高阶模型审查时，使用 `agentos/skills/judge-review/SKILL.md`
- 保存报告到 `agentos/review/reports/`

## 7. PRE-PR

填写：
- `agentos/review/pre-pr-checklist.md`
- PR 中引用 Plan ID 或 quick-change note
- PR 中引用测试证据和 Judge Review 报告
```

### `agentos/engine/stages.md`

写入：

```md
# Stages

默认阶段：

```text
EVALUATE -> PLAN -> BUILD -> TEST -> VERIFY -> REVIEW -> DONE
```

## EVALUATE

确认需求、范围、AC、风险和计划等级。

## PLAN

写实现方案、测试契约、风险和回滚。

## BUILD

按方案实现，不改变方向。

## TEST

补齐并运行测试，失败回 BUILD。

## VERIFY

主动破坏式验证，失败回 BUILD 或 PLAN。

## REVIEW

生成 Review Packet，必要时调用高阶模型 Judge Review。
```

### `agentos/engine/gates.md`

写入：

```md
# Gates

## G1: EVALUATE -> PLAN

通过条件：
- Level 已判定
- M/L 任务需要 Plan ID 或明确计划来源
- AC 至少 3 条，且可判定
- 影响范围已声明

## G2: PLAN -> BUILD

通过条件：
- M/L 任务已登记 Plan ID
- Test Contract 存在
- 每条 AC 有验证方式
- 风险和回滚已声明
- 涉及不可逆决策时已标注人工审批点

## G3: BUILD -> TEST

通过条件：
- 实现覆盖 plan 中的 AC
- 新增或修改测试已列明
- 未按 plan 实现的地方有回退说明

## G4: TEST -> VERIFY

通过条件：
- 阻塞测试全部通过
- eval delta 在阈值内，或风险已说明
- 未运行测试有原因和风险
- flaky test 已记录

## G5: VERIFY -> REVIEW

通过条件：
- 主动破坏式验证完成
- 无未解释 fail 项
- verify artifact 已生成

## G6: REVIEW -> DONE

通过条件：
- Review Packet 已生成
- 需要 Judge Review 时，报告已生成
- CRITICAL/HIGH 问题已修复或有人工接受记录
```

### `agentos/governance/principles.md`

结合项目事实写入 3-5 条。若无法准确判断，使用以下默认版：

```md
# Principles

## P1: 确定性逻辑优先于 LLM 便利

涉及解析、金额、交易字段、配置转正、验真或审计的判断，必须由规则、工具、schema、测试或人工审批兜底。LLM 只能编排、解释、诊断和兜底。

## P2: 数据质量优先于表面成功

不完整、不可信、不满足 schema 的结果不能静默进入后续流程。失败必须显式暴露，并保留可追踪原因。

## P3: 协议变更必须端到端同步

任何 API、SSE 事件、客户端消息类型、schema 或 store 变更，必须同步检查后端实现、前端协议类型、服务调用、状态管理、UI 展示和验证。

## P4: 完成 = 主动破坏且失败

功能完成前必须覆盖正常路径、边界输入、异常路径和降级路径。只跑 happy path 不算完成。

## P5: 大变更先计划后编码，先有测试契约再实现

涉及架构、核心链路、跨前后端、配置、数据库、AgentLoop、RAG、OCR、解析、eval 的变更，必须先有正式计划、Plan ID 和 Test Contract。
```

## 第四步：写 adapter

### `agentos/adapters/superpowers.md`

```md
# Superpowers Adapter

superpowers 是 M/L 任务的推荐计划工具。

## 规则

1. 不移动 superpowers 默认生成目录。
2. 不复制 superpowers 全量计划到 docs/plans。
3. 创建计划后，必须登记到 `agentos/plans/registry.md`。
4. PR 中引用 Plan ID。
5. 如果需要统一入口，可在 `docs/plans/` 下创建 link stub，但不得复制内容导致双源漂移。

## 最低信息要求

superpowers 计划必须能找到：

- Scope
- Acceptance Criteria
- Tasks
- Verification
- Test Contract 或测试计划
- Risk / Rollback
```

### `agentos/adapters/claude-code.md`

```md
# Claude Code Adapter

Claude Code 的 Plan Mode 是草稿态，不是项目事实来源。

## 规则

1. `.claude` 或用户目录中的 plan 不视为正式项目计划。
2. 用户确认 M/L 计划后，必须 promote 成 repo 内 snapshot。
3. snapshot 放在 `agentos/plans/snapshots/P-*.md`。
4. registry 中 Source 标记为 `claude-plan-mode`。
5. 不同步每一次草稿变化，只 promote 已确认版本。
6. `.claude/skills` 可以作为执行能力层，但项目事实来源在 `agentos/`。

## Promote Snapshot 最低结构

- Task
- Scope
- Acceptance Criteria
- Plan Summary
- Tasks
- Test Contract
- Verification
- Risks / Rollback
```

### `agentos/adapters/codex.md`

```md
# Codex Adapter

Codex 使用 `AGENTS.md` 作为主要入口。

## 执行要求

1. 开始前读取 `agentos/engine/runbook.md`。
2. M/L 任务先建立或引用 Plan ID。
3. 修改前尊重 backend/frontend 分入口。
4. 完成后更新 artifact、quick-change note 或 plan snapshot。
5. 无 hook 时，手动追加 corrections。
6. 需要高阶模型审查时，生成 Review Packet，而不是只给 diff。

## Transcript Source

Codex 的会话日志不是 Claude Code 风格的普通 message transcript，而是 rollout JSONL event stream。

常见位置：

```text
Windows:
%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-<timestamp>-<thread_id>.jsonl

Index:
%USERPROFILE%\.codex\session_index.jsonl
```

`session_index.jsonl` 用于找到最近 thread：

```json
{"id":"<thread-id>","thread_name":"...","updated_at":"..."}
```

完整消息在 `sessions/YYYY/MM/DD/rollout-*<thread-id>.jsonl`。

## Transcript Format

Codex JSONL 每行顶层通常是：

```json
{
  "timestamp": "...",
  "type": "response_item",
  "payload": {}
}
```

常见顶层 `type`：

- `session_meta`: 会话元信息，包含 session id、cwd、git、base instructions。
- `turn_context`: 当前 cwd、workspace_roots、model、sandbox、approval policy。
- `event_msg`: UI/事件层消息，例如 `user_message`、`agent_message`、`token_count`。
- `response_item`: 模型消息、工具调用、工具结果、reasoning。

抽取用户和 AI 消息时，优先使用：

```text
line.type == "response_item"
payload.type == "message"
payload.role in ["user", "assistant"]
payload.content[].text
```

用户消息示例：

```json
{
  "type": "response_item",
  "payload": {
    "type": "message",
    "role": "user",
    "content": [
      {"type": "input_text", "text": "..."}
    ]
  }
}
```

助手消息示例：

```json
{
  "type": "response_item",
  "payload": {
    "type": "message",
    "role": "assistant",
    "content": [
      {"type": "output_text", "text": "..."}
    ]
  }
}
```

可作为兜底的 UI 事件：

```text
line.type == "event_msg"
payload.type == "user_message" or "agent_message"
payload.message
```

默认忽略：

- `payload.type == "reasoning"`：可能只有 encrypted_content，不作为普通对话。
- `payload.type == "function_call"`：工具调用。
- `payload.type == "function_call_output"`：工具结果。
- `event_msg token_count`：token 统计。

## Capture Parser

AgentOS 的 Codex capture hook 可以使用以下逻辑：

```python
import json
from pathlib import Path

def extract_codex_messages(session_file: str):
    messages = []
    for line in Path(session_file).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        obj = json.loads(line)
        payload = obj.get("payload") or {}

        if obj.get("type") != "response_item":
            continue
        if payload.get("type") != "message":
            continue

        role = payload.get("role")
        if role not in ("user", "assistant"):
            continue

        texts = []
        for part in payload.get("content") or []:
            if isinstance(part, dict) and "text" in part:
                texts.append(part["text"])

        if texts:
            messages.append({
                "timestamp": obj.get("timestamp"),
                "role": role,
                "text": "\n".join(texts),
            })

    return messages
```

查找最近 session：

```python
import json
from pathlib import Path

codex_home = Path.home() / ".codex"
threads = [
    json.loads(line)
    for line in (codex_home / "session_index.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
latest = max(threads, key=lambda x: x["updated_at"])
thread_id = latest["id"]
session_files = list((codex_home / "sessions").rglob(f"*{thread_id}.jsonl"))
```

## Difference From Claude Code

Claude Code transcript 通常更接近 message transcript，可以直接按 role/content 抽取。

Codex transcript 是 rollout event stream，需要先过滤：

```text
response_item -> payload.type == message -> role/content
```

不要把 `reasoning`、tool call、token_count 当作用户/助手消息。
```

## 第五步：兼容现有 Claude Skill 范式

如果项目已有 `.claude/skills` 或计划引入 `D:\claudeProjects\harness-skill-analysis\docs\paradigm` 下的范式，请按以下职责划分：

```text
.claude/skills/        = Claude Code 执行能力层
.claude/rules/         = Claude Code 加载优化层
agentos/               = 跨工具项目事实、计划索引、测试证据、治理状态
docs/plans/            = manual plan fallback / 可选 link stub
superpowers 默认目录   = superpowers 自己管理，不搬家
```

不要在 `agentos/` 里重复实现已有的 Claude skills。若存在以下 skill，只登记使用方式：

- `pre-pr-check`
- `tech-debt-scan`
- `sop-from-master`
- `multi-model-review`

`agentos/` 负责保存这些 skill 的输出索引、计划 ID、测试证据和 review 报告。

## 第六步：初始化测试体系

### `agentos/test/README.md`

写入：

```md
# Test System

本目录管理业务代码正确性的测试契约、测试策略、统一测试入口和测试报告。

`eval/` 验证 AgentOS 行为和 AI 系统表现；`test/` 验证业务代码正确性。

M/L 任务进入 BUILD 前必须先有 Test Contract。
```

### `agentos/test/strategy.md`

写入：

```md
# Test Strategy

## 测试分层

- Unit: 纯函数、schema、parser、hook、store、工具输入输出
- Integration: API 路由、SSE 流、upload -> task、配置加载、工具执行链
- Contract: API schema、SSE event schema、前后端协议类型、配置 schema
- Eval: Parse / RAG / Agent / domain-specific eval
- Manual: UI、管理后台、Trace、人工复核体验

## 按任务类型的最低要求

| 任务类型 | 必跑测试 |
|---|---|
| XS | 相关文件静态检查即可 |
| S | 相关单测 / build / lint |
| backend-feature | 单测 + 相关集成测试 + py_compile + lint |
| frontend-feature | lint + build + 关键交互 smoke |
| protocol-change | 后端协议测试 + 前端类型/build + SSE/协议解析用例 |
| config-change | 配置 schema 测试 + 审批/回滚验证 |
| agent/rag/ocr/parse | 对应 eval + 回归样本 |
| L 级重构 | baseline before/after + 全量测试 + eval delta |

## 原则

每条 Acceptance Criteria 必须映射到至少一种验证方式。
不能验证的 AC 必须说明原因和人工验收方式。
```

### `agentos/test/test-contract-template.md`

写入：

```md
# Test Contract

Plan ID:
Task:
Owner:
Date:

## Acceptance Criteria Mapping

| AC | 验证方式 | 测试层级 | 文件/命令 | 是否阻塞 |
|---|---|---|---|---|
| AC1 | TBD | unit/integration/contract/eval/manual | TBD | 是/否 |

## Required Test Layers

- [ ] Unit
- [ ] Integration
- [ ] Contract / Schema
- [ ] E2E / Smoke
- [ ] Eval
- [ ] Manual

## Negative Cases

- 空输入:
- 超大输入:
- 无效格式:
- 外部服务超时:
- DB/Cache/Network 异常:
- 并发/重复请求:
- 权限/审批失败:

## Regression Scope

本次改动可能影响：
- ...

## Commands

必须运行：
- ...

可选运行：
- ...

## Not Run

未运行项、原因和风险：
- ...
```

### `agentos/test/run-tests.ps1`

写入一个可编辑模板，不要编造项目命令。根据项目事实填充，未知处保留 `TBD`：

```powershell
param(
    [ValidateSet("backend", "frontend", "protocol", "eval", "full")]
    [string]$Profile = "full"
)

$ErrorActionPreference = "Stop"

switch ($Profile) {
    "backend" {
        Write-Host "Running backend tests..."
        # TODO: replace with project-specific backend commands
        # Example:
        # conda run -n payment-ai python -m pytest backend/tests/ -v
    }
    "frontend" {
        Write-Host "Running frontend checks..."
        # TODO: replace with project-specific frontend commands
        # Example:
        # Push-Location frontend; pnpm lint; pnpm build; Pop-Location
    }
    "protocol" {
        Write-Host "Running protocol/contract checks..."
        # TODO
    }
    "eval" {
        Write-Host "Running eval checks..."
        # TODO
    }
    "full" {
        & $PSCommandPath -Profile backend
        & $PSCommandPath -Profile frontend
        & $PSCommandPath -Profile protocol
        & $PSCommandPath -Profile eval
    }
}
```

### `agentos/debt/radar.md`

除普通技术债外，增加测试债：

```md
# Tech Debt Radar

技术债按 P0/P1/P2 管理。AI 可以帮助扫描和穷举，人负责判断优先级。

## Code Debt

### P0
- TBD

### P1
- TBD

### P2
- TBD

## Test Debt

### P0
- TBD

### P1
- TBD

### P2
- TBD

## 规则

M/L 任务 PLAN 阶段必须回答：

1. 本次需求是否能顺带消化某个技术债或测试债？
2. 如果能，消化哪一项？
3. 如果不能，为什么？
```

## 第七步：初始化高阶模型 Review

### `agentos/review/review-packet-template.md`

写入：

```md
# Review Packet

## 1. Task Background

这次需求要解决什么问题，用户/业务背景是什么。

## 2. Plan Reference

- Plan ID:
- Plan Source:
- Plan Snapshot / Path:

## 3. Acceptance Criteria

- [ ] AC1
- [ ] AC2
- [ ] AC3

## 4. Project Principles

摘录本次相关 principles：
- ...

## 5. Technical Context

相关架构：
- 后端模块:
- 前端模块:
- 协议/API/SSE:
- 配置/eval/数据库影响:

## 6. Changed Files

来自 git diff 的文件清单。

## 7. Diff Summary

按模块总结改了什么。

## 8. Test Evidence

### Commands Run
- ...

### Passed
- ...

### Failed
- ...

### Not Run
- ...

### Coverage / Eval Delta
- ...

### Risk
- ...

## 9. Human Review Focus

希望人工或高阶模型重点看的问题：
- 业务语义
- 架构边界
- 解析/交易/数据风险
- 协议一致性
- 测试充分性
```

### `agentos/skills/judge-review/SKILL.md`

写入：

```md
# Judge Review

## Trigger

用户说：
- judge review
- 高阶模型审查
- pre-pr judge
- 用更强模型 review

## Inputs

- Review Packet
- git diff
- `agentos/governance/principles.md`
- `agentos/knowledge/TECH.md`
- `agentos/review/judge-prompts/*.md`

## Review Dimensions

1. 需求符合度：实现是否满足 AC
2. 架构一致性：是否破坏分层和边界
3. 业务语义：是否误解产品/交易/解析逻辑
4. 协议一致性：前后端/API/SSE/schema 是否同步
5. 错误处理：异常、降级、超时、空数据
6. 测试充分性：是否只测 happy path
7. 安全与数据质量：密钥、客户数据、审计、配置转正
8. 技术债：是否引入新债，是否绕开既有 SOP

## Rules

- 默认只审查，不直接修改代码。
- 必须基于 Review Packet 和 diff。
- 不要只做风格检查。
- CRITICAL/HIGH 必须说明阻塞原因。

## Output

按 CRITICAL / HIGH / MEDIUM / LOW 输出。

每条必须包含：
- 文件/位置
- 问题
- 为什么重要
- 建议修复
- 是否阻塞合并
```

### `agentos/review/judge-prompts/protocol-judge.md`

写入：

```md
# Protocol Judge

你审查的是前后端协议一致性。

重点检查：

1. 后端 SSE event 是否和前端类型定义一致
2. API request/response schema 是否同步
3. store 是否能处理新增/变化字段
4. UI 是否处理 loading/error/empty/partial 状态
5. 是否存在后端返回但前端忽略、或前端期待但后端不返回的字段
6. 是否更新相关测试或验证说明

输出 CRITICAL/HIGH/MEDIUM/LOW。
```

### `agentos/review/judge-prompts/test-judge.md`

写入：

```md
# Test Judge

你审查的是测试充分性和验证证据。

重点检查：

1. 每条 AC 是否有测试或人工验证映射
2. 是否只测 happy path
3. 是否覆盖边界输入、异常路径、降级路径
4. eval delta 是否记录并解释
5. 未运行测试是否有合理原因和风险
6. 测试是否过度脆弱、只验证实现细节
7. 是否引入新的测试债

输出 CRITICAL/HIGH/MEDIUM/LOW。
```

## 第八步：初始化本地技能说明

### `agentos/skills/test-contract/SKILL.md`

写入：

```md
# Test Contract

## Trigger

用户说：
- 生成测试契约
- test contract
- 测试计划
- 测试门禁

## Purpose

在 BUILD 前定义本次任务如何证明正确性。

## Inputs

- Task request
- Plan snapshot
- Acceptance Criteria
- `agentos/test/strategy.md`
- project test/eval commands

## Output

生成或更新 Test Contract，路径建议：

`agentos/artifacts/<task-id>/test-contract.md`

必须包含：
- AC 到测试方式映射
- required test layers
- negative cases
- regression scope
- commands
- not-run risk
```

## 第九步：更新根入口

### 更新 `AGENTS.md`

如果 `AGENTS.md` 不包含 `agentos/engine/runbook.md`，在文件靠前位置追加：

```md
## AgentOS

本项目使用 `agentos/` 作为 AI Coding 治理中枢。

非 XS/S 小改动前，必须先读取：

1. `agentos/engine/runbook.md`
2. `agentos/plans/levels.md`
3. `agentos/governance/principles.md`
4. `agentos/knowledge/PRODUCT.md`
5. `agentos/knowledge/TECH.md`

M/L 任务必须有 Plan ID，并登记在 `agentos/plans/registry.md`。

M/L 任务进入 BUILD 前必须有 Test Contract。

提交前必须生成 Review Packet；需要高风险审查时，使用高阶模型 Judge Review。

进入后端工作继续读取 `backend/AGENTS.md`。
进入前端工作继续读取 `frontend/AGENTS.md`。
```

### 更新 `CLAUDE.md`

如果 `CLAUDE.md` 不包含 `agentos/engine/runbook.md`，追加类似内容：

```md
## AgentOS

Claude Code 可以使用自身 Plan Mode 起草计划，但 `.claude` 中的计划只是草稿。

M/L 任务在开始实现前，必须 promote 到：

- `agentos/plans/snapshots/P-*.md`

并登记到：

- `agentos/plans/registry.md`

M/L 任务必须先有：

- Plan ID
- Test Contract
- Review Packet

正式执行流程见：

- `agentos/engine/runbook.md`

Claude Code skills 是执行能力层；项目事实、计划索引和测试证据以 `agentos/` 为准。
```

## 第十步：初始化 Knowledge

根据 README 和已有 AGENTS/CLAUDE 内容生成：

- `agentos/knowledge/PRODUCT.md`
- `agentos/knowledge/TECH.md`
- `agentos/knowledge/PROJECT.md`
- `agentos/knowledge/IMPROVEMENT.md`

要求：

1. 不要空泛。
2. 必须包含本项目真实启动命令、架构边界、配置规则、测试/评测命令、LLM 使用边界。
3. 如果信息不确定，标记为 `TBD`，不要编造。
4. 不要写密钥或真实客户数据。

## 第十一步：初始化 quick changes

创建：

```text
agentos/artifacts/quick-changes/YYYY-MM.md
```

写入模板：

```md
# Quick Changes - YYYY-MM

用于记录 XS/S 小变更，避免污染 `docs/plans/`。

## 格式

### YYYY-MM-DD - <title>

Level: XS/S

Changed:
- ...

Verification:
- ...

Risk:
- ...
```

## 第十二步：初始化 review

### `agentos/review/pre-pr-checklist.md`

```md
# Pre-PR Checklist

## Change Level

- [ ] XS
- [ ] S
- [ ] M
- [ ] L

## Plan

- Plan ID:
- [ ] Not required because:

## Test Contract

- Path:
- [ ] Not required because:

## Scope

- Changed files:
- Affected backend modules:
- Affected frontend modules:
- Affected protocols/config/eval:

## Verification

- [ ] Backend check
- [ ] Frontend check
- [ ] Test runner
- [ ] Eval check
- [ ] Manual smoke test
- [ ] Active break test

## Review Packet

- Packet:
- Judge Review Report:
- [ ] Not required because:

## Risk

- Main risk:
- Rollback:
- Human review focus:
```

## 第十三步：初始化 hooks 文档

### `agentos/hooks/on-session-start.md`

```md
# Session Start

可选 hook。若当前 agent 支持 session start hook，可注入：

- `agentos/governance/principles.md`
- `agentos/engine/STATE.md`
- `agentos/knowledge/PRODUCT.md`
- `agentos/knowledge/TECH.md`

若 agent 不支持 hook，则通过 `AGENTS.md` / `CLAUDE.md` 显式要求读取。
```

### `agentos/hooks/on-session-end.md`

```md
# Session End

可选 hook。若当前 agent 支持 session end hook，可追加以下内容到 `agentos/corrections.log`：

- CORRECTION: 人纠正了 agent 的地方
- DECISION: 本次产生的重要决策和理由
- DISCOVERY: 新发现的项目事实
- TEST_DEBT: 本次发现但未解决的测试债

若 agent 不支持 hook，则由执行者在任务结束时手动追加。
```

## 第十四步：验证

初始化完成后输出报告：

```md
# AgentOS Init Report

## Created

列出新建文件。

## Updated

列出修改过的已有文件。

## Preserved

说明哪些现有文件未覆盖。

## Project Facts Extracted

列出抽取到的项目事实。

## Plan Compatibility

说明 superpowers、Claude Plan Mode、Codex、manual plan 如何登记。

## Test System

列出发现的测试/构建/eval 命令，以及尚待人工确认的命令。

## Review System

说明 Review Packet、Judge Review、高阶模型审查如何使用。

## Follow-ups

列出需要人工确认的 TBD。
```

## 禁止事项

- 不要删除现有计划。
- 不要移动 superpowers 计划。
- 不要把 `.claude` 私有计划直接当正式计划。
- 不要覆盖已有 `AGENTS.md` / `CLAUDE.md`。
- 不要提交 `.env`、密钥、真实客户数据。
- 不要把所有小需求强制塞进 `docs/plans/`。
- 不要凭空编造技术栈、命令、测试命令或业务规则。
- 不要让高阶模型只看 diff 而不知道需求背景。
- 不要让 M/L 任务在没有 Test Contract 的情况下进入 BUILD。
- 不要把 Review 当作测试的替代品。

## 完成标准

满足以下条件才算完成：

- `agentos/` 目录结构完整。
- 根 `AGENTS.md` 和 `CLAUDE.md` 都能引导到 AgentOS。
- superpowers / Claude Code Plan Mode / Codex / manual plan 都有兼容路径。
- XS/S/M/L 分级机制明确。
- M/L 任务有 Plan ID 规则。
- M/L 任务有 Test Contract 规则。
- 小需求有 quick-change 记录机制。
- 测试策略、测试契约、统一测试入口已建立。
- Review Packet 与高阶模型 Judge Review 机制已建立。
- Pre-PR 机制已建立。
- Knowledge 文件已基于项目事实初始化。
- 初始化报告已输出。
