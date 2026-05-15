"""Generate simple SVG diagrams for Anki knowledge files.

Usage: python3 diagram_generator.py <type> <output.svg> < spec.json
Types: layered, flow, 3col, tree, timeline
"""

import sys
import json
import html


_COLORS = {
    "blue": ("#dae8fc", "#6c8ebf", "#1a1a2e"),
    "orange": ("#ffe6cc", "#d79b00", "#4a3000"),
    "purple": ("#e1d5e7", "#9673a6", "#2d1b4e"),
    "green": ("#d5e8d4", "#82b366", "#1b4a1b"),
    "red": ("#f8cecc", "#b85450", "#4a1b1b"),
    "gray": ("#f5f5f5", "#666666", "#333333"),
    "yellow": ("#fff2cc", "#d6b656", "#4a3a00"),
}

SVG_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


def _color(c):
    return _COLORS.get(c, _COLORS["gray"])


def _escape(text):
    return html.escape(str(text))


def _ml(text, lh=16):
    """Multiline text as tspans centered in parent."""
    lines = text.split("\n")
    y0 = -(len(lines) - 1) * lh / 2
    parts = []
    for i, line in enumerate(lines):
        dy = f'{lh}' if i > 0 else f'{y0 + lh/2}'
        parts.append(f'<tspan x="0" dy="{dy}">{_escape(line.strip())}</tspan>')
    return f'<text text-anchor="middle">{"".join(parts)}</text>'


# ── Generator functions ──────────────────────────────────────────────

def gen_layered(spec):
    layers = spec["layers"]
    title = spec.get("title", "")
    w = spec.get("width", 800)
    h = spec.get("height", 500)

    ml = 30; mt = 70 if title else 20
    lw = (w - ml - 30) // len(layers)
    parts = [SVG_HEADER,
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    if title:
        parts.append(f'<text x="{w//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{_escape(title)}</text>')

    for li, layer in enumerate(layers):
        lx = ml + li * lw
        label = layer.get("label", "")
        if label:
            parts.append(f'<text x="{lx + lw//2}" y="{mt - 12}" text-anchor="middle" font-size="11" fill="#888" font-style="italic">{_escape(label)}</text>')
        items = layer.get("items", [])
        ih = min(60, (h - mt - 60) // max(len(items), 1))
        sy = mt + (h - mt - len(items) * ih) // 2
        for ii, item in enumerate(items):
            iy = sy + ii * ih
            fill, stroke, tc = _color(item.get("color", "gray"))
            parts.append(f'<rect x="{lx + 5}" y="{iy}" width="{lw - 10}" height="{ih - 10}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            parts.append(f'<text x="{lx + lw//2}" y="{iy + (ih-10)//2}" text-anchor="middle" font-size="10" fill="{tc}">{_ml(item.get("text", ""))}</text>')
            sub = item.get("sub", "")
            if sub:
                parts.append(f'<text x="{lx + lw//2}" y="{iy + ih - 14}" text-anchor="middle" font-size="8" fill="#888">{_escape(sub)}</text>')
        if li < len(layers) - 1:
            ax = lx + lw; ay = sy + len(items) * ih // 2; bx = ax + 12
            parts.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{ay}" stroke="#999" stroke-width="1.5"/>')
            parts.append(f'<polygon points="{bx-4},{ay-4} {bx+2},{ay} {bx-4},{ay+4}" fill="#999"/>')
    parts.append('</svg>')
    return "\n".join(parts)


def gen_flow(spec):
    steps = spec["steps"]
    title = spec.get("title", "")
    w = spec.get("width", 800); h = spec.get("height", 200)
    n = len(steps)
    bw = min(120, (w - 60 - (n-1)*45) // n)
    tw = n * bw + (n-1) * 40
    sx = (w - tw) // 2
    cy = h // 2 + (10 if title else 0)
    parts = [SVG_HEADER,
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    if title:
        parts.append(f'<text x="{w//2}" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#333">{_escape(title)}</text>')
    for i, step in enumerate(steps):
        x = sx + i * (bw + 40)
        fill, stroke, tc = _color(step.get("color", "gray"))
        parts.append(f'<rect x="{x}" y="{cy - 30}" width="{bw}" height="60" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + bw//2}" y="{cy - 2}" text-anchor="middle" font-size="10" fill="{tc}">{_escape(step.get("text", ""))}</text>')
        sub = step.get("sub", "")
        if sub:
            parts.append(f'<text x="{x + bw//2}" y="{cy + 16}" text-anchor="middle" font-size="8" fill="#888">{_escape(sub)}</text>')
        if i < n - 1:
            ax = x + bw; ay = cy; bx = x + bw + 40
            parts.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{ay}" stroke="#999" stroke-width="1.5"/>')
            parts.append(f'<polygon points="{bx-5},{ay-4} {bx},{ay} {bx-5},{ay+4}" fill="#999"/>')
    parts.append('</svg>')
    return "\n".join(parts)


def gen_3col(spec):
    cols = spec["cols"]
    title = spec.get("title", "")
    w = spec.get("width", 800); h = spec.get("height", 400)
    m = 20; cw = (w - m * 2) // max(len(cols), 1)
    ys = 55 if title else 20
    max_n = max(len(c.get("items", [])) for c in cols)
    ih = min(30, (h - ys - 40) // max(max_n, 1))
    parts = [SVG_HEADER,
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    if title:
        parts.append(f'<text x="{w//2}" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#333">{_escape(title)}</text>')
    for ci, col in enumerate(cols):
        cx = m + ci * cw
        fill, stroke, tc = _color(col.get("color", "gray"))
        parts.append(f'<rect x="{cx + 3}" y="{ys}" width="{cw - 6}" height="28" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{cx + cw//2}" y="{ys + 18}" text-anchor="middle" font-size="11" font-weight="bold" fill="{tc}">{_escape(col.get("header", ""))}</text>')
        for ii, item in enumerate(col.get("items", [])):
            iy = ys + 35 + ii * ih
            parts.append(f'<rect x="{cx + 3}" y="{iy}" width="{cw - 6}" height="{ih - 2}" rx="2" fill="{fill if ii % 2 == 0 else "white"}" stroke="none"/>')
            parts.append(f'<text x="{cx + cw//2}" y="{iy + ih//2}" text-anchor="middle" font-size="9" fill="#333">{_escape(item)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def gen_tree(spec):
    root = spec["root"]
    title = spec.get("title", "")
    w = spec.get("width", 800); h = spec.get("height", 400)
    parts = [SVG_HEADER,
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    if title:
        parts.append(f'<text x="{w//2}" y="22" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{_escape(title)}</text>')

    def draw(node, x, y, aw):
        fill, stroke, tc = _color(node.get("color", "gray"))
        bw, bh = 120, 32
        parts.append(f'<rect x="{x - bw//2}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x}" y="{y + bh//2}" text-anchor="middle" font-size="9" fill="{tc}">{_escape(node.get("text", ""))}</text>')
        children = node.get("children", [])
        if not children:
            return
        cy = y + bh + 35; n = len(children); cw = aw // n; sx = x - aw // 2 + cw // 2
        for i, child in enumerate(children):
            cx = sx + i * cw
            parts.append(f'<line x1="{x}" y1="{y + bh}" x2="{cx}" y2="{cy}" stroke="#999" stroke-width="1"/>')
            draw(child, cx, cy, cw)

    draw(root, w // 2, 40 if title else 20, w - 80)
    parts.append('</svg>')
    return "\n".join(parts)


def gen_timeline(spec):
    events = spec["events"]
    title = spec.get("title", "")
    w = spec.get("width", 850); h = spec.get("height", 250)
    n = len(events); gap = (w - 80) // n; sx = 40 + gap // 2
    ly = 110 if title else 80
    parts = [SVG_HEADER,
             f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<rect width="{w}" height="{h}" fill="white"/>']
    if title:
        parts.append(f'<text x="{w//2}" y="25" text-anchor="middle" font-size="15" font-weight="bold" fill="#333">{_escape(title)}</text>')
    parts.append(f'<line x1="{sx - 10}" y1="{ly}" x2="{sx + (n-1)*gap + 10}" y2="{ly}" stroke="#999" stroke-width="2"/>')
    for i, ev in enumerate(events):
        x = sx + i * gap
        fill, stroke, tc = _color(ev.get("color", "gray"))
        parts.append(f'<circle cx="{x}" cy="{ly}" r="6" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{ly - 16}" text-anchor="middle" font-size="9" font-weight="bold" fill="{stroke}">{_escape(ev.get("year", ""))}</text>')
        ty = ly + 30 if i % 2 == 0 else ly + 55
        bw = min(90, gap - 10)
        parts.append(f'<rect x="{x - bw//2}" y="{ty}" width="{bw}" height="28" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        parts.append(f'<text x="{x}" y="{ty + 17}" text-anchor="middle" font-size="8" fill="{tc}">{_escape(ev.get("text", ""))}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


GENS = {"layered": gen_layered, "flow": gen_flow, "3col": gen_3col, "tree": gen_tree, "timeline": gen_timeline}

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in GENS:
        print(f"Usage: python3 diagram_generator.py <{'|'.join(GENS.keys())}> <output.svg> < spec.json")
        sys.exit(1)
    spec = json.loads(sys.stdin.read())
    svg = GENS[sys.argv[1]](spec)
    with open(sys.argv[2], "w") as f:
        f.write(svg)
    print(f"OK: {sys.argv[2]}")
