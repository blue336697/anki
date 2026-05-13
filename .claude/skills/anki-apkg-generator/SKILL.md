---
name: anki-apkg-generator
description: Generate Anki APKG flashcard decks from algorithm study notes. Handles note analysis, card design (Basic/Cloze), image embedding, and APKG packaging. Use when the user asks to create Anki cards, APKG files, or study decks from algorithm/technical notes.
version: 1.0.0
---

# Anki APKG Generator

Generate `.apkg` flashcard decks from algorithm study notes for spaced-repetition review.

## Prerequisites

```bash
pip install genanki
```

## When to Invoke

Invoke this skill when the user:
- Asks to "生成 Anki 牌组" or "create Anki cards"
- Wants to build APKG files from algorithm notes
- Needs flashcards for interview preparation review
- Mentions a specific algorithm topic (e.g., "把回溯的卡片也生成一下")

## Skill Structure

```
.claude/skills/anki-apkg-generator/
├── SKILL.md                          # This file
├── scripts/
│   └── apkg_builder.py              # Reusable genanki helper module
└── examples/
    └── build_dp.py                  # Complete example: 37 DP problems, 100 cards
```

## Core Module: `apkg_builder.py`

The reusable module at `scripts/apkg_builder.py` provides 5 functions:

| Function | Signature | Purpose |
|----------|-----------|---------|
| `make_deck` | `(deck_id: int, name: str) -> Deck` | Create a deck; `name` uses `::` hierarchy |
| `add_basic` | `(deck, front: str, back: str)` | Add a Basic Q&A card |
| `add_cloze` | `(deck, text: str, extra: str)` | Add a Cloze fill-in-blank card |
| `img` | `(name: str) -> str` | Track image + return HTML `<img>` tag |
| `build` | `(output_path: str) -> str` | Write APKG, return summary |

### Import Pattern

```python
import sys
from pathlib import Path

# Resolve skill directory — adjust path if your build script is elsewhere
SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')

sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, img, build
```

### img() Behavior

`img('image 5.png')` returns an HTML `<img>` tag and registers the file in the package's media manifest. The image file must exist relative to the **CWD when the build script runs** (not relative to the script file). Always run build scripts from the topic directory where image files live.

## Workflow

### Step 1: Analyze Source Notes

Read the target `.md` file(s) in `算法/<主题>/`. For each problem (marked by `##` heading):

1. Identify the **core algorithm pattern** — state definition, transition, edge cases
2. Identify **distinguishing traits** — what makes this problem different from similar ones
3. Note any **images** that aid understanding (check `![...](image N.png)` references in markdown)
4. Note **common pitfalls** — wrong initial values, off-by-one, overflow, negative cases

### Step 2: Design Cards

**Card count**: 2-5 cards per problem. Don't atomize too finely — each card should test a meaningful chunk of understanding.

**Card types:**

| Type | Best for |
|------|----------|
| **Basic** (Q&A) | Definitions, comparisons, "why" questions, algorithm choice reasoning |
| **Cloze** (`{{cN::...}}`) | Code snippets, formulas, state transition equations, exact syntax |

**For each problem, cover these dimensions (pick the most notable 2-4):**

1. **State definition** — what does `dp[i]` / `dp[i][j]` represent?
2. **Transition equation** — the recurrence relation (cloze)
3. **Key edge case or trap** — initialization, negatives, boundary conditions
4. **Optimization** — space reduction, alternative approach (if notable)

**For a "原理通识" (principles) deck**, cover cross-cutting concepts: when to apply this algorithm, common patterns, comparisons with related approaches, complexity analysis.

**Cloze numbering**: Number clozes per-card, not per-deck. Each card starts fresh with `{{c1::...}}`. Use `c1, c2, c3...` within the same card text for multiple blanks.

### Step 3: Write the Build Script

Follow this template:

```python
"""Build APKG for <topic>."""
import sys
from pathlib import Path

SKILL_DIR = Path(r'D:\anki\.claude\skills\anki-apkg-generator')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, img, build

# --- Principles deck ---
d0 = make_deck(1747300200, '算法::<主题>::原理通识')
add_basic(d0, '明确的问题？', '简洁的答案')
add_cloze(d0, '公式：{{c1::关键部分}}', '可选提示')

# --- Problem decks ---
d1 = make_deck(1747300201, '算法::<主题>::题目名')
add_basic(d1, '问题？' + img('image 1.png'), '答案')
# ...

if __name__ == '__main__':
    print(build('<输出文件名>.apkg'))
```

**Deck ID convention**: Use a 9-digit integer base for each topic, incrementing for each problem deck. Example ranges: DP `1747300100+`, Backtrack `1747300200+`, Greedy `1747300300+`.

**Deck naming**: `算法::<主题>::<题目名>` — the `::` separator creates Anki's hierarchical deck tree.

**Output path**: Write to `../../牌组/<主题>.apkg` when running from `算法/<主题>/`.

### Step 4: Generate

```bash
cd 算法/<主题>          # MUST be in the image directory
python ..\..\.claude\skills\anki-apkg-generator\examples\build_<topic>.py
```

Expected output: `Done: N decks, M cards, K images -> <output>.apkg`

## Image Handling

- Image references in markdown: `![...](image N.png)` → pass filename to `img('image N.png')`
- `img()` returns an HTML string; **concatenate** it to card front or back text
- Images are embedded in the APKG — zero external dependencies after import
- Run from the topic directory so `genanki` finds the files by name

## Card Design Rules

1. **Front asks ONE specific question** — "dp[i] 的含义是？" not "讲讲这道题"
2. **Back is self-contained** — enough context that future-you won't need to re-read notes
3. **Code in cloze, concepts in basic** — equations get `{{cN::...}}`, reasoning gets Basic
4. **Images on the question side** — show the diagram, ask about it; the visual primes recall
5. **No duplicate cards across problems** — if two problems share a pattern, reference the first; don't repeat the same card
6. **Card text must be valid HTML** — use `<br>` for newlines, not `\n`; genanki will warn if it detects unescaped `<`/`>`. Wrap Java generics in backticks or use `&lt;`/`&gt;` if they appear in card text.

## CSS Defaults

Applied automatically by the module:

- Font: Microsoft YaHei, 20px, centered, dark gray (#333)
- Cloze blanks: bold, blue (#2563eb)
- Images: max-width 100%, auto height, 10px top margin, 4px border-radius

## Reference

- [Anki Manual (Chinese)](https://open-spaced-repetition.github.io/anki-manual-zh-CN/editing.html)
- [genanki on PyPI](https://pypi.org/project/genanki/)
- `examples/build_dp.py` — complete 37-problem, 100-card DP deck with 21 embedded images
