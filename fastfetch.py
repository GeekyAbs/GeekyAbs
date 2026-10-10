"""Render the profile's fastfetch panel to fastfetch-dark.svg / fastfetch-light.svg.

Mirrors the fastfetch panel on abesh.site (portfolio: components/terminal/Fastfetch.tsx).
Static, so there's no workflow: edit FACTS or ascii.txt, run `python3 fastfetch.py`, commit.
"""

import os
import xml.etree.ElementTree as ET
from html import escape

FACTS = [
    ("NAME", "Abesh Chakraborty"),
    ("OS", "CachyOS x86_64"),
    ("SHELL", "zsh"),
    ("EDUCATION", "B.Tech CSE (AI), IEM — 2028"),
    ("CURRENT", "AI Generalist Intern @ Gaudi Engineer"),
    ("FOCUS", "Agents, Automation, LLMs,\nMachine Learning, Backend Systems"),
    ("STATUS", "Open to AI/ML internship roles"),
    ("EMAIL", "abeshchakraborty10@gmail.com"),
]

# Same tokens as the portfolio's globals.css (dark) plus an inverted light set.
THEMES = {
    "dark": dict(bg="#000000", line="#2e2e2e", text="#f5f5f5", muted="#a3a3a3", accent="#ffffff"),
    "light": dict(bg="#ffffff", line="#e5e5e5", text="#171717", muted="#737373", accent="#000000"),
}
SWATCHES = ["#000000", "#262626", "#404040", "#525252", "#737373", "#a3a3a3", "#d4d4d4", "#ffffff"]

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
W, PAD = 950, 28
ART_SIZE, ART_LH = 9.5, 11
INFO_X, INFO_SIZE, INFO_LH, VALUE_DX = 450, 14, 24, 112


def load_art():
    lines = open(os.path.join(os.path.dirname(__file__) or ".", "ascii.txt"), encoding="utf-8").read().rstrip().splitlines()
    indent = min(len(l) - len(l.lstrip(" ")) for l in lines if l.strip())
    return [l[indent:].rstrip() for l in lines]


def render(t, art):
    # "\n" in a value continues it on the next row; monospace widths vary by viewer, so long lines overflow
    rows = [(k if j == 0 else "", line) for k, v in FACTS for j, line in enumerate(v.split("\n"))]
    top = PAD + 46  # below the prompt line
    art_h = len(art) * ART_LH
    info_h = (len(rows) + 4) * INFO_LH
    h = int(top + max(art_h, info_h) + PAD - 4)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="abesh@cachyos fastfetch">',
        "<style>",
        f"text{{font-family:{FONT};white-space:pre}}",
        f".p{{fill:{t['muted']};font-size:{INFO_SIZE}px}} .a{{fill:{t['accent']};font-size:{ART_SIZE}px}}",
        f".k{{fill:{t['muted']};font-size:{INFO_SIZE}px}} .v{{fill:{t['text']};font-size:{INFO_SIZE}px}}",
        f".hl{{fill:{t['accent']};font-weight:700}} .b{{fill:{t['accent']};font-size:{INFO_SIZE + 2}px;font-weight:700}}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>',
        f'<text class="p" x="{PAD}" y="{PAD + 14}"><tspan class="hl">abesh@cachyos</tspan> ~ $ fastfetch</text>',
    ]

    out.append('<text class="a" xml:space="preserve">')
    for i, line in enumerate(art):
        out.append(f'<tspan x="{PAD}" y="{top + i * ART_LH:.1f}">{escape(line)}</tspan>')
    out.append("</text>")

    y = top + 4 + max(0, (art_h - info_h) // 2)  # info column centred on the portrait
    out.append(f'<text class="b" x="{INFO_X}" y="{y}">abesh</text>')
    out.append(f'<line x1="{INFO_X + 64}" y1="{y - 5}" x2="{W - PAD}" y2="{y - 5}" stroke="{t["line"]}"/>')
    for i, (k, v) in enumerate(rows, start=1):
        yy = y + i * INFO_LH + 8
        cls = "v hl" if k == "STATUS" else "v"
        out.append(f'<text class="k" x="{INFO_X}" y="{yy}">{k}</text>')
        out.append(f'<text class="{cls}" x="{INFO_X + VALUE_DX}" y="{yy}">{escape(v)}</text>')

    py = y + (len(rows) + 1) * INFO_LH + 16
    out.append(f'<text class="k" x="{INFO_X}" y="{py}">check out my portfolio at <tspan class="hl">abesh.site</tspan></text>')

    sy = py + INFO_LH - 4
    for i, c in enumerate(SWATCHES):
        out.append(f'<rect x="{INFO_X + i * 30}" y="{sy}" width="30" height="16" fill="{c}" stroke="{t["line"]}"/>')

    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    art = load_art()
    for name, theme in THEMES.items():
        svg = render(theme, art)
        ET.fromstring(svg)  # malformed SVG fails loudly instead of committing a broken image
        with open(f"fastfetch-{name}.svg", "w", encoding="utf-8") as f:
            f.write(svg)
