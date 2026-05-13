# Vide Coding | Claude Code优化篇

type: Post
status: Draft
date: 2026/04/28

# 前言

决定彻底抛弃cursor，前面转向claude code+自费国内外大模型的方案，公司每月给的20$的额度基本两天就用了，实在是不够用啊！！

# Claude Code

言归正传，从claude code的配置开始讲起

无交互启动

- 使用 `--headless` 模式运行 Claude Code，无交互后台执行

## 目录结构

### 1. 会话与历史相关

| 目录/文件 | 作用说明 |
| --- | --- |
| `sessions/` | 保存所有会话的完整上下文，包括对话历史、文件修改记录、会话状态，相当于 Claude Code 的「会话存档」。 |
| `session-data/` | 存储当前活跃会话的临时数据，比如对话片段、工具调用缓存、中间状态。 |
| `file-history/` | 保存文件修改的版本历史，相当于 Claude Code 内置的轻量「文件快照/撤销历史」，可以恢复之前的文件内容。 |
| `history.jsonl` | 所有会话的历史记录汇总，JSONL 格式，包含对话、命令执行记录，可用于回溯或分析会话行为。 |

---

### 2. 缓存与性能优化

| 目录/文件 | 作用说明 |
| --- | --- |
| `cache/` | 通用缓存目录，比如文件解析结果、API 响应缓存、工具调用结果缓存，提升后续操作速度。 |
| `downloads/` | Claude Code 自动下载的临时文件，比如依赖、脚本、模型相关资源。 |
| `paste-cache/` | 粘贴内容的临时缓存，比如你复制的代码片段、文本，会在这里暂存以支持跨会话粘贴。 |
| `shell-snapshots/` | 保存终端（shell）会话的快照，比如命令执行前后的环境、输出结果，用于调试或复现终端操作。 |

---

### 3. 任务与工作流相关

| 目录/文件 | 作用说明 |
| --- | --- |
| `tasks/` | 存储 Claude Code 后台任务的定义和状态，比如你触发的异步任务、计划任务。 |
| `plans/` | 保存 Claude Code 生成的「计划」文件，比如任务拆解方案、执行步骤规划，支持后续复用或修改。 |
| `projects/` | 项目级别的配置和状态，比如你打开过的项目、项目专属的规则/设置，支持多项目隔离。 |
| `link-works-tracking/` | 跨文件/跨模块的依赖追踪数据，记录文件间的引用关系、调用链，用于代码理解和重构辅助。 |

---

### 4. 扩展与能力增强

| 目录/文件 | 作用说明 |
| --- | --- |
| `plugins/` | 存放第三方插件/扩展，比如自定义工具、语言支持、集成功能，用来扩展 Claude Code 的能力。 |
| `skills/` | 存储 Claude Code 的「技能」定义，比如自定义命令、工作流模板、常用任务的预设。 |
| `hooks/` | 钩子脚本目录，类似 Git hooks，可配置在特定事件（如提交、会话开始/结束）触发时自动执行的脚本。 |
| `homunculus/` | Claude Code 内部使用的「代理/子进程」相关数据，比如子代理（sub-agent）的状态、任务数据。 |

---

### 5. 监控与统计相关

| 目录/文件 | 作用说明 |
| --- | --- |
| `metrics/` | 性能指标和统计数据，比如会话耗时、Token 消耗、工具调用次数，用于分析 Claude Code 的使用情况。 |
| `telemetry/` | 遥测数据，包含匿名的使用统计、错误日志（取决于你的隐私设置），用于产品优化。 |
| `cost-tracker.log` | 成本追踪日志，记录每次会话/工具调用的 Token 消耗、费用估算，方便你控制成本。 |
| `bash-commands.log` | 所有终端命令执行的日志，包含命令内容、执行结果、退出码，可用于排查命令执行问题。 |

---

### 6. 规则与配置相关

| 目录/文件 | 作用说明 |
| --- | --- |
| `rules/` | 自定义规则目录，比如 Fact-Forcing Gate 这类校验规则、代码审查规则、行为约束，用来限制或引导 Claude Code 的行为。 |
| `settings.json` | Claude Code 的全局配置文件，比如 API 密钥、默认模型、编辑器设置、隐私选项等。这个跟`CLAUDE.md` 一样全局、项目、个人都能创建 |
| `CLAUDE.md` | 项目级别的 Claude Code 配置文件，放在项目根目录，定义该项目的专属规则、上下文、命令模板。 |

---

### 7. 备份相关

| 目录/文件 | 作用说明 |
| --- | --- |
| `backups/` | 自动备份目录，保存会话、文件、配置的备份，防止数据丢失。 |

---

### 💡 常见场景操作指南

- **会话卡顿/异常**：可以删除 `sessions/`、`session-data/` 目录，重置会话状态，不会影响你的代码文件。
- **清理空间**：可以安全删除 `cache/`、`downloads/`、`telemetry/`、`metrics/` 目录，不会影响核心功能。
- **成本控制**：查看 `cost-tracker.log` 可以了解哪些任务消耗了大量 Token，针对性优化。
- **自定义行为**：修改 `rules/`、`hooks/` 或项目根目录的 `CLAUDE.md`，可以实现类似你之前 Fact-Forcing Gate 的自定义校验。

---

如果你需要，我可以帮你写一个一键清理缓存/会话的脚本，或者根据你的工作流配置对应的 `rules/` 和 `hooks/`，要帮你弄吗？

## claude code自动模式

CLI 开启方式是：

> claude –enable-auto-mode
> 

进入会话后，可以按 `Shift + Tab` 切换到 `Auto` 模式。

经验证上面这种方式不起作用，可以用下面的命令强制进入

> claude --dangerously-skip-permissions
> 

## CLAUDE.md

这个配置可以配置在这几个个范围内，Claude Code 启动时，会从当前目录**向上遍历**到文件系统根目录，加载沿途所有的 CLAUDE.md。这意味着在 monorepo 里，子包目录下的 CLAUDE.md 会在你进入该子包时自动生效。

- 全局：~/.claude/CLAUDE.md
- 规则：`.claude/rules/*.md`
- 项目：xx/CLAUDE.md
- 模块：
    - xx/xx-backend/CLAUDE.md
    - xx/xx-frontend/CLAUDE.md
- 个人本地：xx**/CLAUDE.local.md（不提交）**

## Memory

每个agent再开启时，实际上都是一个七秒钟的鱼，他压根不知道你上一次的约束，上次说过的下次还得说，这时就得有个memory告诉上次有什么新的规定。这不是一个配置，而是claude code自己进化的一个机制

**由交互沉淀、经验导向、未来可能复用**

```powershell
~/.claude/projects/<项目>/memory/
  MEMORY.md           # 主记忆文件，每次会话启动时加载
  debugging.md        # 调试经验（按主题拆分）
  patterns.md         # 代码模式
  api-conventions.md  # API 约定
```

## sub-agent

创建子代理有三种方式

- 代码创建，python导入claude-sdk，通过代码创建
- 文档创建，将代理定义为目录中的 Markdown 文件**`.claude/agents/`**
- **内置通用功能`general-purpose`**

| **地点** | **范围** | **优先事项** | **如何创建** |
| --- | --- | --- | --- |
| 管理设置 | 全组织范围 | 1（最高） | 通过[**托管设置部署**](https://code.claude.com/docs/en/settings) |
| **`--agents`**CLI 标志 | 当前会话 | 2 | 启动 Claude Code 时传递 JSON 数据 |
| **`.claude/agents/`** | 当前项目 | 3 | 交互式或手动 |
| **`~/.claude/agents/`** | 你的所有项目 | 4 | 交互式或手动 |
| 插件**`agents/`**目录 | 插件已启用 | 5（最低） | 通过[**插件安装**](https://code.claude.com/docs/en/plugins) |

## MCP

cc连接支持连接三种MCP服务器

- 远程HTTP服务器
- 远程SSE服务器
- 本地stdio服务器

```powershell
# 基本语法
claude mcp add [options] <name> -- <command> [args...]

# 真实示例：添加 Airtable 服务器
claude mcp add --transport stdio --env AIRTABLE_API_KEY=YOUR_KEY airtable \
  -- npx -y airtable-mcp-server
  
# 例如下载dbhub后连接
npx @bytebase/dbhub@latest --transport http --port 8080 --demo

# 连接本地dbhub
claude mcp add --transport http dbhub http://localhost:8080/mcp
```

将连接信息配置到文件中（多数据源中直接用dbhub.toml即可）

**%APPDATA%\Claude\claude_desktop_config.json**

```powershell
{
  "mcpServers": {
    "dbhub": {
      "command": "npx",
      "args": [
        "@bytebase/dbhub@latest",
        "--transport",
        "stdio",
        "--dsn",
        "postgres://user:password@localhost:5432/dbname"
      ]
    }
  }
}
```

### dbhub多数据源

[TOML Configuration - DBHub, Minimal Database MCP Server](https://dbhub.ai/config/toml)

在项目根目录下创建dbhub.toml

```powershell
  [[sources]]
  id = "raven-pre"
  description = "Raven 风控引擎预发数据库（MySQL magpie 库）"
  dsn = "mysql://user:password@ip:port/database"
  lazy = true
  connection_timeout = 10
  query_timeout = 30

  [[tools]]
  name = "execute_sql"
  source = "raven-pre"
  readonly = true
  max_rows = 1000
```

随后项目根目录下启动mcp

```powershell
npx @bytebase/dbhub@latest --transport http --port 8080
```

## plugin

这些插件起到核心作用的有两个：rule与skill，前者被动触发，后者主动触发或cc询问后是否使用后确认使用

- **gstack**：做什么（产品方向）、做成什么样（QA / 设计）、怎么上线（发布）→ **偏产品与交付**。
- **Superpowers**：怎么写好代码（流程、TDD、规范）→ **偏工程质量**。
- **ECC**：全栈工具箱（各种语言 / 工具 / 重构）→ **偏全能编码**。

### superpowers

### everything claude code

### openspec

### gstack

安装

```powershell
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack

cd ~/.claude/skills/gstack

npm install

npx playwright install chrome
```

使用

- `/plan-ceo-review`创始人模式：重新思考问题，寻找10星级产品
- `/plan-eng-review`工程经理模式：锁定架构、数据流、图表、边缘情况
- `/review`资深工程师模式：偏执代码审查，发现生产级bug
- `/ship`发布工程师模式：一键发布，自动化最后里程
- `/browse`QA工程师模式：浏览器自动化，为AI提供眼睛

> 让AI自动打开浏览器测试你的网页（超好用）
/browse https://你的网址.com
> 
- `/qa`QA负责人模式：系统化测试，健康评分，回归检测
- `/setup-browser-cookies`会话管理器：从真实浏览器导入cookie
- `/retro`工程经理模式：团队感知回顾，数据驱动分析
- `/document-release`技术文档模式：自动更新项目文档
- `/qa-only`QA报告模式：纯粹bug报告，无代码更改
- /office-hours:让AI帮你理清需求