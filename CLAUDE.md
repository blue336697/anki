# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概述

个人学习笔记仓库，包含三大板块：算法题解、八股文（技术面试基础）、项目文档。算法部分支持生成 Anki APKG 牌组用于间隔复习。

## 目录结构

```
算法/                           # 算法题解，按主题分目录（含题解与经典算法原理）
  动态规划/                     # 示例：含 Python 构建脚本 + problems/*.md
  二叉树操作（递归 层序遍历）/
  回溯法（递归枚举 剪枝）/
  数据结构与经典算法/             # 面向五年后端面试的算法原理卡
  ...
八股文/                         # 技术面试基础笔记
  Java/（JVM、并发、集合、Spring 等）
  MySQL/ Redis/ Linux/ 计算机组成原理/ 计算机网络/
  分布式系统/ 设计模式/ 消息队列/ ...
面试/                           # 面试经历记录
项目/                           # 项目文档（流水智能体等）
.claude/skills/                 # 仓库级 Skills
  anki-apkg-generator/          # APKG 生成库（scripts/apkg_builder.py）
  anki-patterns/                # 本仓库的工作流约定
```

## Anki APKG 生成管道

部分算法主题目录支持生成 Anki 牌组。管道分为两个阶段：

### 阶段1：拆分原始笔记为独立题目 md

`_split_to_mds.py` — 从原始的单文件笔记（如 `动态规划 xxx.md`）+ `build_*.py` 中提取卡片数据，拆分为 `problems/` 目录下每道题一个 `.md` 文件。

### 阶段2：从独立 md 生成 APKG

`build_from_mds.py` — 读取 `problems/*.md`，调用 `.claude/skills/anki-apkg-generator/scripts/apkg_builder.py` 生成 `.apkg` 文件输出到 `牌组/` 目录。

每个 problem md 使用 `##` 二级标题分区：`题干`、`定义状态`、`转移方程`、`初始化`、`计算顺序`、`返回结果`、`复杂度`、`题解`。构建脚本根据分区名决定卡片类型：cloze 区（定义状态/转移方程/初始化）生成填空卡，basic 区（计算顺序/返回结果/复杂度）生成基础问答卡，题解区提取 Java 代码生成代码卡。

部分主题（如各排序、滑动窗口等）只有一个 `build_*.py`，直接从代码逻辑生成卡片，没有 md 管道。

### Cloze 卡片规范：一次 add = 一个 Note = 一张卡片

**核心原则：每张卡片必须是独立的 Note，确保删除互不影响。**

Anki 中 Card ≠ Note。`add_cloze()` 一次调用创建一个 Note。若文本中含多个不同编号的 `{{c1::}}`、`{{c2::}}`、`{{c3::}}`，一个 Note 会生成多张卡片——但这些卡片共享同一个 Note，删除任意一张会删掉整个 Note，导致所有关联卡片消失。

**必须遵守**：
- 每个 `add_cloze()` 调用中**只使用 `{{c1::}}`**（全部同一编号），确保 1 Note = 1 Card
- 需要多张独立卡片时，**拆成多个 `add_cloze()` 调用**
- `build_from_mds.py` 中的 `normalize_cloze()` 已自动将所有 `{{cN::` 统一为 `{{c1::`，确保从 md 生成的卡片符合规范

**错误示例**（一个 Note 产出 3 张卡片，删除互相关联）：
```python
add_cloze(d, 'Step1: {{c1::A}}<br>Step2: {{c2::B}}<br>Step3: {{c3::C}}')
```

**正确示例**（3 个独立 Note，各自独立）：
```python
add_cloze(d, 'Step1: {{c1::A}}')
add_cloze(d, 'Step2: {{c1::B}}')
add_cloze(d, 'Step3: {{c1::C}}')
```

### add_cloze 参数顺序易错点

`add_cloze(deck, text, extra="")` 的签名是 `(deck, text, extra)`：

- 第一个参数 `text` → 映射到 Cloze Note 的 **Text 字段**，由 `{{cloze:Text}}` 模板渲染，**只有这个字段中的 `{{c1::...}}` 会被解析为填空**
- 第二个参数 `extra` → 映射到 **Back Extra 字段**，仅在背面展示，**填空标记不会被处理**

**错误示例**（标题放在 text，填空放 extra → 正面只有一个光秃秃的标题，填空全部无效）：
```python
add_cloze(d, 'AVL四种旋转场景速查',   # text → 正面只有这个标题，没有任何填空
    'LL → {{c1::右旋}}...'             # extra → 背面补充，{{c1::}} 被当成字面文本
)
```

**正确示例**（填空文本放在 text 参数，标题融入其中，extra 留空或放补充说明）：
```python
add_cloze(d,
    'AVL四种旋转场景速查<br><br>'
    'LL → {{c1::右旋(root)}}<br>'
    'RR → {{c1::左旋(root)}}'
)
```

### 路径注意事项

构建脚本中包含硬编码的绝对路径（如 `D:\anki\算法\...`），在不同机器上运行时需修改 `TOPIC_DIR`、`OUTPUT_PATH` 等路径常量。

## 笔记格式

### 算法笔记

- 代码块使用 Java 语言标注
- **代码注释使用中文**（包括行内注释 `//` 和块注释）
- 配图放在同目录，命名 `image.png`、`image N.png`
- 图片引用中空格需转义为 `%20`

### 八股文笔记

- 按技术栈分一级子目录（Java、MySQL、Redis 等），每个 `.md` 文件是一个独立主题
- 配图放在与 `.md` 同名的子目录或 `images/` 中
- 内容为中文，代码示例使用对应语言标注

### Java 单一知识源

- `八股文/Java/knowledge/<大类>/<知识点>/<知识点>.md` 是 Java 卡片内容的唯一知识源
- Java 根目录不再保留原始长文、摘录或重复专题；仅保留 `JAVA_KNOWLEDGE_MAP.md`、统一构建脚本和必要构建元数据
- Java 卡片必须先修改 knowledge MD，再运行 `build_java_all.py` 生成 APKG；禁止把 Python 硬编码卡片或直接写入 Anki 当作知识源
- knowledge 中只保留 MD 实际引用的媒体文件；未引用的复制图片应清理

## 仓库 Skills

- **anki-apkg-generator** (`/anki-apkg-generator`)：APKG 构建工具库，提供 `make_deck`、`add_basic`、`add_cloze`、`img`、`code`、`build` 等 API
- **anki-patterns** (`/anki-patterns`)：本仓库的提交约定（`add:`/`fix:`/`docs:` 前缀）和工作流规范
