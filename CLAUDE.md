# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概述

个人算法学习笔记仓库，按主题目录组织，包含算法题解、代码示例和配图。

## 目录结构

```
算法/
  <主题>/          # 如 动态规划、回溯、二叉树 等
    *.md           # 算法笔记（主文件）
    image*.png     # 笔记配图，命名格式为 image.png、image 1.png、image 2.png ...
```

## 笔记格式规范

每个 `.md` 文件中一个 H2 (`##`) 标题对应一道题目，遵循以下模式：
1. 题干描述（中文）
2. 配图（如有）
3. 解法代码（Java，写在 markdown 代码块中）

图片引用使用相对路径，如 `![image.png](image.png)`、`![image.png](image%201.png)`。

## 文件命名

- 新主题目录使用中文命名（如 `算法/动态规划/`）
- 笔记文件使用中文主题名
- 图片文件按 `image.png`、`image N.png`（N 为递增数字）命名，与笔记文件放在同一目录

## 注意事项

- 代码块统一使用 Java 语言标注
- 修改图片引用时注意 markdown 中的空格需转义为 `%20`
- 不引入不相关的文件或目录，保持仓库整洁
