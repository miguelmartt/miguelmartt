#!/usr/bin/env python3
"""
Genera un banner tipo terminal (SVG animado con SMIL) que "escribe" unas
líneas de comandos al cargar la página, con un cursor parpadeante.
100% hecho a mano en Python, sin dependencias ni servicios externos.

Crea: assets/terminal-dark.svg y assets/terminal-light.svg

Uso:
    python3 scripts/generate_terminal_banner.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 760
LINE_HEIGHT = 26
PADDING_TOP = 52
PADDING_LEFT = 24
CHAR_WIDTH = 9.7  # aproximado para monospace 15px
EXTRA_PAD = 16  # margen extra para que el clip no corte la última letra
ACCENT = "#B85040"

# (texto, color, es_prompt)
LINES = [
    ("$ whoami", "muted", True),
    ("miguelmartt", "accent", False),
    ("$ cat sobre_mi.txt", "muted", True),
    ("Full Stack Developer & Automatizacion de procesos con IA", "text", False),
    ("$ ls stack/", "muted", True),
    ("php  laravel  java  js  html  css  tailwind  mysql  vite", "accent", False),
    ("$ ./disponibilidad.sh", "muted", True),
    ("> Disponible para nuevos proyectos", "green", False),
]

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "window": "#161b22",
        "border": "#30363d",
        "muted": "#8b949e",
        "text": "#c9d1d9",
        "green": "#3fb950",
        "accent": ACCENT,
        "titlebar_text": "#8b949e",
    },
    "light": {
        "bg": "#ffffff",
        "window": "#f6f8fa",
        "border": "#d0d7de",
        "muted": "#57606a",
        "text": "#24292f",
        "green": "#1a7f37",
        "accent": ACCENT,
        "titlebar_text": "#57606a",
    },
}


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def make_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    height = PADDING_TOP + LINE_HEIGHT * len(LINES) + 24

    dots = "".join(
        f'<circle cx="{28 + i * 20}" cy="20" r="6" fill="{color}"/>'
        for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"])
    )

    lines_svg = ""
    t = 0.15
    for i, (text, color_key, is_prompt) in enumerate(LINES):
        y = PADDING_TOP + i * LINE_HEIGHT
        text_w = len(text) * CHAR_WIDTH + EXTRA_PAD
        dur = max(0.35, len(text) * 0.035)
        color = theme[color_key]
        clip_id = f"clip{theme_name}{i}"

        lines_svg += f'''
  <clipPath id="{clip_id}">
    <rect x="0" y="{y - 16}" width="0" height="22">
      <animate attributeName="width" from="0" to="{text_w:.1f}" dur="{dur:.2f}s" begin="{t:.2f}s" fill="freeze"/>
    </rect>
  </clipPath>
  <text x="{PADDING_LEFT}" y="{y}" fill="{color}" font-family="JetBrains Mono, Consolas, monospace"
        font-size="15" clip-path="url(#{clip_id})">{esc(text)}</text>'''

        # cursor that sits at the end of the currently-typing line, then disappears
        cursor_x = PADDING_LEFT + text_w
        lines_svg += f'''
  <rect x="{cursor_x:.1f}" y="{y - 13}" width="8" height="16" fill="{theme['accent']}" opacity="0">
    <animate attributeName="opacity" values="0;1;0;1;0;1;0" keyTimes="0;0.001;0.15;0.3;0.45;0.6;1"
             dur="{dur + 0.6:.2f}s" begin="{t:.2f}s" fill="freeze"/>
  </rect>'''

        t += dur + 0.12

    svg = f'''<svg width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{WIDTH}" height="{height}" rx="10" fill="{theme['window']}" stroke="{theme['border']}"/>
  <rect width="{WIDTH}" height="34" rx="10" fill="{theme['window']}"/>
  <rect y="24" width="{WIDTH}" height="10" fill="{theme['window']}"/>
  {dots}
  <text x="{WIDTH / 2}" y="21" fill="{theme['titlebar_text']}" font-family="Segoe UI, Helvetica, Arial, sans-serif"
        font-size="12" text-anchor="middle">miguelmartt · powershell</text>
  {lines_svg}
</svg>'''
    return svg


def main():
    out_dir = ROOT / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for theme_name in ("dark", "light"):
        svg = make_svg(theme_name)
        out_path = out_dir / f"terminal-{theme_name}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"Generado {out_path}")


if __name__ == "__main__":
    main()
