#!/usr/bin/env python3
"""Generate self-hosted GitHub stat cards in the Deep Space 3D style.

Run by .github/workflows/stats.yml with GITHUB_TOKEN. Writes
assets/stats-overview.svg and assets/stats-langs.svg, replacing the
github-readme-stats.vercel.app cards whose shared instance is often
rate-limited (HTTP 503) and rendered as broken images.

Usage:
  python scripts/generate_stats.py                # live data (needs token/API)
  python scripts/generate_stats.py --placeholder  # structure-only cards with
                                                  # em-dash values, committed so
                                                  # the README never 404s before
                                                  # the first workflow run
"""

import html
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone

USER = os.environ.get("STATS_USER", "maitraBishwadip")
API = "https://api.github.com"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

NEON = ["#38BDF8", "#818CF8", "#C084FC", "#7DD3FC", "#A5B4FC", "#D8B4FE"]

# GitHub linguist colors for common languages; fallback is neutral gray.
LANG_COLORS = {
    "Python": "#3572A5", "Java": "#b07219", "Jupyter Notebook": "#DA5B0B",
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#663399", "C++": "#f34b7d", "C": "#555555", "Shell": "#89e051",
    "Dockerfile": "#384d54", "TeX": "#3D6117", "R": "#198CE7",
    "MATLAB": "#e16737", "Go": "#00ADD8", "Kotlin": "#A97BFF",
    "PowerShell": "#012456", "SCSS": "#c6538c", "Vue": "#41b883",
    "Ruby": "#701516", "PHP": "#4F5D95", "Swift": "#F05138",
}


def gh(url):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "profile-stats-generator"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("ACCESS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_live():
    user = gh(f"{API}/users/{USER}")

    repos, page = [], 1
    while True:
        batch = gh(f"{API}/users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]

    stars = sum(r.get("stargazers_count", 0) for r in own)
    forks = sum(r.get("forks_count", 0) for r in own)

    lang_bytes = {}
    for r in own:
        try:
            for lang, n in gh(r["languages_url"]).items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + n
        except Exception:
            continue  # a single repo failing should not kill the card

    commits = None
    try:
        commits = gh(f"{API}/search/commits?q=author:{USER}&per_page=1")["total_count"]
    except Exception:
        pass

    created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    years = max(1, math.floor((datetime.now(timezone.utc) - created).days / 365.25))

    top = sorted(lang_bytes.items(), key=lambda kv: kv[1], reverse=True)[:6]
    total_top = sum(n for _, n in top) or 1
    langs = [(name, 100.0 * n / total_top,
              LANG_COLORS.get(name, "#8B949E")) for name, n in top]

    return {
        "stars": f"{stars:,}", "forks": f"{forks:,}",
        "followers": f"{user.get('followers', 0):,}",
        "repos": f"{user.get('public_repos', 0):,}",
        "years": str(years),
        "commits": None if commits is None else f"{commits:,}",
        "langs": langs,
        "placeholder": False,
    }


def placeholder():
    return {"stars": "—", "forks": "—", "followers": "—", "repos": "—",
            "years": "—", "commits": "—", "langs": [], "placeholder": True}


STYLE = """
    @keyframes fu { from { opacity:0; transform:translateY(8px) }
                    to   { opacity:1; transform:translateY(0) } }
    @keyframes tw { 0%,100% { opacity:.15 } 50% { opacity:.9 } }
    @keyframes bob { 0%,100% { transform:translateY(0) } 50% { transform:translateY(-4px) } }
    .r  { opacity:0; animation: fu .7s ease-out forwards }
    .tw { animation: tw 3s ease-in-out infinite }
    .bob { animation: bob 6s ease-in-out infinite }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important } .r { opacity:1 !important }
    }
"""

DEFS = """
  <defs>
    <linearGradient id="ng" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#38BDF8"/>
      <stop offset="0.5" stop-color="#818CF8"/>
      <stop offset="1" stop-color="#C084FC"/>
    </linearGradient>
  </defs>
"""


def card_shell(title, body, aria):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 240" font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" role="img" aria-label="{html.escape(aria)}">
{DEFS}  <style>{STYLE}  </style>
  <rect x="0.5" y="0.5" width="519" height="239" rx="14" fill="#0B1329" stroke="url(#ng)" stroke-opacity="0.5"/>
  <g fill="#CFE9FF">
    <circle class="tw" cx="428" cy="22" r="1.1"/>
    <circle class="tw" cx="470" cy="46" r="0.8" style="animation-delay:-1.3s"/>
    <circle class="tw" cx="392" cy="38" r="0.9" style="animation-delay:-2.2s"/>
  </g>
  <text x="24" y="38" font-size="16" font-weight="700" letter-spacing="3" fill="url(#ng)">{html.escape(title)}</text>
  <text x="496" y="38" text-anchor="end" font-size="12" fill="#64779A">@{USER}</text>
{body}</svg>
"""


def build_overview(d):
    rows = [("Total Stars Earned", d["stars"]), ("Total Forks", d["forks"]),
            ("Followers", d["followers"]), ("Public Repositories", d["repos"]),
            ("Years on GitHub", d["years"])]
    if d["commits"] is not None:
        rows.append(("Public Commits", d["commits"]))

    body, y = [], 72
    for i, (label, value) in enumerate(rows):
        accent = NEON[i % len(NEON)]
        body.append(f"""  <g class="r" style="animation-delay:{0.1 + 0.12 * i:.2f}s">
    <rect x="26" y="{y - 10}" width="9" height="9" rx="1.5" transform="rotate(45 30.5 {y - 5.5})" fill="{accent}"/>
    <text x="48" y="{y}" font-size="14" fill="#94A9C9">{html.escape(label)}</text>
    <text x="492" y="{y}" text-anchor="end" font-size="15" font-weight="700" fill="#E2E8F0">{html.escape(str(value))}</text>
  </g>""")
        y += 27

    # floating mini isometric cube, echoes the hero banner
    cube = """  <g class="bob" stroke-linejoin="round">
    <polygon points="465,196 481,204 465,212 449,204" fill="#1B2C55" stroke="#38BDF8"/>
    <polygon points="449,204 465,212 465,228 449,220" fill="#0D1830" stroke="#38BDF8"/>
    <polygon points="481,204 465,212 465,228 481,220" fill="#12203F" stroke="#38BDF8"/>
  </g>"""
    return card_shell("GITHUB OVERVIEW", "\n".join(body) + "\n" + cube + "\n",
                      f"GitHub overview statistics for {USER}")


def build_langs(d):
    body = []
    if d["placeholder"] or not d["langs"]:
        body.append("""  <rect x="24" y="58" width="472" height="12" rx="6" fill="#1E293B"/>
  <text x="260" y="120" text-anchor="middle" font-size="14" fill="#94A9C9">first sync runs from GitHub Actions</text>
  <text x="260" y="144" text-anchor="middle" font-size="12" fill="#64779A">check back in a minute</text>""")
    else:
        # stacked bar, clipped to rounded rect so end segments stay rounded
        x, segs = 24.0, []
        for i, (name, pct, color) in enumerate(d["langs"]):
            w = 472.0 * pct / 100.0
            segs.append(f'    <rect class="r" style="animation-delay:{0.1 + 0.1 * i:.2f}s" x="{x:.1f}" y="58" width="{w:.1f}" height="12" fill="{color}"/>')
            x += w
        body.append("""  <clipPath id="bar"><rect x="24" y="58" width="472" height="12" rx="6"/></clipPath>
  <rect x="24" y="58" width="472" height="12" rx="6" fill="#1E293B"/>
  <g clip-path="url(#bar)">
""" + "\n".join(segs) + "\n  </g>")

        for i, (name, pct, color) in enumerate(d["langs"]):
            col, row = i % 2, i // 2
            lx, ly = 24 + col * 248, 104 + row * 34
            body.append(f"""  <g class="r" style="animation-delay:{0.3 + 0.1 * i:.2f}s">
    <circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{color}"/>
    <text x="{lx + 20}" y="{ly}" font-size="13" fill="#E2E8F0">{html.escape(name)}</text>
    <text x="{lx + 224}" y="{ly}" text-anchor="end" font-size="13" fill="#94A9C9">{pct:.1f}%</text>
  </g>""")
        body.append('  <text x="24" y="226" font-size="11" fill="#64779A">top languages by code volume across original repositories</text>')

    return card_shell("LANGUAGE DNA", "\n".join(body) + "\n",
                      f"Most used programming languages for {USER}")


def main():
    data = placeholder() if "--placeholder" in sys.argv else fetch_live()
    os.makedirs(OUT_DIR, exist_ok=True)
    for fname, svg in (("stats-overview.svg", build_overview(data)),
                       ("stats-langs.svg", build_langs(data))):
        path = os.path.join(OUT_DIR, fname)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
