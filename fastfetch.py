"""Render the profile's fastfetch panel to fastfetch-dark.svg / fastfetch-light.svg.

Mirrors the fastfetch panel on abesh.site (portfolio: components/terminal/Fastfetch.tsx).
Stdlib only; run by .github/workflows/fastfetch.yml. GITHUB_TOKEN is optional.
"""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from html import escape

USER = "GeekyAbs"

FACTS = [
    ("NAME", "Abesh Chakraborty"),
    ("OS", "CachyOS x86_64"),
    ("SHELL", "zsh"),
    ("LOCATION", "Kolkata, India"),
    ("EDUCATION", "B.Tech CSE (AI), IEM — 2028"),
    ("CURRENT", "AI Generalist Intern @ Gaudi Engineer"),
    ("FOCUS", "Agents, automation, LLMs, backend"),
    ("STATUS", "Open to AI/ML internship roles"),
    ("SITE", "abesh.site"),
]

# Same tokens as the portfolio's globals.css (dark) plus an inverted light set.
THEMES = {
    "dark": dict(bg="#000000", surface="#141414", line="#2e2e2e", text="#f5f5f5", muted="#a3a3a3", accent="#ffffff"),
    "light": dict(bg="#ffffff", surface="#fafafa", line="#e5e5e5", text="#171717", muted="#737373", accent="#000000"),
}
SWATCHES = ["#000000", "#262626", "#404040", "#525252", "#737373", "#a3a3a3", "#d4d4d4", "#ffffff"]

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
W, PAD = 920, 28
ART_SIZE, ART_LH = 9.5, 11
INFO_X, INFO_SIZE, INFO_LH, VALUE_DX = 450, 14, 24, 112


def github_stats():
    def get(path):
        req = urllib.request.Request(f"https://api.github.com{path}", headers={"Accept": "application/vnd.github+json"})
        if token := os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    user = get(f"/users/{USER}")
    # ponytail: first 100 repos only, paginate if public repos ever exceed that
    repos = get(f"/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(r["stargazers_count"] for r in repos if not r["fork"])
    return f"{user['public_repos']} repos · {stars} stars · {user['followers']} followers"


def load_art():
    lines = open(os.path.join(os.path.dirname(__file__) or ".", "ascii.txt"), encoding="utf-8").read().rstrip().splitlines()
    indent = min(len(l) - len(l.lstrip(" ")) for l in lines if l.strip())
    return [l[indent:].rstrip() for l in lines]


def render(t, art, stats):
    facts = FACTS + [("GITHUB", stats)]
    top = PAD + 46  # below the prompt line
    art_h = len(art) * ART_LH
    info_h = (len(facts) + 4) * INFO_LH
    h = int(top + max(art_h, info_h) + 56)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="abesh@kolkata fastfetch">',
        "<style>",
        f"text{{font-family:{FONT};white-space:pre}}",
        f".p{{fill:{t['muted']};font-size:{INFO_SIZE}px}} .a{{fill:{t['accent']};font-size:{ART_SIZE}px}}",
        f".k{{fill:{t['muted']};font-size:{INFO_SIZE}px}} .v{{fill:{t['text']};font-size:{INFO_SIZE}px}}",
        f".hl{{fill:{t['accent']};font-weight:700}} .b{{fill:{t['accent']};font-size:{INFO_SIZE + 2}px;font-weight:700}}",
        "@keyframes blink{50%{opacity:0}} .cur{animation:blink 1.1s steps(1) infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>',
        f'<text class="p" x="{PAD}" y="{PAD + 14}"><tspan class="hl">abesh@kolkata</tspan> ~ $ fastfetch</text>',
    ]

    out.append(f'<text class="a" xml:space="preserve">')
    for i, line in enumerate(art):
        out.append(f'<tspan x="{PAD}" y="{top + i * ART_LH:.1f}">{escape(line)}</tspan>')
    out.append("</text>")

    y = top + 4 + max(0, (art_h - info_h) // 2)  # info column centred on the portrait
    out.append(f'<text class="b" x="{INFO_X}" y="{y}">abesh</text>')
    out.append(f'<line x1="{INFO_X + 64}" y1="{y - 5}" x2="{W - PAD}" y2="{y - 5}" stroke="{t["line"]}"/>')
    for i, (k, v) in enumerate(facts, start=1):
        yy = y + i * INFO_LH + 8
        cls = "v hl" if k == "STATUS" else "v"
        out.append(f'<text class="k" x="{INFO_X}" y="{yy}">{k}</text>')
        out.append(f'<text class="{cls}" x="{INFO_X + VALUE_DX}" y="{yy}">{escape(v)}</text>')

    sy = y + (len(facts) + 1) * INFO_LH + 4
    for i, c in enumerate(SWATCHES):
        out.append(f'<rect x="{INFO_X + i * 30}" y="{sy}" width="30" height="16" fill="{c}" stroke="{t["line"]}"/>')

    py = h - PAD + 4
    out.append(f'<text class="p" x="{PAD}" y="{py}"><tspan class="hl">abesh@kolkata</tspan> ~ $</text>')
    out.append(f'<rect class="cur" x="{PAD + 17 * INFO_SIZE * 0.6 + 4}" y="{py - INFO_SIZE + 2}" width="{INFO_SIZE * 0.6:.1f}" height="{INFO_SIZE}" fill="{t["accent"]}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    art, stats = load_art(), github_stats()
    for name, theme in THEMES.items():
        svg = render(theme, art, stats)
        ET.fromstring(svg)  # malformed SVG fails the run instead of shipping a broken image
        with open(f"fastfetch-{name}.svg", "w", encoding="utf-8") as f:
            f.write(svg)
    print(stats)
