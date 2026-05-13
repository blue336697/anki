"""
Anki APKG builder — reusable module for algorithm flashcard generation.

Usage pattern (write a topic-specific build script):
    import sys
    sys.path.insert(0, r'D:\anki\.claude\skills\anki-apkg-generator\scripts')
    from apkg_builder import make_deck, add_basic, add_cloze, img, build

    d0 = make_deck(10001, '算法::回溯::原理通识')
    add_basic(d0, '什么是回溯？', '回溯 = DFS + 状态重置...')
    build('回溯.apkg')
"""

import genanki

# ============================================================
# Anki Models (shared across all build scripts)
# ============================================================

BASIC_MODEL = genanki.Model(
    1747300001,
    'Basic (算法笔记)',
    fields=[{'name': 'Front'}, {'name': 'Back'}],
    templates=[{
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
    }],
    css=(
        '.card{font-family:"Microsoft YaHei",sans-serif;font-size:20px;'
        'text-align:center;color:#333;padding:20px}'
        'img{max-width:100%;height:auto;margin-top:10px;border-radius:4px}'
    ),
)

CLOZE_MODEL = genanki.Model(
    1747300002,
    'Cloze (算法笔记)',
    model_type=1,
    fields=[{'name': 'Text'}, {'name': 'Back Extra'}],
    templates=[{
        'name': 'Cloze',
        'qfmt': '{{cloze:Text}}',
        'afmt': '{{cloze:Text}}<br>{{Back Extra}}',
    }],
    css=(
        '.card{font-family:"Microsoft YaHei",sans-serif;font-size:20px;'
        'text-align:center;color:#333;padding:20px}'
        '.cloze{font-weight:bold;color:#2563eb}'
        'img{max-width:100%;height:auto;margin-top:10px;border-radius:4px}'
    ),
)

# ============================================================
# Global state (per build session)
# ============================================================

_decks: list[genanki.Deck] = []
_images: set[str] = set()


def img(name: str) -> str:
    """Track image file and return HTML <img> tag to embed in card text."""
    _images.add(name)
    return f'<br><img src="{name}" style="max-width:100%;margin-top:12px">'


def make_deck(deck_id: int, name: str) -> genanki.Deck:
    """Create a deck (hierarchical name with :: separator) and register it."""
    d = genanki.Deck(deck_id, name)
    _decks.append(d)
    return d


def add_basic(deck: genanki.Deck, front: str, back: str) -> None:
    """Add a Basic (Q&A) card to the deck."""
    deck.add_note(genanki.Note(model=BASIC_MODEL, fields=[front, back]))


def add_cloze(deck: genanki.Deck, text: str, extra: str = "") -> None:
    """Add a Cloze (fill-in-blank) card to the deck."""
    deck.add_note(genanki.Note(model=CLOZE_MODEL, fields=[text, extra]))


def build(output_path: str) -> str:
    """Write APKG file. Returns summary string (decks, cards, images)."""
    total = sum(len(d.notes) for d in _decks)
    pkg = genanki.Package(_decks)
    if _images:
        pkg.media_files = list(_images)
    pkg.write_to_file(output_path)
    return (
        f'Done: {len(_decks)} decks, {total} cards, '
        f'{len(_images)} images -> {output_path}'
    )
