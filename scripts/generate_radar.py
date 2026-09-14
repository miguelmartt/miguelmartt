#!/usr/bin/env python3
"""
Genera un radar chart (SVG) a partir de assets/skills.json, dibujado a mano
(sin matplotlib) para poder animar el trazado con SMIL: la línea se "dibuja"
al cargar la página y el área se rellena progresivamente.
 
Crea: assets/radar-dark.svg y assets/radar-light.svg
 
Uso:
    python3 scripts/generate_radar.py
"""
 
import json
import math
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
SKILLS_FILE = ROOT / "assets" / "skills.json"
 
ACCENT = "#B85040"
SIZE = 420
CENTER = SIZE / 2
MAX_R = 150
MAX_VALUE = 10
RINGS = (2, 4, 6, 8, 10)
 
THEMES = {
    "dark": {"bg": "#0d1117", "grid": "#30363d", "text": "#c9d1d9", "fill_alpha": 0.35},
    "light": {"bg": "#ffffff", "grid": "#d0d7de", "text": "#24292f", "fill_alpha": 0.25},
}
 
 
def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
 
 
def load_skills():
    data = json.loads(SKILLS_FILE.read_text(encoding="utf-8"))
    return data["skills"]
 
 
def point(angle, radius):
    x = CENTER + radius * math.sin(angle)
    y = CENTER - radius * math.cos(angle)
    return x, y
 
 
def polygon_points(values, n):
    pts = []
    for i, v in enumerate(values):
        angle = i / n * 2 * math.pi
        r = (v / MAX_VALUE) * MAX_R
        pts.append(point(angle, r))
    return pts
 
 
def path_length(pts):
    total = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        total += math.hypot(x2 - x1, y1 - y2 if False else y2 - y1)
    return total
 
 
def make_radar_svg(skills: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    labels = list(skills.keys())
    values = list(skills.values())
    n = len(labels)
 
    grid_circles = "".join(
        f'<circle cx="{CENTER}" cy="{CENTER}" r="{(ring / MAX_VALUE) * MAX_R:.1f}" '
        f'fill="none" stroke="{theme["grid"]}" stroke-width="1"/>\n'
        for ring in RINGS
    )
 
    spokes = ""
    label_els = ""
    for i, label in enumerate(labels):
        angle = i / n * 2 * math.pi
        x, y = point(angle, MAX_R)
        spokes += (
            f'<line x1="{CENTER}" y1="{CENTER}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="{theme["grid"]}" stroke-width="1"/>\n'
        )
        lx, ly = point(angle, MAX_R + 28)
        anchor = "middle"
        if lx < CENTER - 5:
            anchor = "end"
        elif lx > CENTER + 5:
            anchor = "start"
        label_els += (
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{theme["text"]}" font-size="12" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif" text-anchor="{anchor}" '
            f'dominant-baseline="middle">{esc(label)} ({values[i]})</text>\n'
        )
 
    pts = polygon_points(values, n)
    poly_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    poly_str_closed = poly_str + f" {pts[0][0]:.1f},{pts[0][1]:.1f}"
    length = path_length(pts)
 
    svg = f'''<svg width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{SIZE}" height="{SIZE}" fill="{theme["bg"]}"/>
  {grid_circles}
  {spokes}
  <polygon points="{poly_str}" fill="{ACCENT}" fill-opacity="0">
    <animate attributeName="fill-opacity" from="0" to="{theme['fill_alpha']}" dur="1s" begin="0.4s" fill="freeze"/>
  </polygon>
  <polyline points="{poly_str_closed}" fill="none" stroke="{ACCENT}" stroke-width="2.5"
            stroke-linejoin="round" stroke-dasharray="{length:.1f}" stroke-dashoffset="{length:.1f}">
    <animate attributeName="stroke-dashoffset" from="{length:.1f}" to="0" dur="1.1s" begin="0s"
             fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" keyTimes="0;1" values="{length:.1f};0"/>
  </polyline>
  {"".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ACCENT}" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{1.1 + i * 0.05:.2f}s" fill="freeze"/></circle>' for i, (x, y) in enumerate(pts))}
  {label_els}
</svg>'''
    return svg
 
 
def main():
    skills = load_skills()
    out_dir = ROOT / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for theme_name in ("dark", "light"):
        svg = make_radar_svg(skills, theme_name)
        out_path = out_dir / f"radar-{theme_name}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"Generado {out_path}")
 
 
if __name__ == "__main__":
    main()
 
