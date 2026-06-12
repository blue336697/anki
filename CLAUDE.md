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
  Java/（JVM、并发、集合、Dubbo、Spring 等）
  Go/（类型系统、并发、编译原理等）
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

### 路径注意事项

构建脚本中包含硬编码的绝对路径（如 `D:\anki\算法\...`），在不同机器上运行时需修改 `TOPIC_DIR`、`OUTPUT_PATH` 等路径常量。

## 笔记格式

### 算法笔记

- 代码块使用 Java 语言标注
- **代码注释使用中文**（包括行内注释 `//` 和块注释）
- 配图放在同目录，命名 `image.png`、`image N.png`
- 图片引用中空格需转义为 `%20`

### 八股文笔记

- 按技术栈分一级子目录（Java、Go、MySQL 等），每个 `.md` 文件是一个独立主题
- 配图放在与 `.md` 同名的子目录或 `images/` 中
- 内容为中文，代码示例使用对应语言标注

## 仓库 Skills

- **anki-apkg-generator** (`/anki-apkg-generator`)：APKG 构建工具库，提供 `make_deck`、`add_basic`、`add_cloze`、`img`、`code`、`build` 等 API
- **anki-patterns** (`/anki-patterns`)：本仓库的提交约定（`add:`/`fix:`/`docs:` 前缀）和工作流规范
