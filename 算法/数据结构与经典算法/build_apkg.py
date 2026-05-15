from pathlib import Path
import re
import sys


TOPIC = '数据结构与经典算法'
BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SKILL_DIR = REPO / '.agents' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))

import apkg_builder as anki  # noqa: E402


IMG_RE = re.compile(r'\[\[img:([A-Za-z0-9_.-]+)\]\]')


def iter_tsv_cards(md_path: Path):
    text = md_path.read_text(encoding='utf-8')
    if '```tsv' not in text:
        return
    tsv = text.split('```tsv', 1)[1].split('```', 1)[0].strip()
    for line_no, line in enumerate(tsv.splitlines(), 1):
        parts = line.split('\t')
        if len(parts) != 5:
            raise ValueError(
                f'{md_path}: invalid TSV line {line_no}, '
                f'expected 5 columns, got {len(parts)}'
            )
        yield parts


def render_media(text: str) -> str:
    """Replace [[img:name.svg]] markers and register media in APKG."""
    def repl(match: re.Match) -> str:
        name = match.group(1)
        media_path = BASE / 'diagrams' / name
        if not media_path.exists():
            raise FileNotFoundError(f'Missing diagram media: {media_path}')
        anki._images.add(str(media_path))
        return (
            f'<br><img src="{name}" '
            f'style="max-width:100%;height:auto;margin-top:12px">'
        )

    return IMG_RE.sub(repl, text)


def make_topic_deck(md_path: Path, deck_id: int):
    category = md_path.parent.name
    knowledge = md_path.stem
    return anki.make_deck(
        deck_id,
        f'算法::{TOPIC}::{category}::{knowledge}',
    )


card_count = 0

for idx, md_path in enumerate(sorted((BASE / 'knowledge').glob('*/*.md')), 1):
    deck = make_topic_deck(md_path, 1778800901 + idx)
    for front, back, tags, source, difficulty in iter_tsv_cards(md_path):
        full_front = f'{md_path.stem} | {front}'
        full_back = (
            render_media(back)
            + f'<br><br><hr><small>Tags: {tags}<br>'
            + f'Source: {source}<br>Difficulty: {difficulty}</small>'
        )
        anki.add_basic(deck, full_front, full_back)
        card_count += 1

out_dir = REPO / '牌组' / '算法'
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f'{TOPIC}.apkg'
summary = anki.build(str(out))
print(summary)
print(f'cards={card_count}')
