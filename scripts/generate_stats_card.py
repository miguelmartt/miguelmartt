#!/usr/bin/env python3
"""
Genera una tarjeta de estadísticas de GitHub (SVG) propia, sin depender
de un servicio público de terceros. Usa solo la API pública de GitHub
(no necesita token para datos públicos, aunque se recomienda pasar
GITHUB_TOKEN por variable de entorno para evitar el límite de peticiones).

Crea: assets/card-stats-dark.svg y assets/card-stats-light.svg

Uso:
    GITHUB_TOKEN=xxx python3 scripts/generate_stats_card.py miguelmartt
"""

import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"
ACCENT = "#B85040"

THEMES = {
    "dark": {"bg": "#0d1117", "border": "#30363d", "title": "#c9d1d9", "text": "#8b949e"},
    "light": {"bg": "#ffffff", "border": "#d0d7de", "title": "#24292f", "text": "#57606a"},
}


def gh_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_json(url):
    resp = requests.get(url, headers=gh_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def commit_count(owner, repo, author):
    """Cuenta aproximada de commits de `author` en `repo`, vía el header Link
    de paginación (1 commit por página -> última página = nº de commits)."""
    url = f"{API}/repos/{owner}/{repo}/commits"
    params = {"author": author, "per_page": 1}
    resp = requests.get(url, headers=gh_headers(), params=params, timeout=15)
    if resp.status_code != 200:
        return 0
    link = resp.headers.get("Link", "")
    if 'rel="last"' not in link:
        # 0 o 1 commit
        return len(resp.json())
    for part in link.split(","):
        if 'rel="last"' in part:
            url_part = part.split(";")[0].strip().strip("<>")
            page = url_part.split("page=")[-1]
            try:
                return int(page)
            except ValueError:
                return 0
    return 0


def collect_stats(username):
    user = get_json(f"{API}/users/{username}")
    repos = get_json(f"{API}/users/{username}/repos?per_page=100&type=owner")

    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)

    total_commits = 0
    for r in repos:
        if r.get("fork"):
            continue
        total_commits += commit_count(username, r["name"], username)

    return {
        "Repos públicos": public_repos,
        "Commits (aprox.)": total_commits,
        "Estrellas": stars,
        "Forks": forks,
        "Seguidores": followers,
    }


def render_svg(username, stats, theme_name, out_path):
    theme = THEMES[theme_name]
    width, height = 420, 190
    row_h = 26
    top = 70

    rows = ""
    for i, (label, value) in enumerate(stats.items()):
        y = top + i * row_h
        rows += f'''
    <text x="28" y="{y}" fill="{theme["text"]}" font-size="14">{label}</text>
    <text x="392" y="{y}" fill="{ACCENT}" font-size="14" font-weight="700" text-anchor="end">{value}</text>'''

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Helvetica, Arial, sans-serif">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{theme["bg"]}" stroke="{theme["border"]}"/>
  <text x="28" y="34" fill="{theme["title"]}" font-size="17" font-weight="700">{username} · estadísticas de GitHub</text>
  <line x1="28" y1="46" x2="{width - 28}" y2="46" stroke="{theme["border"]}"/>{rows}
</svg>'''

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    print(f"Generado {out_path}")


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "miguelmartt"
    stats = collect_stats(username)
    render_svg(username, stats, "dark", ROOT / "assets" / "card-stats-dark.svg")
    render_svg(username, stats, "light", ROOT / "assets" / "card-stats-light.svg")


if __name__ == "__main__":
    main()
