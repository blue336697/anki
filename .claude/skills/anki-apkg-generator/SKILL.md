---
name: anki-apkg-generator
description: 从算法学习笔记生成 Anki APKG 牌组。处理笔记分析、卡片设计（Basic/Cloze）、图片嵌入和 APKG 打包。当用户要求创建 Anki 卡片、APKG 文件或从算法/技术笔记生成学习牌组时使用。
version: 3.0.0
---

# Anki APKG 生成器

从算法学习笔记生成 `.apkg` 牌组，用于间隔重复复习。

## 环境准备

```bash
pip install genanki
```

## 何时调用

当用户出现以下情况时调用此技能：
- 要求"生成 Anki 牌组"或"create Anki cards"
- 想从算法笔记构建 APKG 文件
- 需要用于面试准备复习的闪卡
- 提到具体的算法主题（如"把回溯的卡片也生成一下"）
- 要求修复或改进现有 APKG

## 技能结构

```
.claude/skills/anki-apkg-generator/
├── SKILL.md                          # 本文件
├── scripts/
│   └── apkg_builder.py              # 可复用的 genanki 辅助模块
└── examples/
    └── build_dp.py                  # 参考：旧版单体 DP 构建脚本
```

---

## 核心模块：`apkg_builder.py`

位于 `scripts/apkg_builder.py` 的可复用模块提供 7 个函数：

| 函数 | 签名 | 用途 |
|-----------|---------|---------|
| `make_front` | `(problem: str, category: str) -> str` | 构建标准化的 `题目名 \| 分类` 前缀 |
| `make_deck` | `(deck_id: int, name: str) -> Deck` | 创建牌组；`name` 使用 `::` 层级结构 |
| `add_basic` | `(deck, front: str, back: str)` | 添加 Basic 问答卡片 |
| `add_cloze` | `(deck, text: str, extra: str)` | 添加 Cloze 填空卡片 |
| `img` | `(name: str) -> str` | 跟踪图片并返回 HTML `<img>` 标签 |
| `code` | `(java: str) -> str` | 用 `<pre><code class="language-java">` 包裹 Java 代码并进行 HTML 转义 |
| `build` | `(output_path: str) -> str` | 写入 APKG 文件，返回摘要 |

### 导入方式

```python
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, code, build
```

### img() 行为

`img('image 5.png')` 返回 HTML `<img>` 标签，并将文件注册到包的媒体清单中。图片文件必须相对于**运行构建脚本时的当前工作目录**存在（而非相对于脚本文件）。始终从图片文件所在的主题目录运行构建脚本。

### code() 行为

`code(java_str)` 将 Java 源代码包裹在 `<pre><code class="language-java">` 中，并通过 `html.escape()` 进行正确的 HTML 转义。卡片模板中的 `HLJS_HEAD` 使用 highlight.js v11.6.0 CDN 自动高亮。

---

## 推荐架构：先拆分 md 再构建

**关键**：不要写一个硬编码所有卡片的单体构建脚本。应采用两阶段方案：

### 阶段 1：将源 md 拆分为独立题目 md

编写 `_split_to_mds.py` 脚本：
1. 读取单体源 `.md` 文件
2. 将每道题提取为独立的 `problems/<题目名>.md` 文件
3. 每个 md 遵循下方标准的 `## 分区` 模板

**录制 shim 模式** — 用于从旧版构建脚本中提取数据：

```python
import sys, types, html as _html

_record: dict[str, dict] = {}
_current_p: list[str | None] = [None]

def _record_make_deck(deck_id: int, name: str):
    parts = name.split('::')
    _current_p[0] = parts[-1] if len(parts) > 2 else name
    _record[_current_p[0]] = {'deck_id': deck_id, 'cards': []}
    return type('_D', (), {'add_note': lambda s, n: None})()

# 将 mock 模块注入 sys.modules
_apkg = types.ModuleType('apkg_builder')
_apkg.make_deck = _record_make_deck
# ... 类似地赋值所有 mock 函数 ...
sys.modules['apkg_builder'] = _apkg
sys.modules['genanki'] = _genanki

# 执行旧版构建脚本 — 所有调用被捕获
exec(source_code, {'__name__': '__main__'})
# _record 现在包含所有捕获的卡片数据
```

参考：`算法/动态规划/_split_to_mds.py`

### 阶段 2：编写通用的 `build_from_mds.py`

一个可复用的脚本：
1. 通配 `problems/*.md`
2. 解析每个文件的 `# 标题` 和 `## 分区`
3. 自动将分区映射为卡片类型（题干→Basic，定义状态→Cloze 等）
4. 生成 APKG

这种分离意味着：**编辑 md → 重新构建**。修改内容无需触碰 Python 代码。

参考：`算法/动态规划/build_from_mds.py`

---

## 独立题目 MD 模板

每道题必须放在独立的 `.md` 文件中，路径为 `<主题>/problems/<题目名>.md`，包含以下精确的 `##` 分区：

```markdown
# 题目名

## 题干
题目描述文本。可包含图片（`![...](image.png)`）和内联代码（`nums`）。
**不得包含题解代码块（` ```java ``` `）。** 题解代码应放在题解分区。

## 定义状态
dp[i] = {{c1::状态定义}}
> 可选的提示，显示在答案面

## 转移方程
dp[i] = {{c1::递推公式}}
> 可选提示

## 初始化
dp[0] = {{c1::基本情况}}
> 可选提示

## 计算顺序
描述循环方向和理由的纯文本。

## 返回结果
描述返回什么以及为什么的纯文本。

## 复杂度
时间复杂度和空间复杂度，必须包含推导步骤（不能只写答案）。

## 题解(DP)
方法的简要描述。
```java
class Solution { ... }
```

## 题解(分治)   ← 仅当存在多种解法时
简要描述。
```java
class Solution { ... }
```
```

### 分区→卡片映射

`build_from_mds.py` 按以下规则将分区映射为卡片类型：

| 分区 | 卡片类型 | 处理方式 |
|---------|-----------|-------------|
| `题干` | Basic | Markdown→HTML：代码块→`code()`，图片→`img()`，其余转义 |
| `定义状态` | Cloze | `{{c1::...}}` 在文本中，`> 提示` 行 → Back Extra |
| `转移方程` | Cloze | 同上 |
| `初始化` | Cloze | 同上 |
| `计算顺序` | Basic | 纯文本原样保留 |
| `返回结果` | Basic | 纯文本原样保留 |
| `复杂度` | Basic | 纯文本原样保留 |
| `题解(*)` | Basic | 提取 ` ```java ``` ` → `code()`，描述文本作为引言 |

`定义状态`、`转移方程`、`初始化` 分区为 Cloze 类型。其余均为 Basic。

### MD 内容规则（关键）

**题干分区：**
- 必须包含：题目描述、图片、示例、数学解释
- 不得包含：题解代码（` ```java ``` ` 块）
- 原因：题干卡片呈现的是题目 — 题解代码会剧透答案

**复杂度分区：**
- 必须包含推导步骤，不能只写答案
- 格式：`时间 O(f(n))：具体推导过程（每步做什么 × 做多少次） → O(f(n))<br>空间 O(g(n))：哪些数据随n增长`
- 错误示例：`时间 O(n)，空间 O(1)` — 没有推导
- 正确示例：`时间 O(n)：遍历一次，每步做O(1)的min+加法，共n次 → O(n)<br>空间 O(1)：只需dp和res两个变量，不随n增长`
- **必须自包含** — 不能写"同最大子数组和"（引用其他题目）

**题解分区：**
- 分区标题：`题解`（单一解法）或 `题解(DP)`、`题解(分治)`、`题解(BFS)`（命名变体）
- 包含：可选描述 + 必需的 ` ```java ``` ` 代码块
- 代码块前的描述文本成为卡片的引言
- 构建脚本用 `code()` 包裹提取的代码以支持 highlight.js

**Cloze 分区**（定义状态、转移方程、初始化）：
- Cloze 标记：`{{c1::答案}}`、`{{c2::答案}}` 等
- 以 `> ` 开头的行 → Anki 的"Back Extra"字段
- 支持带 `<br>` 的多行 cloze 内容

**换行符：** 统一使用 LF (`\n`)。CRLF 可能导致正则表达式失败。

---

## 分区完整性审查

构建前，验证每个 md 包含所有必需分区：

```python
required = ['题干', '定义状态', '转移方程', '初始化', '计算顺序', '返回结果', '复杂度']
for name in required:
    if f'## {name}' not in text:
        print(f'缺失: {name}')
```

还需检查：
- 去除代码块和空白后，题干不为空
- 复杂度不是简单的"同XXX"引用
- 定义状态/转移方程/初始化包含 cloze 标记 `{{c1::...}}`

---

## 卡片设计规则

### 关键：每张卡片必须包含题目名

使用 `make_front(problem_name, category)` 构建卡片正面前缀。格式：`题目名 | 分类`。

### 牌组命名

`算法::<主题>::<题目名>` — `::` 分隔符创建 Anki 的层级牌组树。

模板牌组（如有）：`算法::<主题>::原理通识` — 必须在独立题目构建中跳过。

### 卡片数量指南

| 题目类型 | 每道题卡片数 |
|-----------|------------------|
| 动态规划 (DP) | 7-9 |
| 回溯法 | 5-6 |
| 双指针 / 滑动窗口 | 4-5 |
| 链表 / 二叉树 | 4-5 |
| 栈队列堆（单调栈） | 4-5 |
| 通用题型（贪心、哈希、矩阵、字符串等） | 3-4 |

---

## 各题型的卡片模板

### 类型 A：动态规划 (DP) — 每题 7-9 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述 + 图片。**无题解代码。** |
| 2 | `定义状态` | Cloze | `dp[i] = {{c1::含义}}` |
| 3 | `转移方程` | Cloze | `dp[i] = {{c1::递推式}}` |
| 4 | `初始化` | Cloze | `dp[0] = {{c1::基本情况}}` |
| 5 | `计算顺序` | Basic | 循环方向和理由 |
| 6 | `返回结果` | Basic | 返回什么及为什么 |
| 7 | `复杂度` | Basic | 时间 + 空间及推导步骤 |
| 8 | `题解` | Basic | Java 代码。命名变体：`题解(DP)`、`题解(分治)` 等 |

### 类型 B：回溯法 — 每题 5-6 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述。无题解代码。 |
| 2 | `回溯-选择列表` | Cloze | `选择列表 = {{c1::...}}` |
| 3 | `回溯-终止+剪枝` | Cloze | `终止条件：{{c1::...}}，剪枝策略：{{c2::...}}` |
| 4 | `复杂度` | Basic | 时间 & 空间及推导 |
| 5 | `题解` | Basic | 代码 |
| 6 | `对比`（可选） | Basic | 与相似题目的区别 |

### 类型 C：双指针/滑动窗口 — 每题 4-5 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述 |
| 2 | `指针策略` | Cloze | `left移动：{{c1::...}}，right移动：{{c2::...}}` |
| 3 | `复杂度` | Basic | 时间 & 空间及推导 |
| 4 | `题解` | Basic | 代码 |

### 类型 D：链表 — 每题 4-5 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述 |
| 2 | `关键技巧` | Basic/Cloze | 哑节点、快慢指针、递归策略 |
| 3 | `复杂度` | Basic | 时间 & 空间及推导 |
| 4 | `题解` | Basic | 代码 |

### 类型 E：二叉树 — 每题 4-5 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述 |
| 2 | `递归策略` | Basic | 前/中/后/层序？递归三部曲 |
| 3 | `复杂度` | Basic | 时间 & 空间及推导 |
| 4 | `题解` | Basic | 代码 |

### 类型 F：栈/队列/堆 / 单调栈 — 每题 4-5 张卡片

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述 |
| 2 | `栈策略` | Cloze | `栈维护{{c1::递增/递减}}，弹出条件：{{c2::...}}` |
| 3 | `复杂度` | Basic | 时间 & 空间及推导 |
| 4 | `题解` | Basic | 代码 |

### 类型 G：通用题型 — 每题 3-4 张卡片

适用于贪心、哈希表、前缀和、矩阵、字符串、图、并查集、拓扑、设计类等。

| # | 分类 | 类型 | 内容 |
|---|----------|------|---------|
| 1 | `题干` | Basic | 题目描述。无题解代码。 |
| 2 | `复杂度` | Basic | 时间 & 空间及推导 |
| 3 | `题解` | Basic | 代码 |
| 4 | `关键技巧`（可选） | Basic/Cloze | 关键思路或技巧 |

---

## 工作流

### 新建主题

**步骤 1：拆分源 md** — 编写 `_split_to_mds.py` 将单体源文件拆分为 `problems/*.md`

```bash
cd 算法/<主题>
python _split_to_mds.py
```

**步骤 2：审查 md** — 检查每个文件是否有缺失分区、题干中有代码、空白复杂度等。

**步骤 3：编写 `build_from_mds.py`** — 一个薄脚本，读取 md 并将分区映射为卡片。从 DP 参考中复制并适配。

**步骤 4：构建**

```bash
python build_from_mds.py
```

期望输出：`N 道题, M 张卡片 -> <output>.apkg`

### 更新已有卡片

编辑 `problems/` 中题目的 `.md` 文件，然后重新运行 `build_from_mds.py`。无需修改 Python 代码。

---

## 常见陷阱及修复

### 1. 题干分区中有代码块

**现象**：Anki 题干卡片在题目描述旁边显示了题解 Java 代码。

**根因**：原始源 md 将题解代码混入了题目描述。拆分时，题目标题下的所有内容都进入了题干。

**修复**：编写清理脚本，仅从题干分区中移除 ` ```java ``` ` 块。模式：

```python
in_tigan = False; in_code = False
for line in lines:
    if stripped.startswith('## 题干'): in_tigan = True
    elif stripped.startswith('## ') and in_tigan: in_tigan = False
    if in_tigan and stripped.startswith('```'):
        in_code = not in_code; continue
    if in_tigan and in_code: continue
    result.append(line)
```

### 2. 空白或"同XXX"的复杂度分区

**现象**：复杂度分区为空或只写了"同最大子数组和"。

**修复**：每道题必须有自己独立的复杂度推导。构建前审查所有 md。

### 3. 正则表达式分组 IndexError

**现象**：`m.group(2)` 处报 `IndexError: no such group`。

**根因**：正则 `r'!\[.*?\]\((.*?)\)'` 只有一个捕获组（括号中的路径）。调用 `m.group(2)` 会失败。

**修复**：使用 `m.group(1)`。仔细数捕获组。在全部文件上运行正则前，先用示例文本测试。

### 4. HTML 实体双重编码

**现象**：Anki 卡片中 Java 代码显示 `&amp;lt;` 而非 `<`。

**根因**：代码先被 HTML 转义，存入 HTML，再被反转义，又重新转义。

**修复**：从 HTML 上下文中提取代码时使用 `_html.unescape()`。将代码包裹为 HTML 显示时使用 `html.escape()`（即 `code()` 函数）。永远不要连续应用两者。

### 5. 原理通识被当成真实题目

**现象**：APKG 中出现一个空的"原理通识"牌组。

**修复**：在 `build_from_mds.py` 中添加跳过列表：
```python
skip_files = {'原理通识.md'}
md_files = [f for f in md_files if f.name not in skip_files]
```

### 6. 换行符不匹配

**现象**：`re.DOTALL` 正则无法匹配 `^## ...` 边界。

**根因**：Windows CRLF (`\r\n`) vs LF (`\n`)。多行模式下的 `^` 在 CRLF 中可能行为不符合预期。

**修复**：处理前统一换行符：`text = text.replace('\r\n', '\n')`。或确保 `.md` 文件仅使用 LF。

### 7. 字符串切片截断分区名

**现象**：分区标题 `初始化(3/5)` 在 `section[:4]` 后变成 `初始化(`。

**修复**：使用显式映射字典而非字符串切片：
```python
step_map = {'初始化(3/5)': '初始化', '定义状态(1/5)': '定义状态', ...}
```

### 8. Markdown→HTML 双重转义（题干正文）

**现象**：题干中的内联代码和格式化文本变成转义的 HTML（`&lt;code&gt;`）。

**修复**：使用 `process_body_with_images()` 中的占位符方案：
1. 提取 ` ``` ``` ` 代码块 → 替换为 `\x00CODE{N}\x00`
2. 提取 `` `inline` `` 内联代码 → 替换为 `\x00INLINE{N}\x00`
3. 提取 `![](images)` 图片 → 替换为 `\x00IMG{N}\x00`
4. 对剩余文本执行 `html.escape()`
5. 按逆序恢复占位符（IMG → INLINE → CODE）
6. 将 `\n` 转换为 `<br>`

### 9. 移除代码后的孤立加粗标题

**现象**：从题干中移除代码块后，独立的加粗行如 `**动态规划**` 下面没有内容。

**修复**：移除代码块后，删除题干中的短加粗行。保留较长的描述性加粗文本。

---

## Cloze 最佳实践

- 每张卡片的 cloze 编号：每张卡片内使用 `c1, c2, c3...`
- 代码 cloze：填空**关键逻辑**（转移方程、循环边界、条件），而非样板代码
- 永远不要 cloze 题目名 — 它已经在 `make_front()` 中了
- 使用 `> 提示文本` 作为 Back Extra 字段（显示在答案面）

## CSS 默认值

自动应用：
- 字体：Microsoft YaHei，20px，居中，深灰色 (#333)
- Cloze 填空：加粗，蓝色 (#2563eb)
- 图片：max-width 100%，自动高度，上边距 10px，圆角 4px
- 代码：pre-wrap，overflow-x auto，max-width 95%

## 参考

- [Anki 手册（中文）](https://open-spaced-repetition.github.io/anki-manual-zh-CN/editing.html)
- [genanki on PyPI](https://pypi.org/project/genanki/)
- DP 参考（先拆分 md 再构建模式）：`算法/动态规划/`
  - `_split_to_mds.py` — 通过录制 shim 提取数据
  - `build_from_mds.py` — 从独立 md 通用构建
  - `problems/*.md` — 独立题目文件
