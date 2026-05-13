# Vide Coding | 入门篇

type: Post
status: Published
date: 2026/04/02
tags: Vibe Coding
category: AI的艺术

# 相关概念

## SDD

## TDD

# 相关工具安装

## Claude Code
https://claude.com/product/claude-code

## CC插件

[https://github.com/affaan-m/everything-claude-code/blob/main/README.zh-CN.md](https://github.com/affaan-m/everything-claude-code/blob/main/README.zh-CN.md)

## CC-API Key管理

[https://github.com/farion1231/cc-switch](https://github.com/farion1231/cc-switch)

![image.png](Vide%20Coding%20%E5%85%A5%E9%97%A8%E7%AF%87/image.png)

[添加 codex作为Claude Code供应商后提示需要登录 · Issue #1997 · farion1231/cc-switch](https://github.com/farion1231/cc-switch/issues/1997#issuecomment-4230615566)

## 美化Windows控制台

[](https://zhuanlan.zhihu.com/p/690118041)

# 相关工具使用

### Hermes Agent

```powershell
# 安装wsl2
wsl --install -d Ubuntu
# 启动
wsl.exe -d Ubuntu
# 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

![image.png](Vide%20Coding%20%E5%85%A5%E9%97%A8%E7%AF%87/image%201.png)

## Claude Code

- 建立工作空间

```powershell
/add-dir <path>
```

## EveryThing CC

**第一步：安装插件**

```powershell
# 添加市场
/plugin marketplace add affaan-m/everything-claude-code

# 安装插件
/plugin install everything-claude-code@everything-claude-code
```

**第二步：安装规则（必需）**

> WARNING: **重要提示：** Claude Code 插件无法自动分发 `rules`，需要手动安装：
> 

```powershell
# 首先克隆仓库
git clone https://github.com/affaan-m/everything-claude-code.git

# 复制规则目录（通用 + 语言特定）
mkdir -p ~/.claude/rules
cp -r everything-claude-code/rules/common ~/.claude/rules/
cp -r everything-claude-code/rules/typescript ~/.claude/rules/   # 选择你的技术栈
cp -r everything-claude-code/rules/python ~/.claude/rules/
cp -r everything-claude-code/rules/golang ~/.claude/rules/
cp -r everything-claude-code/rules/perl ~/.claude/rules/

mkdir -p ~/.claude/agents
# 将代理复制到你的 Claude 配置
cp everything-claude-code/agents/*.md ~/.claude/agents/

mkdir -p ~/.claude/commands
# 将代理复制到你的 Claude 配置
cp everything-claude-code/commands/*.md ~/.claude/commands/

mkdir -p ~/.claude/skills
# 将代理复制到你的 Claude 配置
cp everything-claude-code/skills/*.md ~/.claude/skills/
```

## openspec

**`openspec init：初始化`**

控制台点击空格是选择

**propose `：需求`**

- `proposal.md`：描述“为什么要改”和“打算改什么”；
- `tasks.md`：列出实现步骤清单（后端、前端、测试等）；
- `specs/auth/spec.md`：描述这次变更对认证能力（auth）的**增量规范**。

```powershell
# 1. 新建变更脚手架
You: /opsx:propose add-logout-button
AI:  Created openspec/changes/add-logout-button/
     Ready to create: proposal
```

**ff：快速生成**

```powershell
# 2. 快速生成所有规划制品（提案、规范、设计、任务）
You: /opsx:ff
AI:  Creating all planning artifacts...
     ✓ proposal.md ✓ specs/ ✓ design.md ✓ tasks.md
     Ready for implementation!
     
openspec/changes/add-user-login/
├── proposal.md 
├── tasks.md
└── specs/
    └── auth/
        └── spec.md
```

**`apply：执行`**

```powershell
# 3. 执行任务，实现功能
You: /opsx:apply
AI:  Working through tasks...
     ✓ 新增头部退出按钮 ✓ 实现会话清理 ✓ 增加确认弹窗
     All tasks complete!
```

**`archive：归档`** 

```powershell
# 5. 归档变更，完成开发
You: /opsx:archive
AI:  ✓ Merged specs ✓ Archived change
```

**Exploratory:探索模式**

```powershell
# 1. 启动探索模式，梳理问题
You: /opsx:explore
AI:  What would you like to explore?
You: 想优化页面加载性能，但不知道瓶颈在哪

AI:  分析后发现3个核心瓶颈：
     1. 未优化的大尺寸图片 2. ProductList同步数据请求 3. 上下文变更导致的重复渲染
     请问优先解决哪个？
You: 先解决数据请求问题

# 2. 基于探索结果，新建变更
You: /opsx:new optimize-product-list-fetching
AI:  Created change. Ready to create: proposal

# 3. 逐步骤生成规划制品，可随时调整
You: /opsx:continue
AI:  基于探索结果创建提案... Ready to create: specs, design
You: /opsx:continue
AI:  Creating specs... # 可继续执行continue，直到生成所有需要的制品

```

**并行**

```powershell
# 1. 正在开发暗黑模式，突发登录跳转bug需要修复
You: /opsx:new fix-login-redirect
AI:  Created openspec/changes/fix-login-redirect/

# 2. 快速生成bug修复的规划制品
You: /opsx:ff
AI:  ✓ Created planning artifacts

# 3. 实现bug修复，完成后归档
You: /opsx:apply
AI:  完成登录跳转修复！
You: /opsx:archive
AI:  ✓ Archived fix-login-redirect

# 4. 切回原任务，继续开发暗黑模式
You: /opsx:apply add-dark-mode
AI:  Resuming add-dark-mode... Picking up at task 2.3: Update Header...

/opsx:bulk-archive批量归档
```

## superpowers vs Everything Claude Code

[](https://zhuanlan.zhihu.com/p/2005567847959658521)

**superpower** 

## Figma-Context-MCP使用

Figma-Context-MCP 是一个 Model Context Protocol (MCP) 服务器工具，用于将 Figma 设计稿的布局、样式和组件信息转化为 AI 编码助手（如 Cursor）可理解的格式，从而实现“设计 → 代码”的智能转换。

---

核心用途

- 让 AI 编码助手精准理解 Figma 设计稿
- 自动生成符合设计意图的 React、Vue、Tailwind CSS 等前端代码
- 支持 组件级提取、样式转换、图片下载、响应式布局推断 等功能

---

使用步骤（快速上手）

1. 准备环境
    - 安装 Node.js ≥ 18.0.0
    - 安装 Git 和包管理器（推荐 `pnpm`）
2. 克隆并安装项目
    
    ```bash
    git clone <https://gitcode.com/gh\\_mirrors/fi/Figma-Context-MCP>
    cd Figma-Context-MCP
    pnpm install  或 npm install
    ```
    
3. 配置 Figma API 密钥
    - 登录 [Figma 账号](https://figma.com/) → Settings → Personal access tokens → 创建新令牌
    - 在项目根目录创建 `.env` 文件，填入：
    
    ![image.png](Vide%20Coding%20%E5%85%A5%E9%97%A8%E7%AF%87/image%202.png)
    
4. 启动本地 MCP 服务器
    
    ```bash
    pnpm start  默认运行在 <http://localhost:3333>
    ```
    
5. 在 Cursor 中添加 MCP 服务器
    - 打开 Cursor → 设置 → MCP 服务器 → “Add new MCP server”
    - 填写：
        - Name: `Figma MCP`
        - Type: `sse`
        - Server URL: `http://localhost:3333/sse\\`
    - 连接成功后，状态显示为 已连接，并列出工具：`get-file`、`get-node`
6. 获取 Figma 设计链接
    - 在 Figma 中选中目标组件/页面 → 右键 → Copy link to selection（或按 `⌘L` / `Ctrl+L`）
7. 在 Cursor 中使用 AI 生成代码
    - 将 Figma 链接粘贴到 Cursor 聊天窗口
    - 输入指令，例如：

> “请根据这个 Figma 设计生成 React + Tailwind CSS 的登录页面代码”
> 

AI 将自动调用 Figma-Context-MCP 获取设计数据，并生成高精度代码 。

---

高级功能与技巧

- 精准选择：优先选择 Frame 或组件，而非整个页面，减少上下文噪声
- 命名规范：Figma 中使用清晰命名（如 `Button/Primary`），有助于 AI 生成可读代码
- 使用组件库：Figma 基础组件会被自动转换为可复用的前端组件
- 性能优化：
    - 启用缓存（默认 5 分钟内存缓存 + 24 小时智能缓存）
    - 控制请求频率（避免触发 Figma API 限流）
- 团队协作：统一配置模板，使用环境变量管理 FIGMA\_API\_KEY

---

常见问题排查

- 连接失败：
    - 检查 `pnpm start` 是否正常运行
    - 确认 `localhost:3333/sse` 可访问
    - 验证 Figma API Token 是否有效
- 工具未显示：
    - 确保 Cursor 支持 MCP 协议（需最新版）
    - 重启 Cursor 或重新添加服务器

---

官方资源

- 项目地址：[Figma-Context-MCP](https://gitcode.com/gh_mirrors/fi/Figma-Context-MCP)
- GitHub 镜像（含优化）：[1yhy/Figma-Context-MCP](https://github.com/1yhy/Figma-Context-MCP)
- 文档与贡献指南：查看项目中的 `README.md`、`CONTRIBUTING.md`

通过以上配置，即可实现 Figma 与 AI 编码工具的无缝集成，大幅提升设计到开发的效率。