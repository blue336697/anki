---
name: anki-apkg-generator
description: Generate Anki APKG flashcard decks from algorithm and interview-study notes. Handles note analysis, card design (Basic/Cloze), image embedding, correctness review, technical knowledge cards, and APKG packaging. Use when the user asks to create Anki cards, APKG files, or study decks from algorithm notes, 八股文, Java/JVM/concurrency/database/network notes, or other technical interview material.
version: 3.0.0
---

# Anki APKG Generator

Generate `.apkg` flashcard decks from algorithm and technical interview notes for spaced-repetition review.

## Prerequisites

```bash
pip install genanki
```

## When to Invoke

Invoke this skill when the user:
- Asks to "生成 Anki 牌组" or "create Anki cards"
- Wants to build APKG files from algorithm notes
- Wants to build APKG files from 八股文 / interview notes
- Needs flashcards for interview preparation review
- Mentions a specific algorithm topic (e.g., "把回溯的卡片也生成一下")
- Asks to fix or improve existing APKGs

## Skill Structure

```
.Codex/skills/anki-apkg-generator/
├── SKILL.md                          # This file
├── scripts/
│   └── apkg_builder.py              # Reusable genanki helper module
└── examples/
    └── build_dp.py                  # Reference: legacy monolithic DP build script
```

---

## Core Module: `apkg_builder.py`

The reusable module at `scripts/apkg_builder.py` provides 7 functions:

| Function | Signature | Purpose |
|----------|-----------|---------|
| `make_front` | `(problem: str, category: str) -> str` | Build standardized `题目名 \| 分类` prefix |
| `make_deck` | `(deck_id: int, name: str) -> Deck` | Create a deck; `name` uses `::` hierarchy |
| `add_basic` | `(deck, front: str, back: str)` | Add a Basic Q&A card |
| `add_cloze` | `(deck, text: str, extra: str)` | Add a Cloze fill-in-blank card |
| `img` | `(name: str) -> str` | Track image + return HTML `<img>` tag |
| `code` | `(java: str) -> str` | Wrap Java in `<pre><code class="language-java">` with HTML escaping |
| `build` | `(output_path: str) -> str` | Write APKG, return summary |

### Import Pattern

```python
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.Codex\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_front, make_deck, add_basic, add_cloze, img, code, build
```

### img() Behavior

`img('image 5.png')` returns an HTML `<img>` tag and registers the file in the package's media manifest. The image file must exist relative to the **CWD when the build script runs** (not relative to the script file). Always run build scripts from the topic directory where image files live.

### code() Behavior

`code(java_str)` wraps Java source in `<pre><code class="language-java">` with proper HTML escaping via `html.escape()`. The `HLJS_HEAD` in card templates auto-highlights with highlight.js v11.6.0 CDN.

---

## Output Location

Always keep generated decks categorized under `牌组/`:

- Algorithm decks: `牌组/算法/<主题>.apkg`
- Interview knowledge decks: `牌组/八股文/<技术栈>/<主题>.apkg`, e.g. `牌组/八股文/Java/Java并发样板.apkg`

Do not write new APKGs directly into the `牌组/` root.

## Algorithm Architecture: Split-MD-Then-Build

**CRITICAL**: Do NOT write a monolithic build script that hardcodes every card. Instead, follow the two-phase approach:

### Phase 1: Split source md into individual problem mds

Write a `_split_to_mds.py` script that:
1. Reads the monolithic source `.md` file
2. Extracts each problem into a separate `problems/<题目名>.md` file
3. Each md follows the standard `## section` template below

**Recording shim pattern** for extracting data from legacy build scripts:

```python
import sys, types, html as _html

_record: dict[str, dict] = {}
_current_p: list[str | None] = [None]

def _record_make_deck(deck_id: int, name: str):
    parts = name.split('::')
    _current_p[0] = parts[-1] if len(parts) > 2 else name
    _record[_current_p[0]] = {'deck_id': deck_id, 'cards': []}
    return type('_D', (), {'add_note': lambda s, n: None})()

# Inject mock modules into sys.modules
_apkg = types.ModuleType('apkg_builder')
_apkg.make_deck = _record_make_deck
# ... assign all mock functions similarly ...
sys.modules['apkg_builder'] = _apkg
sys.modules['genanki'] = _genanki

# Execute the legacy build script — all calls are captured
exec(source_code, {'__name__': '__main__'})
# _record now contains all captured card data
```

Reference: `D:\anki\算法\动态规划\_split_to_mds.py`

### Phase 2: Write a generic `build_from_mds.py`

A reusable script that:
1. Globs `problems/*.md`
2. Parses `# Title` and `## Sections` from each
3. Maps sections to card types automatically (题干→Basic, 定义状态→Cloze, etc.)
4. Generates the APKG

This separation means: **edit the md → rebuild**. No need to touch Python code for content changes.

Reference: `D:\anki\算法\动态规划\build_from_mds.py`

---

## Individual Problem MD Template

Every problem MUST be in its own `.md` file at `<主题>/problems/<题目名>.md` with these exact `##` sections:

```markdown
# 题目名

## 题干
Problem description text. Can include images (`![...](image.png)`) and inline code (`nums`).
**Must NOT contain solution code blocks (` ```java ``` `).** Solution code belongs in 题解 sections.

## 定义状态
dp[i] = {{c1::state definition}}
> optional hint for the answer side

## 转移方程
dp[i] = {{c1::recurrence formula}}
> optional hint

## 初始化
dp[0] = {{c1::base case}}
> optional hint

## 计算顺序
Plain text describing loop direction and rationale.

## 返回结果
Plain text describing what to return and why.

## 复杂度
Time and space complexity WITH derivation steps (not just the answer).

## 题解(DP)
Brief description of the approach.
```java
class Solution { ... }
```

## 题解(分治)   ← only if multiple solutions exist
Brief description.
```java
class Solution { ... }
```
```

### Section→Card Mapping

The build_from_mds.py maps sections to card types as follows:

| Section | Card Type | Processing |
|---------|-----------|-------------|
| `题干` | Basic | Markdown→HTML: code blocks→`code()`, images→`img()`, rest escaped |
| `定义状态` | Cloze | `{{c1::...}}` in text, `> hint` lines → Back Extra |
| `转移方程` | Cloze | Same as above |
| `初始化` | Cloze | Same as above |
| `计算顺序` | Basic | Plain text as-is |
| `返回结果` | Basic | Plain text as-is |
| `复杂度` | Basic | Plain text as-is |
| `题解(*)` | Basic | Extracts ` ```java ``` ` → `code()`, description text as intro |

Sections `定义状态`, `转移方程`, `初始化` are treated as Cloze. All others are Basic.

### MD Content Rules (CRITICAL)

**题干 section:**
- MUST contain: problem description, images, examples, mathematical explanation
- MUST NOT contain: solution code (` ```java ``` ` blocks)
- Rationale: The 题干 card presents the problem — solution code spoils the answer

**复杂度 section:**
- MUST include derivation steps, not just the answer
- Format: `时间 O(f(n))：具体推导过程（每步做什么 × 做多少次） → O(f(n))<br>空间 O(g(n))：哪些数据随n增长`
- Bad: `时间 O(n)，空间 O(1)` — no derivation
- Good: `时间 O(n)：遍历一次，每步做O(1)的min+加法，共n次 → O(n)<br>空间 O(1)：只需dp和res两个变量，不随n增长`
- **Must be self-contained** — never write "同最大子数组和" (reference another problem)

**题解 section:**
- Section header: `题解` (single solution) or `题解(DP)`, `题解(分治)`, `题解(BFS)` (named variants)
- Contains: optional description + mandatory ` ```java ``` ` code block
- Description text before the code block becomes the card intro
- The build script wraps extracted code with `code()` for highlight.js

**Cloze sections** (定义状态, 转移方程, 初始化):
- Cloze markers: `{{c1::answer}}`, `{{c2::answer}}`, etc.
- Lines starting with `> ` are hints → Anki "Back Extra" field
- Multi-line cloze content with `<br>` is supported

**Line endings:** Use LF (`\n`) consistently. CRLF can cause regex failures.

---

## Section Completeness Audit

Before building, verify every md has all required sections:

```python
required = ['题干', '定义状态', '转移方程', '初始化', '计算顺序', '返回结果', '复杂度']
for name in required:
    if f'## {name}' not in text:
        print(f'MISSING: {name}')
```

Also check:
- 题干 is not empty after stripping code blocks and whitespace
- 复杂度 is not a bare "同XXX" reference
- 定义状态/转移方程/初始化 have cloze markers `{{c1::...}}`

---

## Card Design Rules

### CRITICAL: Every card MUST include the problem name

Use `make_front(problem_name, category)` to build the card front prefix. Format: `题目名 | 分类`.

### Deck Naming

`算法::<主题>::<题目名>` — the `::` separator creates Anki's hierarchical deck tree.

Template deck (if any): `算法::<主题>::原理通识` — must be skipped from individual-problem builds.

### Card Count Guidelines

| Topic Type | Cards per Problem |
|-----------|------------------|
| 动态规划 (DP) | 7-9 |
| 回溯法 | 5-6 |
| 双指针 / 滑动窗口 | 4-5 |
| 链表 / 二叉树 | 4-5 |
| 栈队列堆（单调栈） | 4-5 |
| 通用题型（贪心、哈希、矩阵、字符串等） | 3-4 |

---

## Interview Knowledge Cards (八股文)

八股文 does not map to "one problem, one solution". Convert it into **knowledge-point groups**. One knowledge point should usually produce **4-6 Basic cards**; fewer than 3 cards often means the concept is under-specified, more than 8 cards usually means the topic should be split.

### Senior Interview Coverage Workflow

When the user asks to process or improve a whole 八股文 folder/category for interview readiness, do **not** only convert existing md files. Default to "interview ability construction" mode:

1. Build a knowledge map for the category first: what a 5-year backend interview candidate should be able to explain, including adjacent high-frequency topics even if the source md omits them.
2. Audit current `knowledge/`: existing files, card counts, whether each topic has mechanism/boundary/misconception coverage, and whether any answers are only definitions.
3. Classify gaps:
   - `P0`: must-have for 5-year ByteDance/Meituan-style backend interviews; missing it creates obvious risk.
   - `P1`: depth and differentiation; useful for follow-up questions and senior signal.
   - `P2`: lower-frequency or specialty topics; add only after P0/P1 if scope allows.
4. Create missing knowledge-point md files instead of forcing unrelated content into existing files.
5. Each important knowledge point should normally include: `概念卡`, `机制卡`, `边界卡`, `工程实践卡` or `对比追问卡`, and `正确性审查卡`.
6. Finish with a coverage report: files/cards added, APKG build result, remaining risks, and whether the category can handle a 10-minute senior-interview drill.

Senior-readiness acceptance question: **If an interviewer keeps asking "why, how, boundary, failure mode, production use" for this category, would the learner still have a structured answer?** If not, keep filling gaps before calling the folder done.

### Knowledge Point MD Template

Use one `.md` per knowledge point under a topic-specific `knowledge/<原文标题>/` directory:

```markdown
# 知识点名

## 概念卡
Q: 它是什么？解决什么问题？

A:
- 核心结论 1
- 核心结论 2

## 机制卡
Q: 内部流程或关键机制是什么？

A:
1. 步骤一
2. 步骤二

## 边界卡
Q: 什么时候不适用？有哪些坑？

A:
- 边界/代价/误区

## 对比追问卡
Q: 和相近概念有什么区别？

A:
- 对比项

## 正确性审查卡
Q: 原文哪些表述要修正或补充？

A:
- 修正说明
```

Cards should ask one precise question and answer in interview-speakable form: 3-6 high-signal bullets, with cause/effect and boundaries. Avoid copying long source paragraphs.

### Required Card Types

Prefer this set; omit only when genuinely irrelevant:

- `概念卡`: definition, purpose, one-sentence thesis.
- `机制卡`: internal flow, lifecycle, data structure, or happens-before chain.
- `边界卡`: limitations, costs, version differences, failure modes.
- `对比追问卡`: compare with adjacent concepts or common interviewer follow-ups.
- `正确性审查卡`: corrections, stale claims, ambiguous wording, source-of-truth notes.
- `图示卡`: only for structural/flow/comparison knowledge where a diagram materially improves recall.

### Correctness Review Rules

For 八股文, correctness is part of card generation:

- Check self-consistency inside the original md.
- Flag stale version-sensitive claims, especially Java/JDK, MySQL, Redis, Spring, Kafka, Linux, and Go behavior.
- Prefer official docs, specs, source code, or authoritative books for claims that may have changed.
- In the generated card, separate "classic teaching model" from "modern runtime/version behavior" when both matter.
- Do not silently encode questionable statements into cards; add a `正确性审查卡` or revise the answer.

### Diagram Policy

Use existing clear images first. Only generate new diagrams when all are true:

1. The knowledge is structural, flow-based, state-machine-like, architecture-like, or a complex comparison.
2. The source md has no usable image for that point.
3. Text alone makes active recall noticeably worse.

Do not add diagrams for pure definitions, plain lists, or short conclusions. If `drawio-skill` is available, use it to generate `.drawio` plus exported PNG and reference the PNG from the knowledge md. Keep image filenames ASCII-friendly for Anki media packaging.

## Card Templates by Problem Type

### Type A: 动态规划 (DP) — 7-9 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement + images. **No solution code.** |
| 2 | `定义状态` | Cloze | `dp[i] = {{c1::含义}}` |
| 3 | `转移方程` | Cloze | `dp[i] = {{c1::recurrence}}` |
| 4 | `初始化` | Cloze | `dp[0] = {{c1::base case}}` |
| 5 | `计算顺序` | Basic | Loop direction and rationale |
| 6 | `返回结果` | Basic | What to return and why |
| 7 | `复杂度` | Basic | Time + Space with derivation steps |
| 8 | `题解` | Basic | Java code. Named variants: `题解(DP)`, `题解(分治)`, etc. |

### Type B: 回溯法 (Backtracking) — 5-6 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement. No solution code. |
| 2 | `回溯-选择列表` | Cloze | `选择列表 = {{c1::...}}` |
| 3 | `回溯-终止+剪枝` | Cloze | `终止条件：{{c1::...}}，剪枝策略：{{c2::...}}` |
| 4 | `复杂度` | Basic | Time & Space with derivation |
| 5 | `题解` | Basic | Code |
| 6 | `对比` (optional) | Basic | Difference from similar problem |

### Type C: 双指针/滑动窗口 — 4-5 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement |
| 2 | `指针策略` | Cloze | `left移动：{{c1::...}}，right移动：{{c2::...}}` |
| 3 | `复杂度` | Basic | Time & Space with derivation |
| 4 | `题解` | Basic | Code |

### Type D: 链表 — 4-5 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement |
| 2 | `关键技巧` | Basic/Cloze | dummy node, fast/slow pointer, recursion strategy |
| 3 | `复杂度` | Basic | Time & Space with derivation |
| 4 | `题解` | Basic | Code |

### Type E: 二叉树 — 4-5 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement |
| 2 | `递归策略` | Basic | Pre/in/post/level order? Recursion 3-step |
| 3 | `复杂度` | Basic | Time & Space with derivation |
| 4 | `题解` | Basic | Code |

### Type F: 栈/队列/堆 / 单调栈 — 4-5 cards/problem

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement |
| 2 | `栈策略` | Cloze | `栈维护{{c1::递增/递减}}，弹出条件：{{c2::...}}` |
| 3 | `复杂度` | Basic | Time & Space with derivation |
| 4 | `题解` | Basic | Code |

### Type G: 通用题型 — 3-4 cards/problem

For 贪心、哈希表、前缀和、矩阵、字符串、图、并查集、拓扑、设计类 etc.

| # | Category | Type | Content |
|---|----------|------|---------|
| 1 | `题干` | Basic | Problem statement. No solution code. |
| 2 | `复杂度` | Basic | Time & Space with derivation |
| 3 | `题解` | Basic | Code |
| 4 | `关键技巧` (optional) | Basic/Cloze | Key insight or trick |

---

## Workflow

### For a New Topic

**Step 1: Split source md** — Write `_split_to_mds.py` to split the monolithic source into `problems/*.md`

```bash
cd 算法/<主题>
python _split_to_mds.py
```

**Step 2: Audit the mds** — Check every file for missing sections, code in 题干, empty complexity, etc.

**Step 3: Write `build_from_mds.py`** — A thin script that reads mds and maps sections to cards. Copy and adapt from the DP reference.

**Step 4: Build**

```bash
python build_from_mds.py
```

Expected: `N problems, M cards -> <output>.apkg`

### For Updating Existing Cards

Edit the problem's `.md` in `problems/`, then re-run `build_from_mds.py`. No Python code changes needed.

---

## Common Pitfalls & Fixes

### 1. Code blocks in 题干 sections

**Symptom**: Anki 题干 cards show solution Java code alongside the problem description.

**Root cause**: The original source md mixes solution code into problem descriptions. During split, all content under the problem heading goes into 题干.

**Fix**: Write a cleanup script that removes ` ```java ``` ` blocks from 题干 sections only. Pattern:

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

### 2. Empty or "同XXX" complexity sections

**Symptom**: 复杂度 section is empty or just says "同最大子数组和".

**Fix**: Every problem must have its own self-contained complexity derivation. Audit all mds before building:

```bash
python -c "check every md's 复杂度 section is not empty and doesn't contain '同'"
```

### 3. Regex group IndexError

**Symptom**: `IndexError: no such group` at `m.group(2)`.

**Root cause**: Regex `r'!\[.*?\]\((.*?)\)'` has only one capture group (the path in parens). Calling `m.group(2)` fails.

**Fix**: Use `m.group(1)`. Count capture groups carefully. Test regex patterns with sample text before running on all files.

### 4. HTML entity double-encoding

**Symptom**: Java code shows `&amp;lt;` instead of `<` in Anki cards.

**Root cause**: Code was HTML-escaped, then stored in HTML, then unescaped, then re-escaped.

**Fix**: Use `_html.unescape()` when extracting code FROM HTML context. Use `html.escape()` (the `code()` function) when wrapping code FOR HTML display. Never apply both in sequence.

### 5. 原理通识 treated as a real problem

**Symptom**: An empty deck for "原理通识" appears in the APKG.

**Fix**: Add a skip list in `build_from_mds.py`:
```python
skip_files = {'原理通识.md'}
md_files = [f for f in md_files if f.name not in skip_files]
```

### 6. Line ending mismatches

**Symptom**: `re.DOTALL` regex fails to match `^## ...` boundaries.

**Root cause**: Windows CRLF (`\r\n`) vs LF (`\n`). `^` in multiline mode may not behave as expected with CRLF.

**Fix**: Normalize line endings: `text = text.replace('\r\n', '\n')` before processing. Or ensure `.md` files use LF only.

### 7. String slicing truncates section names

**Symptom**: Section header `初始化(3/5)` becomes `初始化(` after `section[:4]`.

**Fix**: Use explicit mapping dicts instead of string slicing:
```python
step_map = {'初始化(3/5)': '初始化', '定义状态(1/5)': '定义状态', ...}
```

### 8. Markdown→HTML double-escaping (题干 body)

**Symptom**: Inline code and formatted text in 题干 becomes escaped HTML (`&lt;code&gt;`).

**Fix**: Use the placeholder-based approach in `process_body_with_images()`:
1. Extract ` ``` ``` ` code blocks → replace with `\x00CODE{N}\x00`
2. Extract `` `inline` `` code → replace with `\x00INLINE{N}\x00`
3. Extract `![](images)` → replace with `\x00IMG{N}\x00`
4. `html.escape()` remaining text
5. Restore placeholders in reverse order (IMG → INLINE → CODE)
6. Convert `\n` to `<br>`

### 9. Orphan bold headings after code removal

**Symptom**: After removing code blocks from 题干, standalone bold lines like `**动态规划**` remain with no content under them.

**Fix**: Remove short bold-only lines in 题干 after removing code blocks. Keep longer descriptive bold text.

---

## Cloze Best Practices

- Number clozes per-card: `c1, c2, c3...` within each card
- Code clozes: blank out **key logic** (transition equation, loop bounds, conditions), not boilerplate
- Never cloze the problem name — it's already in `make_front()`
- Use `> hint text` for the Back Extra field (shown on answer side)

## CSS Defaults

Applied automatically:
- Font: Microsoft YaHei, 20px, centered, dark gray (#333)
- Cloze blanks: bold, blue (#2563eb)
- Images: max-width 100%, auto height, 10px top margin, 4px border-radius
- Code: pre-wrap, overflow-x auto, max-width 95%

## Reference

- [Anki Manual (Chinese)](https://open-spaced-repetition.github.io/anki-manual-zh-CN/editing.html)
- [genanki on PyPI](https://pypi.org/project/genanki/)
- DP reference (split-md-then-build pattern): `D:\anki\算法\动态规划\`
  - `_split_to_mds.py` — data extraction via recording shim
  - `build_from_mds.py` — generic build from individual mds
  - `problems/*.md` — individual problem files
