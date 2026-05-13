# Vide Coding | Everything Claude Code 功能完整指南

type: Post
status: Published
date: 2026/04/02
tags: Vibe Coding
category: AI的艺术

---

---

## 快速开始

### 核心工作流

```bash
# 功能开发完整流程
/prp-prd          # 1. 生成产品需求文档
/prp-plan         # 2. 创建实现计划
/prp-implement    # 3. 执行实现
/prp-commit       # 4. 智能提交
/prp-pr           # 5. 创建 Pull Request

# TDD 测试驱动开发
/plan             # 规划任务
/tdd              # TDD 工作流 (RED→GREEN→REFACTOR)
/code-review      # 代码审查
/verify           # 质量验证

# 会话管理
/save-session     # 保存会话状态
/resume-session   # 恢复之前会话
```

### 常用命令速查

| 目的 | 命令 |
| --- | --- |
| 写新功能 | `/plan` → `/tdd` |
| 构建失败 | `/build-fix` 或 `/go-build`、`/rust-build` |
| 代码审查 | `/code-review` |
| 查文档 | `/docs` |
| 清理代码 | `/refactor-clean` |
| 性能优化 | `/benchmark` |

---

## Agents 专用代理

**Agents 是专门化的子代理，用于委托特定任务。系统会自动选择合适的 agent。**

### 🏗️ 架构与规划类

| Agent | 模型 | 用途 | 自动触发场景 |
| --- | --- | --- | --- |
| **architect** | opus | 系统设计、技术决策、ADR 文档 | 架构决策、框架选型 |
| **planner** | opus | 功能规划、任务分解 | 复杂功能开发前 |
| **gan-planner** | opus | 产品规格生成 | GAN 工作流 |

### 🔧 Build 错误修复类

| Agent | 适用语言/场景 | 处理问题 |
| --- | --- | --- |
| **build-error-resolver** | TypeScript/JavaScript | 类型错误、编译失败、依赖问题 |
| **cpp-build-resolver** | C++/CMake | 编译、链接、模板实例化错误 |
| **go-build-resolver** | Go | 编译、go vet、staticcheck 问题 |
| **java-build-resolver** | Java/Maven/Gradle | 编译、注解处理器、依赖问题 |
| **kotlin-build-resolver** | Kotlin/Gradle | 编译、detekt 问题 |
| **rust-build-resolver** | Rust/Cargo | 借用检查器、生命周期、依赖 |
| **pytorch-build-resolver** | PyTorch | 张量形状、CUDA、梯度问题 |

### 👀 代码审查类

| Agent | 专长领域 |
| --- | --- |
| **code-reviewer** | 通用审查、安全检测、SQL/XSS/硬编码秘密 |
| **typescript-reviewer** | 类型安全、异步正确性、React/Next.js |
| **python-reviewer** | PEP 8、类型提示、Django/FastAPI |
| **go-reviewer** | 惯用 Go、并发安全、错误处理 |
| **rust-reviewer** | 所有权、生命周期、unsafe 代码 |
| **java-reviewer** | Spring Boot、JPA、字段注入反模式 |
| **kotlin-reviewer** | 协程安全、Compose、Flow 反模式 |
| **cpp-reviewer** | 内存安全、现代 C++、RAII |
| **flutter-reviewer** | Widget 最佳实践、状态管理 |

### 🛡️ 领域专家审查类

| Agent | 专长 |
| --- | --- |
| **security-reviewer** | OWASP Top 10、秘密检测、注入攻击、不安全加密 |
| **database-reviewer** | PostgreSQL 优化、RLS 安全、索引、Supabase |
| **healthcare-reviewer** | CDSS 准确性、PHI 合规、HIPAA、审计追踪 |

### 📚 文档与通信类

| Agent | 用途 |
| --- | --- |
| **doc-updater** | 生成 codemaps、更新 README 和指南 |
| **docs-lookup** | Context7 MCP 文档查询、API 示例 |
| **chief-of-staff** | 邮件/Slack 分类、起草回复 |

### 🧪 测试类

| Agent | 用途 |
| --- | --- |
| **tdd-guide** | TDD 工作流、Red-Green-Refactor、80%+ 覆盖率 |
| **e2e-runner** | Playwright E2E、测试旅程、产物管理 |

### 🧹 优化与维护类

| Agent | 用途 |
| --- | --- |
| **performance-optimizer** | 性能分析、Bundle 优化、内存泄漏检测 |
| **refactor-cleaner** | 死代码清理 (knip/depcheck/ts-prune) |
| **harness-optimizer** | Agent harness 配置优化 |
| **loop-operator** | 自主 agent 循环监控 |

### 🔓 开源发布流水线

| Agent | 阶段 | 用途 |
| --- | --- | --- |
| **opensource-forker** | 1 | 剥离敏感信息、生成.env.example |
| **opensource-sanitizer** | 2 | 验证清理、生成 PASS/FAIL 报告 |
| **opensource-packager** | 3 | 生成 [CLAUDE.md](http://claude.md/)、LICENSE、[CONTRIBUTING.md](http://contributing.md/) |

### 🎯 GAN Harness

| Agent | 用途 |
| --- | --- |
| **gan-generator** | 实现功能、根据反馈迭代 |
| **gan-evaluator** | Playwright 测试、按标准评分 |

---

## Skills 技能库

### 🔁 自动化与 Agent 编排

| Skill | 用途 | 调用方式 |
| --- | --- | --- |
| **autonomous-agent-harness** | 持久化自主 agent 系统 | `/loop` |
| **continuous-learning** | 自动从会话提取模式 | Stop hook |
| **continuous-learning-v2** | Instinct 学习、置信度评分 | 自动 |
| **dmux-workflows** | tmux 多 agent 并行管理 | `/dmux` |

### 🏗️ 架构与工程

| Skill | 用途 |
| --- | --- |
| **agentic-engineering** | Eval 优先、成本感知模型路由 |
| **ai-first-engineering** | AI 优先团队工程模式 |
| **architecture-decision-records** | 自动创建 ADR 文档 |
| **hexagonal-architecture** | 六边形架构模式 |
| **backend-patterns** | REST API、仓库/服务层 |

### 📦 语言特定技能

### Python

- `python-patterns` - Python 惯用法
- `python-testing` - pytest、TDD
- `django-patterns` - Django 架构
- `django-security` - Django 安全
- `django-tdd` - Django 测试
- `pytorch-patterns` - PyTorch 深度学习

### JavaScript/TypeScript

- `coding-standards` - 通用编码标准
- `frontend-patterns` - React/Next.js 模式
- `bun-runtime` - Bun 运行时
- `nextjs-turbopack` - Next.js 优化

### Go

- `golang-patterns` - 惯用 Go
- `golang-testing` - Go 测试

### Java/Kotlin

- `java-coding-standards` - Java 标准
- `springboot-patterns` - Spring Boot
- `springboot-security` - Spring Security
- `kotlin-patterns` - Kotlin 惯用法
- `kotlin-coroutines-flows` - 协程/Flow
- `compose-multiplatform-patterns` - Compose KMP

### PHP

- `laravel-patterns` - Laravel 架构
- `laravel-security` - Laravel 安全
- `laravel-tdd` - Laravel 测试

### Rust/C++

- `rust-patterns` - Rust 惯用法
- `rust-testing` - Rust 测试
- `cpp-coding-standards` - C++ 标准
- `cpp-testing` - GoogleTest

### 🧪 测试与质量

| Skill | 用途 |
| --- | --- |
| **tdd-workflow** | TDD、80%+ 覆盖率 |
| **e2e-testing** | Playwright E2E、POM |
| **verification-loop** | 质量验证循环 |
| **security-review** | 安全检查清单 |
| **benchmark** | 性能基线检测 |
| **canary-watch** | 部署后监控 |

### 🌐 API 与集成

| Skill | 用途 |
| --- | --- |
| **api-design** | REST API 设计 |
| **claude-api** | Anthropic API/SDK |
| **documentation-lookup** | Context7 MCP 文档 |
| **exa-search** | 神经网络搜索 |
| **deep-research** | 多源深度研究 |

### 💾 数据库

| Skill | 用途 |
| --- | --- |
| **postgres-patterns** | PostgreSQL 优化 |
| **clickhouse-io** | ClickHouse 分析 |
| **database-migrations** | 零停机迁移 |

### 📝 内容创作

| Skill | 用途 |
| --- | --- |
| **article-writing** | 长篇文章写作 |
| **content-engine** | 跨平台内容 |
| **crosspost** | 多平台分发 |

### 💼 业务运营

| Skill | 用途 |
| --- | --- |
| **customer-billing-ops** | 客户账单 |
| **carrier-relationship-management** | 承运商管理 |
| **customs-trade-compliance** | 海关合规 |
| **inventory-demand-planning** | 库存计划 |

### 🏥 医疗专业

| Skill | 用途 |
| --- | --- |
| **healthcare-emr-patterns** | EMR 系统 |
| **healthcare-cdss-patterns** | 临床决策支持 |
| **healthcare-phi-compliance** | HIPAA 合规 |

### 🎨 设计与媒体

| Skill | 用途 |
| --- | --- |
| **design-system** | 设计系统生成 |
| **fal-ai-media** | AI 媒体生成 |
| **video-editing** | AI 视频编辑 |
| **remotion-video-creation** | Remotion 编程视频 |

### 🛠️ 基础设施

| Skill | 用途 |
| --- | --- |
| **docker-patterns** | Docker Compose |
| **deployment-patterns** | CI/CD、部署 |
| **git-workflow** | Git 工作流 |

### 📊 元技能

| Skill | 用途 | 调用 |
| --- | --- | --- |
| **configure-ecc** | ECC 安装器 | `/configure-ecc` |
| **context-budget** | 上下文审计 | `/context-budget` |
| **skill-health** | 技能健康度 | `/skill-health` |
| **codebase-onboarding** | 代码库入职 | `/codebase-onboarding` |

---

## Commands 命令参考

### 🚀 产品需求与规划 (PRP)

```bash
/prp-prd          # 交互式 PRD 生成
/prp-plan         # 创建实现计划
/prp-implement    # 执行计划
/prp-commit       # 智能提交
/prp-pr           # 创建 GitHub PR
```

### 🧪 TDD 测试

```bash
/tdd              # TDD 工作流
/test-coverage    # 覆盖率分析
/e2e              # E2E 测试
/{lang}-test      # 语言特定 TDD (cpp/go/kotlin/rust)
```

### 🔧 Build 修复

```bash
/build-fix        # 通用构建修复
/cpp-build        # C++ 构建
/go-build         # Go 构建
/kotlin-build     # Kotlin 构建
/rust-build       # Rust 构建
/gradle-build     # Gradle 构建
```

### 👀 代码审查

```bash
/code-review      # 本地修改或 PR 审查
/cpp-review       # C++ 审查
/go-review        # Go 审查
/kotlin-review    # Kotlin 审查
/python-review    # Python 审查
/rust-review      # Rust 审查
/santa-loop       # 对抗式双审查
```

### 🤖 多模型协作

```bash
/multi-plan       # 多模型规划
/multi-execute    # 多模型执行
/multi-workflow   # 完整多模型工作流
/multi-backend    # 后端开发 (Codex)
/multi-frontend   # 前端开发 (Gemini)
```

### 📚 会话管理

```bash
/sessions         # 管理会话历史
/save-session     # 保存会话
/resume-session   # 恢复会话
/checkpoint       # 检查点管理
```

### 🧠 学习系统

```bash
/learn            # 提取模式
/learn-eval       # 带评估的学习
/instinct-status  # 查看已学模式
/instinct-import  # 导入模式
/instinct-export  # 导出模式
/promote          # 升级为全局
/prune            # 清理过期
/evolve           # 进化为技能/命令
```

### 🔍 质量与维护

```bash
/verify           # 质量管道
/quality-gate     # 手动质量检查
/refactor-clean   # 死代码清理
/update-codemaps  # 生成架构文档
/update-docs      # 同步文档
/harness-audit    # 仓库健康审计
```

### 🎯 GAN 自主开发

```bash
/gan-build        # 三代理构建循环
/gan-design       # 前端设计循环
```

### 🔧 工具类

```bash
/plan             # 创建计划
/aside            # 快速边车问题
/model-route      # 推荐模型
/skill-create     # 从 git 生成技能
/docs             # 文档查询
/pm2              # PM2 服务配置
```

---

## Rules 规则体系

### 📜 通用规则 (language-agnostic)

| 规则 | 核心要求 |
| --- | --- |
| [**agents.md**](http://agents.md/) | 10+ 代理定义、并行执行 |
| [**code-review.md**](http://code-review.md/) | 函数<50 行、文件<800 行、80%+ 覆盖率 |
| [**coding-style.md**](http://coding-style.md/) | **不可变性**、小文件、显式错误处理 |
| [**development-workflow.md**](http://development-workflow.md/) | 研究→计划→TDD→审查→提交 |
| [**git-workflow.md**](http://git-workflow.md/) | Conventional Commits |
| [**hooks.md**](http://hooks.md/) | PreToolUse/PostToolUse/Stop 钩子 |
| [**patterns.md**](http://patterns.md/) | 仓库模式、API 响应格式 |
| [**performance.md**](http://performance.md/) | 模型选择、上下文管理 |
| [**security.md**](http://security.md/) | 强制安全检查清单 |
| [**testing.md**](http://testing.md/) | 80% 最低覆盖率、TDD |

### 🌍 语言特定规则

每个语言包含 5 个规则文件：

| 语言 | 规则文件 |
| --- | --- |
| TypeScript | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Python | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Go | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Rust | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Java | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Kotlin | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Swift | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| C# | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| PHP | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| C++ | `coding-style`, `hooks`, `patterns`, `security`, `testing` |
| Perl | `coding-style`, `hooks`, `patterns`, `security`, `testing` |

每个规则文件内容：

- `coding-style.md` - 编码风格、格式化、命名约定
- `hooks.md` - 自动格式化、类型检查钩子
- `patterns.md` - 语言特定设计模式
- `security.md` - 秘密管理、注入防护
- `testing.md` - 测试框架、覆盖率工具

### 🇨🇳 中文翻译

`rules/zh/` 目录包含所有通用规则的完整中文翻译。

---

## 典型使用场景

### 场景 1: 新功能开发

```bash
# 1. 需求分析
/prp-prd

# 2. 规划实现
/prp-plan

# 3. TDD 实现
/tdd

# 4. 代码审查
/code-review

# 5. 提交
/prp-commit

# 6. 创建 PR
/prp-pr
```

### 场景 2: Bug 修复

```bash
# 1. 规划修复方案
/plan

# 2. 写复现测试
/tdd

# 3. 实现修复

# 4. 验证
/verify
```

### 场景 3: 构建失败

```bash
# 直接调用对应语言的构建修复
/build-fix        # 通用
/go-build         # Go
/rust-build       # Rust
/cpp-build        # C++
```

### 场景 4: 代码审查

```bash
# 本地未提交修改
/code-review

# GitHub PR 审查
/code-review #123
/code-review <https://github.com/org/repo/pull/123>
```

### 场景 5: 学习新技术

```bash
# 查询文档
/docs

# 或使用 docs-lookup agent
```

### 场景 6: 性能优化

```bash
# 性能分析
/performance-optimizer

# 建立基线
/benchmark

# 清理代码
/refactor-clean
```

### 场景 7: 长期项目管理

```bash
# 每天结束
/save-session

# 次日继续
/resume-session
```

### 场景 8: 关键变更审查

```bash
# 对抗式双审查
/santa-loop
```

### 场景 9: 准备开源发布

```bash
# 自动处理
opensource-forker → opensource-sanitizer → opensource-packager
```

---

## 配置与调用

### 1. 直接输入命令

在 Claude Code 控制台中直接输入：

```bash
/plan 实现用户登录功能
/tdd 添加用户注册
/code-review
/verify
```

### 2. 自动触发 (Hooks)

在 `~/.claude/settings.json` 配置：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": { "tool": "Write", "path": "*.ts$" },
        "command": "/code-review"
      }
    ],
    "Stop": [
      {
        "command": "/save-session"
      }
    ]
  }
}
```

### 3. Agent 工具调用

```markdown
# 指定使用特定 agent
使用 planner agent 规划实现方案

# 或
用 security-reviewer agent 检查这段代码
```

### 4. 模型路由

```bash
# 让系统推荐最佳模型
/model-route 实现工具函数
/model-route 设计微服务架构
```

---

## 附录

### 项目结构

```
everything-claude-code/
├── agents/          # 37 个专业代理
├── skills/          # 150+ 技能
├── commands/        # 70+ 命令
├── rules/           # 73 个规则文件
│   ├── common/      # 通用规则
│   ├── zh/          # 中文翻译
│   └── {language}/  # 语言特定规则
├── hooks/           # 触发式自动化
├── scripts/         # 工具脚本
└── tests/           # 测试套件
```

### 模型分配

| 模型 | Agent 数量 | 适用场景 |
| --- | --- | --- |
| **sonnet** | 27 | 主要编码工作 |
| **opus** | 8 | 复杂推理、架构决策 |
| **haiku** | 1 | 轻量任务、文档 |

### 核心原则

1. **不可变性** - 创建新对象，永不修改现有对象
2. **小文件** - 200-400 行典型，800 行最大
3. **80%+ 测试覆盖率** - 强制要求
4. **TDD** - 先写测试，再实现
5. **无硬编码秘密** - 使用环境变量
6. **显式错误处理** - 永不静默失败

---

*文档生成时间：2026-04-02*